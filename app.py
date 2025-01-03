import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go


# Load the datasets & create parent dataframes
file_path1 = 'Data/Opens_Current_ELO_Ratings.csv'
file_path2 = 'Data/Womens_Current_ELO_Ratings.csv'
file_path3 = 'Data/Opens_Alltime_Tournament_with_ELO_Ratings_Form_H2H.csv'
file_path4 = 'Data/Womens_Alltime_Tournament_with_ELO_Ratings_Form_H2H.csv'
file_path5 = 'Data/Opens_Stats_PER_Top_50.csv'
file_path6 = 'Data/Womens_Stats_PER_Top_50.csv'

opens_current_elo = pd.read_csv(file_path1)
womens_current_elo = pd.read_csv(file_path2)
opens_schedule_h2h = pd.read_csv(file_path3)
womens_schedule_h2h = pd.read_csv(file_path4)
opens_per = pd.read_csv(file_path5)
womens_per = pd.read_csv(file_path6)


################ DATA PREPERATION #################

# Frontpage Elo rankings
opens_current_elo_AUC2024 = (
    opens_current_elo[opens_current_elo['Active'] == 'Y']
    .loc[:, ['Team', 'Elo','AUC24','AUC25 Prediction']]
    .assign(Elo=lambda x: x['Elo'].round(2))
    .sort_values(by='Elo', ascending=False)
)

womens_current_elo_AUC2024 = (
    womens_current_elo[womens_current_elo['Active'] == 'Y']
    .loc[:, ['Team', 'Elo','AUC24','AUC25 Prediction']]
    .assign(Elo=lambda x: x['Elo'].round(2))
    .sort_values(by='Elo', ascending=False)
)


# Win rate calculations womens
w_team_stats = {}
# Looping over the dataframe to update the stats
for index, row in womens_schedule_h2h.iterrows():
    # Extract team names and goals
    team1 = row['team1rough']
    team2 = row['team2rough']
    team1_goals = row['team1_goals']
    team2_goals = row['team2_goals']
    # Initialize team stats if they don't exist
    if team1 not in w_team_stats:
        w_team_stats[team1] = {'games': 0, 'wins': 0}
    if team2 not in w_team_stats:
        w_team_stats[team2] = {'games': 0, 'wins': 0}
    # Increment the games played
    w_team_stats[team1]['games'] += 1
    w_team_stats[team2]['games'] += 1    
    # Determine the winner and increment the wins
    if team1_goals > team2_goals:
        w_team_stats[team1]['wins'] += 1
    elif team2_goals > team1_goals:
        w_team_stats[team2]['wins'] += 1
# Calculate win rate for each team and store in a new DataFrame
w_win_rates = []
for team, stats in w_team_stats.items():
    if stats['games'] > 0:
        win_rate = stats['wins'] / stats['games']
    else:
        win_rate = 0.0  # No games played, no win rate    
    w_win_rates.append({
        'team': team,
        'games_played': stats['games'],
        'games_won': stats['wins'],
        'win_rate': win_rate
    })
# Convert to DataFrame
w_win_rate_df = pd.DataFrame(w_win_rates)
# Filter the w_win_rate_df to only include teams with at least 20 games played, then sorting by team name
w_win_rate_df = w_win_rate_df[w_win_rate_df['games_played'] >= 20]
w_win_rate_df_filtered = w_win_rate_df.sort_values(by='team', ascending=True)
# Sorting by winrate
w_win_rate_df_sorted = w_win_rate_df_filtered.sort_values(by='win_rate', ascending=False)

# Win rate calculations opens
o_team_stats = {}
# Looping over the dataframe to update the stats
for index, row in opens_schedule_h2h.iterrows():
    # Extract team names and goals
    team1 = row['team1rough']
    team2 = row['team2rough']
    team1_goals = row['team1_goals']
    team2_goals = row['team2_goals']    
    # Initialize team stats if they don't exist
    if team1 not in o_team_stats:
        o_team_stats[team1] = {'games': 0, 'wins': 0}
    if team2 not in o_team_stats:
        o_team_stats[team2] = {'games': 0, 'wins': 0}    
    # Increment the games played
    o_team_stats[team1]['games'] += 1
    o_team_stats[team2]['games'] += 1    
    # Determine the winner and increment the wins
    if team1_goals > team2_goals:
        o_team_stats[team1]['wins'] += 1
    elif team2_goals > team1_goals:
        o_team_stats[team2]['wins'] += 1
# Calculate win rate for each team and store in a new DataFrame
o_win_rates = []
for team, stats in o_team_stats.items():
    if stats['games'] > 0:
        win_rate = stats['wins'] / stats['games']
    else:
        win_rate = 0.0  # No games played, no win rate    
    o_win_rates.append({
        'team': team,
        'games_played': stats['games'],
        'games_won': stats['wins'],
        'win_rate': win_rate
    })
# Convert to DataFrame
o_win_rate_df = pd.DataFrame(o_win_rates)
# Filter the w_win_rate_df to only include teams with at least 20 games played, then sorting by team name
o_win_rate_df = o_win_rate_df[o_win_rate_df['games_played'] >= 20]
o_win_rate_df_filtered = o_win_rate_df.sort_values(by='team', ascending=True)
# Sorting by winrate
o_win_rate_df_sorted = o_win_rate_df_filtered.sort_values(by='win_rate', ascending=False)


# Elo tracking womens
# Initialize an Elo dictionary to track the Elo over time for each team
w_team_elo = {}
# List to keep track of the Elo progression for plotting
w_elo_progression = []
# Iterate through the dataframe and track Elo changes
for index, row in womens_schedule_h2h.iterrows():
    team1 = row['team1rough']
    team2 = row['team2rough']
    
    # Ensure Elo for each team starts fresh at the beginning of the year
    if team1 not in w_team_elo or row['year'] not in w_team_elo[team1]:
        # Set initial Elo for the first game of the year
        w_team_elo[team1] = {row['year']: row['team1_ELO_before']}
    if team2 not in w_team_elo or row['year'] not in w_team_elo[team2]:
        # Set initial Elo for the first game of the year
        w_team_elo[team2] = {row['year']: row['team2_ELO_before']}
    
    # Get the Elo for both teams before the game
    o_team1_elo_before = w_team_elo[team1][row['year']]
    o_team2_elo_before = w_team_elo[team2][row['year']]
    
    # Record Elo after the game for team1 (in one row)
    w_elo_progression.append({
        'date': row['date'],
        'team': team1,
        'elo': row['team1_ELO_after'],  # Save Elo after the match
    })
    
    # Record Elo after the game for team2 (in a separate row)
    w_elo_progression.append({
        'date': row['date'],
        'team': team2,
        'elo': row['team2_ELO_after'],  # Save Elo after the match
    })
    
    # Update Elo after the match for both teams (using after Elo values)
    w_team_elo[team1][row['year']] = row['team1_ELO_after']
    w_team_elo[team2][row['year']] = row['team2_ELO_after']
# Convert the list into a DataFrame for easier plotting
w_elo_df = pd.DataFrame(w_elo_progression)
# Ensure date is in datetime format for sorting and plotting
w_elo_df['date'] = pd.to_datetime(w_elo_df['date'])
# Create a 'year' column based on the 'date' column
w_elo_df['year'] = w_elo_df['date'].dt.year


# Elo tracking opens
# Initialize an Elo dictionary to track the Elo over time for each team
o_team_elo = {}
# List to keep track of the Elo progression for plotting
o_elo_progression = []
# Iterate through the dataframe and track Elo changes
for index, row in opens_schedule_h2h.iterrows():
    team1 = row['team1rough']
    team2 = row['team2rough']
    
    # Ensure Elo for each team starts fresh at the beginning of the year
    if team1 not in o_team_elo or row['year'] not in o_team_elo[team1]:
        # Set initial Elo for the first game of the year
        o_team_elo[team1] = {row['year']: row['team1_ELO_before']}
    if team2 not in o_team_elo or row['year'] not in o_team_elo[team2]:
        # Set initial Elo for the first game of the year
        o_team_elo[team2] = {row['year']: row['team2_ELO_before']}
    
    # Get the Elo for both teams before the game
    o_team1_elo_before = o_team_elo[team1][row['year']]
    o_team2_elo_before = o_team_elo[team2][row['year']]
    
    # Record Elo after the game for team1 (in one row)
    o_elo_progression.append({
        'date': row['date'],
        'team': team1,
        'elo': row['team1_ELO_after'],  # Save Elo after the match
    })
    
    # Record Elo after the game for team2 (in a separate row)
    o_elo_progression.append({
        'date': row['date'],
        'team': team2,
        'elo': row['team2_ELO_after'],  # Save Elo after the match
    })
    
    # Update Elo after the match for both teams (using after Elo values)
    o_team_elo[team1][row['year']] = row['team1_ELO_after']
    o_team_elo[team2][row['year']] = row['team2_ELO_after']
# Convert the list into a DataFrame for easier plotting
o_elo_df = pd.DataFrame(o_elo_progression)
# Ensure date is in datetime format for sorting and plotting
o_elo_df['date'] = pd.to_datetime(o_elo_df['date'])
# Create a 'year' column based on the 'date' column
o_elo_df['year'] = o_elo_df['date'].dt.year


# Womens PER Workings
# Team name mapping
womens_team_names_PER = {
    "ELLW2019": "Ellipsis 2019",
    "ELLW2018": "Ellipsis 2018",
    "ELLW2021": "Ellipsis 2021",
    "ELL&2022": "Ellipsis Ampersand 2022",
    "ELL&2023": "Ellipsis Ampersand 2023",
    "GWSB2018": "GWS Blaze 2018",
    "MANU2019": "Manly Ultimate 2019",
    "MANR2021": "Manly Ripped 2021",
    "ELL*2022": "Ellipsis Asterisk 2022",
    "ELL*2023": "Ellipsis Asterisk 2023",
    "ELL*2024": "Ellipsis Asterisk 2024",
    "ELL&2024": "Ellipsis Ampersand 2024",
}
womens_per['team'] = womens_per['team'].map(womens_team_names_PER)
# Column retitling for cleaner headings
womens_per = womens_per.rename(columns={'OVR_PER': 'PER',
                                        'OVR_PER_PerPoint': 'PER Per Point',
                                        'Points played total': 'Points',
                                        'Defensive blocks': 'Blocks',
                                        'team': 'Team',
                                        'Off_PlusMinus':'Off. Plus Minus',
                                        'Def_PlusMinus':'Def. Plus Minus',
                                        'Total completed throw distance (m)':'Throw Distance (m)', 
                                        'Total caught pass distance (m)':'Receive Distance (m)',
                                        'eff_pulls':'Effective Pulls',
                                        })


# Opens PER Workings
# Team name mapping
opens_team_names_PER = {
    "COLM2019": "Colony Mutiny 2019",
    "COLP2018": "Colony Plunder 2018",
    "ELLM2021": "Ellipsis Men 2021",
    "ELLM2022": "Ellipsis Men 2022",
    "ELLM2023": "Ellipsis Men 2023",
    "MAMU2018": "Mammoth Ultimate 2018",
    "MAMU2019": "Mammoth Ultimate 2019",
    "SUNS2021": "Sunder Slice 2021",
    "SUNS2022": "Sunder Slice 2022",
    "SUND2023": "Sunder Dice 2023",
    "ELLM2024": "Ellipsis Men 2024",
    "SUNS2024": "Sunder Slice 2024",
}
opens_per['team'] = opens_per['team'].map(opens_team_names_PER)
# Column retitling for cleaner headings
opens_per = opens_per.rename(columns={'OVR_PER': 'PER',
                                        'OVR_PER_PerPoint': 'PER Per Point',
                                        'Points played total': 'Points',
                                        'Defensive blocks': 'Blocks',
                                        'team': 'Team',
                                        'Off_PlusMinus':'Off. Plus Minus',
                                        'Def_PlusMinus':'Def. Plus Minus',
                                        'Total completed throw distance (m)':'Throw Distance (m)', 
                                        'Total caught pass distance (m)':'Receive Distance (m)',
                                        'eff_pulls':'Effective Pulls',
                                        })


################ IMAGE WORKINGS #################

# Dictionary of image links for each AUC team
team_image_links = {
    "Ellipsis Men": "https://d36m266ykvepgv.cloudfront.net/uploads/media/bK7BbFw4L1/c-160-160/th-1.jpg",
    "Ellipsis Ampersand": "https://d36m266ykvepgv.cloudfront.net/uploads/media/bK7BbFw4L1/c-160-160/th-1.jpg",
    "Ellipsis Asterisk": "https://d36m266ykvepgv.cloudfront.net/uploads/media/bK7BbFw4L1/c-160-160/th-1.jpg",
    "Ellipsis Pilcrow": "https://d36m266ykvepgv.cloudfront.net/uploads/media/bK7BbFw4L1/c-160-160/th-1.jpg",
    "Sunder Slice": "https://d36m266ykvepgv.cloudfront.net/uploads/media/TGYjv5thjP/c-200-200/screenshot-2024-10-08-at-4-38-56-pm.png",
    "Sunder Dice": "https://d36m266ykvepgv.cloudfront.net/uploads/media/TGYjv5thjP/c-200-200/screenshot-2024-10-08-at-4-38-56-pm.png",
    "Manly Mullets":"https://d36m266ykvepgv.cloudfront.net/uploads/media/Nhz4yuMML7/c-172-160/mufl-logo-2019-female-square2-3.png",
    "Manly Mavericks":"https://d36m266ykvepgv.cloudfront.net/uploads/media/Nhz4yuMML7/c-172-160/mufl-logo-2019-female-square2-3.png",
    "Newcastle I-Beam":"https://d36m266ykvepgv.cloudfront.net/uploads/media/3ytKb9Wgba/c-198-160/ibeam1-1.gif",
    "Melbourne Juggernaut":"https://d36m266ykvepgv.cloudfront.net/uploads/media/5RUvk0cH0M/c-174-160/hoslogo.png",
    "Krank":"https://d36m266ykvepgv.cloudfront.net/uploads/media/J1xeSJsjiy/c-160-160/krank-fist.png",
    "Mammoth":"https://d36m266ykvepgv.cloudfront.net/uploads/media/C9yElXlfvL/c-160-160/mammoth.png",
    "Fyshwick United":"https://d36m266ykvepgv.cloudfront.net/uploads/media/AkktUCyJpC/c-114-160/fu-clean.png",
    "Outbreak Mountain":"https://d36m266ykvepgv.cloudfront.net/uploads/media/SjUFfjWA0E/c-160-160/inbound1408309028079138953.jpg",  
    "Hot Chilly":"https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR0nIAmLFyPSlT0tOfZ7JKwBzQ1h0n0tfmM_w&s",
    "Spicy Chilly":"https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR0nIAmLFyPSlT0tOfZ7JKwBzQ1h0n0tfmM_w&s",
    "Sublime Ultimate Club":"https://d36m266ykvepgv.cloudfront.net/uploads/media/i4WHiyNcmw/c-164-160/165428-572233972810084-262051925-n.png",  
    "Fuse":"https://d36m266ykvepgv.cloudfront.net/uploads/media/r2GF1RBzX6/c-127-80/fuse-logo.png",
    "Factory Flash":"https://d36m266ykvepgv.cloudfront.net/uploads/media/fMH49WHSt3/c-160-160/factory-logo-2.png",
    "Kaos":"https://d36m266ykvepgv.cloudfront.net/uploads/media/bcH8XURKPg/c-185-160/kaos-ultimate-logo.jpg",
    "GWS Blaze":"https://d36m266ykvepgv.cloudfront.net/uploads/media/HI7PfARWoW/c-162-160/blaze-profpic.jpg",
    "Rogue":"https://d36m266ykvepgv.cloudfront.net/uploads/media/GqcFy3PtOA/c-160-160/rogue-logo.png",
    "Zig Theory":"https://d36m266ykvepgv.cloudfront.net/uploads/media/Vh8ZZFJXdd/c-160-160/zig-theory-logo.jpg",
    "Melbourne Phoenix":"https://d36m266ykvepgv.cloudfront.net/uploads/media/5RUvk0cH0M/c-174-160/hoslogo.png",
    "NSU Aurora":"https://d36m266ykvepgv.cloudfront.net/uploads/media/w1LcQPWkVe/c-174-160/nsu-logo-1.jpg",
    "Surge":"https://d36m266ykvepgv.cloudfront.net/uploads/media/DgICPvDdQB/c-160-160/12788206-10101839154706327-327686883-n.jpg"
}

# Dictionary of image links for the ELO Formulas
elo_formula_image_links = {
    "Elo Prediction": "https://unity-technologies.github.io/ml-agents/images/elo_expected_score_formula.png",
    "Elo Update": "https://unity-technologies.github.io/ml-agents/images/elo_score_update_formula.png"
}

# Map image links to the DataFrame
opens_current_elo_AUC2024['Club'] = opens_current_elo_AUC2024['Team'].map(team_image_links)
# Reorder columns to make 'club image' the second column
opens_current_elo_AUC2024 = opens_current_elo_AUC2024[['Team', 'Club', 'Elo','AUC25 Prediction']]

# Map image links to the DataFrame
womens_current_elo_AUC2024['Club'] = womens_current_elo_AUC2024['Team'].map(team_image_links)
# Reorder columns to make 'club image' the second column
womens_current_elo_AUC2024 = womens_current_elo_AUC2024[['Team', 'Club', 'Elo','AUC25 Prediction']]


################ TEXT WORKINGS #################
elo_AUC_summary = """
Updated after every tournament. Elo rankings and predicted AUC result may differ depending on AUC seedings & pools.
"""

elo_explanation_1 = """
ELO ratings are a ranking system used to calculate the relative skill levels of players in two-player games most commonly chess, but they can also be applied to sports. Named after Hungarian-American chess player Arpad Elo, the system works by assigning a numerical rating to each player or team based on their performance against other rated players/teams.

In the AUC system, each competing team has been assigned a numerical Elo rating after they play their first game on the Australian Ultimate Championship calendar. Division 1 teams were set at 1500, Division 2 at 1000. The data used for the Elo rankings was pulled from AUC calendar tournaments dating from January 2017.

The standard Elo formula for updating a team's rating is outlined in the picture below. 
"""

elo_explanation_2 = """
The AUC version has a few considerations and modifications:
    
1. **Strength of Squad:** AUC Division 1 Teams were assessed on the strength of the playing squad at each tournament, and marked into one of 3 categories; full strength, mid strength, low strength. This was used as a factor for a team's performance as an indicator of true strength, and adjusted the Elo points gained or lost.
2. **Strength of Win:** A larger score difference between the 2 teams will result in greater Elo changes.
3. **Tournament Significance:** Tournaments on the AUC calendar were assessed on their importance to the playing cohort. Division 1 & 2 Nationals were marked as the most significant, followed by State Championships and then lastly all other warm-up tournaments. Results at more significant tournaments have a greater impact on Elo rating updates.
4. **Changing Squads:** AUC teams have player turnover each year, the Elo point total of a squad from 2023 at the end of the season should not be wholly attributed to the 2024 team. At the beginning of each new season a team's Elo was adjusted towards the mean rating for the Division the team placed, in the previous year.
5. **Teams on the Rise/Fall:** Teams which have recently moved from Division 2 to Division 1 (or vice versa), have a greater K factor. Allowing teams that are improving quickly to have larger Elo increases, or teams which have fallen off to have bigger decreases reflecting current strength quicker.
"""

predictions_explanation ="""
Elo ratings are used to calculate win probabilities leading into each Division 1 Nationals game. For a game between two teams (A and B), Team A's probability of winning is calculated using the below standard Elo expected score formula with two inclusions:

1. **10 Game Form:** Team's that are on a win streak or just performing well recently are more likely to keep winning.
2. **Head-to-Head Performance:** Team's which have a good a head-to-head record against their opposition should be favoured slightly.

The Nationals games are then mocked-up using Monte Carlo simulations, which runs the pool match-ups thousands of times to predict the scores of the two teams and deem a winner. After completing this for all pool games at Nationals the top 8 teams are put into bracket play and the winner determined. Importantly, the simulated games keep track of Elo changes which would have occured based on the results and they are used in any forecasted matches a team may have.
"""

PER_explanation ="""
The top 50 performances from an individual in an Australian Ultimate Championship Grand Final as ranked by PER. 
The data pool is currently consists of the finals spanning from 2018 to 2024, this will be updated each new final.
"""


################ WEBSITE LAYOUT #################
# Start the Streamlit app layout
st.set_page_config(page_title="AUC Elo Rankings", layout="wide")

def Rankings():
    st.title("Australian Ultimate Championships: Elo Rankings & Predictions")

    st.write(elo_AUC_summary)
    
    # Create two columns for the dataframes
    col1, col2 = st.columns(2)

    # Map image links to the DataFrame for Opens
    opens_current_elo_AUC2024['Club'] = opens_current_elo_AUC2024['Team'].map(
        lambda team: f'<img src="{team_image_links.get(team, "")}" width="20" height="20" />'
    )

    # Map image links to the DataFrame for Opens
    womens_current_elo_AUC2024['Club'] = womens_current_elo_AUC2024['Team'].map(
        lambda team: f'<img src="{team_image_links.get(team, "")}" width="20" height="20" />'
    )

    table_style = """
    <style>
    table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 20px;
    }
    th, td {
        padding: 8px;
        text-align: left;
        border-bottom: 1px solid #ddd;
    }
    th {
        background-color: #f2f2f2;
        font-weight: bold;
    }
    tr:hover {
        background-color: #f5f5f5;
    }
    img {
        border-radius: 50%;
        width: 30px;
        height: 30px;
        object-fit: cover;
    }
    h5 {
        margin-bottom: 0px;  /* Remove bottom margin from titles */
        padding-bottom: 0px;  /* Remove padding below titles */
    }
    </style>
"""
    # Inject the CSS to style the tables
    st.markdown(table_style, unsafe_allow_html=True)

    # Now, displaying the tables with enhanced styling
    with col1:
        st.markdown("##### Open's Predictions")
        st.markdown(opens_current_elo_AUC2024.reset_index(drop=True).to_html(escape=False, index=False), unsafe_allow_html=True)

    with col2:
        st.markdown("##### Women's Predictions")
        st.markdown(womens_current_elo_AUC2024.reset_index(drop=True).to_html(escape=False, index=False), unsafe_allow_html=True)

        
def Elo_Explanation():
    st.title("Elo Explanation")

    st.subheader("AUC Team Elo Ratings")
    st.write(elo_explanation_1)
    st.image(elo_formula_image_links["Elo Update"], caption="Updating Elo post match", width=500)
    st.write(elo_explanation_2)
       
    st.subheader("Predictions")
    st.write(predictions_explanation)
    st.image(elo_formula_image_links["Elo Prediction"], caption="Elo Prediction", width=500)

def Opens_Win_Rates():
    st.title("Opens Win Rates")

    # Dropdown to select a single team, including the "All" option
    team_selected = st.selectbox("Select a team to view their win rate stats:", 
                                 ["All"] + sorted(o_win_rate_df_filtered['team'].tolist()))

    
    # If "All" is selected, we want to show all bars in the same color (no highlighting)
    if team_selected == "All":
        o_win_rate_df_sorted['color'] = 'lightgray'  # No highlights, all bars in light gray
    else:
        # Create a new column 'color' for conditional coloring based on team selection
        o_win_rate_df_sorted['color'] = o_win_rate_df_sorted['team'].apply(
            lambda team: 'blue' if team == team_selected else 'lightgray'  # Highlight the selected team
        )

    o_bar_all = px.bar(o_win_rate_df_sorted, 
             x='team', 
             y='win_rate', 
             title='Win Rate by Team',
             labels={'win_rate': 'Win Rate', 'team': 'Team'},
             color='win_rate',  
             color_continuous_scale='cividis',
             hover_data={'games_played': True, 'games_won': True})
   
    # Create the Bar Plot using plotly.graph_objects
    o_bar_team = go.Figure()

    # Add bars for the sorted win rates
    o_bar_team.add_trace(go.Bar(
        x=o_win_rate_df_sorted['team'],  # Team names
        y=o_win_rate_df_sorted['win_rate'],  # Win rates
        marker=dict(color=o_win_rate_df_sorted['color']),  # Color based on the 'color' column
        hovertext=o_win_rate_df_sorted['team'] + "<br>Games Played: " + o_win_rate_df_sorted['games_played'].astype(str) + "<br>Games Won: " + o_win_rate_df_sorted['games_won'].astype(str),
        hoverinfo='text'
    ))

    # Update layout (adjusting the chart for better visuals)
    o_bar_team.update_layout(
        title="Win Rate by Team (Comparison)",
        xaxis_title="Team",
        yaxis_title="Win Rate",
        coloraxis_showscale=False,  # Disable color scale legend
        xaxis_tickangle=-45,  # Tilt the x-axis labels for readability
        showlegend=False  # Hide the legend
    )

    # Add a description and show details for the selected team
    if team_selected == "All":
        st.plotly_chart(o_bar_all)

    # Add a description and show details for the selected team
    if team_selected != "All":
        st.subheader(f"Win Statistics for {team_selected}")
        team_details = o_win_rate_df_sorted[o_win_rate_df_sorted['team'] == team_selected]
        # Update column names and reset index
        team_details = team_details[['team', 'games_played', 'games_won', 'win_rate']].reset_index(drop=True)
        # Rename columns to more user-friendly names
        team_details = team_details.rename(columns={
            'team': 'Team',
            'games_played': 'Games Played',
            'games_won': 'Games Won',
            'win_rate': 'Win Rate'
        })
        # Format the 'win_rate' column as percentage
        team_details['Win Rate'] = (team_details['Win Rate'] * 100).round(2).astype(str) + '%'
        # Display the table without the index and with updated column names
        st.dataframe(team_details,hide_index=True)
        # Show the chart
        st.plotly_chart(o_bar_team)
    
def Womens_Win_Rates():
    st.title("Womens Win Rates")
     
    # Dropdown to select a single team, including the "All" option
    team_selected = st.selectbox("Select a team to view their win rate stats:", 
                                 ["All"] + sorted(w_win_rate_df_filtered['team'].tolist()))

    
    # If "All" is selected, we want to show all bars in the same color (no highlighting)
    if team_selected == "All":
        w_win_rate_df_sorted['color'] = 'lightgray'  # No highlights, all bars in light gray
    else:
        # Create a new column 'color' for conditional coloring based on team selection
        w_win_rate_df_sorted['color'] = w_win_rate_df_sorted['team'].apply(
            lambda team: 'gold' if team == team_selected else 'lightgray'  # Highlight the selected team
        )

    w_bar_all = px.bar(w_win_rate_df_sorted, 
             x='team', 
             y='win_rate', 
             title='Win Rate by Team',
             labels={'win_rate': 'Win Rate', 'team': 'Team'},
             color='win_rate',  
             color_continuous_scale='Viridis',
             hover_data={'games_played': True, 'games_won': True})
   
    # Create the Bar Plot using plotly.graph_objects
    w_bar_team = go.Figure()

    # Add bars for the sorted win rates
    w_bar_team.add_trace(go.Bar(
        x=w_win_rate_df_sorted['team'],  # Team names
        y=w_win_rate_df_sorted['win_rate'],  # Win rates
        marker=dict(color=w_win_rate_df_sorted['color']),  # Color based on the 'color' column
        hovertext=w_win_rate_df_sorted['team'] + "<br>Games Played: " + w_win_rate_df_sorted['games_played'].astype(str) + "<br>Games Won: " + w_win_rate_df_sorted['games_won'].astype(str),
        hoverinfo='text'
    ))

    # Update layout (adjusting the chart for better visuals)
    w_bar_team.update_layout(
        title="Win Rate by Team (Comparison)",
        xaxis_title="Team",
        yaxis_title="Win Rate",
        coloraxis_showscale=False,  # Disable color scale legend
        xaxis_tickangle=-45,  # Tilt the x-axis labels for readability
        showlegend=False  # Hide the legend
    )

    # Add a description and show details for the selected team
    if team_selected == "All":
        st.plotly_chart(w_bar_all)

    # Add a description and show details for the selected team
    if team_selected != "All":
        st.subheader(f"Win Statistics for {team_selected}")
        team_details = w_win_rate_df_sorted[w_win_rate_df_sorted['team'] == team_selected]
        # Update column names and reset index
        team_details = team_details[['team', 'games_played', 'games_won', 'win_rate']].reset_index(drop=True)
        # Rename columns to more user-friendly names
        team_details = team_details.rename(columns={
            'team': 'Team',
            'games_played': 'Games Played',
            'games_won': 'Games Won',
            'win_rate': 'Win Rate'
        })
        # Format the 'win_rate' column as percentage
        team_details['Win Rate'] = (team_details['Win Rate'] * 100).round(2).astype(str) + '%'
        # Display the table without the index and with updated column names
        st.dataframe(team_details,hide_index=True)
        # Show the chart
        st.plotly_chart(w_bar_team)     

def Opens_Elo():
    st.title("Opens Historical Elo Rankings")

    # Streamlit multiselect for team selection, sorted alphabetically
    o_team_options = sorted(o_elo_df['team'].unique())  # Sort team names alphabetically
    o_selected_teams = st.multiselect("Select teams to compare", o_team_options)

    # Add dropdown for selecting a single year
    o_year_options = sorted(o_elo_df['year'].unique())  # Get unique years from the data
    o_selected_year = st.selectbox(
        "Select a year", 
        o_year_options,  # Options are the years from the data
        index=len(o_year_options)-1  # Default to the most recent year
    )

    # Filter the data based on selected year
    o_filtered_data = o_elo_df[(o_elo_df['year'] == o_selected_year)]
    
    # Create a 'game_number' column that counts only the games played in the selected year for each team
    o_filtered_data['game_number'] = o_filtered_data.groupby(['team', 'year']).cumcount() + 1

    # Plotting for selected teams and filtered data by year and time period
    if o_selected_teams:
        o_elo_fig = go.Figure()

        # Loop through each selected team and add to the plot
        for team in o_selected_teams:
            o_team_elo_df = o_filtered_data[o_filtered_data['team'] == team]
            o_elo_fig.add_trace(go.Scatter(
                x=o_team_elo_df['game_number'],  # Use game_number for x-axis
                y=o_team_elo_df['elo'],
                mode='lines+markers',
                name=team,
                line=dict(width=2),
                marker=dict(size=5)
            ))

        # Customize plot layout
        o_elo_fig.update_layout(
            title=f"Elo Rankings (Year: {o_selected_year})",
            xaxis_title=f"Recorded Games Played in {o_selected_year}",
            yaxis_title="Elo Rating",
            template="plotly_dark",
            showlegend=True,
            xaxis=dict(
                tickmode='linear',  # Continuous numbering for games
                tick0=1,  # Start from game 1
                dtick=1,  # Show every game number as a tick
            )
        )

        # Display the plot
        st.plotly_chart(o_elo_fig)
    else:
        st.write("Please select at least one team to compare.")

def Womens_Elo():
    st.title("Womens Historical Elo Rankings")

    # Streamlit multiselect for team selection, sorted alphabetically
    w_team_options = sorted(w_elo_df['team'].unique())  # Sort team names alphabetically
    w_selected_teams = st.multiselect("Select teams to compare", w_team_options)

    # Add dropdown for selecting a single year
    w_year_options = sorted(w_elo_df['year'].unique())  # Get unique years from the data
    w_selected_year = st.selectbox(
        "Select a year", 
        w_year_options,  # Options are the years from the data
        index=len(w_year_options)-1  # Default to the most recent year
    )

    # Filter the data based on selected year and time period (January 1 - April 30)
    w_filtered_data = w_elo_df[(w_elo_df['year'] == w_selected_year)]
    
    # Create a 'game_number' column that counts only the games played in the selected year for each team
    w_filtered_data['game_number'] = w_filtered_data.groupby(['team', 'year']).cumcount() + 1

    # Plotting for selected teams and filtered data by year and time period
    if w_selected_teams:
        w_elo_fig = go.Figure()

        # Loop through each selected team and add to the plot
        for team in w_selected_teams:
            w_team_elo_df = w_filtered_data[w_filtered_data['team'] == team]
            w_elo_fig.add_trace(go.Scatter(
                x=w_team_elo_df['game_number'],  # Use game_number for x-axis
                y=w_team_elo_df['elo'],
                mode='lines+markers',
                name=team,
                line=dict(width=2),
                marker=dict(size=5)
            ))

        # Customize plot layout
        w_elo_fig.update_layout(
            title=f"Elo Rankings (Year: {w_selected_year})",
            xaxis_title=f"Recorded Games Played in {w_selected_year}",
            yaxis_title="Elo Rating",
            template="plotly_dark",
            showlegend=True,
            xaxis=dict(
                tickmode='linear',  # Continuous numbering for games
                tick0=1,  # Start from game 1
                dtick=1,  # Show every game number as a tick
            )
        )

        # Display the plot
        st.plotly_chart(w_elo_fig)
    else:
        st.write("Please select at least one team to compare.")

def Opens_PER():
    st.title("Opens Player Efficiency Ratings")
    st.write(PER_explanation)
    st.markdown('For a more detailed breakdown of the PER formula check out my article on [Medium](https://medium.com/@mshudson9/a-new-per-for-ultimate-3691b2f9cb88)')
    
    # Dropdown for searching by Player or Team
    search_type = st.selectbox("Search by", ["Player", "Team"])

    # For Player search, add 'All' option to the dropdown
    if search_type == "Player":
        player_list = sorted(list(opens_per['Player'].unique()))  # Sort player list alphabetically
        player_list = ["All"] + player_list  # Add "All" to the top of the list
        player_name = st.selectbox("Select Player", player_list)
        if player_name == "All":
            filtered_data_per = opens_per
        else:
            filtered_data_per = opens_per[opens_per['Player'] == player_name]

    # For Team search, no 'All' option, just the list of teams
    elif search_type == "Team":
        team_list = sorted(list(opens_per['Team'].unique()))  # Sort team list alphabetically
        team_name = st.selectbox("Select Team", team_list)
        filtered_data_per = opens_per[opens_per['Team'] == team_name]

    # Dropdown for selecting Box Score or Advanced Stats
    stats_type = st.selectbox("Select Stats View", ["Box Score", "Advanced Stats"])

    # Displaying the filtered summary with selected columns
    if not filtered_data_per.empty:
        st.write("### Player/Team Summary")
        
        # Define columns for Box Score and Advanced Stats
        if stats_type == "Box Score":
            summary_columns = ['Player', 'Team', 'PER', 'Points', 'Goals', 'Assists', 'Blocks', 'Turnovers', 'Effective Pulls']
        elif stats_type == "Advanced Stats":
            summary_columns = ['Player', 'Team', 'PER', 'Points', 'PER Per Point', 'Off. Plus Minus', 'Def. Plus Minus', 'Throw Distance (m)', 'Receive Distance (m)']
    
        st.dataframe(filtered_data_per[summary_columns], hide_index=True)
    else:
        st.write("No data found for the selected option.")

def Womens_PER():
    st.title("Womens Player Efficiency Ratings")
    st.write(PER_explanation)
    st.markdown('For a more detailed breakdown of the PER formula check out my article on [Medium](https://medium.com/@mshudson9/a-new-per-for-ultimate-3691b2f9cb88)')
    
    # Dropdown for searching by Player or Team
    search_type = st.selectbox("Search by", ["Player", "Team"])

    # For Player search, add 'All' option to the dropdown
    if search_type == "Player":
        player_list = sorted(list(womens_per['Player'].unique()))  # Sort player list alphabetically
        player_list = ["All"] + player_list  # Add "All" to the top of the list
        player_name = st.selectbox("Select Player", player_list)
        if player_name == "All":
            filtered_data_per = womens_per
        else:
            filtered_data_per = womens_per[womens_per['Player'] == player_name]

    # For Team search, no 'All' option, just the list of teams
    elif search_type == "Team":
        team_list = sorted(list(womens_per['Team'].unique()))  # Sort team list alphabetically
        team_name = st.selectbox("Select Team", team_list)
        filtered_data_per = womens_per[womens_per['Team'] == team_name]

    # Dropdown for selecting Box Score or Advanced Stats
    stats_type = st.selectbox("Select Stats View", ["Box Score", "Advanced Stats"])

    # Displaying the filtered summary with selected columns
    if not filtered_data_per.empty:
        st.write("### Player/Team Summary")
        
        # Define columns for Box Score and Advanced Stats
        if stats_type == "Box Score":
            summary_columns = ['Player', 'Team', 'PER', 'Points', 'Goals', 'Assists', 'Blocks', 'Turnovers', 'Effective Pulls']
        elif stats_type == "Advanced Stats":
            summary_columns = ['Player', 'Team', 'PER', 'Points', 'PER Per Point', 'Off. Plus Minus', 'Def. Plus Minus', 'Throw Distance (m)', 'Receive Distance (m)']
    
        st.dataframe(filtered_data_per[summary_columns], hide_index=True)
    else:
        st.write("No data found for the selected option.")
   
pages = {
    "Elo & Predictions": [
        st.Page(Rankings, title="Live Rankings"),
        st.Page(Elo_Explanation),
    ],
    "Opens Dashboard": [
        st.Page(Opens_Win_Rates, title="Win Rates"),
        st.Page(Opens_Elo, title="Historical Elo"),
        st.Page(Opens_PER, title="PER"),
    ],
    "Womens Dashboard": [
        st.Page(Womens_Win_Rates, title="Win Rates"),
        st.Page(Womens_Elo, title="Historical Elo"),
        st.Page(Womens_PER, title="PER"),
    ],
}


page = st.navigation(pages) 
page.run()
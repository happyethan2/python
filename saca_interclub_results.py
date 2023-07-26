import requests
from bs4 import BeautifulSoup
import pandas as pd

# send the request
response = requests.get('https://sachess.org.au/interclub-teams-tournament-2023-results/')
soup = BeautifulSoup(response.text, 'html.parser')

# find all the tables
tables = soup.find_all('table')[11:]  # we're only interested in tables from 12th onward

matches = []
data = []

# loop through tables
for i, table in enumerate(tables):
    
    # get match metadata
    metadata_rows = table.find_all('thead')
    for metadata_row in metadata_rows:
        metadata_cols = metadata_row.find_all('th')
        metadata_cols = [col.text.strip() for col in metadata_cols]
        matches.append(metadata_cols)

    # get match data
    rows = table.find('tbody').find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        cols = [col.text.strip() for col in cols]
        data.append(cols)

# convert lists to dataframes
metadata_df = pd.DataFrame(matches, columns=['Match Number', 'Team 1 Rating', 'Team 1', 'Team 1 Score', 'Team 2 Score', 'Team 2', 'Team 2 Rating'])
data_df = pd.DataFrame(data, columns=['Table Number', 'Team 1 Rating', 'Team 1 Player', 'Team 1 Result', 'Team 2 Result', 'Team 2 Player', 'Team 2 Rating'])

# drop any rows with missing data
metadata_df = metadata_df.dropna()
data_df = data_df.dropna()

# print some of the data
print(metadata_df.head(20))
print(data_df.head(20))

# get rid of columns we don't need
metadata_df = metadata_df.drop(['Team 1 Rating', 'Team 2 Rating'], axis=1)

# convert result columns to numeric
data_df['Team 1 Result'] = data_df['Team 1 Result'].replace({'1 F': 1, '0 F': 0, '½': 0.5}).astype(float)
data_df['Team 2 Result'] = data_df['Team 2 Result'].replace({'1 F': 1, '0 F': 0, '½': 0.5}).astype(float)

# convert team score columns to numeric
metadata_df['Team 1 Score'] = pd.to_numeric(metadata_df['Team 1 Score'], errors='coerce')
metadata_df['Team 2 Score'] = pd.to_numeric(metadata_df['Team 2 Score'], errors='coerce')

# split the metadata into two separate dataframes based on the team
team1_df = metadata_df[['Match Number', 'Team 1', 'Team 1 Score']].copy()
team1_df.columns = ['Match Number', 'Team', 'Score']

team2_df = metadata_df[['Match Number', 'Team 2', 'Team 2 Score']].copy()
team2_df.columns = ['Match Number', 'Team', 'Score']

# join the two dataframes
team_df = pd.concat([team1_df, team2_df])

# calculate total score for each team
team_total_score = team_df.groupby('Team')['Score'].sum()

# Sort the scores in descending order
team_total_score = team_total_score.sort_values(ascending=False)

print(team_total_score)

# split the data into two separate dataframes based on the player's team
team1_df = data_df[['Table Number', 'Team 1 Rating', 'Team 1 Player', 'Team 1 Result']].copy()
team1_df.columns = ['Table Number', 'Rating', 'Player', 'Result']
team1_df['Opponent Rating'] = data_df['Team 2 Rating']

team2_df = data_df[['Table Number', 'Team 2 Rating', 'Team 2 Player', 'Team 2 Result']].copy()
team2_df.columns = ['Table Number', 'Rating', 'Player', 'Result']
team2_df['Opponent Rating'] = data_df['Team 1 Rating']

# join the two dataframes
player_df = pd.concat([team1_df, team2_df])

# convert the 'Result' column to numeric
player_df['Result'] = player_df['Result'].replace({'1 F': 1, '0 F': 0, '½': 0.5}).astype(float)

# convert the 'Rating' and 'Opponent Rating' columns to numeric
player_df['Rating'] = pd.to_numeric(player_df['Rating'], errors='coerce')
player_df['Opponent Rating'] = pd.to_numeric(player_df['Opponent Rating'], errors='coerce')

# calculate average opponent rating, total score, and total games for each player
player_avg_opponent_rating = player_df.groupby('Player')['Opponent Rating'].mean().round(0)  
player_total_score = player_df.groupby('Player')['Result'].sum()
player_total_games = player_df.groupby('Player')['Result'].count()  

# combine results into one dataframe
player_performance = pd.concat([player_avg_opponent_rating, player_total_score, player_total_games], axis=1)
player_performance.columns = ['Avg Opp Rtg', 'Total Score', 'Total Games']

# sort the dataframe by 'Total Score' in descending order
player_performance = player_performance.sort_values('Total Score', ascending=False)

print(player_performance)

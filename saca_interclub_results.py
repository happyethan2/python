import requests
from bs4 import BeautifulSoup
import pandas as pd
from collections import defaultdict
import math

def get_soup(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup

def extract_tables(soup):
    tables = soup.find_all('table')[11:]
    return tables

def extract_data(tables):
    matches = []
    data = []

    for table in tables:
        metadata_rows = table.find_all('thead')
        for metadata_row in metadata_rows:
            metadata_cols = metadata_row.find_all('th')
            metadata_cols = [col.text.strip() for col in metadata_cols]
            matches.append(metadata_cols)

        rows = table.find('tbody').find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            cols = [col.text.strip() for col in cols]
            data.append(cols)

    return matches, data

def create_dataframes(matches, data):
    metadata_df = pd.DataFrame(matches, columns=['Match Number', 'Team 1 Rating', 'Team 1', 'Team 1 Score', 'Team 2 Score', 'Team 2', 'Team 2 Rating'])
    data_df = pd.DataFrame(data, columns=['Table Number', 'Team 1 Rating', 'Team 1 Player', 'Team 1 Result', 'Team 2 Result', 'Team 2 Player', 'Team 2 Rating'])

    metadata_df = metadata_df.dropna()
    data_df = data_df.dropna()

    return metadata_df, data_df

def process_data(metadata_df, data_df):
    metadata_df = metadata_df.drop(['Team 1 Rating', 'Team 2 Rating'], axis=1)

    data_df['Team 1 Result'] = data_df['Team 1 Result'].replace({'1 F': 1, '0 F': 0, '½': 0.5}).astype(float)
    data_df['Team 2 Result'] = data_df['Team 2 Result'].replace({'1 F': 1, '0 F': 0, '½': 0.5}).astype(float)

    metadata_df['Team 1 Score'] = pd.to_numeric(metadata_df['Team 1 Score'], errors='coerce')
    metadata_df['Team 2 Score'] = pd.to_numeric(metadata_df['Team 2 Score'], errors='coerce')

    return metadata_df, data_df

def calculate_team_scores(metadata_df):
    team1_df = metadata_df[['Match Number', 'Team 1', 'Team 1 Score']].copy()
    team1_df.columns = ['Match Number', 'Team', 'Score']

    team2_df = metadata_df[['Match Number', 'Team 2', 'Team 2 Score']].copy()
    team2_df.columns = ['Match Number', 'Team', 'Score']

    team_df = pd.concat([team1_df, team2_df])

    team_total_score = team_df.groupby('Team')['Score'].sum()

    team_total_score = team_total_score.sort_values(ascending=False)

    return team_total_score

def calculate_player_performance(data_df):
    team1_df = data_df[['Table Number', 'Team 1 Rating', 'Team 1 Player', 'Team 1 Result']].copy()
    team1_df.columns = ['Table Number', 'Rating', 'Player', 'Result']
    team1_df['Opponent Rating'] = data_df['Team 2 Rating']

    team2_df = data_df[['Table Number', 'Team 2 Rating', 'Team 2 Player', 'Team 2 Result']].copy()
    team2_df.columns = ['Table Number', 'Rating', 'Player', 'Result']
    team2_df['Opponent Rating'] = data_df['Team 1 Rating']

    player_df = pd.concat([team1_df, team2_df])

    player_df['Result'] = player_df['Result'].replace({'1 F': 1, '0 F': 0, '½': 0.5}).astype(float)

    player_df['Rating'] = pd.to_numeric(player_df['Rating'], errors='coerce')
    player_df['Opponent Rating'] = pd.to_numeric(player_df['Opponent Rating'], errors='coerce')

    rated_games_df = player_df[player_df['Opponent Rating'] != 0]

    player_avg_opponent_rating = rated_games_df.groupby('Player')['Opponent Rating'].mean().round(0)

    player_total_score = player_df.groupby('Player')['Result'].sum()
    player_total_games = player_df.groupby('Player')['Result'].count()

    player_performance = pd.concat([player_avg_opponent_rating, player_total_score, player_total_games], axis=1, join='outer')
    player_performance.columns = ['Avg Opp Rtg', 'Total Score', 'Total Games']

    player_performance = player_performance.sort_values('Total Score', ascending=False)

    return player_performance

def calculate_elo(data_df, player_performance_df):
    
    # elo rating calculation
    def elo_expected(rating1, rating2):
        return 1 / (1 + 10 ** ((rating2 - rating1) / 400))

    def elo_update(rating, expected, result, k=120):
        if rating == 0:
            rating = 1000
            
        return rating + k * (result - expected)

    # Initialize ratings and results
    ratings = {}  # We'll fill this with actual initial ratings
    initial_ratings = {}  # We'll use this to store the initial ratings before they are updated
    results = defaultdict(list)

    # Iterate over matches
    for idx, row in data_df.iterrows():
        player1, player2 = row['Team 1 Player'], row['Team 2 Player']
        
        # Skip if player is 'BYE'
        if player1 == 'BYE' or player2 == 'BYE':
            continue

        # Initialize player ratings if not done already
        if player1 not in ratings:
            initial_rating1 = pd.to_numeric(row['Team 1 Rating'], errors='coerce')
            ratings[player1] = initial_rating1 if initial_rating1 != 0 else 0
            initial_ratings[player1] = ratings[player1] 
        if player2 not in ratings:
            initial_rating2 = pd.to_numeric(row['Team 2 Rating'], errors='coerce')
            ratings[player2] = initial_rating2 if initial_rating2 != 0 else 0
            initial_ratings[player2] = ratings[player2] 
            
        rating1, rating2 = ratings[player1], ratings[player2]
        expected1, expected2 = elo_expected(rating1, rating2), elo_expected(rating2, rating1)

        # Update ratings based on match result
        result1, result2 = row['Team 1 Result'], row['Team 2 Result']
        ratings[player1] = elo_update(rating1, expected1, result1)
        ratings[player2] = elo_update(rating2, expected2, result2)

        # Store results for final dataframe
        results[player1].append(ratings[player1])
        results[player2].append(ratings[player2])

    # Add initial and final Elo ratings to player performance dataframe
    player_performance_df['Rating'] = pd.Series({player: initial_ratings[player] for player in player_performance_df.index if player in initial_ratings})
    player_performance_df['Performance'] = pd.Series({player: round(ratings[-1]) for player, ratings in results.items()})
    return player_performance_df





def main():
    url = 'https://sachess.org.au/interclub-teams-tournament-2023-results/'
    soup = get_soup(url)
    tables = extract_tables(soup)
    matches, data = extract_data(tables)
    metadata_df, data_df = create_dataframes(matches, data)
    metadata_df, data_df = process_data(metadata_df, data_df)

    team_total_score = calculate_team_scores(metadata_df)
    player_performance = calculate_player_performance(data_df)
    player_performance = calculate_elo(data_df, player_performance)

    print(team_total_score)
    pd.set_option('display.max_rows', None)
    print(player_performance)

if __name__ == "__main__":
    main()

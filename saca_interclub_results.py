import requests
from bs4 import BeautifulSoup
import pandas as pd

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

def main():
    url = 'https://sachess.org.au/interclub-teams-tournament-2023-results/'
    soup = get_soup(url)
    tables = extract_tables(soup)
    matches, data = extract_data(tables)
    metadata_df, data_df = create_dataframes(matches, data)
    metadata_df, data_df = process_data(metadata_df, data_df)

    team_total_score = calculate_team_scores(metadata_df)
    player_performance = calculate_player_performance(data_df)

    print(team_total_score)
    pd.set_option('display.max_rows', None)
    print(player_performance)

if __name__ == "__main__":
    main()

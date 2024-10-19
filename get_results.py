import requests
import pandas as pd
from datetime import date


######################### VARIABLES ###########################

base_url = 'https://api.motogp.pulselive.com/motogp/v1/results/'
category_id_motogp = 'e8c110ad-64aa-4e8e-8a86-f2f152f6a942'

out_filename = './data/results.csv'

sessions_csv = './data/sessions.csv'


######################### FUNCTIONS ###########################

def request_api(base_url, endpoint):
    """
    Args:
        base_url (str)
        endpoint (str)

    Returns:
        data (json)
    """
    response = requests.get(base_url + endpoint)

    if response.status_code == 200:
        print("Successfully retrieved data")
        data = response.json()
        
    else:
        print(f"Failed to retrieve data. Status code: {response.status_code}")
        data = []

    return data

def specific_results(json_session_results):
    """
    
    """
    flattened_data = []
    for entry in json_session_results['classification']:
        flattened_entry ={
            'id': entry['id'],
            'position': entry['position'],
            'average_speed': entry['average_speed'] if entry.get('average_speed') else None,
            'gap_to_first': entry['gap']['first'] if entry.get('gap') else None,
            'total_laps': entry['total_laps'] if entry.get('total_laps') else None,
            'total_time': entry['time'] if entry.get('time') else None,
            'points': entry['points'] if entry.get('points') else None,
            'rider_id': entry['rider']['id']
        }

        flattened_data.append(flattened_entry)
    
    df_session_results = pd.DataFrame(flattened_data)

    return df_session_results

def all_seasons_results(sessions_csv, start_year=1949, end_year=date.today().year):
    """
    """
    list_all_results = []
    i = 0

    df_sessions = pd.read_csv(sessions_csv, sep=';', encoding='unicode_escape')
    df_sessions = df_sessions.drop(['date', 'number', 'track_condition', 'air_temperature', 'humidity', 'ground_temperature', 'weather', 'circuit', 'session_type', 'event_id'], axis=1)

    for session in df_sessions.itertuples(index=False):
        session_id = session.id
        year = session.season

        # Skip if the season is out of the given period
        if year < start_year or year > end_year:
            continue

        results_sessions_ep = 'session/' + session_id + '/classification'

        print(session_id)
        json_session_results = request_api(base_url, results_sessions_ep)
        if json_session_results == []:
            continue

        df_session_results = specific_results(json_session_results)
        df_session_results['session_id'] = session_id

        list_all_results.append(df_session_results)
        i += 1
        print(i)
            
    df_all_results = pd.concat(list_all_results, ignore_index=True)
    return df_all_results

def fetch_new_results(out_filename, sessions_csv, start_year=1949, end_year=date.today().year):
    """
    Requests data from the API and fetches it to the data already stored on the csv

    Args:
        events_csv (csv): csv containing the events for all MotoGP seasons
        start_year (int): year from which you want to get the data
        end_year (int): year until which you want to get the data
    
    Returns:
        Saves updated data to the same csv
    """
    # Extract data from start_year into a DataFrame
    new_results_df = all_seasons_results(sessions_csv, start_year=start_year, end_year=end_year)
    
    # Load existing data from CSV
    existing_results_df = pd.read_csv(out_filename, sep=';', encoding='unicode_escape')

    # Find new data that is not already in the CSV
    updated_results_df = pd.concat([existing_results_df, new_results_df]).drop_duplicates(subset='id')

    # Save updated data back to the CSV
    updated_results_df.to_csv(out_filename, index=False, sep=';')


######################### LAUNCH ###########################

# Get all results from all seasons and save it on a csv
#df_all_seasons_results_motogp = all_seasons_results(sessions_csv, start_year=2024)
#df_all_seasons_results_motogp.to_csv(out_filename, index=False, sep=';')

# Add sessions from specific seasons to an already existant csv
fetch_new_results(out_filename, sessions_csv, start_year=2024)
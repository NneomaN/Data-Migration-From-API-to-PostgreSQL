from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import requests
import psycopg2
import base64
import json

# Define your database connection parameters
with open("materials\postgresql_config.json", 'r') as ch_conn:
        DB_PARAMS = json.load(ch_conn)

# Define your Spotify API and other parameters
CLIENT_ID = "<your_client_id>"
CLIENT_SECRET = "<your_client_secret>"
refresh_token = "<your_refresh_token>"
#Function to generate new valid access token
def refresh_access_token():
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    }
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }
    response = requests.post(url, headers=headers, data=data)
    response_data = response.json()
    if "access_token" in response_data:
        return response_data["access_token"]
    else:
        raise Exception(f"Failed to refresh token: {response_data}")


TOKEN = refresh_access_token()
API_URL = "https://api.spotify.com/v1/me/player/recently-played?limit=50"

# Define the function to retrieve data from Spotify
def fetch_spotify_data():
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {TOKEN}"
    }

    today = datetime.now() 
    yesterday = today - timedelta(hours=6)
    yesterday_unix_timestamp = int(yesterday.timestamp()) * 1000  # convert to milliseconds

    response = requests.get(f"{API_URL}&after={yesterday_unix_timestamp}", headers=headers)
    return response.json()  # Assuming this returns the data you want to load into the DB

# Function to load the data into PostgreSQL
def load_to_postgresql(data):
    # Connect to PostgreSQL database
    conn = psycopg2.connect(**DB_PARAMS)
    cursor = conn.cursor()

    # Create table if it doesn't exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS spotify_recently_playeds (
        played_at_utc TIMESTAMP PRIMARY KEY,
        track_id TEXT,
        track_name TEXT,
        duration_ms INT,
        artist_id TEXT,
        artist_NAME TEXT,
        album_id TEXT,
        album_name TEXT
    );
    """)

    # Insert data into the table
    for track in data['items']:  
        played_at = track['played_at']
        track_id =  track['track']['id']
        track_name = track['track']['name']
        duration_ms = track['track']['duration_ms']    
        artist_id = track['track']['artists'][0]['id']
        artist_name = track['track']['artists'][0]['name']
        album_id = track['track']['album']['id'] 
        album_name = track['track']['album']['name'] 

        insert_query = """
        INSERT INTO spotify_recently_played (played_at, track_id, track_name, duration_ms, artist_id, artist_name, album_id, album_name)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (played_at) DO NOTHING;
        """

        cursor.execute(insert_query, (played_at, track_id, track_name, duration_ms, artist_id, artist_name, album_id, album_name))
    
    # Commit the changes
    conn.commit()

    # Close cursor and connection to db
    cursor.close()
    conn.close()


# Define the Airflow DAG
with DAG(
    'spotify_to_postgresql',
    default_args={
        'owner': 'airflow',
        'retries': 1,
        'retry_delay': timedelta(minutes=5),
    },
    description='Fetch data from Spotify and load it to PostgreSQL',
    schedule=timedelta(hours=1),  # Schedule this to run hourly
    start_date=datetime(2024, 11, 20),  # Use the appropriate start date
    catchup=False,
) as dag:
    
    #Task to refresh access token
    refresh_token_task = PythonOperator(
        task_id='refresh_token',
        python_callable=refresh_access_token,
    )

    # Task to fetch data from Spotify
    fetch_data_task = PythonOperator(
        task_id='fetch_spotify_data',
        python_callable=fetch_spotify_data,
    )
    
    # Task to load data into PostgreSQL
    load_data_task = PythonOperator(
        task_id='load_to_postgresql',
        python_callable=load_to_postgresql,
        op_args=[fetch_data_task.output],  # Pass data from the fetch task
    )

    # Set task dependencies
    refresh_token_task >> fetch_data_task >> load_data_task

    

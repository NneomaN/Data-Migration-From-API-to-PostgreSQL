import requests
import base64
import pandas
import psycopg2

CLIENT_ID = "<your_client_id>"
CLIENT_SECRET = "<your_client_secret>"
REDIRECT_URI = "http://localhost:8888/callback/"
AUTH_CODE = "<your_auth_code>"  #code_from_previous_step

token_url = "https://accounts.spotify.com/api/token"
payload = {
    "grant_type": "authorization_code",
    "code": AUTH_CODE,
    "redirect_uri": REDIRECT_URI,
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
}

response = requests.post(token_url, data=payload)
print(response.json())
refresh_token = response.json()['refresh_token']
print(refresh_token)

##copy out refresh token to use it in DAG file

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

# Example usage
new_access_token = refresh_access_token()
print("New Access Token:", new_access_token)

#Call API to extract data
from datetime import datetime
import datetime 


#Define GET url headers 
headers = {
        "Accept" : "application/json",
        "Content-Type" : "application/json",
        "Authorization" : "Bearer {token}".format(token=new_access_token)
    }
    

#Convert time to Unix timestamp in miliseconds      
today = datetime.datetime.now()          #instantiate the current datetime
yesterday = today - datetime.timedelta(hours=6)       #instantiate "6 hours ago" datetime
yesterday_unix_timestamp = int(yesterday.timestamp()) * 1000   #convert timestamp to unixtimestamp as requested by spotifiy API

#Download all songs you've listened to which means in the last 6 hours
data = requests.get("https://api.spotify.com/v1/me/player/recently-played?limit=50&after={time}".format(time=yesterday_unix_timestamp), headers = headers)
data = data.json()
data


#begin to explore data 
#get keys in data
for k,v in data.items():            
  print('keys : ',k)
  print(type(v))

#get keys in tracks
track = data['items'][0]              
for k,v in track.items():            
  print('keys : ',k)
  print(type(v))    

#get one track to explore content
trackDetails = track['track']        
for k,v in trackDetails.items():
  print('keys : ',k)
  print(type(v))  


#get one artists to explore content
trackArtists = trackDetails['artists'][0]      
print(trackArtists.keys())
print(trackArtists['id'])
print(trackArtists['name'])
print(trackArtists['type'])


#get one album to explore content
trackAlbum = trackDetails['album']      
for k,v in trackAlbum.items():
  print('keys : ',k)

trackAlbum['name']
trackAlbum['id']


# list all datapoints  of interest
'''
data['items'][0][played_at]                              #time song was played
data['items'][0]['track']['id']                          #track id
data['items'][0]['track']['name']                        #track name
data['items'][0]['track']['duration_ms']                 #duration of track/duration played
data['items'][0]['track']['artists'][0]['id']            # primary artist's id
data['items'][0]['track']['artists'][0]['name']          # primary artist's name
data['items'][0]['track']['album']['id']                 # album id
data['items'][0]['track']['album']['name']               # album name
'''


# Database connection parameters
host = "<your_postreSQL_instance_name>"
database = "<your_database_name"
user = "<your_username>"
password = "<your_password>"
port = "5432"  # Default port for PostgreSQL


# Establish the connection
conn = psycopg2.connect(
    host=host,
    database=database,
    user=user,
    password=password,
    port=port
)

# Create a cursor object to interact with the database
cursor = conn.cursor()

create_table_query = """
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
"""

cursor.execute(create_table_query)
conn.commit()  # Commit the changes

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

# Close the connection to the database
conn.close()


# Validation check to see if the latest insert matches the latest listening time
cursor.execute("SELECT MAX(played_at) FROM spotify_recently_played;")
rows = cursor.fetchall()
for row in rows:
    print(row)
    
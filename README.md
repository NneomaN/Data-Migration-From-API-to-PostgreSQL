# Data-migration-from-api-to-postgresql
This is an ETL and Orchestration case study which demonstrates making API data calls, data exploration and pipeline orchestration. It was implemented using the Spotify API, Apache Airflow, and a PostgreSQL DB hosted on Azure.

**Prerequisites:**
1. Basic understanding of Python and SQL syntax.
2. A Spotify account.
3. A PostgreSQL instance hosted on Azure.
4. An Airflow environment.

![Visual representation of data flow; from API throw Airflow pipeline to PostgreSQL DB](/assets/ETL_Overview.jpg "Process Architecture")

### Extract
#### Set up Spotify App
To access Spotify data, I created a Spotify app:
- First, I logged on to the [Spotify developer page](developer.spotify.com) using my Spotify account's credentials.
- I followed the [documentation](developer.spotify.com/documentation/web-api) to create an App on the dashboard.
  - During set up, I set the Redirect URI to "http\://localhost:8888/callback/", which is required to return the authorisation code
  - I made sure to select "Web API" and noted the app credentials.

#### Get Authorisation Code
Because playlist history is protected, I needed to obtain an authorization code:
  - Using the *Authorisation URL* in a web browser and I pass the Client-ID and Redirect URI values exactly as it appears on the App.
    ```
    --- Authorisation URL ---
    
    https://accounts.spotify.com/authorize?
    client_id=<client_id>
    &response_type=code
    &redirect_uri=<redirect_uri>
    &scope=user-read-recently-played
    ```
  - Running the correctly configured Authorisation URL returns a code in the browser search bar in the format ``` <redirect_uri>?code= <authorisation-code> ``` .

The autorisation code is then used to generate a Token.

#### Get Data using Access Token
Using the requests module in a python development environment I access data, following the details outlined in the [python notebook](#).


### Explore and Transform
Once I accessed the data, I explored it looking through keys and value structure and transformed it for analysis.

I identified and extracted relevant data points including:
  - Time played
  - Track ID
  - Track name
  - Track duration
  - Primary artist's name
  - Album ID
  - Album name


### Load into database
I loaded the transformed data into a cloud-based PostgreSQL database:
* I connected to the postgreSQL instance using the _psycopg2_ package.
* I created tables with appropriate constraints using SQL queries executed through Python.
* I iterated through the track data, extracting the relevant data points and inserting them into the table created.
* I committed all changes and closed the database connection.

## Orchestrate using Apache Airflow
To automate the ETL process, I implemented an Airflow pipeline to run every six hours:
1. I defined three modular functions for:
   - Refreshing the access token.
   - Calling the API to retrieve data.
   - Loading data into the PostgreSQL database.
2. I created a Directed Acyclic Graph (DAG) in Airflow to schedule and manage the tasks, ensuring dependencies were set appropriately.

The full implementation is detailed in this [dag file](#) .

### Outcome
At the end of the implementation I get a store of my Spotify listening history in a cloud based PostgreSQL database, to slice, dice and wrap how ever I want 😁.

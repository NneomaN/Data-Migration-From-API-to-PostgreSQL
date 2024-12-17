# Data-migration-from-api-to-postgresql
This is an ETL and Orchestration case study using the Spotify API, Apache Airflow, and a PostgreSQL DB hosted on Azure.

**Prerequisite:**
1. Basic understanding of Python and SQL syntax.
2. A Spotify Account.
3. A PostgreSQL instance hosted on Azure.
4. An Airflow environment.

![Visual representation of data flow; from API throw Airflow pipeline to PostgreSQL DB](/assets/ETL_Overview.jpg "Process Architecture")

### Extract
- Set up Spotify App
  - First, I logged on to the [Spotify developer page](developer.spotify.com) using the credentials associated with my Spotify account.
  - On the dashboard, I created an App following the instructions in the [documentation](developer.spotify.com/documentation/web-api).
    During set up, I set the Redirect URI to "http\://localhost:8888/callback/", which is required for return the authorisation code, making sure to select "Web API" and taking note of the app credentials.
- Get Authorisation Code: This step is required because playlist history is protected information.
  - Using the *Authorisation URL* in a web browser and I pass the Client-ID and Redirect URI values as it appears on the APP
    ```
    ---Authorisation URL ------
    
    https://accounts.spotify.com/authorize?
    client_id=<client_id>
    &response_type=code
    &redirect_uri=<redirect_uri>
    &scope=user-read-recently-played
    ```
  - Running the correctly configured Authorisation URL returns a code in the browser search bar in the format '<redirect_uri>?code=<authorisation-code>'
    used to generate a Token. 
- Using the requests module in a python development environment I access data, following the details outlined in the [python notebook](#).

### Transform
* I explored Spotify data, looking through keys and value structure
* Identify and extract relevant data points (timeplayed, songname, artistname, 
* I structured the data points in a dataframe ready to be loaded into the database

### Load
* Connect to PostgreSQL DB
* Create table with relevant constraints
* Loop through data selected inserting into instance

### Orchestrate using Apache Airflow
*  Set up Airflow environment
*  Define functions to execute tasks
*  Define DAG
*  Set task order

At the end you get a store of listening history to slice and dice however you like. Enjoy!

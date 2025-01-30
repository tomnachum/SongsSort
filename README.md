# How to run? 
1. clone the project
2. packages are handled by pipenv:
   1. run in terminal ```pipenv install```
   2. then run ```pipenv shell```
3. create .env file with the following env vars:
   1. SONGS_DIRECTORY: a path to the song's folder to run the sorting on 
   2. SPOTIFY_CLIENT_ID: log in to https://developer.spotify.com/, choose your app-> settings
   3. SPOTIFY_CLIENT_SECRET 
   4. DISCOGS_API_KEY: go to https://www.discogs.com/settings/developers, choose your app->settings
   5. DISCOGS_API_SECRET
   6. DEBUG: for extra logs set to True
4. run the ```main.py``` file

For debugging, the program will create in the same directory as SONGS_DIRECTORY 2 folders:
- modified: will have all the songs that has been modified by the algorithm
- invalid: will have all the songs that the program found as invalid 

In order to edit specific files manually, use MusicBrainz Picard
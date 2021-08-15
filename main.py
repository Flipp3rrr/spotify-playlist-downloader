# Import Spotify.py to use Spotify features
import spotify.sync as spotify
# Import urllib.request to search YouTube
import urllib.request
# Import youtube_dl to download YouTube videos
import youtube_dl
# Import os to save data to files
import os
# Import logging
import logging

# Output log to 'spotify-playlist-downloader.log'
if os.path.exists("spotify-playlist-downloader.log"):
    os.remove("spotify-playlist-downloader.log")

open("spotify-playlist-downloader.log","w+")
logging.basicConfig(filename='spotify-playlist-downloader.log', filemode='w', level=logging.WARNING)

logging.info("Succesfully loaded modules & started logging")

# Get current directory
runDir = os.path.dirname(__file__)

# Get Spotify client ID from file or ask for ID and save to file
if os.path.exists("clientId.secret"):
    logging.debug("'clientId.secret' exists")
    with open("clientId.secret", "r") as file:
        clientId = file.read().replace("\n", "")
    logging.info("Spotify client ID retrieved from 'clientId.secret'")
else:
    logging.debug("'clientId.secret' does not exist")
    open("clientId.secret", "w+")
    logging.info("'clientId.secret' created")
    clientId = input("Spotify client ID: ")
    with open("clientId.secret", "a") as myfile:
        myfile.write(clientId)
    logging.info("Spotify client ID saved to 'clientId.secret'")

# Get Spotify secret from file or ask for secret and save to file
if os.path.exists("spotifySecret.secret"):
    logging.debug("'spotifySecret.secret' exists")
    with open("spotifySecret.secret") as file:
        spotifySecret = file.read().replace("\n", "")
    logging.info("Spotify secret retrieved from 'spotifySecret.secret'")
else:
    logging.debug("'spotifySecret.secret' does not exist")
    open("spotifySecret.secret", "w+")
    logging.info("'spotifySecret.secret' created")
    spotifySecret = input("Spotify secret: ")
    with open("spotifySecret.secret", "a") as myfile:
        myfile.write(spotifySecret)
    logging.info("Spotify client ID saved to 'spotifySecret.secret'")

# Get Spotify token from file or ask for token and save to file
if os.path.exists("spotifyToken.secret"):
    logging.debug("'spotifyToken.secret' exists")
    with open("spotifyToken.secret") as file:
        spotifyToken = file.read().replace("\n", "")
    logging.info("Spotify token retrieved from 'spotifyToken.secret'")
else:
    logging.debug("'spotifyToken.secret' does not exist")
    open("spotifyToken.secret", "w+")
    logging.info("'spotifyToken.secret' created")
    spotifyToken = input("Spotify token: ")
    with open("spotifyToken.secret", "a") as myfile:
        myfile.write(spotifyToken)
    logging.info("Spotify token saved to 'spotifyToken.secret'")
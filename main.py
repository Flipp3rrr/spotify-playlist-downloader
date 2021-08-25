# Import Spotipy to use Spotify features
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
# Import urllib.request to search YouTube
import urllib.request
# Import youtube_dl to download YouTube videos
import youtube_dl
# Import os to save data to files
import os
# Import logging
import logging
# Import JSON to dump data to a JSON file
import json
# Import time to sleep
import time

# Output log to 'spotify-playlist-downloader.log'
if os.path.exists("spotify-playlist-downloader.log"):
    os.remove("spotify-playlist-downloader.log")

open("spotify-playlist-downloader.log","w+")
logging.basicConfig(filename='spotify-playlist-downloader.log', filemode='w', level=logging.DEBUG)

logging.info("Succesfully loaded modules & started logging")

# Get current directory
runDir = os.path.dirname(__file__)

def retrieveFromFile(fileName, purpose):
    # Check for and then read data from file
    if os.path.exists(fileName):
        logging.info("Checked for '{file}' and it exists".format(file=fileName))
        with open(fileName, "r") as file:
            dataFromFile = file.read().replace("\n", "")
        logging.info("Data retrieved from '{file}'".format(file=fileName))
        # Return data
        return(dataFromFile)
    # Ask for data and write if file didn't exist in check
    else:
        logging.info("Checked for '{file}' and it does not exist".format(file=fileName))
        open(fileName, "w+")
        logging.info("'{file}' created".format(file=fileName))
        dataToFile = input("{purpose}: ".format(purpose=purpose))
        with open(fileName, "a") as file:
            file.write(dataToFile)
        logging.info("{purpose} saved to '{file}'".format(purpose=purpose, file=fileName))
        return(dataToFile)

def deleteFile(fileName):
    if os.path.exists(fileName):
        logging.info("Checked for '{file}' and it exists".format(file=fileName))
        os.remove(fileName)
        logging.info("Deleted '{file}'".format(file=fileName))

def deleteFileExt(ext):
    files = os.listdir(runDir)
    for item in files:
        if item.endswith(ext):
            os.remove(os.path.join(runDir, item))
            logging.info("Checked for '{ext}' and '{file}' exists, deleted".format(ext=ext, file=item))

print("""SPOTIFY-PLAYLIST-DOWNLOADER
(get you client ID and secret from 'developer.spotify.com')

[1] Download playlists
[2] Delete data""")

choice = input(">> ")

if choice == "1":
    # Get ID and secret
    clientID = retrieveFromFile("clientID.secret", "Spotify client ID")
    spotifySecret = retrieveFromFile("spotifySecret.secret", "Spotify secret")

    # ID and secret to SpotifyClientCredentials
    clientCreds = SpotifyClientCredentials(clientID, spotifySecret)
    sp = spotipy.Spotify(client_credentials_manager=clientCreds)

def retrieveTrackIDs(ID):
    IDList = []
    playlist = sp.playlist(playlistID)
    for item in playlist["tracks"]["items"]:
        track = item["track"]
        IDList.append(track["id"])
    return IDList

def retrieveTrackData(trackID):
    meta = sp.track(trackID)
    trackDetails = {"name": meta["name"], "artist": meta["album"]["artists"][0]["name"]}
    return trackDetails

if choice == "1":
    playlistURL = input("Playlist URL: ")
    # playlist URL = https://open.spotify.com/playlist/<ID>?si=<junk>
    #                (34)                              (ID)(20)
    # Now remove the first 34 and last 20 characters to get the playlist ID
    playlistID = playlistURL[34:-20]

    trackIDs = retrieveTrackIDs(playlistID)
    print("There are {songs} songs in this playlist".format(songs = len(trackIDs)))
    logging.debug("Got the following IDs from playlist {id}: {tracks}".format(id=playlistID, tracks=trackIDs))

    tracks = []
    for i in range(len(trackIDs)):
        time.sleep(.1)
        track = retrieveTrackData(trackIDs[i])
        tracks.append(track)

    if os.path.exists("playlist-{id}.json".format(id=playlistID)):
        logging.info("Checked for '{file}' and it exists".format(file="playlist-{id}.json".format(id=playlistID)))
        os.remove("playlist-{id}.json".format(id=playlistID))
        logging.info("Deleted '{file}'".format(file="playlist-{id}.json".format(id=playlistID))) 
        time.sleep(.1) 

    with open("playlist-{id}.json".format(id=playlistID), "w+") as file:
        json.dump(tracks, file, indent=4)

elif choice == "2":
    deleteFileExt(".secret")
    deleteFileExt(".json")

else:
    print("No such option")
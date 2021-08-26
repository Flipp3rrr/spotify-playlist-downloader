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
# Import SSL just so I can bypass SSL verification later
import ssl
# Regex yeet
import re
# Shutil to yeet things into place
import shutil

# Check for log file, delete it if it exists
if os.path.exists("spotify-playlist-downloader.log"):
    os.remove("spotify-playlist-downloader.log")

# Start logging to 'spotify-playlist-downloader.log'
open("spotify-playlist-downloader.log","w+")
logging.basicConfig(filename='spotify-playlist-downloader.log', filemode='w', level=logging.INFO)

logging.info("Succesfully loaded modules & started logging")

# Get current directory
runDir = os.path.dirname(__file__)

# Output directory, make it if it doesn't exist
outDir = os.path.join(runDir, "output")
if not os.path.exists(outDir):
    os.makedirs(outDir)

# Function to retrieve data from a file, or ask for the information to then put in a file
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
        # Return data
        return(dataToFile)

# Function to delete a file, if it exists
def deleteFile(fileName):
    if os.path.exists(fileName):
        logging.info("Checked for '{file}' and it exists".format(file=fileName))
        os.remove(fileName)
        logging.info("Deleted '{file}'".format(file=fileName))

# Function to delete all files with 'ext' file extension, if any exist
def deleteFileExt(ext):
    # List all files in the current directory
    files = os.listdir(runDir)
    # Check every file, delete it if it has 'ext' extension
    for item in files:
        if item.endswith(ext):
            os.remove(os.path.join(runDir, item))
            logging.info("Checked for '{ext}' and '{file}' exists, deleted".format(ext=ext, file=item))

# User options and input
print("""
SPOTIFY-PLAYLIST-DOWNLOADER
(get you client ID and secret from 'developer.spotify.com')

[1] Download playlists
[2] Delete data
""")
choice = input(">> ")

# Choice '1', download playlist
if choice == "1":
    # Get ID and secret
    clientID = retrieveFromFile("clientID.secret", "Spotify client ID")
    spotifySecret = retrieveFromFile("spotifySecret.secret", "Spotify secret")

    # ID and secret to SpotifyClientCredentials
    clientCreds = SpotifyClientCredentials(clientID, spotifySecret)
    sp = spotipy.Spotify(client_credentials_manager=clientCreds)

# Function to retrieve track IDs from playlist
def retrieveTrackIDs(ID):
    IDList = []
    playlist = sp.playlist(playlistID)
    for item in playlist["tracks"]["items"]:
        track = item["track"]
        IDList.append(track["id"])
    return IDList

# Function to retrieve details from tracks
def retrieveTrackData(trackID):
    meta = sp.track(trackID)
    trackDetails = {"name": meta["name"], "artist": meta["album"]["artists"][0]["name"]}
    return trackDetails

# Continue choice '1', download playlist
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
    for a in range(len(trackIDs)):
        time.sleep(.1)
        track = retrieveTrackData(trackIDs[a])
        tracks.append(track)

    # Check if a JSON file for the current playlist exists, delete it if it does
    if os.path.exists("playlist-{id}.json".format(id=playlistID)):
        logging.info("Checked for '{file}' and it exists".format(file="playlist-{id}.json".format(id=playlistID)))
        os.remove("playlist-{id}.json".format(id=playlistID))
        logging.info("Deleted '{file}'".format(file="playlist-{id}.json".format(id=playlistID))) 

    # Dump data to file
    with open("playlist-{id}.json".format(id=playlistID), "w+") as file:
        json.dump(tracks, file, indent=4)
    
    # Playlist directory
    playlistDir = os.path.join(outDir, "playlist-{id}/".format(id=playlistID))
    
    # Delete directory contents if it exists
    if os.path.exists(playlistDir):
        shutil.rmtree(playlistDir)

    # Create directory if it doesn't exist
    if not os.path.exists(playlistDir):
        os.makedirs(playlistDir)

    for b in range(len(tracks)):
        # Create search query
        currentTrack = tracks[b]
        currentTrackName = currentTrack["name"]
        currentTrackArtist = currentTrack["artist"]
        searchUnsan = currentTrackName + " " + currentTrackArtist

        # I need only alphanumeric characters or urllib will complain
        search = re.sub("[^A-Za-z0-9]+", " ", searchUnsan)
        logging.info("Changed '{search1}' to '{search2}'".format(search1=searchUnsan, search2=search))

        # Fuck you SSL
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE 

        # Create URL from query
        youtubeURL = "http://www.youtube.com/results?search_query=" + search.replace(" ", "%20")

        # Results
        logging.info("Getting results from {url}".format(url=youtubeURL))
        result = urllib.request.urlopen(youtubeURL, context=ctx)

        # Get first video ID from the results and put it in a URL
        videoID = re.findall(r"watch\?v=(\S{11})", result.read().decode())
        downloadURL = "https://www.youtube.com/watch?v=" + videoID[0]
        print("Downloading '{track}' from '{url}'".format(track=currentTrackName, url=downloadURL))
        logging.info("Downloading '{track}' from '{url}'".format(track=currentTrackName, url=downloadURL)

        time.sleep(.1)

        # Download...
        try:
            noSSL = {
                "nocheckcertificate": True,
            }
            videoInfo = youtube_dl.YoutubeDL(noSSL).extract_info(url=downloadURL, download=False)
            filename = f"{videoInfo['title']}.mp3"
            filePath = os.path.join(runDir, filename)
            options = {
                "format": "bestaudio/best",
                "keepvideo": False,
                "outtmpl": filename,
                # And again, fuck you SSL
                "nocheckcertificate": True,
            }
            with youtube_dl.YoutubeDL(options) as ydl:
                ydl.download([videoInfo['webpage_url']])
        except Exception as error:
            logging.warning("Did not download {track} because of {error}".format(track=currentTrackName, error=error))
            print("Did not download {track} because of {error}".format(track=currentTrackName, error=error))

        try:
            # Move to 'playlistDir'
            filePlace = os.path.join(playlistDir, filename)
            shutil.move(filePath, playlistDir)
            print("Downloaded {track} and moved to {location}".format(track=currentTrackName, location=filePlace))
        except Exception as error:
            logging.warning("Couldn't move {file} because {error}".format(file=filename, error=error))

# Choice 2, delete data
elif choice == "2":
    deleteFileExt(".secret")
    deleteFileExt(".json")

# Backup in case of ID10T error
else:
    print("No such option")
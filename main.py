try:
    # Import Spotipy to get the track list from the playlist and track information
    import spotipy
    from spotipy.oauth2 import SpotifyClientCredentials
    # Import youtube_dl to download YouTube videos
    import youtube_dl
except Exception as error:
    raise Exception("Failed to import either 'spotipy' or 'youtube_dl', {error}".format(error=error))
# Import urllib.request which will later be used to search YouTube videos
import urllib.request
# Import os and shutil to do things with files and directories
import os
import shutil
# Import logging
import logging
# Import JSON to dump data to a JSON file, it's not actually needed but it's nice to be able
# to see the information I got from Spotify
import json
# Import time to wait for a short time so Spotify and YouTube won't think it's a DOS attack
import time
# Import SSL just so I can bypass SSL verification later
import ssl
# Import regex
import re
# Import unicodedata which will be used to convert special characters in song names and artist names,
# because those have to be ascii
import unicodedata

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
outDir = os.path.join(runDir, "spotify-download-output")
if not os.path.exists(outDir):
    os.makedirs(outDir)

# Function to retrieve data from a file, or ask for the information to then put in a file
def retrieveFromFile(fileName, purpose):
    # Check for file and then read data from file
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
def deleteFile(fileName, directory):
    if os.path.exists(os.path.join(directory, fileName)):
        logging.info("Checked for '{file}' and it exists".format(file=fileName))
        os.remove(os.path.join(directory, fileName))
        logging.info("Deleted '{file}'".format(file=fileName))

# Function to delete all files with 'ext' file extension in the 'directory' directory, if any exist
def deleteFileMatch(match, directory):
    # Check every file, delete it if it starts with 'match'
    for file in os.listdir(directory):
        if file.startswith(match):
            os.remove(os.path.join(runDir, file))

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
    # I only need the name of the track and the artist, get it here
    trackDetails = {"name": meta["name"], "artist": meta["album"]["artists"][0]["name"]}
    return trackDetails

# User options and input
print("""
SPOTIFY-PLAYLIST-DOWNLOADER
(get you client ID and secret from 'developer.spotify.com')

[1] Download playlists
[2] Delete data (client ID, secret, logs, output, etc.)
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

    # Ask for the URL to the playlist
    playlistURL = input("Playlist URL: ")
    # Playlist URL = https://open.spotify.com/playlist/<ID>?si=<junk>
    #                (34)                              (ID)(20)
    # Now remove the first 34 and last 20 characters to get the playlist ID
    playlistID = playlistURL[34:-20] # Yeah hardcoding this is a bad idea, need to fix it sometime

    # Get all the track IDs
    trackIDs = retrieveTrackIDs(playlistID)
    print("There are {songs} songs in this playlist".format(songs = len(trackIDs)))
    logging.debug("Got the following IDs from playlist {id}: {tracks}".format(id=playlistID, tracks=trackIDs))

    tracks = []
    for a in range(len(trackIDs)):
        # Wait for a tiny while just so it will look less like a DOS
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
        logging.info("Checked for '{dir}' and '{dir}' exists, deleted".format(dir=playlistDir))

    # Create directory
    os.makedirs(playlistDir)

    # Go through the playlist and download each track
    for b in range(len(tracks)):
        # Create search query
        currentTrack = tracks[b]
        currentTrackName = currentTrack["name"]
        currentTrackArtist = currentTrack["artist"]
        searchUnsan = currentTrackName + " " + currentTrackArtist

        # Convert to ascii, otherwise urllib won't work
        search = unicodedata.normalize('NFKD', searchUnsan).encode('ascii', 'ignore')
        logging.info("Changed '{search1}' to '{search2}'".format(search1=searchUnsan, search2=search))

        # Create 'ctx' context to bypass SSL when searching with 'urllib'
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE 

        # Create URL from query
        youtubeURL = "http://www.youtube.com/results?search_query=" + search.replace(" ", "%20")

        # Make request with 'youtubeURL' and output results to 'result'
        logging.info("Getting results from {url}".format(url=youtubeURL))
        result = urllib.request.urlopen(youtubeURL, context=ctx)

        # Get first video ID from the results and put it in a URL
        videoID = re.findall(r"watch\?v=(\S{11})", result.read().decode())
        downloadURL = "https://www.youtube.com/watch?v=" + videoID[0]
        print("Downloading '{track}' from '{url}'".format(track=currentTrackName, url=downloadURL))
        logging.info("Downloading '{track}' from '{url}'".format(track=currentTrackName, url=downloadURL))

        # Wait for a tiny while just so it will look less like a DOS
        time.sleep(.1)

        # Download
        try: # Internet connection can be weird so let's do some error handling
            # Disable SSL by using 'noSSL' with youtube_dl
            noSSL = {
                "nocheckcertificate": True,
            }
            videoInfo = youtube_dl.YoutubeDL(noSSL).extract_info(url=downloadURL, download=False)
            filename = f"{videoInfo['title']}.mp3"
            filePath = os.path.join(runDir, filename)
            
            # Options for the download
            options = {
                "format": "bestaudio/best",
                "keepvideo": False,
                "outtmpl": filename,
                # Again disable SSL
                "nocheckcertificate": True,
            }

            # Actual download
            with youtube_dl.YoutubeDL(options) as ydl:
                ydl.download([videoInfo['webpage_url']])

        except Exception as error: # Most likely this exception would be because the video is age restriction
            logging.warning("Did not download {track} because of {error}".format(track=currentTrackName, error=error))
            print("Did not download {track} because of {error}".format(track=currentTrackName, error=error))

        else: # Only move the file if the download actually was done
            try:
                # Move to 'playlistDir'
                filePlace = os.path.join(playlistDir, filename)
                shutil.move(filePath, playlistDir)
                print("Downloaded {track} and moved to {location}".format(track=currentTrackName, location=filePlace))
            except Exception as error:
                logging.warning("Couldn't move {file} because {error}".format(file=filename, error=error))

# Choice 2, delete data
elif choice == "2":
    # Delete files that end up in the directory containing 'main.py'
    #deleteFile("spotify-playlist-downloader.log", runDir)
    deleteFile("clientID.secret", runDir)
    deleteFile("spotifySecret.secret", runDir)
    deleteFileMatch("playlist-", runDir)
    # Delete everything in the output directory and the directory itself
    if os.path.exists(outDir):
        shutil.rmtree(outDir)

# Backup in case of ID10T error
else:
    print("No such option")
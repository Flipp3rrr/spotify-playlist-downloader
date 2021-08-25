# Import Spotify.py to use Spotify features
import spotifypy
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

print("""SPOTIFY-PLAYLIST-DOWNLOADER

[1] Download playlists
[2] Delete data""")

choice = input(">> ")

if choice == "1":
    clientId = retrieveFromFile("clientId.secret", "Spotify client ID")
    spotifySecret = retrieveFromFile("spotifySecret.secret", "Spotify secret")

    playlistUrl = input("Playlist URL: ")
    print(playlistUrl)

elif choice == "2":
    deleteFile("clientId.secret")
    deleteFile("spotifySecret.secret")
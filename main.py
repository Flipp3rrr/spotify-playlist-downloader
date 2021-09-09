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
run_dir = os.path.dirname(__file__)

# Output directory, make it if it doesn't exist
out_dir = os.path.join(run_dir, "spotify-download-output")
if not os.path.exists(out_dir):
    os.makedirs(out_dir)

# Function to retrieve data from a file, or ask for the information to then put in a file
def retrieve_from_file(filename, purpose):
    # Check for file and then read data from file
    if os.path.exists(filename):
        logging.info("Checked for '{file}' and it exists".format(file=filename))
        with open(filename, "r") as file:
            data_from_file = file.read().replace("\n", "")
        logging.info("Data retrieved from '{file}'".format(file=filename))
        # Return data
        return(data_from_file)
    # Ask for data and write if file didn't exist in check
    else:
        logging.info("Checked for '{file}' and it does not exist".format(file=filename))
        open(filename, "w+")
        logging.info("'{file}' created".format(file=filename))
        data_to_file = input("{purpose}: ".format(purpose=purpose))
        with open(filename, "a") as file:
            file.write(data_to_file)
        logging.info("{purpose} saved to '{file}'".format(purpose=purpose, file=filename))
        # Return data
        return(data_to_file)

# Function to delete a file, if it exists
def delete_file(filename, directory):
    if os.path.exists(os.path.join(directory, filename)):
        logging.info("Checked for '{file}' and it exists".format(file=filename))
        os.remove(os.path.join(directory, filename))
        logging.info("Deleted '{file}'".format(file=filename))

# Function to delete all files with 'ext' file extension in the 'directory' directory, if any exist
def delete_file_match(match, directory):
    # Check every file, delete it if it starts with 'match'
    for file in os.listdir(directory):
        if file.startswith(match):
            os.remove(os.path.join(run_dir, file))

# Function to retrieve track IDs from playlist
def retrieve_track_ids(id):
    id_list = []
    playlist = sp.playlist(playlist_id)
    for item in playlist["tracks"]["items"]:
        track = item["track"]
        id_list.append(track["id"])
    return id_list

# Function to retrieve details from tracks
def retrieve_track_data(track_id):
    meta = sp.track(track_id)
    # I only need the name of the track and the artist, get it here
    track_details = {"name": meta["name"], "artist": meta["album"]["artists"][0]["name"]}
    return track_details

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
    client_id = retrieve_from_file("client_id.secret", "Spotify client ID")
    spotify_secret = retrieve_from_file("spotify_secret.secret", "Spotify secret")

    # ID and secret to SpotifyClientCredentials
    client_creds = SpotifyClientCredentials(client_id, spotify_secret)
    sp = spotipy.Spotify(client_credentials_manager=client_creds)

    # Ask for the URL to the playlist
    playlist_url = input("Playlist URL: ")
    # Playlist URL = https://open.spotify.com/playlist/<ID>?si=<junk>
    #                (34)                              (ID)(20)
    # Now remove the first 34 and last 20 characters to get the playlist ID
    playlist_id = playlist_url[34:-20] # Yeah hardcoding this is a bad idea, need to fix it sometime

    # Get all the track IDs
    track_ids = retrieve_track_ids(playlist_id)
    print("There are {songs} songs in this playlist".format(songs = len(track_ids)))
    logging.debug("Got the following IDs from playlist {id}: {tracks}".format(id=playlist_id, tracks=track_ids))

    tracks = []
    for a in range(len(track_ids)):
        # Wait for a tiny while just so it will look less like a DOS
        time.sleep(.1)
        track = retrieve_track_data(track_ids[a])
        tracks.append(track)

    # Check if a JSON file for the current playlist exists, delete it if it does
    if os.path.exists("playlist-{id}.json".format(id=playlist_id)):
        logging.info("Checked for '{file}' and it exists".format(file="playlist-{id}.json".format(id=playlist_id)))
        os.remove("playlist-{id}.json".format(id=playlist_id))
        logging.info("Deleted '{file}'".format(file="playlist-{id}.json".format(id=playlist_id))) 

    # Dump data to file
    with open("playlist-{id}.json".format(id=playlist_id), "w+") as file:
        json.dump(tracks, file, indent=4)
    
    # Playlist directory
    playlist_dir = os.path.join(out_dir, "playlist-{id}/".format(id=playlist_id))
    
    # Delete directory contents if it exists
    if os.path.exists(playlist_dir):
        shutil.rmtree(playlist_dir)
        logging.info("Checked for '{dir}' and '{dir}' exists, deleted".format(dir=playlist_dir))

    # Create directory
    os.makedirs(playlist_dir)

    # Go through the playlist and download each track
    for b in range(len(tracks)):
        # Create search query
        current_track = tracks[b]
        current_track_name = current_track["name"]
        current_track_artist = current_track["artist"]
        search_unsan = current_track_name + " " + current_track_artist

        # Convert to ascii, otherwise urllib won't work
        search = unicodedata.normalize('NFKD', search_unsan).encode('ascii', 'ignore')
        logging.info("Changed '{search1}' to '{search2}'".format(search1=search_unsan, search2=search))

        # Create 'ctx' context to bypass SSL when searching with 'urllib'
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE 

        # Create URL from query
        youtube_url = "http://www.youtube.com/results?search_query=" + search.replace(" ", "%20")

        # Make request with 'youtube_url' and output results to 'result'
        logging.info("Getting results from {url}".format(url=youtube_url))
        result = urllib.request.urlopen(youtube_url, context=ctx)

        # Get first video ID from the results and put it in a URL
        video_id = re.findall(r"watch\?v=(\S{11})", result.read().decode())
        download_url = "https://www.youtube.com/watch?v=" + video_id[0]
        print("Downloading '{track}' from '{url}'".format(track=current_track_name, url=download_url))
        logging.info("Downloading '{track}' from '{url}'".format(track=current_track_name, url=download_url))

        # Wait for a tiny while just so it will look less like a DOS
        time.sleep(.1)

        # Download
        try: # Internet connection can be weird so let's do some error handling
            # Disable SSL by using 'no_ssl' with youtube_dl
            no_ssl = {
                "nocheckcertificate": True,
            }
            video_info = youtube_dl.YoutubeDL(no_ssl).extract_info(url=download_url, download=False)
            filename = f"{video_info['title']}.mp3"
            file_path = os.path.join(run_dir, filename)
            
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
                ydl.download([video_info['webpage_url']])

        except Exception as error: # Most likely this exception would be because the video is age restriction
            logging.warning("Did not download {track} because of {error}".format(track=current_track_name, error=error))
            print("Did not download {track} because of {error}".format(track=current_track_name, error=error))

        else: # Only move the file if the download actually was done
            try:
                # Move to 'playlist_dir'
                file_place = os.path.join(playlist_dir, filename)
                shutil.move(file_path, playlist_dir)
                print("Downloaded {track} and moved to {location}".format(track=current_track_name, location=file_place))
            except Exception as error:
                logging.warning("Couldn't move {file} because {error}".format(file=filename, error=error))

# Choice 2, delete data
elif choice == "2":
    # Delete files that end up in the directory containing 'main.py'
    #delete_file("spotify-playlist-downloader.log", run_dir)
    delete_file("client_id.secret", run_dir)
    delete_file("spotify_secret.secret", run_dir)
    delete_file_match("playlist-", run_dir)
    # Delete everything in the output directory and the directory itself
    if os.path.exists(out_dir):
        shutil.rmtree(out_dir)

# Backup in case of ID10T error
else:
    print("No such option")
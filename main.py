try:
    import spotipy
    from spotipy.oauth2 import SpotifyClientCredentials
    import youtube_dl
except Exception as error:
    raise Exception("Failed to import either 'spotipy' or 'youtube_dl', {error}".format(error=error))
import urllib.request
import os
import shutil
import logging
import json
import time
import ssl
import re
import unicodedata
import tkinter
import argparse

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

# Argparse setup
parser = argparse.ArgumentParser()

# CLI arguments
parser.add_argument("-ng", "--nogui", help="Run the interactive command line interface instead of the GUI", action="store_true")
parser.add_argument("-sc", "--script", help="Run the command without asking for input", action="store_true")
parser.add_argument("-id", "--id", help="Specify the Spotify ID to be used")
parser.add_argument("-s", "--secret", help="Specify the Spotify secret to be used")
parser.add_argument("-p", "--playlist", help="Specify the playlist to download", type=str)
parser.add_argument("-cd", "--cleardata", help="Delete all saved data", action="store_true")

args = parser.parse_args()

# Silence youtube_dl output
class youtube_dl_logger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)

# Function to retrieve secret from a file, or ask for the information to then put in a file
def get_setting(name):
    purpose = name
    settings_file_path = os.path.join(run_dir, "settings.json")
    if os.path.exists(settings_file_path):
        with open(settings_file_path) as settings_file:
            settings = json.load(settings_file)

        if name in settings:
            return_value = settings[name]
            return(return_value)
        else:
            new_key = name
            new_value = input("{purpose}: ".format(purpose = purpose))
            new_dict = {"{key}".format(key = new_key): "{value}".format(value = new_value)}

            settings.update(new_dict)
            settings_file = open(settings_file_path, "w+")
            json.dump(settings, settings_file, indent = 4)

            return_value = settings[name]
            return(return_value)

    else:
        new_key = name
        new_value = input("{purpose}: ".format(purpose = purpose))
        new_dict = {"{key}".format(key = new_key): "{value}".format(value = new_value)}

        settings = new_dict
        settings_file = open(settings_file_path, "w+")
        json.dump(settings, settings_file, indent = 4)

        return_value = settings[name]
        return(return_value)

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

# Get IDs, secrets and credentials ready
client_id = get_setting("client-id")
spotify_secret = get_setting("spotify-secret")
# ID and secret to SpotifyClientCredentials
client_creds = SpotifyClientCredentials(client_id, spotify_secret)
sp = spotipy.Spotify(client_credentials_manager=client_creds)

# Function to retrieve track IDs from playlist
def retrieve_track_ids(playlist_id):
    id_list = []
    playlist = sp.playlist(playlist_id)
    for item in playlist["tracks"]["items"]:
        track = item["track"]
        id_list.append(track["id"])
    return id_list

# Download playlist option
def download_playlist():
    if args.script:
        playlist_url = args.playlist
    else:
        playlist_url = input("Playlist URL: ")

    # Playlist URL = https://open.spotify.com/playlist/<ID>?si=<junk>
    #                (34)                              (ID)    (20)
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
        search1 = unicodedata.normalize('NFKD', search_unsan)
        search2 = search1.replace(" ", "%20")
        search = re.sub("[^A-Za-z0-9%]+", "", search2)
        logging.info("Changed '{search1}' to '{search2}'".format(search1=search_unsan, search2=search))

        # Create 'ctx' context to bypass SSL when searching with 'urllib'
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE 

        # Create URL from query
        youtube_url = "http://www.youtube.com/results?search_query={id}".format(id=search)

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
                "logger": youtube_dl_logger(),
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

# Function to retrieve details from tracks
def retrieve_track_data(track_id):
    meta = sp.track(track_id)
    # I only need the name of the track and the artist, get it here
    track_details = {"name": meta["name"], "artist": meta["album"]["artists"][0]["name"]}
    return track_details

# Delete data option
def delete_data():
    # Delete files that end up in the directory containing 'main.py'
    #delete_file("spotify-playlist-downloader.log", run_dir)
    delete_file("client-id.secret", run_dir)
    delete_file("spotify-secret.secret", run_dir)
    delete_file_match("playlist-", run_dir)
    # Delete everything in the output directory and the directory itself
    if os.path.exists(out_dir):
        shutil.rmtree(out_dir)

if args.cleardata:
    delete_data()

elif args.script:
    if args.playlist:
        download_playlist()
    else:
        parser.error("Playlist has to be specified with --playlist URL")

elif args.nogui:
    # User options and input
    print("""
    SPOTIFY-PLAYLIST-DOWNLOADER
    (get you client ID and secret from 'developer.spotify.com')

    [1] Download playlists
    [2] Delete data (client ID, secret, logs, output, etc.)
    """)
    choice = input(">> ")

    if choice == "1":
        download_playlist()

    elif choice == "2":
        delete_data()

    # Backup in case of ID10T error
    else:
        print("No such option")
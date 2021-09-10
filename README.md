# spotify-playlist-downloader
A tool to download playlists from Spotify from YouTube
## Requirements
* spotipy (`pip3 install -U spotipy`)
* youtube_dl (`pip3 install -U youtube_dl`)
* a client ID and client secret (from `developer.spotify.com`)
## Usage
You can run the program with `python3 main.py`
### Command line options
| Option            | Help text                                                     | Implemented? |
| ----------------- | ------------------------------------------------------------- | ------------ |
| `-ng, --nogui`    | Run the interactive command line interface instead of the GUI | Mostly       |
| `-sc, --script`   | Run the command without asking for input                      | Mostly       |
| `-id, --id`       | Specify the Spotify ID to be used                             | Yes          |
| `-s, --secret`    | Specify the Spotify secret to be used                         | Yes          |
| `-p, --playlist`  | Specify the playlist to download                              | Yes          |
| `-cd, --clearata` | Delete all saved data                                         | No           |
## Contributing
I don't expect anyone to contribute, but it's nice to have these resources that I used saved here.
### Resources
#### youtube-dl
* https://codefather.tech/blog/youtube-search-python/
* https://dev.to/stokry/download-youtube-video-to-mp3-with-python-26p
* https://pypi.org/project/youtube_dl/
#### spotipy
* https://www.promptcloud.com/blog/extracting-songs-data-from-your-spotify-playlist-using-python/
* https://spotipy.readthedocs.io/
#### tkinter
* https://docs.python.org/3/library/tkinter.html
* https://coderslegacy.com/python/python-gui/
#### argparse
* https://docs.python.org/2/library/argparse.html

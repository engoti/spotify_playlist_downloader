import os
import json
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import yt_dlp

app = Flask(__name__, static_folder='static')
CORS(app)

class SpotifyPlaylistDownloader:
    def __init__(self, client_id, client_secret):
        self.client_credentials_manager = SpotifyClientCredentials(
            client_id=client_id, 
            client_secret=client_secret
        )
        self.sp = spotipy.Spotify(client_credentials_manager=self.client_credentials_manager)

    def get_playlist_tracks(self, playlist_id):
        results = self.sp.playlist_tracks(playlist_id)
        tracks = results['items']
        
        while results['next']:
            results = self.sp.next(results)
            tracks.extend(results['items'])
        
        return tracks

    def format_track_name(self, track):
        artists = ' '.join([artist['name'] for artist in track['track']['artists']])
        return f"{track['track']['name']} {artists}"

    def download_track(self, track_name, output_path):
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            }],
            'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
            'nooverwrites': True,
            'no_color': True,
            'quiet': False,
            'no_warnings': False,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(f"ytsearch:{track_name}", download=True)
                if 'entries' in info:
                    for download in info.get('entries', []):
                        if 'requested_downloads' in download:
                            return download['requested_downloads'][0]['filepath']
            except Exception as e:
                print(f"Error downloading {track_name}: {e}")
                return None

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/download-playlist', methods=['POST'])
def download_playlist():
    data = request.json
    client_id = data.get('clientId')
    client_secret = data.get('clientSecret')
    playlist_id = data.get('playlistId')

    try:
        output_directory = os.path.join(os.path.expanduser('~'), 'Downloads', 'SpotifyDownloads')
        os.makedirs(output_directory, exist_ok=True)

        downloader = SpotifyPlaylistDownloader(client_id, client_secret)
        tracks = downloader.get_playlist_tracks(playlist_id)
        
        downloaded_tracks = []
        for track in tracks:
            track_name = downloader.format_track_name(track)
            print(f"Downloading: {track_name}")
            
            downloaded_file = downloader.download_track(track_name, output_directory)
            
            if downloaded_file:
                downloaded_tracks.append({
                    'original_name': track_name,
                    'file_path': downloaded_file
                })
        
        log_path = os.path.join(output_directory, 'download_log.json')
        with open(log_path, 'w') as f:
            json.dump(downloaded_tracks, f, indent=2)
        
        return jsonify({
            'success': True,
            'trackCount': len(downloaded_tracks),
            'tracks': downloaded_tracks
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    os.makedirs('static', exist_ok=True)
    app.run(host='0.0.0.0', port=5000, debug=True)
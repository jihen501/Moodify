import sys
from flask import Flask, redirect, request,jsonify
import subprocess
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from pymongo import MongoClient
from bson.json_util import dumps
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
CLIENT_ID = "0ef9800fc77142d99a18577b30e0b0a6"
CLIENT_SECRET = "5da965b0da714041bcfb355bc4c877c9"
REDIRECT_URI = "https://da03-197-240-197-68.ngrok-free.app/callback"
SCOPE = "user-read-currently-playing user-read-playback-state"


sp_oauth = SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=SCOPE,
    cache_path=".cache"
)

client = MongoClient("mongodb://localhost:27017")  # adapte l'URI si besoin
db = client["moodify"]
weekly_reports_collection = db["weekly_reports"]
recommendations_collection = db["recommendations"]


def login_spotify():
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/auth_spotify')
def callback():
    login_spotify()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    access_token = token_info['access_token']
    sp = Spotify(auth=access_token)
    user_profile = sp.current_user()
    user_id = user_profile['id']
    subprocess.Popen([sys.executable, '../streaming/spotify_producer.py', user_id])
    return redirect(f"http://localhost:5173/?user_id={user_id}")

@app.route('/recommendations/<user_id>', methods=["GET"])
def get_latest_recommendations(user_id):
    '''
    latest_doc=recommendations_collection.find_one(
        {"user_id": user_id},
        sort=[("timestamp", -1)]
    )

    if not latest_doc:
        return jsonify({"error": "No recommendations found for user"}), 404

    # Préparer les recommandations
    track_names = latest_doc.get("recommended_track_names", [])
    track_artists = latest_doc.get("recommended_track_artists", [])
    
    recommendations = [
        {"track_name": name, "track_artist": artist}
        for name, artist in zip(track_names, track_artists)
    ]

    return jsonify({
        "user_id": user_id,
        "timestamp": latest_doc["timestamp"],
        "mood": latest_doc["mood"],
        "recommendations": recommendations
    })'''
    return jsonify({
        "user_id": user_id,
        "timestamp": "2023-10-01T12:00:00Z",
        "mood": "Happy",
        "recommendations": [
            {"track_name": "Happy Song", "track_artist": "Artist A"},
            {"track_name": "Joyful Tune", "track_artist": "Artist B"},
            {"track_name": "Uplifting Melody", "track_artist": "Artist C"}
        ]
    })

@app.route('/weekly_stats/<user_id>', methods=["GET"])
def get_user_weekly_stats(user_id):
    # Récupère le dernier rapport pour ce user (par sécurité, on trie par insertion ou timestamp si dispo)
    #report = weekly_reports_collection.find_one({"user_id": user_id}, sort=[("_id", -1)])

    #if report:
        #return dumps(report), 200  # dumps pour gérer les objets BSON comme ObjectId
  #  else:
        #return jsonify({"error": "No report found for user"}), 404
        return (jsonify({
  "user_id": "abc12",
  "track_count": 45,
  "total_duration_ms": 7560000,
  "mood_counts": {
    "Happy": 20,
    "Sad": 15,
    "Energetic": 7
  },
  "most_common_mood": "Happy",
  "most_common_mood_count": 20,
  "total_duration_min": 128.0,
  "mood_variety": 3,
  "dominance_ratio": 0.476
})
)





if __name__ == '__main__':
    app.run(debug=True)
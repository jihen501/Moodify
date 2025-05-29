import json
import sys
from flask import Flask, redirect, request, jsonify
import subprocess
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from pymongo import MongoClient
from bson.json_util import dumps
from flask_cors import CORS
from kafka import KafkaConsumer
from flask_socketio import SocketIO, emit
import threading

app = Flask(__name__)
CORS(app)
CLIENT_ID = "0ef9800fc77142d99a18577b30e0b0a6"
CLIENT_SECRET = "5da965b0da714041bcfb355bc4c877c9"
REDIRECT_URI = "https://da03-197-240-197-68.ngrok-free.app/callback"
SCOPE = "user-read-currently-playing user-read-playback-state"
socketio = SocketIO(app, cors_allowed_origins="*")

sp_oauth = SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=SCOPE,
    cache_path=".cache"
)

client = MongoClient("mongodb://localhost:27017")
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
    subprocess.Popen(
        [sys.executable, '../streaming/spotify_producer.py', user_id])
    return redirect(f"http://localhost:5173/?user_id={user_id}")

# --- REMOVED /recommendations/<user_id> endpoint ---

@app.route('/weekly_stats/<user_id>', methods=["GET"])
def get_user_weekly_stats(user_id):
    report = weekly_reports_collection.find_one(
        {"user_id": 'user_001'}, sort=[("_id", -1)])

    if report:
        print(dumps(report))
        return dumps(report), 200
    else:
        return jsonify({"error": "No report found for user"}), 404

# --- Kafka Consumer Thread for Real-Time Updates ---
def kafka_realtime_consumer():
    consumer = KafkaConsumer(
        'moodify-updates',
        bootstrap_servers='127.0.0.1:29092',
        auto_offset_reset='latest',
        enable_auto_commit=True,
        group_id="websocket-consumer",
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )
    for msg in consumer:
        data = msg.value
        socketio.emit('recommendation_update', data)

threading.Thread(target=kafka_realtime_consumer, daemon=True).start()

if __name__ == '__main__':
    socketio.run(app, debug=True)
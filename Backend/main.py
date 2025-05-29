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
    subprocess.Popen(
        [sys.executable, '../streaming/spotify_producer.py', user_id])
    return redirect(f"http://localhost:5173/?user_id={user_id}")


@app.route('/recommendations/<user_id>', methods=["GET"])
def get_latest_recommendations(user_id):
    user_id = 'user_001'
    consumer = KafkaConsumer(
        'moodify-updates',
        bootstrap_servers='127.0.0.1:29092',
        auto_offset_reset='latest',
        enable_auto_commit=True,
        group_id=None,  # Use None for a new consumer group each time
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )

    print(f"Listening for Kafka messages for user: {user_id}")

    max_messages = 50
    matched_message = None

    for i, msg in enumerate(consumer):
        data = msg.value
        if data.get("user_id") == user_id:
            matched_message = data
            print('this is matched messages ', matched_message)
            break
        if i >= max_messages:
            break
    consumer.close()

    if not matched_message:
        return jsonify({"error": "No Kafka message found for this user"}), 404
    print('kafka found ', jsonify({
        "user_id": matched_message["user_id"],
        "timestamp": matched_message["timestamp"],
        "mood": matched_message["mood"],
        "track_name": matched_message.get("track_name"),
        "duration_ms": matched_message.get("duration_ms"),
        "recommendations": matched_message.get("recommendations", [])
    }))
    return jsonify({
        "user_id": matched_message["user_id"],
        "timestamp": matched_message["timestamp"],
        "mood": matched_message["mood"],
        "track_name": matched_message.get("track_name"),
        "duration_ms": matched_message.get("duration_ms"),
        "recommendations": matched_message.get("recommendations", [])
    })


@app.route('/weekly_stats/<user_id>', methods=["GET"])
def get_user_weekly_stats(user_id):
    # Récupère le dernier rapport pour ce user (par sécurité, on trie par insertion ou timestamp si dispo)
    report = weekly_reports_collection.find_one(
        {"user_id": 'user_001'}, sort=[("_id", -1)])

    if report:
        print(dumps(report))
        # dumps pour gérer les objets BSON comme ObjectId
        return dumps(report), 200
    else:
        return jsonify({"error": "No report found for user"}), 404


if __name__ == '__main__':
    app.run(debug=True)

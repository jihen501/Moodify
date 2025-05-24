import requests
from spotipy.oauth2 import SpotifyOAuth

# --- Paramètres à renseigner ---
CLIENT_ID = "734aafef80964f24ab1e2754d7e6958c"
CLIENT_SECRET = "3f28a87d472b49b6a8c3d8eec1ffa7be"
REDIRECT_URI = "https://384e-197-14-206-17.ngrok-free.app"
SCOPE = "user-read-currently-playing user-read-playback-state user-modify-playback-state"

sp_oauth = SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=SCOPE,
    cache_path=".cache"  # fichier pour stocker le token et refresh token
)
token_info = sp_oauth.get_access_token(as_dict=True)

if not token_info:
    print("❌ Aucun token trouvé dans .cache. Lance une auth d'abord.")
    exit()

if sp_oauth.is_token_expired(token_info):
    token_info = sp_oauth.refresh_access_token(token_info["refresh_token"])

access_token = token_info["access_token"]

# --- ID du morceau à ajouter (hardcodé) ---
track_uri = "spotify:track:4iV5W9uYEdYUVa79Axb7Rh"

# --- Envoi de la requête POST vers l’API Spotify ---
headers = {
    "Authorization": f"Bearer {access_token}"
}
params = {
    "uri": track_uri
}

response = requests.post(
    "https://api.spotify.com/v1/me/player/queue",
    headers=headers,
    params=params
)

# --- Résultat ---
if response.status_code >= 200 and response.status_code < 300:
    print("✅ Chanson ajoutée à la file d’attente !")
else:
    print(f"❌ Erreur [{response.status_code}]: {response.text}")

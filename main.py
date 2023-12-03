import requests
from bs4 import BeautifulSoup
from auth import SPOTIFY_ID, SPOTIFY_SECRET
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pprint

redirect_uri="http://example.com"

date = input("Which date do you want to travel to? "
             "Type the date in this format: YYYY-MM-DD: ")

URL = "https://www.billboard.com/charts/hot-100/"
URL += date

#Scrap top 100 from billboard.com
response = requests.get(URL)
billboard_page = response.text
soup = BeautifulSoup(billboard_page, "html.parser")

print(f"Scrapping top 100 tracks on {date} from billboard.com...")
songs = [track.getText().strip() for track
         in soup.select(selector="li>ul>li>h3")]

print(f"Scrapping track artists from previous list...")
artists = [artist.getText().strip() for artist
           in soup.select(selector="li>ul>li>span.c-label.a-no-trucate")]

tracks = list(zip(songs, artists))

#Connection to Spotify
scope = "playlist-modify-public"
sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            client_id=SPOTIFY_ID,
            client_secret=SPOTIFY_SECRET,
            redirect_uri=redirect_uri,
            scope=scope))

#year = date.split("-")[0]

#Get Spotify URIs:
print(f"Fetching the songs from Spotify...")
spotify_songs_URIs = [sp.search(q=f"track: {song} artist: {artist}", limit=1, type="track")["tracks"]["items"][0]["uri"]
                      for (song, artist) in tracks]

#Get Spotify user, needed to create the list:
user = sp.current_user()["id"]
#Create the empty list:
playlist_name = f"Billboard.com top 100 on {date}"
print(f"Creating playlist {playlist_name} for user {user} in Spotify...")
playlist = sp.user_playlist_create(user=user, name=playlist_name, public=True,
                                   description=playlist_name)
#Add previously fetched songs to that list:
print(f"Adding fetched tracks from {date} to playlist {playlist_name}...")
result = sp.user_playlist_add_tracks(user, playlist["id"], spotify_songs_URIs)
if result:
    print("Songs successfully added:")
    pp = pprint.PrettyPrinter(depth=4)
    pp.pprint(tracks)

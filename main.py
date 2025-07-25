import requests
from bs4 import BeautifulSoup
from auth import SPOTIFY_IDs, SPOTIFY_SECRETs
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pprint

redirect_uri="http://example.com"

def get_date_pitchfork():
    valid_year = False
    while not valid_year:
        try:
            year = int(input("Pitchfork has top 100 lists from 2019 to 2023, "
                             "please choose one year in that interval: "))
            if year < 2019 or year > 2023:
                print("Please introduce a valid year in the mentioned range!")
            else:
                valid_year = True
        except ValueError:
                print("The value entered is not a number!")
    return str(year)

def get_date_billboard():
    date = input("Which date do you want to travel to? "
                 "Type the date in this format: YYYY-MM-DD: ")
    return date


def pitchfork_get_tracks(year):
    URL = "https://pitchfork.com/features/lists-and-guides/best-songs-"
    URL += year

    #Scrap top 100 from pitchfork.com
    response = requests.get(URL)
    billboard_page = response.text
    soup = BeautifulSoup(billboard_page, "html.parser")

    print(f"Scrapping top 100 tracks of {year} from pitchfork.com...")
    artists_songs = [track.getText().strip() for track
             in soup.select(selector="div.BodyWrapper-kufPGa.cmVAut.body.body__container.article__body div.body__inner-container h2")]

    songs = [entry.split(": ")[0] for entry in artists_songs]
    artists = [entry.replace("“","").replace("”","").split(": ")[1] for entry in artists_songs]
    billboard_positions = range(1, len(songs)+1)

    tracks = list(zip(billboard_positions, songs, artists))
    return tracks

def billboard_get_tracks(date):
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

    billboard_positions = range(1, len(songs)+1)

    tracks = list(zip(billboard_positions, songs, artists))
    return tracks

def handle_spotify(tracks, date, origin, user):
    #Connection to Spotify
    scope = "playlist-modify-public"
    sp = spotipy.Spotify(
            auth_manager=SpotifyOAuth(
                client_id=SPOTIFY_IDs[user],
                client_secret=SPOTIFY_SECRETs[user],
                redirect_uri=redirect_uri,
                scope=scope))

    year = date.split("-")[0]

    #Get Spotify URIs:
    print(f"Fetching the songs from Spotify...")
    try:
        spotify_songs_URIs = [sp.search(q=f"track: {song} artist: {artist}",
                                        limit=1,
                                        type="track")["tracks"]["items"][0]["uri"]
                              for (billboard_positions, song, artist) in tracks]

    except spotipy.oauth2.SpotifyOauthError as e:
        print("spotipy.oauth2.SpotifyOauthError: ", e)
        print("Could not authenticate to Spotify! Exiting immediately!")
        exit(1)

    #Get Spotify user, needed to create the list:
    user = sp.current_user()["id"]

    #Create the empty list:
    playlist_name = f"{origin}.com top 100 on {date}"
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

valid_option = False
while not valid_option:
    print("Please choose one of the two options to create a Spotify playlist:")
    print("1- Billboard.com (exact date)")
    print("2- Pitchfork.com (hits for the full year from 2019 to 2023)")
    option = int(input("Select your option, 1 or 2: "))
    if option < 1 or option > 2:
        print("Please select a valid option!")
    else:
        valid_option = True

if option == 1:
    date = get_date_billboard()
    tracks = billboard_get_tracks(date)
    origin = "Billboard"

elif option == 2:
    year = get_date_pitchfork()
    tracks = pitchfork_get_tracks(year)
    date = f"{year}-12-31"
    origin = "Pitchfork"

valid_user = False
while not valid_user:
    print("Please choose one Spotify user from the list:")
    user = input(f"{list(SPOTIFY_IDs.keys())}: ")
    if user in SPOTIFY_IDs.keys():
        valid_user = True
    else:
        print("The user entered is not in the list!")

handle_spotify(tracks, date, origin, user)

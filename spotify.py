import os
import spotipy, speech_recognition as sr
from spotipy.oauth2 import SpotifyOAuth

client_id = "05cdbf03c5f346dfa9eed9e932208d54"
client_secret = "058a8bbc83234e2b944be74881fa6831"
redirect_uri = "http://localhost:8888/callback/"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                               client_secret=client_secret,
                                               redirect_uri=redirect_uri,
                                               scope="user-read-private user-read-email user-library-read "
                                                     "user-library-modify user-read-playback-state "
                                                     "user-modify-playback-state playlist-read-private "
                                                     "playlist-modify-public playlist-modify-private"))

def isPlaying():
    current_playback = sp.current_playback()
    if current_playback is not None:
        return sp.current_playback()["is_playing"]
    else:
        return False


def playPause():
    playback_state = sp.current_playback()
    if playback_state is None:
        print("No active device found.")
        return
    device_id = playback_state["device"]["id"]
    if device_id is None:
        print("No active device found.")
        return

    playing = isPlaying()
    if not playing:
        sp.start_playback(device_id=device_id)
    else:
        sp.pause_playback(device_id=device_id)


def toggleLikedCurrentSong():
    activeSong = getActiveSong()
    if (activeSong is not None):
        id = activeSong["item"]["id"]
        if sp.current_user_saved_tracks_contains(tracks=[id])[0]:
            sp.current_user_saved_tracks_delete(tracks=[id])
        else:
            sp.current_user_saved_tracks_add(tracks=[id])


def isLikedSong():
    activeSong = getActiveSong()
    if (activeSong is not None):
        if (activeSong["item"] is None):
            return False
        id = activeSong["item"]["id"]
        return sp.current_user_saved_tracks_contains(tracks=[id])[0]


def getActiveSong():
    playing = sp.currently_playing()
    if playing is None:
        return None
    else:
        return playing


def toggleShuffle():
    if (isPlaying()):
        sp.shuffle(not sp.current_playback()["shuffle_state"])


def isShuffle():
    if (isPlaying()):
        return sp.current_playback()["shuffle_state"]
    else:
        return False


def skip():
    if (isPlaying()):
        sp.next_track()


def previous():
    if (isPlaying()):
        sp.previous_track()


def setLoudness(loudness):
    try:
        sp.volume(int(loudness * 100))
    except:
        pass


def addSongs(amount):
    playback = sp.current_playback()["item"]["id"]
    recommendations = sp.recommendations(seed_tracks=[playback])["tracks"]

    index = 0
    for song in recommendations:
        if (index > amount):
            break
        sp.add_to_queue(song["id"])
        index += 1


def clearQueue():
    sp.start_playback(uris=[])


def searchPlaySong(songName, callback=None):
    song = sp.search(q=songName, limit=1, type="track")["tracks"]["items"][0]
    try:
        sp.add_to_queue(song["id"])
        callback(song)
    except:
        pass

def getCurrentSongLink():
    return sp.current_playback()["item"]["external_urls"]["spotify"]
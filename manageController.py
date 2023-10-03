import threading
import subprocess
import pyautogui
import speech_recognition as sr
import pyperclip

import spotify as sp
import audio
import json
import mido
import time

messageInputCooldown = 0.031

displayMidiInputs = False


def reload():
    # load json into soundClasses from soundClasses.json
    global soundClasses
    with open("soundClasses.json", "r") as file:
        soundClasses = json.load(file)


def setLight(note, color):
    if outport is not None:
        outport.send(mido.Message('note_on', note=note, velocity=color))


def changeLight(note, onOff):
    if outport is not None:
        try:
            if (onOff):
                outport.send(mido.Message('note_on', note=note, velocity=noteColors[note]))
            else:
                outport.send(mido.Message('note_on', note=note, velocity=0))
        except Exception as e:
            print(f"Error sending MIDI message: {e}")


def checkSoundClasses():
    for key in soundClasses:
        if (int(key) in changedClass and changedClass[int(key)]):
            audio.changeLevelsForClass(key, loudnessForClass[int(key)])
            changedClass[key] = False


previousSong = None
lastChangedSpotifyInformations = 0


def checkAudioDisplay():
    if (lastChangedLoudness + howLongDisplay > time.time()):
        informations = {
            "tabs": []
        }

        maxAmount = 4
        for i in range(maxAmount):
            id = maxAmount - i
            informations["tabs"].append(
                {'title': classNames[id], 'percentage': loudnessForClass[id], 'color': classColors[id]})

    #     windowOverlay.setOpacity(0.8)
    #     windowOverlay.setInformation(informations)
    # else:
    #     if (lastChangedSpotifyInformations + howLongDisplaySpotify > time.time()):
    #         windowOverlay.setPage("spotify")
    #         windowOverlay.setOpacity(0.9)
    #     else:
    #         windowOverlay.setOpacity(0)


lastChangedSpotify = time.time()


def checkNotesToCheckFor():
    global previousSong, spotifyChanged, lastChangedSpotify

    spotifyKeys = keyChecker["spotify"]
    if (lastChangedSpotify - time.time() > 60 or spotifyChanged):
        spotifyChanged = False
        lastChangedSpotify = time.time()
        for note in spotifyKeys:
            checkKey(note, spotifyKeys[note])

    audio = keyChecker["audio"]
    for note in audio:
        checkKey(note, audio[note])

    appStarter = keyChecker["apps"]
    for note in appStarter:
        checkKey(note, appStarter[note])


def checkKey(note, function):
    if (function()):
        changeLight(note, True)
    else:
        changeLight(note, False)


def changeGlobalAudioOne(level):
    global globalVolumes, globalsChanged
    globalVolumes[0] = level
    globalsChanged[0] = True


def changeGlobalAudioTwo(level):
    global globalVolumes, globalsChanged
    globalVolumes[1] = level
    globalsChanged[1] = True


def checkGlobalVolumes():
    global globalVolumes, globalsChanged

    if (globalsChanged[0]):
        threading.Thread(target=audio.changeGlobalLoudness, args=(globalVolumes[0],)).start()
        globalsChanged[0] = False

    if (globalsChanged[1]):
        threading.Thread(target=sp.setLoudness, args=(globalVolumes[1],)).start()
        globalsChanged[1] = False


def returnTrue():
    return True


def returnFalse():
    return False


outport = None


def handleMidiStuff():
    global lastCalledNote, spotifyChanged, lastChangedLoudness, changedClass, loudnessForClass, outport
    # display all midi devices
    print(mido.get_input_names())
    print(mido.get_output_names())


    with mido.open_input("DJControl Instinct P8 0") as inport:
        with mido.open_output("DJControl Instinct P8 1") as outport:
            outport = outport
            for msg in inport:
                if (displayMidiInputs):
                    print(msg)
                if (msg.type == 'note_on'):
                    if ((msg.note in lastCalledNote and lastCalledNote[
                        msg.note] + messageInputCooldown < time.time()) or msg.note not in lastCalledNote):
                        lastCalledNote[msg.note] = time.time()
                        if (msg.velocity == 127):
                            # Note was pressed on
                            if msg.note in keyListener:
                                keyListener[msg.note]()
                        else:
                            # Note off
                            pass
                        spotifyChanged = True

                elif (msg.type == 'control_change'):
                    if (msg.control in noteForClass):
                        classForNote = noteForClass[msg.control]
                        loudnessForClass[classForNote] = msg.value / 127
                        changedClass[classForNote] = True
                        lastChangedLoudness = time.time()
                    if (msg.control in potentiometerListener):
                        potentiometerListener[msg.control](msg.value / 127)


def startProgram(program):
    threading.Thread(target=lambda: subprocess.call(program)).start()


def pressKey(key):
    pyautogui.press(key)


def generateRandomString(length):
    import random
    import string
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


def enterRandomString():
    pyautogui.write(generateRandomString(20))


def toggleShuffle():
    global spotifyChanged
    spotifyChanged = True
    sp.toggleShuffle()


listening = False


def playSpeech():
    r = sr.Recognizer()

    with sr.Microphone() as source:
        print("Listening...")
        audio = r.listen(source, phrase_time_limit=2)

        try:
            result = r.recognize_google(audio, language="de-DE")
            print(result)
            sp.searchPlaySong(result, callback=setInfo)
        except sr.UnknownValueError:
            print("Could not understand audio.")
        except sr.RequestError as e:
            print(f"Error: {e}")


def setInfo(info):
    pass
    # global lastChangedSpotifyInformations
    # informations = {
    #     'Song Name': info['name'],
    #     'Artist': info['artists'][0]['name'],
    #     'Album': info['album']['name'],
    #     'Album Art': info['album']['images'][0]['url']
    # }
    # windowOverlay.setSpotifyInformations(informations)
    # lastChangedSpotifyInformations = time.time()


def listenAndPlay():
    global listening
    listening = True
    playSpeech()
    listening = False


def isPlaying():
    global listening
    return listening


def copy(string):
    pyperclip.copy(string)


spotifyChanged = True

lastCalledNote = {

}

lastChangedLoudness = time.time()
howLongDisplay = 1
howLongDisplaySpotify = 5

noteColors = {
    25: 127,
    26: 1,
    27: 126,
    28: 126,
    34: 1,
    35: 1,
    57: 126,
    58: 1,
    59: 127,
    60: 1,
    73: 1,
    74: 127,
    75: 126,
    76: 126,
}

keyChecker = {
    "spotify": {
        25: sp.isLikedSong,
        26: returnTrue,
        27: returnTrue,
        28: returnTrue,
        35: sp.isShuffle,
    },
    "audio": {
        73: audio.getMuted,
        74: returnTrue,
        75: returnTrue,
        76: returnTrue,
    },
    "apps": {
        57: returnTrue,
        58: returnTrue,
        59: returnTrue,
        60: returnTrue,
        34: isPlaying,
    }
}

classColors = {
    1: "gray",
    2: "blue",
    3: "darkgreen",
    4: "yellow",
    6: "yellow",
    7: "yellow"
}

keyListener = {
    25: lambda: sp.toggleLikedCurrentSong(),
    26: lambda: sp.playPause(),
    27: lambda: sp.previous(),
    28: lambda: sp.skip(),

    33: lambda: sp.addSongs(3),
    34: lambda: listenAndPlay(),
    35: lambda: toggleShuffle(),

    57: lambda: startProgram("C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe"),
    58: lambda: startProgram("C:\\Users\\janne\\AppData\\Local\\Discord\\app-1.0.9012\\Discord.exe"),
    59: lambda: startProgram("C:\\Users\\janne\\AppData\\Roaming\\Spotify\\Spotify.exe"),
    60: lambda: startProgram("C:\\Program Files (x86)\\Steam\\steam.exe"),

    73: lambda: audio.toggleMute(),
    74: lambda: pressKey("playpause"),
    75: lambda: pressKey("prevtrack"),
    76: lambda: pressKey("nexttrack"),

    81: lambda: copy(sp.getCurrentSongLink()),
}

classNames = {
    1: "Discord",
    2: "Games",
    3: "Music",
    4: "Browser",
    6: " - ",
    7: " - "
}

noteForClass = {
    68: 1,
    70: 2,
    72: 3,
    80: 4,
    82: 6,
    84: 7,
}

loudnessForClass = {
    1: 1,
    2: 1,
    3: 1,
    4: 1,
    6: 1,
    7: 1
}

changedClass = {
    1: False,
    2: False,
    3: False,
    4: False,
    6: False,
    7: False
}

globalVolumes = {
    1: 0,
    2: 1,
}
globalsChanged = {
    0: False,
    1: False
}

potentiometerListener = {
    66: changeGlobalAudioOne,
    64: changeGlobalAudioTwo
}

soundClasses = {}

reload()

audio.setSoundClasses(soundClasses)


def checkEverything():
    checkSoundClasses()
    checkNotesToCheckFor()
    checkGlobalVolumes()
    checkAudioDisplay()

    threading.Timer(0.1, checkEverything).start()


# threading.Thread(target=handleMidiStuff).start()
threading.Thread(target=checkEverything).start()
handleMidiStuff()
# windowOverlay.__init__(checkEverything)
print("Finished init")

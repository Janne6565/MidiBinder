from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume, IAudioEndpointVolume
from comtypes import CLSCTX_ALL, CoUninitialize, CoInitialize, POINTER, cast

apps = {

}

running = False


def setSound(name, futureVolume):
    global coInitialized, running
    running = True
    CoInitialize()

    try:
        sessions = AudioUtilities.GetAllSessions()
        if sessions is not None:
            found = False
            for session in sessions:
                volume = session._ctl.QueryInterface(ISimpleAudioVolume)
                if session.Process:
                    if session.Process.name() == name:
                        found = True
                        volume.SetMasterVolume(futureVolume, None)
    except Exception as e:
        print("Error changing loudness for", name, ":", e)

    running = False
    return found


def setSounds(names, futureVolume):
    for i in names:
        setSound(i, futureVolume)


def getListOfAllApps():
    sessions = AudioUtilities.GetAllSessions()
    sessionsList = []
    for session in sessions:
        if session.Process:
            sessionsList.append({"name": session.Process.name()})
    return sessionsList


def setSoundClasses(items):
    global apps
    apps = items


def changeLevelsForClass(classId, futureVolume):
    global apps

    if str(classId) in apps:
        setSounds(apps[str(classId)], futureVolume)
    else:
        pass


def changeGlobalLoudness(futureVolume):
    # print("Changing global loudness to", futureVolume)
    global coInitialized, running
    running = True

    CoInitialize()

    try:
        devices = AudioUtilities.GetSpeakers()
        if devices is not None:
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            if interface is not None:
                volume = cast(interface, POINTER(IAudioEndpointVolume))

                volume.SetMasterVolumeLevelScalar(futureVolume, None)
    except Exception as e:
        print("Error changing global loudness:", e)
    running = False


def toggleMute():
    global coInitialized
    running = True
    CoInitialize()

    try:
        devices = AudioUtilities.GetSpeakers()
        if devices is not None:
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            if getMuted():
                volume.SetMute(0, None)
            else:
                volume.SetMute(1, None)
    except Exception as e:
        print("Error getting mute state:", e)
    finally:
        if 'volume' in locals():
            volume.Release()
    running = False


coInitialized = False

stillRunning = False

lastValue = None


def getMuted():
    global coInitialized, lastValue, running

    if (running):
        return lastValue

    CoInitialize()
    running = True
    try:
        devices = AudioUtilities.GetSpeakers()
        if devices is not None:
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            if interface is not None:
                # noinspection PyTypeChecker
                volume = cast(interface, POINTER(IAudioEndpointVolume))

                if (volume.GetMute() == 0):
                    lastValue = False
                    return False
                else:
                    lastValue = True
                    return True
    except Exception as e:
        print("Error getting mute state:", e)
    finally:
        if 'volume' in locals():
            volume.Release()
    running = False

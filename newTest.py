import mido
import time


class Trigger:

    def checkActivation(self, msg):
        if (msg.velocity == 0):
            return False
        else:
            return True


class Action:

    def run(self):
        pass


def parseMessage(message):
    if (message.type == 'note_on'):
        noteListener(message)


def noteListener(message):
    activated = None

    if (message.velocity == 0):
        activated = False
    else:
        activated = True
    if (activated):
        outport.send(mido.Message('note_on', note=message.note, velocity=127))
    else:
        outport.send(mido.Message('note_off', note=message.note, velocity=127))


# with mido.open_input() as inport:
#    for msg in inport:
#        # parseMessage(msg)

with mido.open_output('DJControl Instinct P8 1') as outport:
    for i in range(128):
        outport.send(mido.Message('note_on', note=27, velocity=i))
        time.sleep(0.1)
        print(i)

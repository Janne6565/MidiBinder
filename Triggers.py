from Actions import Action
from mido import Message


class Trigger:
    def checkActivation(self, msg: Message, action: Action):
        pass


class BaseNoteTrigger(Trigger):
    def __init__(self, note):
        self.note = note

    def checkActivation(self, msg: Message, action: Action):
        if (msg.type == 'note_on' and msg.note == self.note):
            action.run()
            return True
        else:
            return False

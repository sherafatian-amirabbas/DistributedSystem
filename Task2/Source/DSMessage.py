import enum


class DSMessageType(enum.Enum):
    Ping = 1
    Nudge = 2
    StartElection = 3
    NewCoordinator = 4
    List = 6
    Clock = 7
    GetClock = 9
    SetTime = 10
    ResetClock = 11
    Kill = 12
    Freeze = 13
    Unfreeze = 14



class DSMessage:
    def __init__(self, messageType, argument = None, tag = None):
        self.Type = messageType
        self.Argument = argument
        self.Tag = tag

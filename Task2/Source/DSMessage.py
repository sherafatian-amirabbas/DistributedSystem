import enum


class DSMessageType(enum.Enum):
    Ping = 1
    Nudge = 2
    StartElection = 3
    NewCoordinator = 4
    UpdateParticipation = 5
    List = 6
    Clock = 7
    UpdateClock = 8
    GetClock = 9


class DSMessage:
    def __init__(self, messageType, argument = None, tag = None):
        self.Type = messageType
        self.Argument = argument
        self.Tag = tag

import enum

class DSMessageType(enum.Enum):
    Ping = 1

class DSMessage:
    def __init__(self, messageType, argument = None, tag = None):
        self.Type = messageType
        self.Argument = argument
        self.Tag = tag

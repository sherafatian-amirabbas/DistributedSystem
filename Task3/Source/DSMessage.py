import enum


class DSMessageType(enum.Enum):
    Ping = 1
    SetNewValue = 10
    RollbackValues = 20
    SyncNewProcess = 30
    GetData = 40
    ArbitraryFailure = 50

    InitRequest = 1000
    VoteRequest = 2000
    VoteCommit = 3000
    VoteAbort = 4000
    GlobalCommit = 5000
    GlobalAbort = 6000

class DSMessage:
    def __init__(self, messageType, argument = None, tag = None):
        self.Type = messageType
        self.Argument = argument
        self.Tag = tag

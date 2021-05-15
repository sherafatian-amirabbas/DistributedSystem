import enum


class DSMessageType(enum.Enum):
    Ping = 1
    SetNewValue = 10
    RollbackValues = 20
    SyncNewProcess = 30
    GetData = 40
    ArbitraryFailure = 50
    TimeFailure = 60
    GetParticipantState = 70

    InitRequest = 1000
    VoteRequest = 2000
    VoteCommit = 3000
    VoteAbort = 4000
    GlobalCommit = 5000
    GlobalAbort = 6000

class DSMessage:
    def __init__(self, messageType, argument = None, tag = None, timeout = 5):
        self.Type = messageType
        self.Argument = argument
        self.Tag = tag
        
        # by default we simulate 10 seconds to respond. If during this duration DSSocket couldn't make the
        # connection to its process it will respond with a specific code to the caller. in this way we
        # are handling the time failure. if each process want to define its own timeout, then its more than
        # easy just to overwrite this attribute when it's sending a message to a process socket
        self.Timeout = timeout
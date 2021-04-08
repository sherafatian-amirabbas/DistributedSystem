import enum

from DSMessage import DSMessageType



class DSSocketStatus(enum.Enum):
    Open = 1
    Closed = 2


class DSSocketAddress:
    def __init__(self, port, host = "127.0.0.1"):
        self.Port = port
        self.Host = host

    def IsEqualTo(self, socketAddress):
        return self.Host == socketAddress.Host and self.Port == socketAddress.Port


class DSSocket:
    def __init__(self, dsSocketAddress, bullyProcess):
        self.SocketAddress = dsSocketAddress
        self.BullyProcess = bullyProcess
        self.Status = DSSocketStatus.Closed


    def Open(self):
        self.Status = DSSocketStatus.Open


    def Close(self):
        self.Status = DSSocketStatus.Closed
        

    def SendMessage(self, dsMessage):
        result = None

        if dsMessage.Type == DSMessageType.Ping:
            result = self.BullyProcess.PingCommandHandler(dsMessage)
        if dsMessage.Type == DSMessageType.Nudge:
            result = self.BullyProcess.NudgeCommandHandler(dsMessage)
        if dsMessage.Type == DSMessageType.StartElection:
            result = self.BullyProcess.StartElectionCommandHandler(dsMessage)
        if dsMessage.Type == DSMessageType.NewCoordinator:
            result = self.BullyProcess.NewCoordinatorCommandHandler(dsMessage)
        if dsMessage.Type == DSMessageType.UpdateParticipation:
            result = self.BullyProcess.UpdateParticipationCommandHandler(dsMessage)
        if dsMessage.Type == DSMessageType.List:
            result = self.BullyProcess.ListCommandHandler(dsMessage)

        return result
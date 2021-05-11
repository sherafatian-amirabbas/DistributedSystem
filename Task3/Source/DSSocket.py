import enum

from DSMessage import DSMessageType


class DSSocketStatus(enum.Enum):
    Open = 1
    Closed = 2


class DSSocketAddress:
    def __init__(self, port, host="127.0.0.1"):
        self.Port = port
        self.Host = host

    def IsEqualTo(self, socketAddress):
        return self.Host == socketAddress.Host and self.Port == socketAddress.Port


class DSSocket:
    def __init__(self, dsSocketAddress, dsProcess):
        self.SocketAddress = dsSocketAddress
        self.DSProcess = dsProcess
        self.Status = DSSocketStatus.Closed

    def Open(self):
        self.Status = DSSocketStatus.Open

    def Close(self):
        self.Status = DSSocketStatus.Closed

    def SendMessage(self, dsMessage):

        if self.Status == DSSocketStatus.Closed:
            return 'socket is not open'

        result = None

        if dsMessage.Type == DSMessageType.Ping:
            result = self.DSProcess.PingCommandHandler(dsMessage)


        elif dsMessage.Type == DSMessageType.SetNewValue:
            result = self.DSProcess.SetNewValueCommandHandler(dsMessage)

        elif dsMessage.Type == DSMessageType.InitRequest:
            result = self.DSProcess.InitRequestCommandHandler(dsMessage)

        elif dsMessage.Type == DSMessageType.VoteRequest:
            result = self.DSProcess.VoteRequestCommandHandler(dsMessage)

        elif dsMessage.Type == DSMessageType.VoteCommit:
            result = self.DSProcess.VoteCommitCommandHandler(dsMessage)

        elif dsMessage.Type == DSMessageType.VoteAbort:
            result = self.DSProcess.VoteAbortCommandHandler(dsMessage)

        elif dsMessage.Type == DSMessageType.GlobalCommit:
            result = self.DSProcess.GlobalCommitCommandHandler(dsMessage)

        elif dsMessage.Type == DSMessageType.GlobalAbort:
            result = self.DSProcess.GlobalAbortCommandHandler(dsMessage)


        elif dsMessage.Type == DSMessageType.RollbackValues:
            result = self.DSProcess.RollbackValuesCommandHandler(dsMessage)


        elif dsMessage.Type == DSMessageType.SyncNewProcess:
            result = self.DSProcess.SyncNewProcessCommandHandler(dsMessage)

        elif dsMessage.Type == DSMessageType.GetData:
            result = self.DSProcess.GetDataCommandHandler(dsMessage)

        elif dsMessage.Type == DSMessageType.ArbitraryFailure:
            result = self.DSProcess.ArbitraryFailureCommandHandler(dsMessage)

        return result

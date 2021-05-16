import enum

from DSMessage import DSMessageType
from DSBlocker import DSBlocker


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
        self.DSBlocker = DSBlocker(self.unblockerHander)

    def Open(self):
        self.Status = DSSocketStatus.Open

    def Close(self):
        self.Status = DSSocketStatus.Closed

    def SendMessage(self, dsMessage):

        if self.Status == DSSocketStatus.Closed:
            return 'socket is not open'

        if self.DSProcess.timeFailure == True:
            val = self.DSBlocker.Block(dsMessage.Timeout)
            # if we get val as 0, means that the process is back from the time failure meaning that
            # we can proceed. But if  we get 1, meants that we reached the timeout and process is still
            # unavailable, so wen shouldn't proceed
            if val == 1:
                return 'timeout'

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

        elif dsMessage.Type == DSMessageType.PreCommit:
            result = self.DSProcess.PreCommitCommandHandler(dsMessage)

        elif dsMessage.Type == DSMessageType.PreCommitAcknowledge:
            result = self.DSProcess.PreCommitAcknowledgeCommandHandler(dsMessage)

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

        elif dsMessage.Type == DSMessageType.TimeFailure:
            result = self.DSProcess.TimeFailureCommandHandler(dsMessage)

        elif dsMessage.Type == DSMessageType.GetParticipantState:
            result = self.DSProcess.GetParticipantStateCommandHandler(dsMessage)


        return result

    # -------------------------- private methods

    def unblockerHander(self):
        return not self.DSProcess.timeFailure

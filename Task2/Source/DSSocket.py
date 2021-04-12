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
        msg = "The command is not available for Suspended processes"


        if dsMessage.Type == DSMessageType.Ping:
            result = self.BullyProcess.PingCommandHandler(dsMessage)


        if dsMessage.Type == DSMessageType.Nudge:
            if self.BullyProcess.isSuspended():
                return msg
            result = self.BullyProcess.NudgeCommandHandler(dsMessage)


        if dsMessage.Type == DSMessageType.StartElection:
            if self.BullyProcess.isSuspended():
                return msg
            result = self.BullyProcess.StartElectionCommandHandler(dsMessage)


        if dsMessage.Type == DSMessageType.NewCoordinator:
            if self.BullyProcess.isSuspended():
                return msg
            result = self.BullyProcess.NewCoordinatorCommandHandler(dsMessage)


        if dsMessage.Type == DSMessageType.List:
            result = self.BullyProcess.ListCommandHandler(dsMessage)


        if dsMessage.Type == DSMessageType.Clock:
            result = self.BullyProcess.ClockCommandHandler(dsMessage)


        if dsMessage.Type == DSMessageType.GetClock:
            if self.BullyProcess.isSuspended():
                return msg
            result = self.BullyProcess.GetClockCommandHandler(dsMessage)


        if dsMessage.Type == DSMessageType.SetTime:
            if self.BullyProcess.isSuspended():
                return msg
            result = self.BullyProcess.SetTimeCommandHandler(dsMessage)


        if dsMessage.Type == DSMessageType.Kill:
            if self.BullyProcess.isSuspended():
                raise Exception(msg)
            result = self.BullyProcess.KillCommandHandler(dsMessage)


        if dsMessage.Type == DSMessageType.ResetClock:
            if self.BullyProcess.isSuspended():
                return msg
            result = self.BullyProcess.ResetClockCommandHandler(dsMessage)


        if dsMessage.Type == DSMessageType.Freeze:
            if self.BullyProcess.isSuspended():
                return msg
            result = self.BullyProcess.FreezeCommandHandler(dsMessage)


        if dsMessage.Type == DSMessageType.Unfreeze:
            if self.BullyProcess.isRun():
                return "The command is not available for Running processes"
            result = self.BullyProcess.UnfreezeCommandHandler(dsMessage)

        return result

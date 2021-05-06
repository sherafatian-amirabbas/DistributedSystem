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
        result = None

        if dsMessage.Type == DSMessageType.Ping:
            result = self.DSProcess.PingCommandHandler(dsMessage)

        return result

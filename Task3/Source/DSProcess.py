import enum

from DSPortManager import portManager
from DSSocket import DSSocketAddress, DSSocket
from DSMessage import DSMessage, DSMessageType
from DSTimer import DSTimer


class DSProcessStatus(enum.Enum):
    Stopped = 0
    Running = 1


class DSProcess():
    def __init__(self, id):
        self.Id = id
        self.Status = DSProcessStatus.Stopped
        self.DSSocket = None
        self.timer = DSTimer(1, self.timer_elapsed)

    def Run(self, startTimer = True):
        self.Status = DSProcessStatus.Running

        port = portManager.GetANewPort()
        socketAddress = DSSocketAddress(port)
        self.DSSocket = DSSocket(socketAddress, self)
        self.DSSocket.Open()

        if startTimer:
            self.timer.Start()

    def Dispose(self):
        self.Status = DSProcessStatus.Stopped
        self.DSSocket.Close()
        self.timer.Cancel()

    # ---------------------------------------------------------------------------------------- handlers

    def timer_elapsed(self):
        self.timer.Restart()

    # ---------------------------------------------------------------------------------------- Commands

    def PingCommandHandler(self, dsMessage):
        if self.Status == DSProcessStatus.Stopped:
            return "I am stopped :( , my ID is: '" + str(self.Id) + "'"
        elif self.Status == DSProcessStatus.Running:
            return "Hey... I'm running and my ID is: '" + str(self.Id) + "'"

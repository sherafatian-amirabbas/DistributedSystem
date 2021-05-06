import enum

from DSPortManager import portManager
from DSSocket import DSSocketAddress, DSSocket
from DSMessage import DSMessage, DSMessageType
from DSTimer import DSTimer


class DSProcessStatus(enum.Enum):
    Stopped = 0
    Running = 1


class DSProcess():
    def __init__(self, id, isCoordinator):
        self.Id = id
        self.IsCoordinator = isCoordinator
        self.DSStatus = DSProcessStatus.Stopped
        self.DSSocket = None
        self.timer = DSTimer(1, self.timer_elapsed)

    def Run(self, startTimer = True):
        self.DSStatus = DSProcessStatus.Running

        port = portManager.GetANewPort()
        socketAddress = DSSocketAddress(port)
        self.DSSocket = DSSocket(socketAddress, self)
        self.DSSocket.Open()

        if startTimer:
            self.timer.Start()

    def Dispose(self):
        self.DSStatus = DSProcessStatus.Stopped
        self.DSSocket.Close()
        self.timer.Cancel()

    # ---------------------------------------------------------------------------------------- handlers

    def timer_elapsed(self):
        self.timer.Restart()

    # ---------------------------------------------------------------------------------------- Commands

    def PingCommandHandler(self, dsMessage):
        if self.DSStatus == DSProcessStatus.Stopped:
            return "I am stopped :( , my ID is: '" + str(self.Id) + "'"
        elif self.DSStatus == DSProcessStatus.Running:
            return "Hey... I'm running and my ID is: '" + str(self.Id) + "'"

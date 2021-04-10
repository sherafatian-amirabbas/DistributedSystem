import enum
import threading

from DSPortManager import portManager

from DSSocket import DSSocketAddress, DSSocket
from DSMessage import DSMessage, DSMessageType

from DSTimer import DSTimer


class BullyProcessStatus(enum.Enum):
    Killed = 0
    Run = 1
    Suspended = 2


class BullyProcess():
    def __init__(self, id, name, participationCounter, clock):
        self.Id = id
        self.CoordinatorProcessId = None
        self.Name = name
        self.ParticipationCounter = participationCounter
        self.DefaultClock = clock
        self.Clock = clock
        self.Status = BullyProcessStatus.Killed
        self.sharedData = None

        self.DSSocket = None
        self.timer = DSTimer(3, self.timer_elapsed)
        self.timer.Start()

    def Init(self, sharedData):
        self.sharedData = sharedData

    def Run(self):
        self.Status = BullyProcessStatus.Run

        port = portManager.GetANewPort()
        socketAddress = DSSocketAddress(port)
        self.DSSocket = DSSocket(socketAddress, self)
        self.DSSocket.Open()

    def ToString(self):
        inf = str(self.Id) + ", " + self.Name + "_" + str(self.ParticipationCounter) + ", " + self.Clock
        if self.isCoordinator():
            inf += " (Coordinator)"
            
        if self.isSuspended():
            inf += " (Suspended)"

        return inf

    def Dispose(self):
        self.DSSocket.Close()

    # ---------------------------------------------------------------------------------------- handlers

    def timer_elapsed(self):
        if BullyProcess.GetCoordinator(self.sharedData):
            self.clockSynchronization()
        else:
            BullyProcess.StartElection(self.sharedData)
            self.clockSynchronization()

        self.timer.Restart()

    def clockSynchronization(self):
        if not self.isCoordinator():
            self.syncClock()


    # ---------------------------------------------------------------------------------------- Commands

    def PingCommandHandler(self, dsMessage):
        return "Hey... I am alive!"

    def NudgeCommandHandler(self, dsMessage):
        return self.Id

    def StartElectionCommandHandler(self, dsMessage):
        nextProcessId = self.getNextProcessID()

        if nextProcessId == -1:
            self.notifyProcessesAboutNewCoordinator()
        else:
            processes = list(filter(lambda x: x.Id == nextProcessId, self.sharedData.BullyProcesses))
            processes = BullyProcess.GetSortProcessList(processes)
            nextProc = processes[0]

            msg = DSMessage(DSMessageType.StartElection)
            nextProc.DSSocket.SendMessage(msg)

    def NewCoordinatorCommandHandler(self, dsMessage):
        self.CoordinatorProcessId = int(dsMessage.Argument)

    def UpdateParticipationCommandHandler(self):
        self.ParticipationCounter = self.ParticipationCounter + 1

    def ListCommandHandler(self, dsMessage):
        desc = str(self.Id) + ", " + self.Name + "_" + str(self.ParticipationCounter)
        if self.Id == self.CoordinatorProcessId:
            desc += " (Coordinator)"
        desc += "\n"

        processes = list(filter(lambda x: x.Id > self.Id, self.sharedData.BullyProcesses))
        processesLength = len(processes)
        if processesLength != 0:
            processes = BullyProcess.GetSortProcessList(processes)
            nextProc = processes[0]
            msg = DSMessage(DSMessageType.List)
            result = nextProc.DSSocket.SendMessage(msg)
            desc += result

        return desc

    def ClockCommandHandler(self, dsMessage):

        self.updateClock()

        desc = self.Name + "_" + str(self.ParticipationCounter) + ", " + self.Clock + "\n"

        processes = list(filter(lambda x: x.Id > self.Id, self.sharedData.BullyProcesses))
        processesLength = len(processes)
        if processesLength != 0:
            processes = BullyProcess.GetSortProcessList(processes)
            nextProc = processes[0]
            msg = DSMessage(DSMessageType.Clock)
            result = nextProc.DSSocket.SendMessage(msg)
            desc += result
        return desc

    def SetTimeCommandHandler(self, dsMessage):
        self.Clock = dsMessage.Argument
        return "Clock is changed"

    def GetClockCommandHandler(self, dsMessage):
        return self.Clock

    def KillCommandHandler(self, dsMessage):
        self.kill()
        if self.isCoordinator():
            self.resetClocks()

    def ResetClockCommandHandler(self, dsMessage):
        self.Clock = self.DefaultClock

    def FreezeCommandHandler(self, dsMessage):
        self.Status = BullyProcessStatus.Suspended
        self.timer.Cancel()
        self.Dispose()

        if self.isCoordinator():
            BullyProcess.StartElection(self.sharedData)



    # --------------------------------------------------------------------------------- Private Methods

    def kill(self):
        self.Status = BullyProcessStatus.Killed
        self.sharedData.RemoveProcess(self.Id)
        self.Dispose()

    def syncClock(self):
        if BullyProcess.GetCoordinator(self.sharedData):
            self.Clock = self.getCoordinatorClock()
        else:
            self.Clock = self.DefaultClock

    def getCoordinatorClock(self):
        process = BullyProcess.GetCoordinator(self.sharedData)
        return process.DSSocket.SendMessage(DSMessage(DSMessageType.GetClock))

    def isCoordinator(self):
        return self.Id == self.CoordinatorProcessId and not self.isSuspended()

    def updateClock(self):
        if not self.isCoordinator() and not self.isSuspended():
            self.syncClock()

    def resetClocks(self):
        for process in self.sharedData.BullyProcesses:
            process.DSSocket.SendMessage(DSMessage(DSMessageType.ResetClock))

    def getNextProcessID(self):
        NextProcessId = -1

        processes = list(filter(lambda x: x.Id > self.Id and not x.isSuspended(), self.sharedData.BullyProcesses))
        processesLength = len(processes)
        if processesLength != 0:

            processIds = []
            for index, process in enumerate(processes):
                msg = DSMessage(DSMessageType.Nudge)
                result = process.DSSocket.SendMessage(msg)

                if result:
                    processId = int(result)
                    if processId:
                        processIds.append(processId)

            if len(processIds) != 0:
                processIds.sort()
                NextProcessId = processIds[0]

        return NextProcessId

    def notifyProcessesAboutNewCoordinator(self):
        self.CoordinatorProcessId = self.Id
        for index, process in enumerate(self.sharedData.BullyProcesses):
            if process.Id != self.Id:
                msg = DSMessage(DSMessageType.NewCoordinator, self.Id)
                process.DSSocket.SendMessage(msg)

    def isSuspended(self):
        return self.Status == BullyProcessStatus.Suspended

    # --------------------------------------------------------------------------------- static Methods

    @staticmethod
    def StartElection(sharedData):
        
        # Double-checked locking
        # https://en.wikipedia.org/wiki/Double-checked_locking

        if not BullyProcess.GetCoordinator(sharedData):
            with sharedData.Lock:
                if not BullyProcess.GetCoordinator(sharedData):
                    processes = list(filter(lambda x: not x.isSuspended(), sharedData.BullyProcesses))
                    processes = BullyProcess.GetSortProcessList(processes)
                    firstProc = processes[0]
                    firstProc.DSSocket.SendMessage(DSMessage(DSMessageType.StartElection))

    @staticmethod
    def GetCoordinator(sharedData):
        coordinatorProc = None
        for _, process in enumerate(sharedData.BullyProcesses):
            if process.CoordinatorProcessId == process.Id and not process.isSuspended():
                coordinatorProc = process
                break

        return coordinatorProc

    @staticmethod
    def GetSortProcessList(processes):
        return sorted(processes, key=lambda proc: proc.Id)

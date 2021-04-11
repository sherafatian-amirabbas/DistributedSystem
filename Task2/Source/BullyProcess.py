import enum

from DSPortManager import portManager
from DSSharedData import sharedData

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

        self.DSSocket = None
        self.timer = DSTimer(10, self.timer_elapsed)
        self.timer.Start()
  
    def Kill(self):
        self.Status = BullyProcessStatus.Killed

    def Run(self):
        self.Status = BullyProcessStatus.Run

        port = portManager.GetANewPort()
        socketAddress = DSSocketAddress(port)
        self.DSSocket = DSSocket(socketAddress, self)
        self.DSSocket.Open()

    def ToString(self):
        return str(self.Id) + ", " + self.Name + "_" + str(self.ParticipationCounter) + ", " + self.Clock


    # ---------------------------------------------------------------------------------------- handlers

    def timer_elapsed(self):
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
            processes = list(filter(lambda x: x.Id == nextProcessId, sharedData.BullyProcesses))
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

        processes = list(filter(lambda x: x.Id > self.Id, sharedData.BullyProcesses))
        processesLength = len(processes)
        if processesLength != 0:
            processes = BullyProcess.GetSortProcessList(processes)
            nextProc = processes[0]
            msg = DSMessage(DSMessageType.List)
            result = nextProc.DSSocket.SendMessage(msg)
            desc += result

        return desc

    def ReloadCommandHandler(self,dsMessage):
        activeProcessesId=[process.Id for process in sharedData.BullyProcesses]
        allProcesses=sharedData.ReloadProcesses
        processofReloaded=[]
        if len(activeProcessesId)==len(allProcesses):
            return "all processes are in the list"
        else:
            for process in allProcesses:
                if process.Id not in activeProcessesId:
                    processofReloaded.append(process)

        for incremental, process in enumerate(processofReloaded):
            process.Run()
            sharedData.BullyProcesses.append(process)
            process.ParticipationCounter+=incremental
            self.StartElectionCommandHandler(process)
            for process in sharedData.BullyProcesses:
                 process.ParticipationCounter+=1
            
        return "Processes are reloaded"

                
            
            



            



            




    def ClockCommandHandler(self, dsMessage):

        self.updateClocks()

        desc = self.Name + "_" + str(self.ParticipationCounter) + ", " + self.Clock + "\n"

        processes = list(filter(lambda x: x.Id > self.Id, sharedData.BullyProcesses))
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


    def UpdateClockCommandHandler(self, dsMessage):
        if not self.isCoordinator():
            self.syncClock()

    def GetClockCommandHandler(self, dsMessage):
        return self.Clock

    # --------------------------------------------------------------------------------- Private Methods

    def syncClock(self):
        self.Clock = self.getCoordinatorClock()

    def getCoordinator(self):
        coordinatorProc = None
        for index, process in enumerate(sharedData.BullyProcesses):
            if self.CoordinatorProcessId == process.Id:
                coordinatorProc = process
                break

        return coordinatorProc

    def getCoordinatorClock(self):
        process = self.getCoordinator()
        return process.DSSocket.SendMessage(DSMessage(DSMessageType.GetClock))

    def isCoordinator(self):
        return self.Id == self.CoordinatorProcessId

    def updateClocks(self):
        for process in sharedData.BullyProcesses:
            process.DSSocket.SendMessage(DSMessage(DSMessageType.UpdateClock))

    def getNextProcessID(self):
        NextProcessId = -1

        processes = list(filter(lambda x: x.Id > self.Id, sharedData.BullyProcesses))
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
        for index, process in enumerate(sharedData.BullyProcesses):
            if process.Id != self.Id:
                msg = DSMessage(DSMessageType.NewCoordinator, self.Id)
                process.DSSocket.SendMessage(msg)

    # --------------------------------------------------------------------------------- static Methods

    @staticmethod
    def GetSortProcessList(processes):
        return sorted(processes, key=lambda proc: proc.Id)

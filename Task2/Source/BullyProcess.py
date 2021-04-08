import enum

from DSPortManager import portManager
from DSSharedData import sharedData

from DSSocket import DSSocketAddress, DSSocket
from DSMessage import DSMessage, DSMessageType


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


    def Run(self):
        self.Status = BullyProcessStatus.Run

        port = portManager.GetANewPort()
        socketAddress = DSSocketAddress(port)
        self.DSSocket = DSSocket(socketAddress, self)
        self.DSSocket.Open()
        

    def ToString(self):
        return str(self.Id) + ", " + self.Name + "_" + str(self.ParticipationCounter) + ", " + self.Clock


    # ---------------------------------------------------------------------------------------- Commands

    def PingCommandHandler(self, dsMessage):
        return "Hey... I am alive!"


    def NudgeCommandHandler(self, dsMessage):
        return self.Id


    def StartElectionCommandHandler(self, dsMessage):
        nextProcessId = self.nudgeOtherProcessesAndGetNextProcessID()

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


    def UpdateParticipation(self):
        self.CoordinatorProcessId = self.CoordinatorProcessId + 1


    def ListCommandHandler(self, dsMessage):
        return "List Command Was Executed"

    # --------------------------------------------------------------------------------- Private Methods

    def nudgeOtherProcessesAndGetNextProcessID(self):
        NextProcessId = -1

        processes = list(filter(lambda x: x.Id > self.Id, sharedData.BullyProcesses))
        processesLength = len(processes)
        if processesLength != 0 :

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
            return sorted(processes, key=lambda proc : proc.Id)
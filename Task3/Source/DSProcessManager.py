import threading

class DSProcessManager():

    def __init__(self):
        self.DSProcesses = []

    def Initialize(self, ListOfDSProcesses):
        self.DSProcesses = ListOfDSProcesses

    def AddProcesses(self, ListOfDSProcesses):
        for process in ListOfDSProcesses:
            self.DSProcesses.append(process)

    def RemoveProcess(self, processId):
        processes = []
        for p in self.DSProcesses:
            if p.Id != processId:
                processes.append(p)
        self.DSProcesses = processes

    def GetProcessByID(self, processId):
        result = None
        processes = list(filter(lambda x: x.Id == processId, self.DSProcesses))
        if len(processes) != 0:
            result = processes[0]
        return result

    def setAnotherProcessAsCoordinator(self):
        self.DSProcesses[0].IsCoordinator = True

    def getProcessesCount(self):
        return len(self.DSProcesses)

    def GetProcessDescriptions(self):
        result = []
        for p in self.DSProcesses:
            str = p.Id
            if p.IsCoordinator:
                str = str + ' (coordinator)'
            result.append(str)

        return result

    def GetCoordinator(self):
        result = None
        processes = list(filter(lambda x: x.IsCoordinator == True, self.DSProcesses))
        if len(processes) != 0:
            result = processes[0]
        return result

    def GetParticipants(self):
        processes = list(filter(lambda x: x.IsCoordinator == False, self.DSProcesses))
        return processes


dsProcessManager = DSProcessManager()
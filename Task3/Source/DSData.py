import threading

class DSData():

    def __init__(self):
        self.DSProcesses = []
        self.DataValueHistory = []

    def Initialize(self, ListOfDSProcesses, dataValueHistory):
        self.DSProcesses = ListOfDSProcesses
        self.DataValueHistory = dataValueHistory

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

    def GetCoordinator(self):
        result = None
        processes = list(filter(lambda x: x.IsCoordinator == True, self.DSProcesses))
        if len(processes) != 0:
            result = processes[0]

        return result

    def AddHistory(self, value):
        self.DataValueHistory.append(value)


dsData = DSData()
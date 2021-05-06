import threading

class DSData():

    def __init__(self):
        self.DSProcesses = []

    def AddProcess(self, ListOfDSProcesses):
        for process in ListOfDSProcesses:
            self.DSProcesses.append(process)

    def GetProcessByID(self, processId):
        result = None
        processes = list(filter(lambda x: x.Id == processId, self.DSProcesses))
        if len(processes) != 0:
            result = processes[0]

        return result

    def RemoveProcess(self, processId):
        processes = []
        for p in self.DSProcesses:
            if p.Id != processId:
                processes.append(p)

        self.DSProcesses = processes
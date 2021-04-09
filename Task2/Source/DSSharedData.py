import threading

class DSSharedData():

    def __init__(self):
        self.BullyProcesses = []
        self.Lock = threading.Lock()

    def Initialize(self, ListOfBullyProcesses):
        self.BullyProcesses = ListOfBullyProcesses

    def GetProcessByID(self, processId):
        result = None
        processes = [p for p in self.BullyProcesses if p.Id == processId]
        if len(processes) != 0:
            result = processes[0]

        return result

    def RemoveProcess(self, processId):
        processes = []
        for p in self.BullyProcesses:
            if p.Id != processId:
                processes.append(p)

        self.BullyProcesses = processes


sharedData = DSSharedData()
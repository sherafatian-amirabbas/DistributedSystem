import threading

class DSSharedData():

    def __init__(self):
        self.BullyProcesses = []
        self.Lock = threading.Lock()

    def AddProcess(self, ListOfBullyProcesses):
        for process in ListOfBullyProcesses:
            self.BullyProcesses.append(process)

    def GetProcessByID(self, processId):
        result = None
        processes = list(filter(lambda x: x.Id == processId, self.BullyProcesses))
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
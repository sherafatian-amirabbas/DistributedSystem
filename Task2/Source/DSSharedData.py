
class DSSharedData():

    def __init__(self):
        self.BullyProcesses = []
        self.ReloadProcesses=[]
        

    def Initialize(self, ListOfBullyProcesses):
        self.BullyProcesses = ListOfBullyProcesses
    def ReloadProcess(self,listofprocesses):
        self.ReloadProcesses=listofprocesses
        

    def GetProcessByID(self, processId):
        result = None
        processes = [p for p in self.BullyProcesses if p.Id == processId]
        if len(processes) != 0:
            result = processes[0]

        return result

sharedData = DSSharedData()
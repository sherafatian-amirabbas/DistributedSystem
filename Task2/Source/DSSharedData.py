
class DSSharedData():

    def __init__(self):
        self.BullyProcesses = []

    def Initialize(self, ListOfBullyProcesses):
        self.BullyProcesses = ListOfBullyProcesses

sharedData = DSSharedData()
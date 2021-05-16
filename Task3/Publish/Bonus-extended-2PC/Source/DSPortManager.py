
class DSPortManager():

    def __init__(self, startingPort, portInterval):
        self.startingPort = startingPort
        self.portInterval = portInterval
        self.usedPorts = []


    def GetANewPort(self):
        port = self.startingPort

        usedPortsLength = len(self.usedPorts)
        if usedPortsLength > 0:
            self.usedPorts.sort()
            lastPort = self.usedPorts[usedPortsLength - 1]
            if port <= lastPort:
                port = lastPort + self.portInterval

        self.usedPorts.append(port)
        return port

portManager = DSPortManager(65000, 1)
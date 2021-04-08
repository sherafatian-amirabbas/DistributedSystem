
class DSPortManager():

    def __init__(self, startingPort, portInterval):
        self.__startingPort = startingPort;
        self.__portInterval = portInterval;
        self.__usedPorts = []


    def GetANewPort(self):
        port = self.__startingPort

        usedPortsLength = len(self.__usedPorts)
        if usedPortsLength > 0:
            self.__usedPorts.sort()
            lastPort = self.__usedPorts[usedPortsLength - 1]
            if port <= lastPort:
                port = lastPort + self.__portInterval

        self.__usedPorts.append(port)
        return port

portManager = DSPortManager(65000, 1)
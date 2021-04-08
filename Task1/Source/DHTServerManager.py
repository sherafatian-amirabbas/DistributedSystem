from DHTSocket import DHTSocket, DHTSocketArg, DHTSocketAddress
from DHTServer import DHTServer
import socket

class DHTServerManager():
    def __init__(self, startingPort, portInterval):
        self.__startingPort = startingPort;
        self.__portInterval = portInterval;
        self.__serversDic = None
        self.__tempUsedPorts = []


    def GetTheServerWithTheLowestDataValue(self):
        values = []
        for key in self.__serversDic:
            server = self.__serversDic[key]
            values.append(server.DHTNodeDataValue.Value)

        values.sort()
        return self.GetServerByDataValue(values[0])


    def IsServerAvailable(self, key):
        result = False
        if key in self.__serversDic:
            result = True
        return result
        

    def GetServerByDataValue(self, dataValue):
        result = None
        for key in self.__serversDic:
            if int(key.split(":")[2]) == dataValue:
                result = self.__serversDic[key]
        return result


    def addServer(self, dhtServer):
        key = DHTServer.GetKey(dhtServer.Host, dhtServer.Port, dhtServer.DHTNodeDataValue.Value)
        dic = {key: dhtServer}
        if self.__serversDic == None:
            self.__serversDic = dic
        else:
            self.__serversDic.update(dic)


    def AssignHostAndPort(self, dhtServer):
        host, port = self.GetANewHostAndPort()
        self.__tempUsedPorts.append(port)

        dhtServer.Host = host
        dhtServer.Port = port


    def StartServer(self, dhtServer):
        dhtSocketArg = DHTSocketArg(dhtServer.Host, dhtServer.Port, dhtServer.OnRequest)
        dhtSocket, worker = DHTSocket.InitAsync(dhtSocketArg)
        dhtServer.Initialize(dhtSocket, worker)

        self.addServer(dhtServer)
        return dhtServer
        

    def PingTheHostAndPort(self, host, port, dhtMessage):
        return DHTSocket.OpenASocketAndSendTheRequest(host, port, dhtMessage)


    def SendRequestTo(self, dhtServer, dhtMessage):
        key = DHTServer.GetKey(dhtServer.Host, dhtServer.Port, dhtServer.DHTNodeDataValue.Value)
        if self.IsServerAvailable(key):
            dhtMessage.OriginDHTSocketAddress = DHTSocketAddress(dhtServer.Host, dhtServer.Port)
            return DHTSocket.OpenASocketAndSendTheRequest(dhtServer.Host, dhtServer.Port, dhtMessage)
        else:
            return "server is not alive!!"


    def GetANewHostAndPort(self):
        port = self.__startingPort

        usedPorts = []
        if self.__serversDic != None:
            for key in self.__serversDic:
                usedPorts.append(self.__serversDic[key].Port)
                
        length = len(usedPorts);
        if length > 0:
            usedPorts.sort()
            port = usedPorts[length - 1] + self.__portInterval

        tempUsedPortsLength = len(self.__tempUsedPorts)
        if tempUsedPortsLength > 0:
            self.__tempUsedPorts.sort()
            lastTempPort = self.__tempUsedPorts[tempUsedPortsLength - 1]
            if port <= lastTempPort:
                port = lastTempPort + self.__portInterval

        return ("127.0.0.1", port)


    def ShutdownDHTServerByKey(self, dataValue):
        result = False

        dhtServer = self.GetServerByDataValue(dataValue)
        # TODO: check if its available, and then shuting down
        # TODO: result = ????

        return result



dhtServerManager = DHTServerManager(62770, 1)
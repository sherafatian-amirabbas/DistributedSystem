from DHTMessage import DHTMessage, DHTMessageType
from DHTSocket import DHTSocketAddress, DHTSocket
import time


class DHTServer():
    def __init__(self, host = None, port = None, onRequestHandler = None):
        self.Host = host
        self.Port = port
        self.OnRequestHandler = onRequestHandler

        self.DHTNodeDataValue = None            # will keep the node data (DHTNodeDataValue class)
        
        # list of Data the node knows about (List of DHTNodeDataValue classes)
        self.DHTNodeDataValueList = None 
        self.PrevDHTServerSocketAddress = None      # A reference to previous DHTSocketAddress class
        self.SuccessorDHTServerSocketAddress = None      # the Successor as a DHTSocketAddress class
        self.NextSuccessorDHTServerSocketAddress = None  # the next successor as a DHTSocketAddress class
        
        # list of shortcuts (List of None Classes)
        self.FingerDHTServerSocketAddresses = []   

        self.__dhtSocket = None
        self.__worker = None

        self.__interval = 1000
        self.__timeout = 2000


    def IsDataValueIncluded(self, dataValue):
        result = False
        for value in self.DHTNodeDataValueList:
            if(value == dataValue):
                result = True
                break
        return result


    def Initialize(self, dhtSocket, worker):
        self.__dhtSocket = dhtSocket;
        self.__worker = worker;
    

    def GetDHTSocketAddress(self):
        return DHTSocketAddress(self.Host, self.Port)


    def Upload(self, dhtNodeDataValue, dhtNodeDataValueList, prevDHTServerSocketAddress, successorDHTServerSocketAddress, nextSuccessorDHTServerSocketAddress, fingerDHTServerSocketAddresses):
        self.DHTNodeDataValue = dhtNodeDataValue                
        self.DHTNodeDataValueList = dhtNodeDataValueList    
        self.PrevDHTServerSocketAddress = prevDHTServerSocketAddress
        self.SuccessorDHTServerSocketAddress = successorDHTServerSocketAddress
        self.NextSuccessorDHTServerSocketAddress = nextSuccessorDHTServerSocketAddress
        self.FingerDHTServerSocketAddresses = fingerDHTServerSocketAddresses


    def OnRequest(self, dataBytes):
        dataStr = dataBytes.decode("utf-8")
        msg = DHTMessage.deserialize(dataStr)

        if self.OnRequestHandler != None:
            self.OnRequestHandler(msg)

        return str(self.handleMessage(msg))


    # ----------------------------------------------------------------------------------- private methods

    def updateReferences(self, param):
        # TODO: references to Successor/NextSuccessor/PrevDHTServerSocketAddress/finger
        pass


    def checkSuccessorInInterval(self):

        # TODO: Open the socket to ping and wait for the response
        # TODO: if it's not getting back in timeout duration, "updateReferences" (with param) is called
        
        #try:
            # TODO: DHTSocket.OpenASocketAndSendTheRequestWithTimeout(self.__timeout)
        #except timeoutexception:
            # self.updateReferences()

        pass

    def onTimeStart(self):
        checkSuccessorInInterval()
        pass

    def setTheTimer(self, onTimeStart):

        # TODO: defining the timer and using "interval"

        #new Timer(self.__interval)
        #{
        #    OnStart += () => {

        #        onTimeStart()
        #    }
        #}

        pass

    def getInfoDataAsString(self):
         return self.DHTNodeDataValue.ToString()


    def getValueFromTheCurrentRequest(self, socketAddresses_tuple, socketAddress):
        val = ''
        for address_tuple in socketAddresses_tuple:
            if address_tuple[0].IsEqualTo(socketAddress):
                val += str(address_tuple[1])
                break
        return val


    def GetShortcutsDataValueAsString(self, socketAddresses_tuple):
        shortcuts = ''
        if self.FingerDHTServerSocketAddresses:
            for fingerSocketAddress in self.FingerDHTServerSocketAddresses:

                res = ''
                res += self.getValueFromTheCurrentRequest(socketAddresses_tuple, fingerSocketAddress)
                if res == None or res == '':
                    shortcuts += DHTSocket.OpenASocketAndSendTheRequest(fingerSocketAddress.Host, fingerSocketAddress.Port, DHTMessage(DHTMessageType.DataAsString)) + ','
                else:
                    shortcuts += res + ','
        
        if shortcuts == '':
            shortcuts += ','

        return shortcuts



    def GetSuccessorDataValueAsString(self, socketAddresses_tuple):
        successorDataAsString = ""
        successorDataAsString += self.getValueFromTheCurrentRequest(socketAddresses_tuple, self.SuccessorDHTServerSocketAddress)

        if successorDataAsString == "":
            successorDataAsString = DHTSocket.OpenASocketAndSendTheRequest(self.SuccessorDHTServerSocketAddress.Host, self.SuccessorDHTServerSocketAddress.Port, DHTMessage(DHTMessageType.DataAsString))

        return successorDataAsString



    def GetNextSuccessorDataValueAsString(self, socketAddresses_tuple):
        nextSuccessorDataAsString = ""
        nextSuccessorDataAsString += self.getValueFromTheCurrentRequest(socketAddresses_tuple, self.NextSuccessorDHTServerSocketAddress)

        if nextSuccessorDataAsString == "":
            nextSuccessorDataAsString = DHTSocket.OpenASocketAndSendTheRequest(self.NextSuccessorDHTServerSocketAddress.Host, self.NextSuccessorDHTServerSocketAddress.Port, DHTMessage(DHTMessageType.DataAsString))

        return nextSuccessorDataAsString


    def DataValueAsStringCommandHandler(self, dhtMessage):
        return self.getInfoDataAsString()


    # ---------------------------------------------------------------------------------------- Commands
    

    def handleMessage(self, dhtMessage):
        result = None
        if dhtMessage.Type == DHTMessageType.Ping:
            result = self.Ping(dhtMessage)
        if dhtMessage.Type == DHTMessageType.Lookup:
            result = self.Lookup(dhtMessage)
        if dhtMessage.Type == DHTMessageType.Join:
            result = self.Join(dhtMessage)
        if dhtMessage.Type == DHTMessageType.List:
            result = self.ListCommandHandler(dhtMessage)
        if dhtMessage.Type == DHTMessageType.DataAsString:
            result = self.DataValueAsStringCommandHandler(dhtMessage)
        if dhtMessage.Type == DHTMessageType.Shortcut:
            result = self.Shortcut(dhtMessage)

        return result


    def Ping(self, dhtMessage):
        return "hey.. I'm alive.."

    def Lookup(self, dhtMessage):
        pass

    def Join(self, dhtMessage):
        
        addressofJoinedNode = DHTSocketAddress(dhtMessage.Argument, int(dhtMessage.Tag))    
        datavalueofJoinedNode=int(dhtMessage.Nodevalue)
         
         
        serverDataAsString = self.getInfoDataAsString() #server node value as string
        serverAddress = self.GetDHTSocketAddress()      # host and port number
         
        if dhtMessage.OriginDHTSocketAddress.IsEqualTo(serverAddress):
            dhtMessage.OriginArgument = serverDataAsString
            dhtMessage.Tag = serverAddress.Host + "|" + str(serverAddress.Port) + "|" + serverDataAsString + "_"
        else:
            dhtMessage.Tag += serverAddress.Host + "|" + str(serverAddress.Port) + "|" + serverDataAsString + "_"
            
         
         
    def Shortcut(self, dhtMessage):
        result = ""
        address = DHTSocketAddress(dhtMessage.Argument, int(dhtMessage.Tag))
        isExisted = False
        for add in self.FingerDHTServerSocketAddresses:
            if add.IsEqualTo(address):
                isExisted = True
                break

        if isExisted:
            return "the node has already listed as shortcut, try another one..."
        else:
            self.FingerDHTServerSocketAddresses.append(address)  
            return "shortcut is established now"
            

        
    def ListCommandHandler(self, dhtMessage):
        serverDataAsString = self.getInfoDataAsString()

        serverAddress = self.GetDHTSocketAddress()
        if dhtMessage.OriginDHTSocketAddress.IsEqualTo(serverAddress):
            dhtMessage.OriginArgument = serverDataAsString
            dhtMessage.Tag = serverAddress.Host + "|" + str(serverAddress.Port) + "|" + serverDataAsString
        else:
            dhtMessage.Tag += "_" + serverAddress.Host + "|" + str(serverAddress.Port) + "|" + serverDataAsString

        
        socketAddresses_tuple = []
        traversedServers = dhtMessage.Tag.split("_")
        for ts in traversedServers:
            inf = ts.split("|")
            socketAddresses_tuple.append((DHTSocketAddress(inf[0], int(inf[1])), int(inf[2])))


        shortcuts = self.GetShortcutsDataValueAsString(socketAddresses_tuple)
        successorDataAsString = self.GetSuccessorDataValueAsString(socketAddresses_tuple)
        nextSuccessorDataAsString = self.GetNextSuccessorDataValueAsString(socketAddresses_tuple)
        
        dataAsStr = '%s:%s S-%s, NS-%s' % (serverDataAsString, shortcuts, successorDataAsString, nextSuccessorDataAsString) + "\n"

        isTheLastOne = dhtMessage.OriginDHTSocketAddress.IsEqualTo(self.SuccessorDHTServerSocketAddress)
        if isTheLastOne == False:
            dataAsStr += DHTSocket.OpenASocketAndSendTheRequest(self.SuccessorDHTServerSocketAddress.Host, self.SuccessorDHTServerSocketAddress.Port, dhtMessage)

        return dataAsStr


    # ---------------------------------------------------------------------------------------- Commands


    def GetKey(host, port, dataValue):
        return host + ":" + str(port) + ":" + str(dataValue)


DHTServer.GetKey = staticmethod(DHTServer.GetKey)
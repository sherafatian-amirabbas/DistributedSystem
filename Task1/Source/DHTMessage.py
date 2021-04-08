import enum
from DHTSocket import DHTSocketAddress

class DHTMessageType(enum.Enum):
   Ping = 1
   Lookup = 2
   Join = 3
   Shortcut= 4
   List = 5
   DataAsString = 6

class DHTMessage:
    def __init__(self, messageType):
        self.Type = messageType
        self.Argument = None
        self.OriginArgument = None
        self.OriginDHTSocketAddress = None
        self.PrevServerDHTSocketAddress = None
        self.NextServerDHTSocketAddress = None
        self.Tag = None
        self.Nodevalue=None

    def serialize(self):
        type = self.Type.value
        arg = "-1" if self.Argument == None else self.Argument
        
        originHost = "-1" if self.OriginDHTSocketAddress == None else self.OriginDHTSocketAddress.Host
        originPort = -1 if self.OriginDHTSocketAddress == None else self.OriginDHTSocketAddress.Port
        
        nextServerHost = "-1" if self.NextServerDHTSocketAddress == None else self.NextServerDHTSocketAddress.Host
        nextServerPort = -1 if self.NextServerDHTSocketAddress == None else self.NextServerDHTSocketAddress.Port

        tag = "-1" if self.Tag == None else self.Tag

        prevServerHost = "-1" if self.PrevServerDHTSocketAddress == None else self.PrevServerDHTSocketAddress.Host
        prevServerPort = -1 if self.PrevServerDHTSocketAddress == None else self.PrevServerDHTSocketAddress.Port

        originArg = "-1" if self.OriginArgument == None else self.OriginArgument

        return (
            "Type***" + str(type) + 
            "***Argument***" + str(arg) + 
            "***OriginHost***" + originHost  + 
            "***OriginPort***" + str(originPort) +
            "***NextServerHost***" + nextServerHost + 
            "***NextServerPort***" + str(nextServerPort) +
            "***Tag***" + tag +
            "***PrevServerHost***" + prevServerHost + 
            "***PrevServerPort***" + str(prevServerPort) +
            "***OriginArgument***" + str(originArg)
        )

    def deserialize(str):
        props = str.split("***")

        type = DHTMessageType(int(float(props[1])))
        arg = None if props[3] == "-1" else props[3]
        
        originHost = None if props[5] == "-1" else props[5]
        op = int(float(props[7]))
        originPort = None if op == -1 else op

        nextServerHost = None if props[9] == "-1" else props[9]
        np = int(float(props[11]))
        nextServerPort = None if np == -1 else np

        tag = None if props[13] == "-1" else props[13]

        prevServerHost = None if props[15] == "-1" else props[15]
        pp = int(float(props[17]))
        prevServerPort = None if pp == -1 else pp

        originArg = None if props[19] == "-1" else props[19]


        msg = DHTMessage(type)
        msg.Argument = arg
        msg.OriginArgument = originArg
        msg.OriginDHTSocketAddress = None if originHost == None else DHTSocketAddress(originHost, originPort)
        msg.PrevServerDHTSocketAddress = None if prevServerHost == None else DHTSocketAddress(prevServerHost, prevServerPort)
        msg.NextServerDHTSocketAddress = None if nextServerHost == None else DHTSocketAddress(nextServerHost, nextServerPort)
        msg.Tag = tag

        return msg

DHTMessage.deserialize = staticmethod(DHTMessage.deserialize)
    



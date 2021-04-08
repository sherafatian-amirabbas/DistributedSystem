import click
from click_shell import shell
import time

from DHTNodeDataValue import DHTNodeDataValue
from DHTServer import DHTServer
from DHTServerManager import dhtServerManager
from DHTMessage import DHTMessage, DHTMessageType
from DHTSocket import DHTSocketAddress


KeySpaceRange = None


# ------------------------------------------------------------------------------- private functions

def getDHTNodeDataValueListFromRange(range):
    datalist = []
    for i in range:
        datalist.append(DHTNodeDataValue(i))
    return datalist


def initialize(file):
    ## Key space
    key_space = "#key-space"
    key_space_range = None

    ## Nodes
    nodes = "#nodes"
    node_array_str = None

    ## Shortcuts
    shortcuts = "#shortcuts"
    shortcuts_array = []

    file_name = file
    file_object = open(file_name , "r")
    file_list = file_object.read().splitlines()
    

    my_list = list(filter(lambda x: x is not None and x != " " and x != "", file_list))
    for index, line in enumerate(my_list):
        if(line.lower() == key_space):
            key = my_list[index + 1]
            key_array = key.split(',')
            if len(key_array) > 0:
                key_space_range = range(int(key_array[0]), int(key_array[1]) + 1)

        if(line.lower() == nodes):
            key = my_list[index + 1]
            node_array_str = key.split(',')

        if(line.lower() == shortcuts):
            key = my_list[index + 1]
            if key.startswith("#") == False:
                shortcuts_array = key.split(',')

    node_array = []
    for i in node_array_str:
        if i != " " and i != "":
            value = int(i)
            if value <= key_space_range[-1]:
                node_array.append(value)

    node_array.sort()
    file_dictionary = dict()
    for i, value in enumerate(node_array):
        dht_server = DHTServer()
        dhtServerManager.AssignHostAndPort(dht_server)
        socket_address = dht_server.GetDHTSocketAddress()
        file_dictionary[value] = (dht_server, socket_address)
        servers = [dht_server]


    lastIndex = len(node_array) - 1
    
    for i, value in enumerate(node_array):

        prevIndex = (i - 1) if i != 0 else lastIndex
        nextIndex = 0 if i == lastIndex else i + 1

        if i == lastIndex - 1:
            nextNextIndex = 0
        elif i == lastIndex:
            nextNextIndex = 1
        else:
            nextNextIndex = i + 2

        if lastIndex == 0:
            nextNextIndex = 0

        prevServerAddress = file_dictionary[node_array[prevIndex]][1]
        successorServerAddress = file_dictionary[node_array[nextIndex]][1]
        nextSuccessorServerAddress = file_dictionary[node_array[nextNextIndex]][1]


        shortcutsArray = []
        for shortcut in shortcuts_array:
            shortcutInfo = shortcut.split(':')
            if int(shortcutInfo[0]) == node_array[i]:
                if int(shortcutInfo[1]) in file_dictionary:
                    shortcutsArray.append(file_dictionary[int(shortcutInfo[1])][1])

        dataList = None
        if i == 0:
            dataList = getDHTNodeDataValueListFromRange(range(node_array[lastIndex] + 1, key_space_range[-1] + 1))
            dataList.extend(getDHTNodeDataValueListFromRange(range(key_space_range[0], node_array[i] + 1)))
        else:
            firstData = node_array[i - 1] + 1
            lastData = node_array[i]
            dataList = getDHTNodeDataValueListFromRange(range(firstData, lastData + 1))


        server = file_dictionary[node_array[i]][0]
        server.Upload(DHTNodeDataValue(node_array[i]), dataList, prevServerAddress, successorServerAddress, nextSuccessorServerAddress, shortcutsArray)
        

    servers = []
    for key in file_dictionary:
        servers.append(file_dictionary[key][0])
    
    return (servers, key_space_range)
    

def runDHTServers(dhtServers):
    servers = []
    for dhtServer in dhtServers:
        dhtServer = dhtServerManager.StartServer(dhtServer)
        servers.append(dhtServer)
        
    return servers


def AddShortcutToNode(nodeValue, shortcutNodeValue):

        if (not nodeValue) or nodeValue == '':
            return "the node to add the shortcut to, is not valid"

        if (not shortcutNodeValue) or shortcutNodeValue == '':
            return "the shortcut node to add the shortcut to, is not valid"

        try:
            nodeValue = int(nodeValue)
        except:
            return "the node data value for the node to add the shortcut to, is not valid"

        try:
            shortcutNodeValue = int(shortcutNodeValue)
        except:
            return "the shortcut node data value, is not valid"



        server = dhtServerManager.GetServerByDataValue(nodeValue)
        
        if server==None:
            return "the node to add the shortcut to, was not found"

        shortcutserver = dhtServerManager.GetServerByDataValue(shortcutNodeValue)
        if shortcutserver == None:
            return "the node is supposed to be added as a shortcut, was not found"
        
        msg=DHTMessage(DHTMessageType.Shortcut)
        msg.Argument=shortcutserver.Host
        msg.Tag=str(shortcutserver.Port)
        return dhtServerManager.SendRequestTo(server,msg)
    
    
    
def joinTheData(param):
    if param =='':
        return "the node is not valid"
    
    try:
        param=int(param)
    except:
        return "the join node data value, is not valid"
    
    server = dhtServerManager.GetServerByDataValue(param)
     
    if server ==None:
        
        dhtServer4= DHTServer()
        dhtServer4.DHTNodeDataValue=DHTNodeDataValue(param)
        dhtServerManager.AssignHostAndPort(dhtServer4)
        socketAddress4 = dhtServer4.GetDHTSocketAddress()
        
        serverLovestValue= dhtServerManager.GetTheServerWithTheLowestDataValue()
        
        msg=DHTMessage(DHTMessageType.Join)
        msg.Argument=dhtServer4.Host
        msg.Tag=str(dhtServer4.Port)
        msg.Nodevalue=str(param)
        
        return dhtServerManager.SendRequestTo(serverLovestValue,msg)
        
    else:
        return 'chord table already has this node'
#def initialize(file):
        
#    dhtServer5 = DHTServer()
#    dhtServerManager.AssignHostAndPort(dhtServer5)
#    socketAddress5 = dhtServer5.GetDHTSocketAddress()

#    dhtServer17 = DHTServer()
#    dhtServerManager.AssignHostAndPort(dhtServer17)
#    socketAddress17 = dhtServer17.GetDHTSocketAddress()

#    datalist5 = getDHTNodeDataValueListFromRange(range(93, 101))
#    datalist5.extend(getDHTNodeDataValueListFromRange(range(1, 6)))
#    dhtServer5.Upload(DHTNodeDataValue(5), datalist5, socketAddress17, socketAddress17, socketAddress5, [])

#    dhtServer17.Upload(DHTNodeDataValue(17), getDHTNodeDataValueListFromRange(range(6, 18)), socketAddress5, socketAddress5, socketAddress17, [])

#    servers = [dhtServer5, dhtServer17]
#    keySpace = range(1, 101)

#    return (servers, keySpace)


def validateLeaveParam(param):
    result = False

    # TODO result = ????

    return result

# ------------------------------------------------------------------------------- private functions



@shell(prompt='dht > ')
def main():
    pass


@main.command()
@click.argument('file')
def init(file):
    
    (servers, keySpace) = initialize(file)
    KeySpaceRange = keySpace
    dhtServers = runDHTServers(servers)

    click.echo("Initialized Done... Server(s) created and you can ping them. Server(s) is/are as follow:")
    for dhtServer in dhtServers:
         click.echo("Host: " + dhtServer.Host + " , Port: " + str(dhtServer.Port))


@main.command()
@click.argument('host')
@click.argument('port')
def ping(host, port):
    result = dhtServerManager.PingTheHostAndPort(host, int(port), DHTMessage(DHTMessageType.Ping))
    click.echo(result)


@main.command()
@click.argument('param')

def join(param):
    result = ""
    param=param
   
    result= joinTheData(param)
        
    click.echo(result)

@main.command()
@click.argument('param')
def lookup(param):
    #msg = DHTMessage(DHTMessageType.Ping)
    #msg.DataValue = 7
    result = ""
    click.echo(result)

@main.command()
@click.argument('shortcut')

def shortcut(shortcut):
    result = ""
    nodes = shortcut.split(':')
    if len(nodes) != 2:
        result="the input format is not satisfied, e.g. <Node_Value>:<ShortcutNode_Value>"
    else:
        result= AddShortcutToNode(nodes[0], nodes[1])
        
    click.echo(result)
    List()



@main.command()
def List():
    server = dhtServerManager.GetTheServerWithTheLowestDataValue()
    if server == None:
        click.echo("the Ring is not initialized!!")
        return

    result = dhtServerManager.SendRequestTo(server, DHTMessage(DHTMessageType.List))
    click.echo(result)




@main.command()
@click.argument('param')
def leave(param):

    #if validateLeaveParam(param):
    #    dataValue = int(param)
    #    dhtServer = dhtServerManager.ShutdownDHTServerByKey(dataValue)

    #result = ""
    #click.echo(result)
    pass


if __name__ == '__main__':
    main()

import multiprocessing as mp
import socket
import time


class DHTSocketAddress:
    def __init__(self, host, port):
        self.Host = host
        self.Port = port

    def IsEqualTo(self, SocketAddress):
        return self.Host == SocketAddress.Host and self.Port == SocketAddress.Port


class DHTSocketArg:
    def __init__(self, host, port, onReceiveDataHandler):
        self.Host = host
        self.Port = port
        self.OnReceiveDataHandler = onReceiveDataHandler


class DHTSocket:
    def __init__(self, dhtSocketArg):
        self.__host = dhtSocketArg.Host
        self.__port = dhtSocketArg.Port
        self.__onReceiveDataHandler = dhtSocketArg.OnReceiveDataHandler
        self.__socket = None

        
    def initialize(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as mySocket:
            self.__socket = mySocket
            mySocket.bind((self.__host, self.__port))
            mySocket.listen()
            self.accept()


    def accept(self):
        conn, addr = self.__socket.accept()
        with conn:
            while True:
                data = conn.recv(1024)
                if not data:
                    self.accept()
                result = self.__onReceiveDataHandler(data)
                if result:
                    conn.sendall(bytes(result, 'utf-8'))


    def InitAsync(dhtSocketArg):
        dhtSocket = DHTSocket(dhtSocketArg)

        worker = mp.Process(target=_init, args=(dhtSocket,))
        worker.daemon = True
        worker.start()
        return (dhtSocket, worker)

    def OpenASocketAndSendTheRequestWithTimeout(host, port, dhtMessage, timeout):

        # TODO: apply timeout

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sckt:
            sckt.connect((host, port))
            msg = dhtMessage.serialize()
            sckt.sendall(bytes(msg, 'utf-8'))
            result = sckt.recv(1024)
            resultStr = result.decode("utf-8")
            return resultStr

    def OpenASocketAndSendTheRequest(host, port, dhtMessage):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sckt:
            sckt.connect((host, port))
            msg = dhtMessage.serialize()
            sckt.sendall(bytes(msg, 'utf-8'))
            result = sckt.recv(1024)
            resultStr = result.decode("utf-8")
            return resultStr


DHTSocket.InitAsync = staticmethod(DHTSocket.InitAsync)
DHTSocket.OpenASocketAndSendTheRequest = staticmethod(DHTSocket.OpenASocketAndSendTheRequest)
DHTSocket.OpenASocketAndSendTheRequestWithTimeout = staticmethod(DHTSocket.OpenASocketAndSendTheRequestWithTimeout)


def _init(dhtSocket):
    dhtSocket.initialize()
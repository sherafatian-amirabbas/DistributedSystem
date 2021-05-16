
import enum

from DSProcessManager import dsProcessManager
from DSMessage import DSMessage, DSMessageType


class DSCoordinatorTransactionStatus(enum.Enum):
    INIT = 1
    WAIT = 10
    ABORT = 20
    COMMIT = 30


GlobalTransactionID = 0
class DSCoordinatorTransaction:
    def __init__(self, onCommitHandler, onAbortHandler):
        self.Id = self.getNewID() # by defining Id, we can later follow up each transaction
        self.onCommitHandler = onCommitHandler
        self.onAbortHandler = onAbortHandler
        self.State = None
        self.Operation = None # by encapsulating the operation, we can log the whole transaction object as a state together with the operation
        self.ProcessesVoteRequestIsSentTo = []
        self.NumberOfProcessesWithVoteCommit = 0


    def Open(self):
        self.State = DSCoordinatorTransactionStatus.INIT
        return self.notifyProcessesAboutANewOperation()


    def Operate(self, dsMessage):
        self.State = DSCoordinatorTransactionStatus.WAIT
        self.Operation = dsMessage
        (err, pid) = self.sendVoteRequest()
        if err == 'timeout':
            self.Abort() # in the case of timeout, we send global abort
            return (err, pid)
        else:
            return ('', 0)


    def HandleAcknowledge(self, IsVoteCommit):
        if IsVoteCommit == True:
            self.NumberOfProcessesWithVoteCommit += 1
            if self.NumberOfProcessesWithVoteCommit == len(self.ProcessesVoteRequestIsSentTo):
                self.Commit()
        else:
            self.Abort()


    def Commit(self):
        self.State = DSCoordinatorTransactionStatus.COMMIT
        self.sendGlobalCommit()
        self.onCommitHandler(self.Operation)


    def Abort(self):
        self.State = DSCoordinatorTransactionStatus.ABORT
        self.sendGlobalAbort()
        self.onAbortHandler()

    # ------------------------------ private methods

    def getNewID(self):
        global GlobalTransactionID 
        GlobalTransactionID = GlobalTransactionID + 1
        return GlobalTransactionID


    def notifyProcessesAboutANewOperation(self):
        processes = dsProcessManager.GetParticipants()
        val = ('', '')
        for p in processes:
            res = p.DSSocket.SendMessage(DSMessage(DSMessageType.InitRequest, self.Id)) # by passing the Id of the transactin we can follow up the transaction if needed
            if res == 'timeout':
                val = ('timeout', p.Id)
                break
        return val


    def sendVoteRequest(self):
        processes = dsProcessManager.GetParticipants()
        self.ProcessesVoteRequestIsSentTo = processes
        val = ('', '')
        for p in processes:
            res = p.DSSocket.SendMessage(DSMessage(DSMessageType.VoteRequest, self.Operation, self.Id))
            if res == 'timeout':
                val = ('timeout', p.Id)
                break
        return val


    def sendGlobalCommit(self):
        processes = dsProcessManager.GetParticipants()
        for p in processes:
            p.DSSocket.SendMessage(DSMessage(DSMessageType.GlobalCommit, self.Id))


    def sendGlobalAbort(self):
        processes = dsProcessManager.GetParticipants()
        for p in processes:
            p.DSSocket.SendMessage(DSMessage(DSMessageType.GlobalAbort, self.Id))
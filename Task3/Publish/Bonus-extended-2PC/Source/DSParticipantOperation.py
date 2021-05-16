
import enum
from os import abort

from DSProcessManager import dsProcessManager
from DSMessage import DSMessage, DSMessageType
from DSTimeout import DSTimeout

class DSParticipantOperationStatus(enum.Enum):
    INIT = 1
    READY = 10
    ABORT = 20
    COMMIT = 30


GlobalParticipantOperationID = 0
class DSParticipantOperation:
    def __init__(self, dsProcess, coordinatorTransactionId, currentData, flipParticipantAcknowledge, onCommitHandler, onAbortHandler):
        self.Id = self.getNewID() # by defining Id, we can later follow up each operation
        self.DSProcess = dsProcess
        self.CoordinatorTransactionId = coordinatorTransactionId
        self.CurrentData = currentData
        self.State = None

        self.timeout = 5 # timeout to wait for coordinator
        self.dsTimeout = DSTimeout(self.timeout)

        self.onCommitHandler = onCommitHandler
        self.onAbortHandler = onAbortHandler
        self.Operation = None # by encapsulating the operation, we can log the whole object as a state together with the operation
        self.TempValue = None # to clone and keep everything temporarily until it's being committed
        self.flipParticipantAcknowledge = flipParticipantAcknowledge
        self.init()

    def SetFlipParticipantAcknowledge(self, value):
        self.flipParticipantAcknowledge = value

    def Operate(self, dsMessageAsOperation):
        self.Operation = dsMessageAsOperation
        self.handleOperationAndAcknowledgeTheCoordinator()
        
    def Commit(self):
        self.commitOperation()
        self.clearTemporarilyData()
        self.State = DSParticipantOperationStatus.COMMIT
        self.onCommitHandler()

    def Abort(self):
        self.clearTemporarilyData()
        self.State = DSParticipantOperationStatus.ABORT
        self.onAbortHandler()

    # ------------------------------ private methods

    def init(self):
        self.State = DSParticipantOperationStatus.INIT
        self.dsTimeout.Run(self.onInitTimeout)


    def onInitTimeout(self):
        # if we are still in INIT state we can safely change the state to abort. And we safe with this
        # approach because for each operation we are creating an instance of this object
        if self.State == DSParticipantOperationStatus.INIT:
            self.Abort()


    def getNewID(self):
        global GlobalParticipantOperationID
        GlobalParticipantOperationID = GlobalParticipantOperationID + 1
        return GlobalParticipantOperationID


    def handleOperationAndAcknowledgeTheCoordinator(self):
        messageType = None
        
        if self.Operation.Type == DSMessageType.SetNewValue:
            self.temporarilySetNewValueHandler()
            messageType = DSMessageType.VoteCommit

        elif self.Operation.Type == DSMessageType.RollbackValues:
            self.temporarilyRollbackValuesHandler()
            messageType = DSMessageType.VoteCommit


        if self.flipParticipantAcknowledge == True:
            if messageType == DSMessageType.VoteCommit:
                messageType = DSMessageType.VoteAbort
            else:
                messageType = DSMessageType.VoteCommit


        if messageType == DSMessageType.VoteCommit:
            self.State = DSParticipantOperationStatus.READY
        else:
            self.Abort()
            

        coordinatorProcess = dsProcessManager.GetCoordinator()
        coordinatorProcess.DSSocket.SendMessage(DSMessage(messageType, self.CoordinatorTransactionId))


        # if messageType == DSMessageType.VoteCommit:
        #     #if we are sending VoteCommit, means that the participant in the ready state
        #     # and should wait specific amount of time for the response from coordinatory
        #     self.dsTimeout.Run(self.onReadyTimeout)
        

    def onReadyTimeout(self):
        # in the case of timeout when the participant is in the ready state, we should contact
        # other participants to find their state. we are deciding as follow based on the other prticipant's state:
        # if other participant's State is INIT => this participant will be ABORT
        # if other participant's State is ABORT => this participant will be ABORT
        # if other participant's State is COMMIT => this participant will be COMMIT
        # if other participant's State is READY => we will reach another participant, if all others are in ready state, 
        # we need to wait for the coordinator to be recovered
        if self.State == DSParticipantOperationStatus.READY:
            processes = dsProcessManager.GetParticipants()
            for p in processes:
                if p.Id != self.DSProcess.Id:
                    state = p.DSSocket.SendMessage(DSMessage(DSMessageType.GetParticipantState, self.CoordinatorTransactionId))
                    if state == DSParticipantOperationStatus.INIT or state == DSParticipantOperationStatus.ABORT:
                        self.Abort()
                    elif state == DSParticipantOperationStatus.COMMIT:
                        self.Commit()


    def temporarilySetNewValueHandler(self):
        self.TempValue = self.Operation.Argument # value to be added is being kept temporarily


    def temporarilyRollbackValuesHandler(self):
        self.TempValue = self.Operation.Argument # position is being kept temporarily


    def commitOperation(self):
        if self.Operation.Type == DSMessageType.SetNewValue:
            self.CurrentData.append(self.TempValue)
        elif self.Operation.Type == DSMessageType.RollbackValues:
            for x in range(int(self.TempValue)):
                self.CurrentData.pop(len(self.CurrentData) - 1)

    
    def clearTemporarilyData(self):
        self.TempValue = None
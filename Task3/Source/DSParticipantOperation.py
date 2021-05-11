
import enum

from DSProcessManager import dsProcessManager
from DSMessage import DSMessage, DSMessageType


class DSParticipantOperationStatus(enum.Enum):
    INIT = 1
    READY = 10
    ABORT = 20
    COMMIT = 30


GlobalParticipantOperationID = 0
class DSParticipantOperation:
    def __init__(self, coordinatorTransactionId, currentData, flipParticipantAcknowledge, onCommitHandler, onAbortHandler):
        self.Id = self.getNewID() # by defining Id, we can later follow up each operation
        self.CoordinatorTransactionId = coordinatorTransactionId
        self.State = DSParticipantOperationStatus.INIT
        self.CurrentData = currentData
        self.onCommitHandler = onCommitHandler
        self.onAbortHandler = onAbortHandler
        self.Operation = None # by encapsulating the operation, we can log the whole object as a state together with the operation
        self.TempValue = None # to clone and keep everything temporarily until it's being committed
        self.flipParticipantAcknowledge = flipParticipantAcknowledge

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

    def getNewID(self):
        global GlobalParticipantOperationID
        GlobalParticipantOperationID = GlobalParticipantOperationID + 1
        return GlobalParticipantOperationID


    def handleOperationAndAcknowledgeTheCoordinator(self):
        messageType = None
        state = None
        
        if self.Operation.Type == DSMessageType.SetNewValue:
            self.temporarilySetNewValueHandler()
            messageType = DSMessageType.VoteCommit
            state = DSParticipantOperationStatus.READY

        elif self.Operation.Type == DSMessageType.RollbackValues:
            self.temporarilyRollbackValuesHandler()
            messageType = DSMessageType.VoteCommit
            state = DSParticipantOperationStatus.READY


        if self.flipParticipantAcknowledge == True:
            if messageType == DSMessageType.VoteCommit:
                messageType = DSMessageType.VoteAbort
            else:
                messageType = DSMessageType.VoteCommit


        if messageType == DSMessageType.VoteCommit:
            self.State = state
        else:
            self.Abort()
            

        coordinatorProcess = dsProcessManager.GetCoordinator()
        coordinatorProcess.DSSocket.SendMessage(DSMessage(messageType, self.CoordinatorTransactionId))
        

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
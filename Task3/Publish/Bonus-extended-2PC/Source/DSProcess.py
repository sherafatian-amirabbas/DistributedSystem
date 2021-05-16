import enum

from DSPortManager import portManager
from DSSocket import DSSocketAddress, DSSocket
from DSMessage import DSMessage, DSMessageType
from DSProcessManager import dsProcessManager
from DSCoordinatorTransaction import DSCoordinatorTransaction
from DSParticipantOperation import DSParticipantOperation
from DSTimer import DSTimer
from DSTimeout import DSTimeout


class DSProcessStatus(enum.Enum):
    Stopped = 0
    Running = 1


class DSProcess():
    def __init__(self, id, isCoordinator):
        self.Id = id
        self.IsCoordinator = isCoordinator
        self.Data = None
        self.DSStatus = DSProcessStatus.Stopped
        self.DSSocket = None
        self.CurrentCoordinatorTransaction = None
        self.CurrentParticipantOperation = None
        self.CoordinatorTransactionLog = []
        self.OperationTransactionLog = []
        self.flipParticipantAcknowledge = False
        self.timeFailure = False
        self.timeFailureTimeout = 0
        self.timer = DSTimer(1, self.timer_elapsed)

    def Initialize(self, data):
        self.Data = data

    def Run(self, startTimer = True):
        self.DSStatus = DSProcessStatus.Running

        port = portManager.GetANewPort()
        socketAddress = DSSocketAddress(port)
        self.DSSocket = DSSocket(socketAddress, self)
        self.DSSocket.Open()

        if startTimer:
            self.timer.Start()

    def Dispose(self):
        self.DSStatus = DSProcessStatus.Stopped
        self.DSSocket.Close()
        self.timer.Cancel()

    # ---------------------------------------------------------------------------------------- handlers

    def timer_elapsed(self):

        if self.timeFailure == True:
            self.timeFailureTimeout -= 1
            if self.timeFailureTimeout <= 0:
                self.timeFailure = False
                self.timeFailureTimeout = 0
                print('process ' + self.Id + ' is back from time failure')

        self.timer.Restart()

    # ---------------------------------------------------------------------------------------- Commands

    def PingCommandHandler(self, dsMessage):
        if self.DSStatus == DSProcessStatus.Stopped:
            return "I am stopped :( , my ID is: '" + str(self.Id) + "'"
        elif self.DSStatus == DSProcessStatus.Running:
            return "Hey... I'm running and my ID is: '" + str(self.Id) + "'"

    def GetDataCommandHandler(self, dsMessage):
        return  "[" + ", ".join(self.Data) + "]"

    def ArbitraryFailureCommandHandler(self, dsMessage):
        self.toggleFlipParticipantAcknowledge()

        timeout = dsMessage.Argument
        dsTimeout = DSTimeout(timeout)
        dsTimeout.Run(self.toggleFlipParticipantAcknowledge)

        return str(timeout) + ' seconds of arbitrary failure applied for the process ' + self.Id

    def TimeFailureCommandHandler(self, dsMessage):
        if dsMessage.Argument > 0:
            self.timeFailureTimeout = dsMessage.Argument
            self.timeFailure = True
            return 'timeFailure applied'

    # ------------- private methods

    def toggleFlipParticipantAcknowledge(self):
        self.flipParticipantAcknowledge = not self.flipParticipantAcknowledge
        if self.CurrentParticipantOperation != None:
            self.CurrentParticipantOperation.SetFlipParticipantAcknowledge(self.CurrentParticipantOperation)

        if self.flipParticipantAcknowledge == False:
            print('process ' + self.Id + ' is back from arbitrary failure')

    # ------------------------------------- coordinator-side command handlers

    def SetNewValueCommandHandler(self, dsMessage):
        return self.HandleOperation(dsMessage)

    def RollbackValuesCommandHandler(self, dsMessage):
        return self.HandleOperation(dsMessage)

    def VoteCommitCommandHandler(self, dsMessage):
        if self.CurrentCoordinatorTransaction != None and self.CurrentCoordinatorTransaction.Id == dsMessage.Argument:
            self.CurrentCoordinatorTransaction.HandleAcknowledge(True)

    def VoteAbortCommandHandler(self, dsMessage):
        if self.CurrentCoordinatorTransaction != None and self.CurrentCoordinatorTransaction.Id == dsMessage.Argument:
            self.CurrentCoordinatorTransaction.HandleAcknowledge(False)

    def PreCommitAcknowledgeCommandHandler(self, dsMessage):
        if self.CurrentCoordinatorTransaction != None and self.CurrentCoordinatorTransaction.Id == dsMessage.Argument:
            self.CurrentCoordinatorTransaction.HandlePreCommitAcknowledge()

    def SyncNewProcessCommandHandler(self, dsMessage):
        newProcess = dsMessage.Argument
        newProcess.Initialize(self.Data.copy())

    # ------------- private methods

    def HandleOperation(self, dsMessage):
        self.CurrentCoordinatorTransaction = DSCoordinatorTransaction(self.onTransactionCommitHandler, self.onTransactionAbortHandler)

        (err, pid) = self.CurrentCoordinatorTransaction.Open()
        if err == 'timeout':
            return 'the operation aborted since the process with the id \'' + pid + '\' is not responding'

        (err, pid) = self.CurrentCoordinatorTransaction.Operate(dsMessage)
        if err == 'timeout':
            return 'the operation aborted since the process with the id \'' + pid + '\' is not responding'

        return ", ".join(self.Data)

    def onTransactionCommitHandler(self, operation):
        self.applyChangesInCoordinatorData(operation)
        self.onEndTransaction()

    def onTransactionAbortHandler(self):
        self.onEndTransaction()

    def onEndTransaction(self):
        self.CoordinatorTransactionLog.append(self.CurrentCoordinatorTransaction)

    def applyChangesInCoordinatorData(self, operation):
        if operation.Type == DSMessageType.SetNewValue:
            self.Data.append(operation.Argument)
        elif operation.Type == DSMessageType.RollbackValues:
            for x in range(int(operation.Argument)):
                self.Data.pop(len(self.Data) - 1)

    # ------------------------------------- participant-side command handlers

    def InitRequestCommandHandler(self, dsMessage):
        self.CurrentParticipantOperation = DSParticipantOperation(self, dsMessage.Argument, self.Data, self.flipParticipantAcknowledge, self.onOperationCommitHandler, self.onOperationAbortHandler)

    def VoteRequestCommandHandler(self, dsMessage):
        if self.CurrentParticipantOperation != None and self.CurrentParticipantOperation.CoordinatorTransactionId == dsMessage.Tag:
            self.CurrentParticipantOperation.Operate(dsMessage.Argument) # dsMessage.Argument containing a dsMessage determining an operation

    def PreCommitCommandHandler(self, dsMessage):
        if self.CurrentParticipantOperation != None and self.CurrentParticipantOperation.CoordinatorTransactionId == dsMessage.Argument:
            self.CurrentParticipantOperation.PreCommit()
            
    def GlobalCommitCommandHandler(self, dsMessage):
        if self.CurrentParticipantOperation != None and self.CurrentParticipantOperation.CoordinatorTransactionId == dsMessage.Argument:
            self.CurrentParticipantOperation.Commit()

    def GlobalAbortCommandHandler(self, dsMessage):
        if self.CurrentParticipantOperation != None and self.CurrentParticipantOperation.CoordinatorTransactionId == dsMessage.Argument:
            self.CurrentParticipantOperation.Abort()

    def GetParticipantStateCommandHandler(self, dsMessage):
        operation = self.CurrentParticipantOperation
        if operation == None:
            coordinatorTransactionId = dsMessage.Argument
            for o in self.OperationTransactionLog:
                if o.CoordinatorTransactionId == coordinatorTransactionId:
                    operation = o
                    break
        return operation.State

    # ------------- private methods

    def onOperationCommitHandler(self):
        self.onEndOperation()

    def onOperationAbortHandler(self):
        self.onEndOperation()

    def onEndOperation(self):
        self.OperationTransactionLog.append(self.CurrentParticipantOperation)
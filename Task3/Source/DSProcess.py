import enum

from DSPortManager import portManager
from DSSocket import DSSocketAddress, DSSocket
from DSMessage import DSMessage, DSMessageType
from DSProcessManager import dsProcessManager
from DSCoordinatorTransaction import DSCoordinatorTransaction
from DSParticipantOperation import DSParticipantOperation
from DSTimer import DSTimer


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
        self.timer.Restart()

    # ---------------------------------------------------------------------------------------- Commands

    def PingCommandHandler(self, dsMessage):
        if self.DSStatus == DSProcessStatus.Stopped:
            return "I am stopped :( , my ID is: '" + str(self.Id) + "'"
        elif self.DSStatus == DSProcessStatus.Running:
            return "Hey... I'm running and my ID is: '" + str(self.Id) + "'"

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

    def SyncNewProcessCommandHandler(self, dsMessage):
        newProcess = dsMessage.Argument
        newProcess.Initialize(self.Data.copy())

    def GetDataCommandHandler(self, dsMessage):
        return ", ".join(self.Data)

    # ------------- private methods

    def HandleOperation(self, dsMessage):
        self.CurrentCoordinatorTransaction = DSCoordinatorTransaction(self.onTransactionCommitHandler, self.onTransactionAbortHandler)
        self.CurrentCoordinatorTransaction.Open()
        self.CurrentCoordinatorTransaction.Operate(dsMessage)
        return ", ".join(self.Data)

    def onTransactionCommitHandler(self, operation):
        self.applyChangesInCoordinatorData(operation)
        self.onEndTransaction()

    def onTransactionAbortHandler(self):
        self.onEndTransaction()

    def onEndTransaction(self):
        self.CoordinatorTransactionLog.append(self.CurrentCoordinatorTransaction)
        self.CurrentCoordinatorTransaction = None

    def applyChangesInCoordinatorData(self, operation):
        if operation.Type == DSMessageType.SetNewValue:
            self.Data.append(operation.Argument)
        elif operation.Type == DSMessageType.RollbackValues:
            for x in range(int(operation.Argument)):
                self.Data.pop(len(self.Data) - 1)

    # ------------------------------------- participant-side command handlers

    def InitRequestCommandHandler(self, dsMessage):
        self.CurrentParticipantOperation = DSParticipantOperation(dsMessage.Argument, self.Data, self.onOperationCommitHandler, self.onOperationAbortHandler)

    def VoteRequestCommandHandler(self, dsMessage):
        if self.CurrentParticipantOperation != None and self.CurrentParticipantOperation.CoordinatorTransactionId == dsMessage.Tag:
            self.CurrentParticipantOperation.Operate(dsMessage.Argument) # dsMessage.Argument containing a dsMessage determining an operation

    def GlobalCommitCommandHandler(self, dsMessage):
        if self.CurrentParticipantOperation != None and self.CurrentParticipantOperation.CoordinatorTransactionId == dsMessage.Argument:
            self.CurrentParticipantOperation.Commit()

    def GlobalAbortCommandHandler(self, dsMessage):
        if self.CurrentParticipantOperation != None and self.CurrentParticipantOperation.CoordinatorTransactionId == dsMessage.Argument:
            self.CurrentParticipantOperation.Abort()

    # ------------- private methods

    def onOperationCommitHandler(self):
        self.onEndOperation()

    def onOperationAbortHandler(self):
        self.onEndOperation()

    def onEndOperation(self):
        self.CoordinatorTransactionLog.append(self.CurrentParticipantOperation)
        self.CurrentParticipantOperation = None
import click
from click_shell import shell

from DSProcessManager import dsProcessManager
from DSProcess import DSProcess
from DSMessage import DSMessage, DSMessageType


# ------------------------------------------------------------------------------- private functions

def initialize(inputFile):
    (dsProcesses, data) = getProcessesAndLogsFromFile(inputFile)
    
    for p in dsProcesses:
        p.Initialize(data.copy())
        p.Run()

    dsProcessManager.Initialize(dsProcesses)


def getProcessesAndLogsFromFile(inputFile):

    dsProcesses = []
    data = []

    with open(inputFile, "r") as file_object:
        lines = file_object.read().splitlines()

        isProcessId = False
        history = False

        for _, line in enumerate(lines):

            if line is None or line == " " or line == "":
                continue

            if(not line.lower().find("#system") == -1):
                isProcessId = True
                continue

            if(not line.lower().find("#state") == -1):
                isProcessId = False
                history = True
                continue

            if(isProcessId == True):
                processInfo = line.strip()
                processInfoList = processInfo.split(';')
                if(len(processInfoList) == 2):
                    process = DSProcess(processInfoList[0].strip(), not processInfoList[1].lower().find("coordinator") == -1)
                    dsProcesses.append(process)
                else:
                    dsProcesses.append(DSProcess(processInfo, False))
                continue

            if (history == True):
                logInfo = line.split(';')
                if (len(logInfo) == 2 and (not (logInfo[1] == ' ' or logInfo[1] == '' or logInfo[1] == None))):
                    data = [log.strip() for log in logInfo[1].split(',')]
                continue

    return (dsProcesses, data)


def setNewValue(value):
    coordinator = dsProcessManager.GetCoordinator()
    if coordinator == None:
        return 'coordinator is not available'

    return coordinator.DSSocket.SendMessage(DSMessage(DSMessageType.SetNewValue, value))


def rollbackFromPosition(position):
    coordinator = dsProcessManager.GetCoordinator()
    if coordinator == None:
        return 'coordinator is not available'

    return coordinator.DSSocket.SendMessage(DSMessage(DSMessageType.RollbackValues, position))


def addProcess(pid):
    coordinator = dsProcessManager.GetCoordinator()
    if coordinator == None:
        return 'coordinator is not available'

    newProcess = dsProcessManager.GetProcessByID(pid)
    if newProcess != None:
        return 'the process id is duplicate'

    newProcess = DSProcess(pid, False)
    coordinator.DSSocket.SendMessage(DSMessage(DSMessageType.SyncNewProcess, newProcess))
    newProcess.Run()
    dsProcessManager.AddProcesses([newProcess])
    dataStr = newProcess.DSSocket.SendMessage(DSMessage(DSMessageType.GetData))
    return 'the process with the id \'' + pid + '\' is added and its data is [' + dataStr + ']'
    

def removeProcess(pid):
    process = dsProcessManager.GetProcessByID(pid)
    if process == None:
        return 'the process id is not valid'

    if dsProcessManager.getProcessesCount() == 1:
        return 'it\'s not possible to remove the last node'

    process.Dispose()
    dsProcessManager.RemoveProcess(process.Id)

    str = ''
    if process.IsCoordinator == True:
        dsProcessManager.setAnotherProcessAsCoordinator()
        str = ', (coordinator changed)'

    return 'the process with the id \'' + process.Id + '\' is removed' + str


def applyArbitraryFailure(pid, timeout):
    process = dsProcessManager.GetProcessByID(pid)
    if process == None:
        return 'the process id is not valid'    
    return process.DSSocket.SendMessage(DSMessage(DSMessageType.ArbitraryFailure, int(timeout)))


def getProcessData(pid):
    process = dsProcessManager.GetProcessByID(pid)
    if process == None:
        return 'the process id is not valid'
    return process.DSSocket.SendMessage(DSMessage(DSMessageType.GetData))


def getProcesses():
    ids = dsProcessManager.GetProcessDescriptions()
    return ", ".join(ids)

# -------------------------------------------------------------------------------

@shell(prompt='2PC > ')
def main():
    pass


@main.command()
@click.argument('file')
def init(file):
    initialize(file)
    click.echo('Ready to go!')


@main.command()
@click.argument('value')
def set(value):
    result = setNewValue(value)
    click.echo(result)


@main.command()
@click.argument('position')
def rollback(position):
    result = rollbackFromPosition(position)
    click.echo(result)


@main.command()
@click.argument('pid')
def add(pid):
    result = addProcess(pid)
    click.echo(result)


@main.command()
@click.argument('pid')
def remove(pid):
    result = removeProcess(pid)
    click.echo(result)

@main.command()
@click.argument('pid')
@click.argument('timeout')
def arbitrary_failure(pid, timeout):
    result = applyArbitraryFailure(pid, timeout)
    click.echo(result)

@main.command()
@click.argument('pid')
def get_data(pid):
    result = getProcessData(pid)
    click.echo(result)


@main.command()
def get_processes():
    result = getProcesses()
    click.echo(result)


if __name__ == '__main__':
    main()

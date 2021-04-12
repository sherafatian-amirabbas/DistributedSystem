import click
from click_shell import shell

from DSSharedData import sharedData

from BullyProcess import BullyProcess
from DSMessage import DSMessage, DSMessageType
import time


# ------------------------------------------------------------------------------- private functions

InputFile = None

def initializeFromFile(file):
    global InputFile
    InputFile = file
    processes = getProcessesFromFile()
    initializeFromProcesses(processes, False)


def initializeFromProcesses(processes, startTimer):
    sharedData.AddProcess(processes)
    for process in processes:
        process.Init(sharedData)
        process.Run(startTimer)


def getProcessesFromFile():
    bullyProcesses = []

    with open(InputFile, "r") as file_object:
        lines = file_object.read().splitlines()

        for _, line in enumerate(lines):

            if line is None or line == " " or line == "":
                continue

            dataArray = line.split(', ')
            id = dataArray[0]

            nameAndParticipationStr = dataArray[1]
            nameAndParticipationArr = nameAndParticipationStr.split('_')
            name = nameAndParticipationArr[0]
            participation = None

            clock = dataArray[2]

            process = BullyProcess(int(id), name, participation, clock)
            bullyProcesses.append(process)

    return bullyProcesses


def startProcessTimers():
    for process in sharedData.BullyProcesses:
        process.ResetTimer()

# -------------------------------------------------------------------------------

@shell(prompt='clock-sync-by-bully > ')
def main():
    pass


@main.command()
@click.argument('process_id')
def ping(process_id):
    processId = int(process_id)
    process = sharedData.GetProcessByID(processId)
    if process != None:
        result = process.DSSocket.SendMessage(DSMessage(DSMessageType.Ping))
        click.echo(result)
    else:
        click.echo("ProcessId is not valid, the process wasn't found.")


@main.command()
@click.argument('file')
def init(file):
    initializeFromFile(file)
    BullyProcess.StartElectionFromFirstProcess(sharedData)
    startProcessTimers()
    coordinatorProcess = BullyProcess.GetCoordinator(sharedData)
    click.echo("The Process with the Id: '" + str(coordinatorProcess.Id) + "' is the Coordinator now.")


@main.command()
def list():
    processes = BullyProcess.GetSortProcessList(sharedData.BullyProcesses)
    firstProc = processes[0]
    msg = DSMessage(DSMessageType.List)
    result = firstProc.DSSocket.SendMessage(msg)
    click.echo(result)


@main.command()
def show():
    processes = BullyProcess.GetSortProcessList(sharedData.BullyProcesses)
    result = ""
    for i in processes:
        result += i.ToString() + "\n"
    click.echo(result)


@main.command()
@click.argument('process_id')
@click.argument('clock')
def set_time(process_id, clock):
    processId = int(process_id)
    process = sharedData.GetProcessByID(processId)
    if process != None:
        msg=DSMessage(DSMessageType.SetTime)
        msg.Argument = clock
        result = process.DSSocket.SendMessage(msg)
        click.echo(result)
    else:
        click.echo("ProcessId is not valid, the process wasn't found.")


@main.command()
def clock():
    processes = BullyProcess.GetSortProcessList(sharedData.BullyProcesses)
    firstProc = processes[0]
    msg = DSMessage(DSMessageType.Clock)
    result = firstProc.DSSocket.SendMessage(msg)
    click.echo(result)


@main.command()
@click.argument('process_id')
def kill(process_id):
    processId = int(process_id)
    process = sharedData.GetProcessByID(processId)
    if process != None:
        result = process.DSSocket.SendMessage(DSMessage(DSMessageType.Kill))
        if result == None:
            click.echo("The process is killed now.")
        else:
            click.echo("The process is killed now - the process with ID '" + str(result) + "' started election.")

    else:
        click.echo("Process is not found")


@main.command()
@click.argument('process_id')
def freeze(process_id):
    processId = int(process_id)
    process = sharedData.GetProcessByID(processId)
    if process != None:
        result = process.DSSocket.SendMessage(DSMessage(DSMessageType.Freeze))
        click.echo(result)
    else:
        click.echo("Process is not found")


@main.command()
@click.argument('process_id')
def unfreeze(process_id):
    processId = int(process_id)
    process = sharedData.GetProcessByID(processId)
    if process != None:
        result = process.DSSocket.SendMessage(DSMessage(DSMessageType.Unfreeze))
        click.echo(result)
    else:
        click.echo("Process is not found")


@main.command()
def reload():
    defaultProcesses = getProcessesFromFile()

    newProcesses = []
    for process in defaultProcesses:
        existedProc = sharedData.GetProcessByID(process.Id)
        if existedProc == None:
            newProcesses.append(process)

    if len(newProcesses) == 0:
        click.echo("No new process(es) initialized")
        return

    initializeFromProcesses(newProcesses, True)
    BullyProcess.StartElectionFromFirstProcess(sharedData)
    coordinatorProcess = BullyProcess.GetCoordinator(sharedData)

    click.echo("New process(es) initialized - the process with ID '" + str(coordinatorProcess.Id) + "' is the new coordinator.")


if __name__ == '__main__':
    main()

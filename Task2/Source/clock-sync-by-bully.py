import click
from click_shell import shell

from DSSharedData import sharedData

from BullyProcess import BullyProcess
from DSMessage import DSMessage, DSMessageType
import time


# ------------------------------------------------------------------------------- private functions

def initialize(file):
    processes = getProcessesFromFile(file)

    sharedData.Initialize(processes)

    for process in processes:
        process.Run()

    startElection()

    return getCoordiatorID()


def getProcessesFromFile(file_name):
    bullyProcesses = []

    with open(file_name, "r") as file_object:
        lines = file_object.read().splitlines()

        for _, line in enumerate(lines):

            if line is None or line == " " or line == "":
                continue

            dataArray = line.split(', ')
            id = dataArray[0]

            nameAndParticipationStr = dataArray[1]
            nameAndParticipationArr = nameAndParticipationStr.split('_')
            name = nameAndParticipationArr[0]
            participation = nameAndParticipationArr[1]

            clock = dataArray[2]

            process = BullyProcess(int(id), name, int(participation), clock)
            bullyProcesses.append(process)

    return bullyProcesses


def startElection():
    processes = BullyProcess.GetSortProcessList(sharedData.BullyProcesses)

    firstProc = processes[0]

    msg = DSMessage(DSMessageType.StartElection)
    firstProc.DSSocket.SendMessage(msg)


def getCoordiatorID():
    return sharedData.BullyProcesses[0].CoordinatorProcessId


# -------------------------------------------------------------------------------


@shell(prompt='clock-sync-by-bully > ')
def main():
    pass


@main.command()
@click.argument('file')
def init(file):
    coordinatorId = initialize(file)
    click.echo("The Process with the Id: '" + str(coordinatorId) + "' is the Coordinator now.")


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
def reload():
    processes =sharedData.BullyProcesses
    process=processes[0]
    msg=DSMessage(DSMessageType.Reload)
    result=process.DSSocket.SendMessage(msg)
    click.echo('kaya')


    
@main.command()
@click.argument('process_id')
@click.argument('clock')
def set_time(process_id, clock):
    processId = int(process_id)
    process = sharedData.GetProcessByID(processId)
    if process:
        msg=DSMessage(DSMessageType.SetTime)
        msg.Argument = clock
        result = process.DSSocket.SendMessage(msg)
        click.echo(result)
    else:
        click.echo("Process is not found please try again")


@main.command()
def clock():
    processes = BullyProcess.GetSortProcessList(sharedData.BullyProcesses)
    firstProc = processes[0]
    msg = DSMessage(DSMessageType.Clock)
    result = firstProc.DSSocket.SendMessage(msg)
    click.echo(result)



if __name__ == '__main__':
    main()

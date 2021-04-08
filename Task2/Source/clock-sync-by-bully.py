import click
from click_shell import shell

from DSSharedData import sharedData

from BullyProcess import BullyProcess
from DSMessage import DSMessage, DSMessageType


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

        for index, line in enumerate(lines):

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
def clock():
    processes = BullyProcess.GetSortProcessList(sharedData.BullyProcesses)
    firstProc = processes[0]
    msg = DSMessage(DSMessageType.Clock)
    result = firstProc.DSSocket.SendMessage(msg)
    click.echo(result)


if __name__ == '__main__':
    main()

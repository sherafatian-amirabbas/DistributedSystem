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

            dataArrkay = line.split(', ')
            id = dataArrkay[0]
            
            nameAndParticipationStr = dataArrkay[1]
            nameAndParticipationArr = nameAndParticipationStr.split('_')
            name = nameAndParticipationArr[0]
            participation = nameAndParticipationArr[1]

            clock = dataArrkay[2]

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


# ------------------------------------------------------------------------------- private functions


@shell(prompt='clock-sync-by-bully > ')
def main():
    pass


@main.command()
@click.argument('file')
def init(file):
    coordinatorId = initialize(file)
    click.echo("The Process with the Id: '" + str(coordinatorId) + "' is the Coordinator now.")


if __name__ == '__main__':
    main()

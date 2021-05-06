import click
from click_shell import shell

from DSData import dsData
from DSProcess import DSProcess
from DSMessage import DSMessage, DSMessageType


# ------------------------------------------------------------------------------- private functions

def initialize(inputFile):
    (dsProcesses, dataLogs) = getProcessesAndLogsFromFile(inputFile)
    
    for p in dsProcesses:
        p.Run()

    dsData.Initialize(dsProcesses, dataLogs)

def getProcessesAndLogsFromFile(inputFile):

    dsProcesses = []
    dataLogs = []

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
                    dataLogs = [log.strip() for log in logInfo[1].split(',')]
                continue

    return (dsProcesses, dataLogs)

# -------------------------------------------------------------------------------


@shell(prompt='2PC > ')
def main():
    pass


@main.command()
@click.argument('file')
def init(file):
    initialize(file)
    click.echo("Ready to go!")


@main.command()
@click.argument('process_id')
def ping(process_id):
    pass


if __name__ == '__main__':
    main()

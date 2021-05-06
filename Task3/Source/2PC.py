import click
from click_shell import shell

import DSData
from DSProcess import DSProcess
from DSMessage import DSMessage, DSMessageType


# ------------------------------------------------------------------------------- private functions

def initialize(inputFile):
    pass

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

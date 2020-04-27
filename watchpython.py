# WatchPython
# By Al Sweigart al@inventwithpython.com

__version__ = '0.1.0'

import os
import subprocess
import sys
import time

import click


@click.command()
@click.version_option(version=__version__)
@click.option('-b', '--beep', is_flag=True, help='Beep if command has a non-zero exit.')
@click.option('-n', '--interval', default=2, help='Seconds to wait between updates.', type=float)
@click.argument('command')
def main(command, beep, interval):
    """Run the given command until Ctrl-C is pressed."""
    clearScreen()
    commandStdOutput = ''
    try:
        while True:
            try:
                result = subprocess.run(
                    command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, shell=True, check=True
                )
                resultStdOut = result.stdout
            except subprocess.CalledProcessError as excObj:
                # This code runs when the command returns a non-zero exit code:
                if beep:
                    click.echo(chr(7))  # Play a beep noise.

                resultStdOut = excObj.stdout

            if resultStdOut != commandStdOutput:
                commandStdOutput = resultStdOut
                clearScreen()
                click.echo(commandStdOutput)

            time.sleep(interval)
    except KeyboardInterrupt:
        sys.exit()


def clearScreen():
    """Clear the screen by running the cls/clear command.

    This isn't how the real watch command works, but it's close enough. This
    means that when watchpython exits, the original text on the screen won't
    be restored."""
    if sys.platform == 'win32':
        os.system('cls')  # Windows uses the cls command.
    else:
        os.system('clear')  # macOS and Linux use the clear command.


if __name__ == '__main__':
    main()

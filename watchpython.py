# WatchPython
# By Al Sweigart al@inventwithpython.com

__version__ = '0.1.0'

import os
import shutil
import subprocess
import sys
import time

import click


@click.command()
@click.version_option(version=__version__)
@click.option('-b', '--beep', is_flag=True, help='Beep if command has a non-zero exit.')
@click.option('-e', '--errexit', is_flag=True, help='Exit if command has a non-zero exit.')
@click.option('-g', '--chgexit', is_flag=True, help='Exit when output from command changes.')
@click.option('-n', '--interval', default=2.0, help='Seconds to wait between updates.')
@click.option('-t', '--no-title', is_flag=True, help='Turn off header.')
@click.argument('command')
def main(command, beep, errexit, chgexit, interval, no_title):
    """Run the given command until Ctrl-C is pressed."""
    clearScreen()
    commandStdOutput = ''
    doExit = False
    exitCode = 0
    isInitialOutput = True
    try:
        while True:
            try:
                result = subprocess.run(
                    command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, shell=True, check=True
                )
                resultStdOut = result.stdout
                exitCode = 0  # No need to set this to result.returncode because if it wasn't 0, CalledProcessError would have been raised.
            except subprocess.CalledProcessError as excObj:
                # This code runs when the command returns a non-zero exit code:
                if beep:
                    click.echo(chr(7))  # Play a beep noise.
                if errexit:
                    # watchpython should exit if errexit is set and the command exited with a non-zero exit code:
                    doExit = True
                    exitCode = excObj.returncode

                resultStdOut = excObj.stdout

            if resultStdOut != commandStdOutput:
                # Refresh the screen if the command output has changed:
                commandStdOutput = resultStdOut
                clearScreen()
                if not no_title:
                    click.echo(getTitle(command, interval))
                click.echo(commandStdOutput)  # Display the command output.

                if not isInitialOutput and chgexit:
                    # Exit when chgexit is set and the command output has changed:
                    doExit = True


            if doExit:
                # Terminate watchpython:
                if exitCode != 0:
                    click.echo('Command exited with a exit code: ' + str(exitCode))
                sys.exit(exitCode)

            isInitialOutput = False  # Set to False after the first time the command is run.

            time.sleep(interval)  # Pause in between running commands.
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


def getHostname():
    """Return a string of the computer's hostname, obtained by runnning the
    `hostname` command. Returns a blank string if it was unable to do so."""

    try:
        result = subprocess.run(
            'hostname', stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, shell=True, check=True
        )
    except subprocess.CalledProcessError:
        return ''

    return result.stdout.strip()


def getTitle(command, interval):
    """Return a string of to use for the title at the top."""
    width = shutil.get_terminal_size()[0]

    # Get the interval message:
    intervalMsg = 'Every ' + str(interval) + 's: '

    # Get the command message:
    commandMsg = command + ' '  # Add a space after the message.

    # Get the host and timestamp message:
    hostname = getHostname()
    if hostname != '':
        hostAndTimeMsg = hostname + ': ' + time.strftime('%c')
    else:
        hostAndTimeMsg = time.strftime('%c')

    # If the terminal window isn't wide enough, truncate commandMsg:
    spaceForCommandMsg = width - (len(intervalMsg) + len(hostAndTimeMsg))
    if spaceForCommandMsg < len(commandMsg) and spaceForCommandMsg >= 4:
        commandMsg = commandMsg[:spaceForCommandMsg - 4] + '... '
    elif spaceForCommandMsg < len(commandMsg):
        commandMsg = ''

    # If the terminal window still isn't wide enough, cut the interval message:
    if width - (len(intervalMsg) + len(hostAndTimeMsg)) < 0:
        intervalMsg = ''

    # If the terminal window still isn't wide enough, cut the host/timestamp message:
    if width < len(hostAndTimeMsg):
        hostAndTimeMsg = ''

    # If the terminal window has enough space, right-justify the host/timestamp message:
    if width - (len(intervalMsg) + len(commandMsg) + len(hostAndTimeMsg)) > 0:
        return intervalMsg + commandMsg + hostAndTimeMsg.rjust(width - (len(intervalMsg) + len(commandMsg)))
    else:
        return intervalMsg + commandMsg + hostAndTimeMsg






if __name__ == '__main__':
    main()

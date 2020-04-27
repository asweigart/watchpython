#!/usr/bin/env python3
"""WatchPython
By Al Sweigart al@inventwithpython.com

A re-implementation of the Unix watch command in Python.

The windows binary can be downloaded from https://inventwithpython.com/watch.exe

I created this because the Cygwin watch command on Windows has weird
display issues and doesn't seem to work right."""

# NOTE TO SELF: I was only able to generate a Windows binary if I install
# pyinstaller to Python 3.5 (it fails with Python 3.8 in a pipenv virtual environment)
# and then run "pyinstaller.exe watchpython.spec --onefile" (be sure to use
# the pyinstaller.exe for Python 3.5.) The watchpython.spec file is generated
# from running "pyinstaller.exe watchpython.py --onefile" (though the binary
# that generates doesn't work? For some reason?)


"""
List of differences between this implementation and the Unix watch command:

- Doesn't use curses, so the original terminal text isn't restored after this
  program terminates.
- If there's more output than the terminal height can handle, only one
  screenful of text is displayed. If -f is specified, than the full text
  is displayed by the terminal window will scroll down the to the bottom.
- The timestamp in the title bar shows the last time the command was run
  AND changed text, not just the last time the command was run.
- --color and color output isn't supported.
- --differences and difference highlighting isn't supported.
- --precise isn't supported.
- --exec isn't supported.
- Probably some other minor things aren't supported either.
"""

__version__ = '0.1.2'

import os
import shutil
import socket
import subprocess
import sys
import time

import click


@click.command()
@click.version_option(version=__version__)
@click.option('-b', '--beep', is_flag=True, help='Beep if command has a non-zero exit.')
@click.option('-e', '--errexit', is_flag=True, help='Exit if command has a non-zero exit.')
@click.option('-f', '--full-text', is_flag=True, help='Display full text even if it\'s more than one screen long.')
@click.option('-g', '--chgexit', is_flag=True, help='Exit when output from command changes.')
@click.option('-n', '--interval', default=2.0, help='Seconds to wait between updates.')
@click.option('-t', '--no-title', is_flag=True, help='Turn off header.')
@click.argument('command')
def main(command, beep, errexit, full_text, chgexit, interval, no_title):
    """Repeatedly run the given command. Press Ctrl-C to quit.

By Al Sweigart al@inventwithpython.com https://pypi.org/project/WatchPython/"""
    clearScreen()
    commandStdOutput = ''
    doExit = False
    exitCode = 0
    isInitialOutput = True
    prevWidth, prevHeight = shutil.get_terminal_size()  # Used to detect if the terminal window was resized.
    try:
        while True:
            width, height = shutil.get_terminal_size()  # Get the size of the terminal window.
            if not no_title:
                height -= 1  # Adjust height for the line the header takes up.

            try:
                result = subprocess.run(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True,
                    shell=True,
                    check=True,
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

            if resultStdOut != commandStdOutput or (width, height) != (prevWidth, prevHeight):
                # Refresh the screen if the command output has changed, or the terminal was resized:
                commandStdOutput = resultStdOut
                clearScreen()
                if not no_title:
                    click.echo(getTitle(command, interval))

                if not full_text:
                    # If a single line is longer than the width of the
                    # terminal, it's actually multiple lines for our
                    # purposes of only displaying one screen of text.
                    commandStdOutputLines = commandStdOutput.splitlines()
                    numLines = 0
                    for i, line in enumerate(commandStdOutputLines):
                        finishedDisplayingOutput = False
                        for i in range(0, len(line), width):
                            # Print the "line" (without a newline because the last one shouldn't have a newline)
                            click.echo(line[i:i + width], nl=False)
                            numLines += 1
                            if numLines == height:
                                finishedDisplayingOutput = True
                                break
                            click.echo()  # Print a newline.
                        if finishedDisplayingOutput:
                            break
                else:
                    # Display the full output:
                    click.echo(commandStdOutput, nl=False)

                if not isInitialOutput and chgexit:
                    # Exit when chgexit is set and the command output has changed:
                    doExit = True

            if doExit:
                # Terminate watchpython:
                if exitCode != 0:
                    click.echo('Command exited with a exit code: ' + str(exitCode))
                sys.exit(exitCode)

            # Do a bunh of post-command actions before looping back:
            prevWidth, prevHeight = width, height
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


def getTitle(command, interval):
    """Return a string of to use for the title at the top."""
    width = shutil.get_terminal_size()[0]  # Get the width of the terminal window.

    # Get the interval message:
    intervalMsg = 'Every ' + str(interval) + 's: '

    # Get the command message:
    commandMsg = command + ' '  # Add a space after the message.

    # Get the host and timestamp message:
    hostname = socket.gethostname()
    if hostname != '':
        hostAndTimeMsg = hostname + ': ' + time.strftime('%c')
    else:
        hostAndTimeMsg = time.strftime('%c')

    # If the terminal window isn't wide enough, truncate commandMsg:
    spaceForCommandMsg = width - (len(intervalMsg) + len(hostAndTimeMsg))
    if spaceForCommandMsg < len(commandMsg) and spaceForCommandMsg >= 4:
        commandMsg = commandMsg[: spaceForCommandMsg - 4] + '... '
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

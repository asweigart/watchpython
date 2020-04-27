# watchpython
A re-implementation of the Unix watch command in Python.

The windows binary can be downloaded from https://inventwithpython.com/watch.exe

I created this because the Cygwin watch command on Windows has weird
display issues and doesn't seem to work right.

    Usage: watchpython.py [OPTIONS] COMMAND

      Repeatedly run the given command. Press Ctrl-C to quit.

      By Al Sweigart al@inventwithpython.com
      https://pypi.org/project/WatchPython/

    Options:
      --version             Show the version and exit.
      -b, --beep            Beep if command has a non-zero exit.
      -e, --errexit         Exit if command has a non-zero exit.
      -f, --full-text       Display full text even if it's more than one screen
                            long.
      -g, --chgexit         Exit when output from command changes.
      -n, --interval FLOAT  Seconds to wait between updates.
      -t, --no-title        Turn off header.
      --help                Show this message and exit.
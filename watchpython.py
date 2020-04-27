# WatchPython
# By Al Sweigart al@inventwithpython.com

__version__ = '0.1.0'

import click

@click.command()
@click.option("--count", default=1, help="Number of greetings.")
@click.argument('nameeee')
def main(count, nameeee):
    """Simple program that greets NAME for a total of COUNT times."""
    for _ in range(count):
        click.echo(f"Hello, {nameeee}!")

if __name__ == '__main__':
    main()
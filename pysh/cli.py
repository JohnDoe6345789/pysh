"""Command-line entry point for PySH."""

import os
import os.path
import sys

from pysh import Completer, PySH


def main():
    if sys.stdin.isatty():
        completer = Completer()
        completer.install()

    console = PySH(os.getenv("PATH"))

    if len(sys.argv) == 1:
        console.interact()
        return

    filename = sys.argv[1]
    sys.argv = sys.argv[1:]

    if not os.path.isfile(filename):
        raise ValueError("Could not find file: " + filename)
    elif not os.access(filename, os.R_OK):
        raise ValueError("File is not readable: " + filename)

    with open(filename) as handle:
        console.runscript(handle)

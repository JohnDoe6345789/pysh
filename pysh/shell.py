# Copyright (c) 2012 Antoine d'Otreppe de Bouvette
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import code
import getpass
import keyword
import os
import pydoc
import re
import shlex
import socket
import sys

from pysh.meta import __version__
from pysh.utils import InlineExec, InlineVar, PySHUtils

ANSI_BOLD_GREEN = "\033[1;32m"
ANSI_BOLD_BLUE = "\033[1;34m"
ANSI_RESET = "\033[0m"


class PySH(code.InteractiveConsole):
    banner = "PySH " + __version__ + " / Python " + sys.version + os.linesep + \
        "Type \"help\" for available commands."
    inlineShellPattern = re.compile(r'`([^`]+)`')
    linePattern = re.compile(r'(\s*)(.+)')

    def __init__(self, path=""):
        self.paths = path.split(":")
        self.util = PySHUtils(self.paths)
        self.user = getpass.getuser()
        self.host = socket.gethostname().split(".", 1)[0]
        self._primary_prompt_token = "<pysh_primary_prompt>"
        self._secondary_prompt_token = "<pysh_secondary_prompt>"
        self.super.__init__({
            "__pysh__": self.util,
            "pyhelp": pydoc.help
        })

    def runscript(self, f):
        for line in f:
            self.push(line)
        else:
            self.push("\n")

    def push(self, line):
        m = self.linePattern.match(line)

        if m is not None:
            indent = m.group(1)
            line = m.group(2)

            try:
                shelements = shlex.split(line)
                first = shelements[0]
            except ValueError:
                line = self.processInlineShell(line)
            else:
                if first in keyword.kwlist or first in self.locals:
                    line = self.processInlineShell(line)
                elif shelements is not None and hasattr(self.util, "cmd_" + first):
                    line = self.processCommand(shelements)
                elif self.util.find(first) is not None:
                    line = self.translate(shelements)
                else:
                    line = self.processInlineShell(line)

            line = indent + line

        return self.super.push(line)

    def interact(self):
        previous_ps1 = getattr(sys, "ps1", ">>> ")
        previous_ps2 = getattr(sys, "ps2", "... ")
        sys.ps1 = self._primary_prompt_token
        sys.ps2 = self._secondary_prompt_token

        try:
            self.super.interact(self.banner)
        finally:
            sys.ps1 = previous_ps1
            sys.ps2 = previous_ps2

    def translate(self, shelements):
        return "(__pysh__.shrun(" + repr(self.inlineVars(shelements)) + "))"

    def inlineVars(self, command):
        for i, arg in enumerate(command):
            if arg.startswith("$"):
                varname = arg[1:]
                if varname:
                    command[i] = InlineVar(varname)
                else:
                    raise SyntaxError("Empty variable name")

        return command

    def processInlineShell(self, line):
        def replacer(match):
            command = shlex.split(match.group(1))
            command = self.inlineVars(command)
            return "(__pysh__.inline(" + repr(command) + "))"

        return self.inlineShellPattern.sub(replacer, line)

    def processCommand(self, shelements):
        shelements = self.inlineVars(shelements)
        return "(__pysh__.cmd_" + shelements[0] + "(" + repr(shelements[1:]) + "))"

    def raw_input(self, prompt=""):
        if prompt == self._primary_prompt_token:
            prompt = self.build_prompt()
        elif prompt == self._secondary_prompt_token:
            prompt = self.build_secondary_prompt()

        return self.super.raw_input(prompt)

    def build_prompt(self):
        cwd = self.format_cwd()
        return f"{ANSI_BOLD_GREEN}{self.user}@{self.host}{ANSI_RESET}:{ANSI_BOLD_BLUE}{cwd}{ANSI_RESET}$ "

    def build_secondary_prompt(self):
        return f"{ANSI_BOLD_GREEN}> {ANSI_RESET}"

    def format_cwd(self):
        cwd = os.getcwd()
        home = os.path.expanduser("~")

        if cwd == home:
            display = "~"
        elif cwd.startswith(home + os.sep):
            display = "~" + cwd[len(home):]
        else:
            display = cwd

        return display.replace("\\", "/")

    @property
    def super(self):
        return super(PySH, self)


__all__ = ["PySH"]

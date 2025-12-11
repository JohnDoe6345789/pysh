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

import glob
import os
import subprocess
import sys

PYSHRC = os.path.expanduser("~/.pyshrc")


class PySHUtils:
    def __init__(self, path):
        self.path = path

    def cmd_cd(self, arguments):
        """Change current working directory"""

        if arguments:
            target = os.path.expanduser(arguments[0])
            if os.path.isdir(target):
                os.chdir(target)
            else:
                print(f"Not a directory: {target}", file=sys.stderr)
        else:
            os.chdir(os.path.expanduser("~"))

    def cmd_migrate(self, arguments):
        """Migrate from your previous shell to pysh

        When you're ready to install pysh, execute this command first
        to migrate your current settings to the ~/.pyshrc file.
        This is necessary to keep your PATH and other important variables.
        """

        print("Warning: this will overwrite your .pyshrc file.")
        yesno = input("Do you wish to continue ? y/n: ")
        if yesno == "y":
            with open(PYSHRC, "w") as f:
                f.write("export PATH={!r}\n".format(os.getenv("PATH")))

    def cmd_help(self, arguments):
        """Get help on pysh"""

        if arguments:
            command = arguments[0]

            if command.startswith("("):
                # Bet user wanted pydoc's help ?
                print('For pydoc help, type "help(...)" with no space or use pyhelp()')
            else:
                attrName = "cmd_" + command
                try:
                    method = getattr(self, attrName)
                except AttributeError:
                    print("No such command: " + command)
                else:
                    for line in map(lambda x: x.lstrip(), method.__doc__.split("\n")):
                        print(line)
        else:
            commands = []
            for attrName in dir(self):
                if attrName.startswith("cmd_"):
                    commands.append(attrName)

            longest = max(map(lambda x: len(x), commands)) if commands else 0

            print('For python help, use "pyhelp()"')
            print('For detailed help on a specific command, type "help <command>"')
            print()

            for command in commands:
                method = getattr(self, command)
                command_name = command[4:]
                brief = method.__doc__.split("\n", 1)[0]
                print(f"  {command_name:<{longest}}{brief}")

    def shrun(self, shelements):
        try:
            self.parseAndMake(shelements).wait()
        except OSError as e:
            print(e)

    def parseAndMake(self, shelements, stdout=sys.stdout):
        # Find subprocesses
        processes = []
        process = []
        for element in shelements:
            if element == "|":
                processes.append(process)
                process = []
            else:
                if "~" in element:
                    element = os.path.expanduser(element)
                if glob.has_magic(element):
                    process.extend(glob.glob(element))
                else:
                    process.append(element)
        else:
            processes.append(process)

        lastProcess = processes.pop()
        stdin = sys.stdin

        for process in processes:
            p = self.makeProcess(process, stdin, subprocess.PIPE)
            stdin = p.stdout

        return self.makeProcess(lastProcess, stdin, stdout)

    def find(self, command):
        if command.startswith("./"):
            return command

        for path in self.path:
            filename = os.path.join(path, command)
            if os.path.isfile(filename):
                return filename

    def makeProcess(self, args, stdin, stdout):
        name = self.find(args[0])

        if name is None:
            raise Exception("Command not found: %s" % name)

        args[0] = name
        return subprocess.Popen(args, stdin=stdin, stdout=stdout)

    def inline(self, shelements):
        return InlineExec(self.parseAndMake(shelements, subprocess.PIPE))


class InlineExec:
    def __init__(self, process):
        self.process = process

    def __str__(self, encoding=None):
        encoding = self.getencoding(encoding)
        return self.process.stdout.read().decode(encoding)

    def __bytes__(self):
        return self.process.stdout.read()

    def __iter__(self, encoding=None):
        encoding = self.getencoding(encoding)

        data = self.process.stdout.readline()
        while data:
            yield data.decode(encoding).rstrip(os.linesep)
            data = self.process.stdout.readline()

    def getencoding(self, encoding):
        if encoding is None:
            encoding = sys.getdefaultencoding()
        return encoding


class InlineVar:
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name


__all__ = ["PYSHRC", "PySHUtils", "InlineExec", "InlineVar"]

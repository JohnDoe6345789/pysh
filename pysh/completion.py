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

import os

import readline


class Completer:
    def __init__(self):
        self.lastText = None
        self.lastResults = None

    def complete(self, text, index):
        if text != self.lastText or index == 0:
            self.lastText = text
            self.results = self.search(text)

        try:
            return self.results[index]
        except IndexError:
            return None

    def search(self, text):
        results = []

        if text != "." and os.path.isdir(text):
            if text[-1] == os.path.sep:
                dirname = text
            else:
                dirname = text + os.path.sep

            fname = ""
            results.append(dirname)

        else:
            dirname = os.path.dirname(text)
            fname = os.path.basename(text)

        files = os.listdir(os.path.expanduser(dirname) or ".")

        for f in files:
            if f.startswith(fname):
                full = os.path.join(dirname, f)

                if os.path.isdir(os.path.expanduser(full)):
                    full += os.path.sep

                results.append(full)

        return results

    def install(self):
        readline.set_completer(self.complete)

        delims = readline.get_completer_delims()
        delims = delims.replace("/", "")
        readline.set_completer_delims(delims)

        if "libedit" in readline.__doc__:
            readline.parse_and_bind("bind '\\t' rl_complete")
        else:
            readline.parse_and_bind("tab: complete")


__all__ = ["Completer"]

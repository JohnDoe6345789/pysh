pysh
####

pysh is a Shell that mixes Python and Bash syntax.

Requirements
============

pysh requires only Python3 to run, and should work on Linux and OSX platforms (and probably other UNIX environments).

Installing
==========

Poetry is used to build and publish PySH. If you already have Poetry installed,
run:

  poetry install

You can then start the shell with `poetry run pysh`, or build/install the wheel
with `poetry build && pip install dist/*.whl`. Jump to "Discover it" if you just
want to run the version in this repository without installing.

! Important ! PySH is still beta software, and you should not use it for your everyday work unless your know what you are doing.
If, like me, you want to use PySH as default shell, the best option is to set it only in your terminal emulator (gnome-terminal, Apple terminal app...) via the preferences of the application.

Discover it
===========

It's really easy to get started. All you need is Python3. Download the zip file, unzip it on the destination of your choice, chmod the `pysh` file and execute it. ::

  unzip aspyct-pysh-xxxx.zip -d aspyct-pysh
  cd aspyct-pysh
  chmod +x bin/pysh
  ./bin/pysh

You are now in what looks like a regular python interpreter. Try to write some python::

  > print("Hello")
  > if True:
  .    print("pysh looks terrific ! :)")

Shell commands also work, as well as autocompletion with tab::

  > ls
  > vi <yourfile>

You can also mix python and shell::

  > if True:
  .    ls
  . 
  > myvar = `ls`
  > print(myvar)

Prompt styling
==============

PySH now renders an Ubuntu-style prompt every time you run it interactively. The username and host appear in bold green, the current directory in bold blue, and the prompt mimics bash with a trailing `$`, so you get the same `r@formatme:/var/log$` look and feel (along with automatic updates after `cd`). This keeps the experience visually consistent with a real bash session.

Internals
=========

pysh uses the built-in *code* module to emulate the python interpreter, and tries to detect whether a line is a shell command or regular python code. Every line is translated before it is fed to the interpreter.

In the pysh shell, there is a special variable named `__pysh__` that is used to make shell commands happen. You may use this class directly, but it will probably not make your code cleaner.

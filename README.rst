PySH
====

PySH is a lightweight shell that lets you mix Python expressions and statements with traditional shell commands. It is powered by the standard Python `code` module and intercepts each line to automatically decide whether you meant to run Python or execute a system command.

Features
--------

- Write Python code and run shell commands without switching contexts.
- Prompt updates automatically after `cd` and matches the familiar Bash look.
- Access the special `__pysh__` helper when you need to interact directly with the shell layer.

Requirements
------------

- Python 3.6 or newer.
- A UNIX-like platform (Linux, macOS, WSL, etc.).

Installation
------------

1. Clone the repository and install dependencies with Poetry:

   .. code-block:: bash

      $ git clone https://github.com/aspyct/pysh.git
      $ cd pysh
      $ poetry install

2. Run the shell from this checkout:

   .. code-block:: bash

      $ poetry run pysh

3. To build and install a wheel for wider use:

   .. code-block:: bash

      $ poetry build
      $ pip install dist/*.whl

Once installed, `pysh` is available as a runnable script and can be set as the shell in your terminal emulator just like any other shell.

Usage
-----

After launching PySH you can interleave Python and shell commands:

.. code-block:: bash

   > print("Hello")
   > if True:
.      print("pysh looks terrific!")

   > ls
   > vi README.rst
   > myvar = `ls`
   > print(myvar)

Shell commands behave the same as in Bash, and Python statements keep their usual semantics. Autocompletion with Tab works for both languages.

Prompt styling
--------------

PySH renders an Ubuntu-inspired prompt: the username and host are bold green, the current directory is bold blue, and the ending `$` mirrors Bash. The prompt updates automatically after commands such as `cd`.

Internals
---------

Under the hood, PySH uses `code.InteractiveConsole` to simulate the interpreter loop. Each line is inspected to decide whether it is a shell request, and the `__pysh__` helper exposes lower-level hooks into that detection logic.

Development
-----------

Run tests with:

.. code-block:: bash

   $ poetry run pytest

Contributions are welcome: fork the repo, add a test, and send a pull request.

License
-------

MIT. See the `LICENSE` file for details.

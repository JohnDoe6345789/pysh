# Technical Documentation

## Purpose
PySH is a minimal shell that routes each line through Python's interpreter while still allowing traditional shell workflows. This document explains how the entry point, interactive console, helper utilities, inline shell syntax, and completion hooks work together so contributors can extend or debug the project without relying on high-level prose.

## Command-line entry
- `pysh.cli.main` wires the shell to the environment: when stdin is a TTY it installs the completion helper, then instantiates `PySH` with the current `PATH`. With no arguments the shell enters interactive mode; a script argument is validated (must exist and be readable) and passed to `PySH.runscript`, which feeds every line via `push` and finishes with a newline to flush any final input.

## Interactive shell internals (`pysh.shell.PySH`)
- `PySH` subclasses `code.InteractiveConsole`, injecting `__pysh__` (the utils object) and `pyhelp` helpers into the console locals so inline helpers can be invoked just like built-ins.
- The `push` override tokenizes each user line with `shlex` to determine whether it represents Python keywords, builtin locals, a registered `cmd_*` helper, or a resolvable external command. Python and custom commands continue down the normal interpreter path, while shell commands are rewritten into calls to `__pysh__` helpers before evaluation.
- Inline shell expressions (`` `...` ``) and variable references (leading `$`) are rewritten in `processInlineShell`/`inlineVars` so they evaluate as `__pysh__.inline`/`InlineVar`, the same mechanism that `translate` uses to route pipelines through `__pysh__.shrun`.
- Prompt rendering handles primary and secondary prompts via `raw_input` tokens. The prompt shows bold `user@host`, the current working directory (with `~` substitution for the home path), and a bash-like `$`, while the continuation prompt emits a green `> `. This keeps the REPL visually familiar.

## Shell utilities (`pysh.utils`)
- `PySHUtils` is the fa?ade available as `__pysh__`. It stores the resolved search path (split `PATH`) and implements every `cmd_*` command plus helpers for subprocess orchestration:
  - `cmd_cd`, `cmd_migrate`, and `cmd_help` provide built-in shell commands; `cmd_help` enumerates methods that start with `cmd_`, derives their documentation, and prints summaries or full docstrings when requested.
  - `shrun` and `parseAndMake` turn tokenized commands into subprocess chains, honoring globbing, `~` expansion, and pipe segments before calling `makeProcess`.
  - `makeProcess` resolves the executable with `find`, ensures the command exists (raising when not found), and uses `subprocess.Popen` to spawn processes with custom stdin/stdout streams.
  - `inline` wraps a pipeline in `InlineExec`, which exposes `__str__`, `__bytes__`, and iteration to read command output as text, bytes, or lines.
- Inline helpers include `InlineVar` (represents `$var` placeholders) and `InlineExec` (reads command output lazily via the process's stdout), so inline shell expressions feel seamless in Python code.

## Autocompletion (`pysh.completion.Completer`)
- Installing the completer configures `readline` so that tab completion searches the filesystem relative to the current working directory, respects directories by appending separators, and removes `/` from `readline` delimiters so paths complete naturally.
- The completer caches the last prefix and results so repeated completions are efficient; the `search` method lists the parent directory, filters by prefix, and makes directories visually distinct by appending `os.path.sep`.
- Compatibility code binds either `rl_complete` (libedit) or the default readline handler to `Tab`, ensuring PySH behaves the same across common Python builds.

## Testing and contribution notes
- Tests live under `tests/` and rely on helpers such as `tests._readline_patch.readline_stub` to isolate `readline`. Run the suite with `poetry run pytest tests` after `poetry install`, and refer to `tests/test_utils.py` and `tests/test_shell.py` for examples of how `PySHUtils` and `PySH` are exercised.
- Because PySH runs user code via `code.InteractiveConsole`, extra care is needed when introducing new built-in commands; prefer unit tests that run the `push` logic or spawn subprocesses through `shrun` to cover the translation layers before merging.

## Runtime expectations
- PySH adapts the current working directory for the prompt and command resolution, so built-in commands like `cd` update the console's state immediately before the next prompt.
- Inline shell expressions spawn subprocesses with pipes or capture code and integrate their output via `InlineExec`, enabling Python statements like `myvar = `ls`` (using backticks), while `$VAR` references objects already defined in the Python scope.
- Credentials, environment setup, and migration live outside the interpreter: `cmd_migrate` prompts to overwrite `~/.pyshrc`, writing the current `PATH` so future sessions keep shell-native variables.

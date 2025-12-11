import io
import os
import tempfile
import unittest
from unittest import mock

from tests._readline_patch import readline_stub

readline_stub.reset()

from pysh.utils import InlineExec, InlineVar, PySHUtils


class CmdCdTest(unittest.TestCase):
    def test_cd_changes_directory_when_target_exists(self):
        utils = PySHUtils([])
        original = os.getcwd()
        with tempfile.TemporaryDirectory() as tmpdir:
            try:
                utils.cmd_cd([tmpdir])
                self.assertEqual(os.getcwd(), tmpdir)
            finally:
                os.chdir(original)

    def test_cd_reports_error_for_missing_directory(self):
        utils = PySHUtils([])
        stream = io.StringIO()
        missing = os.path.join(os.getcwd(), "nope")

        with mock.patch("sys.stderr", stream):
            utils.cmd_cd([missing])

        self.assertIn("Not a directory", stream.getvalue())


class CmdMigrateTest(unittest.TestCase):
    def test_migrate_writes_pyshrc_when_confirmed(self):
        utils = PySHUtils([])
        with tempfile.TemporaryDirectory() as tmpdir:
            target = os.path.join(tmpdir, ".pyshrc")

            with mock.patch("pysh.utils.PYSHRC", target):
                with mock.patch("builtins.input", return_value="y"):
                    with mock.patch.dict(os.environ, {"PATH": "custom_path"}):
                        with mock.patch("builtins.print"):
                            utils.cmd_migrate([])

            with open(target, "r") as handle:
                content = handle.read()

        self.assertIn("custom_path", content)


class CmdHelpTest(unittest.TestCase):
    def test_help_lists_commands_when_no_arguments(self):
        utils = PySHUtils([])
        output = io.StringIO()

        with mock.patch("sys.stdout", output):
            utils.cmd_help([])

        text = output.getvalue()
        self.assertIn("For python help", text)
        self.assertIn("cd", text)

    def test_help_reports_unknown_command(self):
        utils = PySHUtils([])
        output = io.StringIO()

        with mock.patch("sys.stdout", output):
            utils.cmd_help(["missing"])

        self.assertIn("No such command", output.getvalue())


class ParseAndMakeTest(unittest.TestCase):
    def test_parse_and_make_expands_glob_and_handles_pipe(self):
        utils = PySHUtils([])
        result_processes = []

        def make_process(args, stdin, stdout):
            process = mock.Mock()
            process.stdout = f"pipe{len(result_processes)}"
            result_processes.append((list(args), stdin, stdout))
            return process

        with mock.patch("pysh.utils.glob.has_magic", lambda element: "*" in element):
            with mock.patch("pysh.utils.glob.glob", return_value=["match1", "match2"]):
                with mock.patch.object(PySHUtils, "makeProcess", side_effect=make_process):
                    final = utils.parseAndMake(["echo", "*", "|", "cat"])

        self.assertEqual(len(result_processes), 2)
        self.assertEqual(result_processes[0][0], ["echo", "match1", "match2"])
        self.assertEqual(result_processes[1][0], ["cat"])
        self.assertIsNotNone(final)

    def test_find_returns_command_from_path_or_with_dot(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            filename = os.path.join(tmpdir, "cmd")
            open(filename, "w").close()
            utils = PySHUtils([tmpdir])
            self.assertEqual(utils.find("./script"), "./script")
            self.assertEqual(utils.find("cmd"), filename)

    def test_make_process_raises_on_missing_command(self):
        utils = PySHUtils([])

        with self.assertRaises(Exception) as context:
            utils.makeProcess(["missing"], None, None)

        self.assertIn("Command not found", str(context.exception))


class ShrunTest(unittest.TestCase):
    def test_shrun_logs_os_error(self):
        utils = PySHUtils([])
        error = OSError("boom")
        process = mock.Mock()
        process.wait.side_effect = error

        with mock.patch.object(PySHUtils, "parseAndMake", return_value=process):
            with mock.patch("builtins.print") as printer:
                utils.shrun(["cmd"])

        printer.assert_called_once_with(error)


class InlineHelpersTest(unittest.TestCase):
    def test_inline_exec_str_and_bytes(self):
        stdout_one = io.BytesIO(b"one")
        process_one = mock.Mock()
        process_one.stdout = stdout_one

        exec_one = InlineExec(process_one)
        self.assertEqual(str(exec_one), "one")

        stdout_two = io.BytesIO(b"bytes")
        process_two = mock.Mock()
        process_two.stdout = stdout_two
        self.assertEqual(bytes(InlineExec(process_two)), b"bytes")

    def test_inline_exec_iterates_over_lines(self):
        stdout = io.BytesIO(b"first\nsecond\n")
        process = mock.Mock()
        process.stdout = stdout

        exec_obj = InlineExec(process)
        self.assertEqual(list(exec_obj.__iter__()), ["first", "second"])

    def test_inline_method_wraps_process(self):
        utils = PySHUtils([])
        process = mock.Mock()

        with mock.patch.object(PySHUtils, "parseAndMake", return_value=process):
            inline = utils.inline(["cmd"])

        self.assertIsInstance(inline, InlineExec)
        self.assertIs(inline.process, process)

    def test_inline_var_repr(self):
        var = InlineVar("VALUE")
        self.assertEqual(repr(var), "VALUE")

import os
import unittest
from unittest import mock

from tests._readline_patch import readline_stub

readline_stub.reset()

from pysh.shell import PySH
from pysh.utils import InlineVar


class PySHTestCase(unittest.TestCase):
    def setUp(self):
        self.user_patcher = mock.patch("pysh.shell.getpass.getuser",
                                       return_value="tester")
        self.host_patcher = mock.patch("pysh.shell.socket.gethostname",
                                       return_value="host.local")
        self.user_patcher.start()
        self.host_patcher.start()
        self.addCleanup(self.user_patcher.stop)
        self.addCleanup(self.host_patcher.stop)
        self.shell = PySH("")


class InlineHandlingTest(PySHTestCase):
    def test_inline_vars_replaces_named_arguments(self):
        shell = self.shell
        result = shell.inlineVars(["echo", "$HOME"])

        self.assertIsInstance(result[1], InlineVar)
        self.assertEqual(repr(result[1]), "HOME")

    def test_inline_vars_raises_for_empty_name(self):
        with self.assertRaises(SyntaxError):
            self.shell.inlineVars(["$"])

    def test_process_inline_shell_embeds_inline_invocation(self):
        output = self.shell.processInlineShell("before `cmd $VALUE` after")

        self.assertIn("(__pysh__.inline(", output)
        self.assertIn("VALUE", output)
        self.assertIn("before", output)
        self.assertIn("after", output)

    def test_process_command_builds_command_call(self):
        output = self.shell.processCommand(["cmd", "$USER"])

        self.assertIn("(__pysh__.cmd_cmd", output)
        self.assertIn("USER", output)

    def test_translate_wraps_with_shrun(self):
        output = self.shell.translate(["ls", "$PATH"])

        self.assertIn("__pysh__.shrun", output)
        self.assertIn("PATH", output)


class PromptFormattingTest(PySHTestCase):
    def test_format_cwd_returns_tilde_for_home(self):
        home = "C:\\Users\\tester"

        with mock.patch("pysh.shell.os.getcwd", return_value=home):
            with mock.patch("pysh.shell.os.path.expanduser",
                            return_value=home):
                self.assertEqual(self.shell.format_cwd(), "~")

    def test_format_cwd_returns_relative_path_for_subdirectories(self):
        home = "C:\\Users\\tester"
        cwd = os.path.join(home, "projects")

        with mock.patch("pysh.shell.os.getcwd", return_value=cwd):
            with mock.patch("pysh.shell.os.path.expanduser",
                            return_value=home):
                self.assertEqual(self.shell.format_cwd(), "~/projects")

    def test_format_cwd_returns_fixed_path_when_outside_home(self):
        home = "C:\\Users\\tester"
        cwd = "D:\\toolchain"

        with mock.patch("pysh.shell.os.getcwd", return_value=cwd):
            with mock.patch("pysh.shell.os.path.expanduser",
                            return_value=home):
                self.assertEqual(self.shell.format_cwd(), "D:/toolchain")

    def test_build_prompt_includes_user_host_and_path(self):
        with mock.patch.object(PySH, "format_cwd", return_value="~/project"):
            prompt = self.shell.build_prompt()

        self.assertIn("tester@host", prompt)
        self.assertIn("~/project", prompt)
        self.assertTrue(prompt.endswith("$ "))

    def test_build_secondary_prompt_returns_arrow(self):
        result = self.shell.build_secondary_prompt()
        self.assertIn("> ", result)

import os
import tempfile
import unittest

from tests._readline_patch import readline_stub

readline_stub.reset()

from pysh.completion import Completer


class CompleterSearchTest(unittest.TestCase):
    def test_search_directory_includes_directory_and_entries(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            subdir = os.path.join(tmpdir, "subdir")
            os.mkdir(subdir)
            fname = os.path.join(tmpdir, "file.txt")
            with open(fname, "w"):
                pass

            completer = Completer()
            results = completer.search(tmpdir)

            self.assertIn(tmpdir + os.path.sep, results)
            self.assertIn(os.path.join(tmpdir, "subdir") + os.path.sep, results)
            self.assertIn(os.path.join(tmpdir, "file.txt"), results)

    def test_search_prefix_matches_files_and_directories(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            os.mkdir(os.path.join(tmpdir, "match_dir"))
            with open(os.path.join(tmpdir, "matched_file"), "w"):
                pass
            with open(os.path.join(tmpdir, "other"), "w"):
                pass

            completer = Completer()
            prefix = os.path.join(tmpdir, "match")
            results = completer.search(prefix)

            self.assertIn(os.path.join(tmpdir, "match_dir") + os.path.sep, results)
            self.assertIn(os.path.join(tmpdir, "matched_file"), results)
            self.assertNotIn(os.path.join(tmpdir, "other"), results)


class CompleterCompleteTest(unittest.TestCase):
    def test_complete_caches_search_results_until_reset(self):
        completer = Completer()
        mock_search = unittest.mock.MagicMock(side_effect=[["one", "two"], ["three"]])
        completer.search = mock_search

        self.assertEqual(completer.complete("cmd", 0), "one")
        self.assertEqual(mock_search.call_count, 1)
        self.assertEqual(completer.complete("cmd", 1), "two")
        self.assertEqual(mock_search.call_count, 1)
        self.assertEqual(completer.complete("cmd", 0), "three")
        self.assertEqual(mock_search.call_count, 2)


class CompleterInstallTest(unittest.TestCase):
    def setUp(self):
        readline_stub.reset()

    def test_install_with_libedit_binds_libedit_sequence(self):
        readline_stub.reset(doc="readline with libedit")
        completer = Completer()
        completer.install()

        self.assertIsNotNone(readline_stub._completer)
        self.assertIs(readline_stub._completer.__self__, completer)
        self.assertEqual(readline_stub._completer.__func__.__name__, "complete")
        self.assertIn("libedit", readline_stub.__doc__)
        self.assertEqual(readline_stub.last_bindings[-1], "bind '\\t' rl_complete")
        self.assertNotIn("/", readline_stub._delims)

    def test_install_without_libedit_uses_tab_binding(self):
        readline_stub.reset(doc="plain readline")
        completer = Completer()
        completer.install()

        self.assertEqual(readline_stub.last_bindings[-1], "tab: complete")

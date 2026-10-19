import os
import unittest
from unittest import mock

from ebllm import __version__, update
from ebllm.cli import main


class TestUpdate(unittest.TestCase):
    local = dict(version="2.1.0", revision="aaaa111", created="2026-10-19T02:00:00Z", in_image=True)

    def test_higher_release_is_newer(self):
        new, why = update.newer(self.local, dict(tags=["2.1.0", "2.2.0", "latest"], revision="", created=""))
        self.assertTrue(new)
        self.assertIn("2.2.0", why)

    def test_same_release_later_build_of_other_commit_is_newer(self):
        rem = dict(tags=["2.1.0", "latest"], revision="bbbb222", created="2026-10-19T03:00:00Z")
        self.assertTrue(update.newer(self.local, rem)[0])

    def test_own_build_or_older_build_is_not_newer(self):
        same = dict(tags=["2.1.0", "latest"], revision="aaaa111", created="2026-10-19T02:00:00Z")
        older = dict(tags=["2.0.1", "latest"], revision="cccc333", created="2026-10-18T02:00:00Z")
        self.assertFalse(update.newer(self.local, same)[0])
        self.assertFalse(update.newer(self.local, older)[0])

    def test_without_build_times_only_versions_count(self):
        loc = dict(self.local, created="")
        rem = dict(tags=["2.1.0", "latest"], revision="bbbb222", created="2026-10-19T03:00:00Z")
        self.assertFalse(update.newer(loc, rem)[0])

    def test_notice_is_silent_offline_and_when_disabled(self):
        with mock.patch.object(update, "remote_state", side_effect=OSError("offline")):
            self.assertIsNone(update.notice())
        with mock.patch.dict(os.environ, {"ANAXIA_NO_UPDATE_CHECK": "1"}):
            self.assertIsNone(update.notice())

    def test_cli_names(self):
        with self.assertRaises(SystemExit), mock.patch("sys.stdout") as out:
            main(["--version"])
        printed = "".join(c.args[0] for c in out.write.call_args_list)
        self.assertEqual(printed.strip(), f"anaxia {__version__}")

    def test_anaxia_module_alias(self):
        import anaxia
        self.assertEqual(anaxia.__version__, __version__)


if __name__ == "__main__":
    unittest.main()

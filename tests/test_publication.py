"""Release recovery verifies published bytes, not just an upload's return status."""

import hashlib
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from tools.check_published import install_from_index, verify_published


class PublicationTests(unittest.TestCase):
    def test_recovery_rejects_substitution_and_unexpected_download_hosts(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            names = ["terminal_cells-0.1.1.tar.gz", "terminal_cells-0.1.1-py3-none-any.whl"]
            files = {}
            for name in names:
                (root / name).write_bytes(name.encode())
                files[name] = hashlib.sha256(name.encode()).hexdigest()
            manifest = dict(version="0.1.1", commit="abc", files=files)
            records = [
                dict(
                    filename=name,
                    digests={"sha256": files[name]},
                    url=f"https://files.pythonhosted.org/{name}",
                )
                for name in names
            ]

            def fetch(url, **kwargs):
                if url.endswith("/json"):
                    return io.BytesIO(json.dumps({"urls": records}).encode())
                return io.BytesIO(url.rsplit("/", 1)[1].encode())

            with patch("tools.check_published.urlopen", side_effect=fetch):
                verify_published(root, manifest, "abc", "0.1.1")
                records[0]["url"] = "https://attacker.invalid/file"
                with self.assertRaisesRegex(ValueError, "host"):
                    verify_published(root, manifest, "abc", "0.1.1")
                records[0]["url"] = "https://files.pythonhosted.org/tampered"
                with self.assertRaisesRegex(ValueError, "bytes"):
                    verify_published(root, manifest, "abc", "0.1.1")
                records[0]["digests"]["sha256"] = "0" * 64
                with self.assertRaisesRegex(ValueError, "files differ"):
                    verify_published(root, manifest, "abc", "0.1.1")

    def test_index_delay_retries_installation_and_remains_bounded(self):
        failure = subprocess.CalledProcessError(1, ["pip"])
        with (
            patch("tools.check_published.subprocess.run", side_effect=[failure, None]) as run,
            patch("tools.check_published.time.sleep") as sleep,
        ):
            install_from_index("python", "0.1.1", "https://pypi.org/simple/", Path("/tmp"))
            self.assertEqual(run.call_count, 2)
            sleep.assert_called_once_with(5)
        with (
            patch("tools.check_published.subprocess.run", side_effect=failure) as run,
            patch("tools.check_published.time.sleep"),
        ):
            with self.assertRaises(subprocess.CalledProcessError):
                install_from_index("python", "0.1.1", "https://pypi.org/simple/", Path("/tmp"))
            self.assertEqual(run.call_count, 6)


if __name__ == "__main__":
    unittest.main()

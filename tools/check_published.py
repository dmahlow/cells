#!/usr/bin/env python3
"""Verify published PyPI bytes and tolerate bounded index propagation delays."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
from urllib.parse import urlparse
from urllib.request import urlopen

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.release import verify_manifest  # noqa: E402


def verify_published(directory, manifest, commit, version):
    verify_manifest(directory, manifest, commit=commit, expected_version=version)
    # The version comes from a validated release manifest; constrain URL path syntax.
    import re

    if not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+(?:(?:a|b|rc)[0-9]+)?", version):
        raise ValueError("Invalid release version")
    with urlopen(f"https://pypi.org/pypi/terminal-cells/{version}/json", timeout=30) as response:
        records = json.load(response)["urls"]
    published = {record["filename"]: record["digests"]["sha256"] for record in records}
    if len(records) != len(published) or published != manifest["files"]:
        raise ValueError("PyPI files differ from the tested candidate")
    for record in records:
        url = urlparse(record["url"])
        if url.scheme != "https" or url.netloc != "files.pythonhosted.org":
            raise ValueError("Unexpected PyPI artifact host")
        with urlopen(record["url"], timeout=30) as response:
            digest = hashlib.sha256()
            size = 0
            while block := response.read(1024 * 1024):
                size += len(block)
                if size > 100 * 1024 * 1024:
                    raise ValueError("Unexpectedly large PyPI artifact")
                digest.update(block)
        if digest.hexdigest() != manifest["files"][record["filename"]]:
            raise ValueError("Downloaded PyPI bytes differ from the candidate")


def install_from_index(python, version, index, cwd):
    if index not in ("https://pypi.org/simple/", "https://test.pypi.org/simple/"):
        raise ValueError("Unexpected package index")
    for attempt in range(6):
        try:
            subprocess.run(
                [
                    str(python),
                    "-m",
                    "pip",
                    "install",
                    "--no-cache-dir",
                    "--no-deps",
                    "--only-binary=:all:",
                    "--index-url",
                    index,
                    f"terminal-cells=={version}",
                ],
                cwd=cwd,
                check=True,
            )
            return
        except subprocess.CalledProcessError:
            if attempt == 5:
                raise
            print("Waiting for package-index propagation before retrying installation", flush=True)
            time.sleep(5 * (attempt + 1))


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--dist", type=Path, default=Path("dist"))
    cli.add_argument("--manifest", type=Path, default=Path("release-manifest.json"))
    cli.add_argument("--commit", required=True)
    cli.add_argument("--version", required=True)
    args = cli.parse_args()
    verify_published(args.dist, json.loads(args.manifest.read_text()), args.commit, args.version)
    print("Published PyPI archives match the tested candidate byte for byte")


if __name__ == "__main__":
    main()

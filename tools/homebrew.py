#!/usr/bin/env python3
"""Generate a Homebrew tap formula from verified published release artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.release import verify_manifest  # noqa: E402


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--dist", type=Path, required=True)
    cli.add_argument("--manifest", type=Path, required=True)
    cli.add_argument("--output", type=Path, required=True)
    args = cli.parse_args()
    manifest = json.loads(args.manifest.read_text())
    verify_manifest(args.dist, manifest)
    archive = next(name for name in manifest["files"] if name.endswith(".tar.gz"))
    # Derive the version from the validated archive name, avoiding Ruby interpolation
    # from arbitrary manifest fields. setuptools uses the normalized distribution name.
    import re

    match = re.fullmatch(
        r"terminal_cells-([0-9]+\.[0-9]+\.[0-9]+(?:a[0-9]+|b[0-9]+|rc[0-9]+)?)\.tar\.gz", archive
    )
    if not match or match[1] != manifest["version"]:
        raise ValueError("Unexpected source archive version")
    version = match[1]
    formula = """class TerminalCells < Formula
  desc "Living microscope slide in your terminal"
  homepage "https://github.com/kborer/cells"
  url "https://github.com/kborer/cells/releases/download/vVERSION/ARCHIVE"
  sha256 "DIGEST"
  license "0BSD"

  depends_on "python@3.14"

  def install
    libexec.install "terminal_cells"
    (bin/"cells").write <<~PYTHON
      #!#{formula_opt_bin("python@3.14")}/python3.14
      import sys
      sys.path.insert(0, "#{libexec}")
      from terminal_cells.cli import main
      main()
    PYTHON
    chmod 0755, bin/"cells"
    man1.install "docs/cells.1"
  end

  test do
    assert_equal "cells #{version}", shell_output("#{bin}/cells --version").strip
    snapshot = shell_output("#{bin}/cells --snapshot --seed 42 --size 80x24")
    assert_equal 24, snapshot.lines.length
    assert snapshot.lines.all? { |line| line.chomp.length == 80 }
    refute_empty snapshot.strip
  end
end
"""
    for token, value in (
        ("VERSION", version),
        ("ARCHIVE", archive),
        ("DIGEST", manifest["files"][archive]),
    ):
        formula = formula.replace(token, value)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(formula)
    print(args.output)


if __name__ == "__main__":
    main()

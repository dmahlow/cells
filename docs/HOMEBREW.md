# Homebrew tap preparation

Homebrew packaging uses the published, checksummed source archive and Homebrew's
Python 3.14. There are no third-party runtime dependencies or downloaded Python
resources. The formula installs the package in its private prefix, a `cells`
launcher, and the manual page. Its functional test exercises installed snapshots.

After publishing a release, download its wheel and source archive into an otherwise
empty `dist/` directory, with `release-manifest.json` beside that directory. Run:

```sh
python3 tools/homebrew.py --dist dist --manifest release-manifest.json \
  --output /path/to/homebrew-cells/Formula/terminal-cells.rb
```

The generator verifies archive hashes and filenames before using the source hash
and version. It points at the immutable GitHub release asset. Review that formula
in the tap, then run on macOS or a Homebrew Linux installation:

```sh
brew tap kborer/cells /path/to/homebrew-cells
brew install --build-from-source kborer/cells/terminal-cells
brew test kborer/cells/terminal-cells
brew audit --strict kborer/cells/terminal-cells
```

A public `kborer/homebrew-cells` repository makes the installation command
`brew install kborer/cells/terminal-cells`. Publish it only after the formula's
installation and functional test pass. A tap is separate from acceptance into
Homebrew's core repository; bottles can be added later.

See Homebrew's [tap guide](https://docs.brew.sh/How-to-Create-and-Maintain-a-Tap)
and [language-specific formula guidance](https://docs.brew.sh/Language-Specific-Formulae).

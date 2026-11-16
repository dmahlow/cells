# Ubuntu packages

Debian-format packaging lives in `debian/`. CI builds the released upstream
0.1.0 source, verifies its SHA-256, and tests Ubuntu 24.04 and 26.04 separately.
It uses distro build tools, runs the application test suite, checks the result
with Lintian, then exercises installation, reinstallation, snapshot output,
manual-page placement, and removal. This does not establish native Windows
support or inclusion in Ubuntu's default repositories.

## Install from the PPA

The cells PPA is <https://launchpad.net/~bogobogosort/+archive/ubuntu/cells>.
Once Launchpad lists a published package for your Ubuntu release, install it with:

```sh
sudo add-apt-repository ppa:bogobogosort/cells
sudo apt update
sudo apt install terminal-cells
cells
```

The initial PPA versions are `0.1.0-1ppa1~24.04.1` for Ubuntu 24.04 (`noble`)
and `0.1.0-1ppa1~26.04.1` for Ubuntu 26.04 (`resolute`). The executable reports
upstream version `0.1.0`. The PPA is maintained separately from Ubuntu's official
repositories. Alternatively, download the matching `.deb` and checksums from
[the GitHub release](https://github.com/kborer/cells/releases/tag/v0.1.0) and run
`sudo apt install ./terminal-cells_..._all.deb` with its actual filename.

Maintainers can rerun the **Ubuntu packages** workflow with the PPA's repository
signing fingerprint to verify real apt installations in clean containers. Use
the repository key shown on Launchpad, rather than an uploader's personal key.
The check validates that fingerprint before configuring a scoped apt source,
then checks the exact published version, snapshot, manual page, and removal.

## Build locally

Use a clean target Ubuntu VM/container and distro dependencies:

```sh
sudo apt-get update
sudo apt-get install build-essential debhelper dh-python pybuild-plugin-pyproject \
  python3-all python3-setuptools python3-wheel python3-hypothesis lintian
series=$(. /etc/os-release; printf '%s' "$VERSION_CODENAME")
python3 tools/release.py deb-source --output /tmp/cells-deb --series "$series"
cd /tmp/cells-deb/terminal-cells-*
dpkg-buildpackage --no-sign -sa
lintian --fail-on error ../*.changes
sudo apt install ../terminal-cells_*_all.deb
```

PR builds use tracked checkout files, so changes to the application are actually
exercised. Release candidates retain the tested Ubuntu build artifacts for later
GitHub publication. The distro-only quilt patch adapts license metadata for
Ubuntu 24.04's setuptools, preserving 0BSD and all runtime code.

## PPA source preparation

Check out the released tag and download its `release-manifest.json`, wheel, and
source archive. Keep the two Python archives together in an otherwise empty
folder. `release-policy.json` supplies PPA owner, series, and revision; change the
revision deliberately before another upload of the same upstream version.

```sh
python3 tools/release.py ppa-source \
  --output /tmp/cells-ppa-noble --series noble \
  --archive /path/to/dist/terminal_cells-VERSION.tar.gz \
  --manifest /path/to/release-manifest.json \
  --maintainer 'Your Public Name <verified-launchpad-email>' \
  --sign-key YOUR_FULL_SIGNING_FINGERPRINT
```

Repeat with `resolute` in a separate empty directory. The helper checks the
archive manifest, prepares a clean source tree, sets distro-specific versions,
and optionally runs local `debsign`. Install `devscripts` and `dput` locally for
signing/upload. It does not upload automatically. Review the generated source,
then run `dput ppa:bogobogosort/cells ..._source.changes`. Upload source packages,
not `.deb` binaries; CI artifacts are unsigned until you sign them.

Wait for Launchpad's builds and publication, then dispatch **Ubuntu packages**
with its repository signing fingerprint to test apt installation in clean target
containers. Never bypass apt signature checking while waiting for key generation.
The initial 0.1.0 release predates generated manifests; its manually verified
source hash is recorded in the GitHub release's checksum file.

See the official [PPA upload guide](https://ubuntu.com/docs/launchpad/user/how-to/packaging/ppa-package-upload/)
and [Debian Python policy](https://www.debian.org/doc/packaging-manuals/python-policy/).

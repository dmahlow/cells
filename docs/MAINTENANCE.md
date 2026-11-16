# Maintenance and recovery

## Routine checks

Review Dependabot security fixes promptly and ordinary dependency updates weekly.
The Security workflow runs Python/Actions CodeQL, dependency review on PRs,
actionlint, and a vulnerability audit of development/build dependencies. Resolve
or document a finding based on its actual exploitability; do not hide failures
through blanket exclusions. Dependabot never merges or publishes automatically.

Nightly Endurance jobs run extended Hypothesis sequences and one simulated hour
per scene. Download their JSON reports to compare population history, allocation
retention, and early/late update latency. Limits are deliberately generous to
avoid treating shared-runner noise as a product regression. Failures still need
investigation. Seeded reproduction commands are in the logs. Coverage is reported
in CI and the Ubuntu Python 3.14 `.coverage` artifact; use `coverage html` locally
to locate missing branches. Coverage percentage is diagnostic, not a substitute
for assertions about behavior.

Require independent workflow/release review when a second maintainer joins.
CODEOWNERS only requests review; it does not provide independent review while
there is one owner. Account owners should use MFA/passkeys and retain account
recovery codes outside the repository. Current production approval deliberately
permits the sole maintainer to approve a run they started.

## Release checklist

1. Run Prepare release to generate a version/changelog patch. Review it in a PR;
   include user-facing notes and terminal smoke-test results. Merge with checks.
2. Tag the merged commit with its exact upstream version. Never move release tags.
3. Run Publish on that tag with target `testpypi`. This builds and tests Python
   archives and Ubuntu packages and produces a release manifest with source SHA,
   version, archive names, and hashes. Preserve that run's artifacts.
4. Run Publish on the same tag with target `pypi` and the successful candidate run
   ID. Review the production environment approval. Production downloads the same
   candidate archives; it does not rebuild them. It verifies the candidate run,
   commit, version, file set, and digests before uploading.
5. The workflow checks an actual installation from PyPI, assembles Python and
   Ubuntu assets/checksums/source bundles, adds GitHub provenance, uploads a draft,
   then publishes the complete immutable GitHub release. PyPI also emits its
   publish attestations. Confirm links and download checksums.
6. Prepare PPA source packages from the manifest and released source, review and
   sign locally, upload, wait for Launchpad builds, then run the live PPA apt check.
   The PPA's archive key is separate from your upload signing key.

Build artifacts expire under GitHub's retention policy. If a candidate has
expired, prepare a fresh candidate with a new package version when the previous
version has already been uploaded. Publishing filenames cannot be overwritten.
If publication partly succeeds, inspect PyPI and the draft release before any
retry; do not force-upload or assume a failed job means nothing was published.
If the immutable release is already public, ship corrections in a new release.

## Signing-key backup and recovery

Keep an encrypted backup of your OpenPGP private key and its revocation
certificate in secure offline storage, separate from the computer and repository.
Test recovery with GnuPG in an isolated temporary keyring. Keep the passphrase
and account recovery codes in your password manager. Never send a private key,
passphrase, or revocation certificate to GitHub, Launchpad, an issue, or chat.

Before the key expires, extend it locally and publish the updated public key to
the Ubuntu keyserver; confirm Launchpad recognizes it before uploading. If lost,
restore from the protected backup or register a replacement key and confirm it
through Launchpad. If compromised, stop uploads, revoke the old key deliberately,
publish the revocation, remove its Launchpad authority, register a replacement,
and review uploads made during the exposure. Revocation is irreversible; the
maintainer must perform that decision and credential replacement.

If a GitHub/PyPI account is compromised, revoke sessions/tokens, recover the
account, inspect workflow and publisher changes, and review releases and signed
provenance. OIDC eliminates a long-lived PyPI upload token, not account compromise.

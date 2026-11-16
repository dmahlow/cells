# Security policy

Report a suspected vulnerability through
[GitHub private vulnerability reporting](https://github.com/kborer/cells/security/advisories/new).
Use [issues](https://github.com/kborer/cells/issues) for ordinary simulation,
rendering, and installation bugs. Do not publish credentials or private keys.

Only the latest released version receives security fixes; 0.1.0 is the first
published release. Acknowledgment and fix timing depend on maintainer availability.
There is no guaranteed response-time commitment.

## Scope

The installed application runs locally, has no networking, reads no simulation
files from strangers, and has no third-party runtime Python dependencies.
Relevant boundaries include CLI validation, terminal input and cleanup, resource
usage during long runs, development archive validation, and the build/publishing
supply chain. Terminal-emulator vulnerabilities belong with the emulator vendor.

CI runs on hosted ephemeral runners with read-only default tokens. Pull-request
checks have no publishing credentials and never run through pull_request_target.
Actions are pinned to full commits. Production PyPI publishing uses short-lived
OIDC credentials, a matching version tag merged into protected main, a successful
TestPyPI candidate for the same commit, and explicit owner approval. The sole
maintainer can approve their own deployment; this is a deliberate approval step,
not independent two-person review. Private PPA signing keys stay outside GitHub.

See [the maintenance guide](docs/MAINTENANCE.md) for release and credential recovery.

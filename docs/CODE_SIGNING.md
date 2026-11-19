# Code signing policy

Free code signing provided by [SignPath.io](https://about.signpath.io), certificate by [SignPath Foundation](https://signpath.org)

Status: the application to SignPath Foundation is pending. Until it is approved, the Windows
installer (`Fontes-Setup-<version>.exe`) is unsigned and Windows SmartScreen warns before it
runs. The Mac installer is signed with an Apple Developer ID and notarised by Apple.

## What is signed

Only `Fontes-Setup-<version>.exe`, built from this repository by
[`.github/workflows/windows.yml`](../.github/workflows/windows.yml) on GitHub Actions when a
release is published. Nothing built outside that workflow is signed. Each signing request is
approved by hand.

## Team

- Committers and reviewers: [the repository's collaborators](https://github.com/ykarapazar/fontes/graphs/contributors).
  Changes from anyone else arrive as pull requests and are reviewed before they are merged.
- Approvers: [Yüce Karapazar](https://github.com/ykarapazar) (owner).

Everyone on the team uses multi-factor authentication for GitHub and SignPath.

## Privacy

Privacy policy: [PRIVACY.md](PRIVACY.md). In short: Fontes fetches legislation and case law
from official sources only when you ask a question, and once a day asks PyPI whether a newer
version exists (can be switched off). Usage counts are off unless you turn them on, and a bug
report is sent only after you see it and confirm.

## Removing it

Uninstall **Fontes** in Settings → Apps (Windows) or open **Fontes Installer** and choose
**Remove** (Mac). See [INSTALL.md](INSTALL.md#backups-reruns-and-removing).

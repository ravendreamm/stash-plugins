# Personal Stash plugins

This repository is intended for independently maintained Stash plugins. It contains an [offline decision prototype](stash-whisparr-prototype/README.md) and an [experimental preview-only renamer](plugins/stash-rename-preview/README.md); the latter has a deployment blocker and is not ready to install.

This repository is not yet a Stash plugin source: it has no hosted package index or installable plugin archives. Do not add the GitHub repository page as a Stash source. Stash expects a URL returning a YAML package index, as described in the [Stash plugin documentation](https://docs.stashapp.cc/in-app-manual/plugins/#source-urls). Publishing a usable source will require a tested plugin, packaged release and hosted index.

Keep production credentials, populated configuration containing secrets, application databases and media files out of the repository. Document compatibility, configuration, tests and deployment instructions when an actual plugin is ready.

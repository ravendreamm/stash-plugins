# Stash Rename Preview — experimental

This preview-only plugin reacts to `Scene.Update.Post` and, when its **Enable previews** setting is on, logs a proposed path for each file in the updated scene. It makes no GraphQL mutations and cannot rename, move, copy, or delete files. It does not contact Whisparr. This code is not yet verified against a running Stash instance and is not ready to install.

**Deployment blocker:** upstream [Stash issue #7293](https://github.com/stashapp/stash/issues/7293) reports that `configuration { plugins }` requests can deadlock Stash v0.31.1 when configuration writes occur concurrently. This plugin currently uses that query to read UI settings. The issue's applicability to the installed build must be resolved before live deployment; do not install or enable it yet.

Preview runs on any scene update, including bulk updates if Stash emits individual hooks. To review one item, edit and save one scene. The plugin writes source and proposed paths to Stash logs; these may include private library details. Unset `enabled` is treated as off. A `movie` tag (whole name, case-insensitive) selects `/data/movies`; other scenes use `/data/scenes`. These fixed roots reflect the documented homelab setup and must be generalized before use elsewhere.

Templates use `$title$`, `$studio_name$`, `$studio_network$`, `$date$`, `$year$` and `$stash_id$`; `{...}` marks optional sections. Values not fetched, including performer, quality and release group, are not populated. The parent studio name is provisional, not a verified Whisparr network mapping. Defaults are `$title$` for both folder and filename; the extension is appended automatically. Existing destinations and sidecars are not checked. Naming is not Whisparr compatible by assertion.

Requires Python 3 and `stashapi` in the Stash runtime. Tests: from this directory run `python3 -B -m unittest -v`.

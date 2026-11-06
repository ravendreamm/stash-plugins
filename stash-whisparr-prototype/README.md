# Offline Stash/Whisparr decision prototype

This local prototype accepts synthetic JSON on standard input and prints a decision. It has no network, filesystem move, plugin, API or persistence functionality. It does not generate filenames or claim a Whisparr match. It is not deployable.

The whole-name, case-insensitive `movie` tag rule (ignoring surrounding whitespace) is a provisional implementation choice. Movie handoff is deliberately unresolved; a scene with one StashDB ID is only a candidate for later checks. No source-path validation, eligibility verification, collision detection, move, retry or import is implemented.

`rename_preview.py` adds an offline destination renderer inspired by [Rename File on Update](https://github.com/stash-of-awesomeness/stash-plugins/tree/main/plugins/rename-file-on-update). It accepts `$token$` fields and independent `{...}` optional sections. It removes unsafe characters from metadata in directory components and filenames, rejects missing required fields and traversal, and preserves the original extension. Filename templates describe the stem only. It does not implement the upstream syntax completely or reproduce Whisparr's formatting rules, and it cannot check collisions or related files. No upstream code was copied.

Supported tokens are `title`, `studio_name`, `studio_network`, `date`, `year`, `performers_female`, `quality`, `stash_id`, and `release_group`. The caller must supply values; mapping and fallback rules remain undecided. In particular, the renderer does not derive Whisparr's CleanTitle or quality semantics.

From this directory, run `python -m unittest -v`. For an example, pipe `{"item":{"organized":true,"tags":[],"stashdb_ids":[]},"handoff_enabled":true}` to `python planner.py`.

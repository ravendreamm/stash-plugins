# Offline Stash/Whisparr decision prototype

This local prototype accepts synthetic JSON on standard input and prints a decision. It has no network, filesystem move, plugin, API or persistence functionality. It does not generate filenames or claim a Whisparr match. It is not deployable.

The whole-name, case-insensitive `movie` tag rule (ignoring surrounding whitespace) is a provisional implementation choice. Movie handoff is deliberately unresolved; a scene with one StashDB ID is only a candidate for later checks. No source-path validation, eligibility verification, collision detection, move, retry or import is implemented.

From this directory, run `python -m unittest -v`. For an example, pipe `{"item":{"organized":true,"tags":[],"stashdb_ids":[]},"handoff_enabled":true}` to `python planner.py`.

"""Stash scene-update preview only; no mutations, shell commands, or moves."""

import json
from pathlib import PurePosixPath
import sys

from rename_preview import preview

PLUGIN_ID = "stash-rename-preview"
SCENE_QUERY = """query PreviewScene($id: ID!) {
  findScene(id: $id) {
    id title date organized
    tags { name }
    studio { name parent_studio { name } }
    files { id path }
    stash_ids { endpoint stash_id }
  }
}"""
CONFIG_QUERY = "query PreviewConfiguration { configuration { plugins } }"


def preview_scene(scene, settings):
    """Build per-file previews from a single retrieved scene; perform no I/O."""
    tags = scene.get("tags") or []
    kind = "movie" if any((tag.get("name") or "").strip().casefold() == "movie" for tag in tags) else "scene"
    studio = scene.get("studio") or {}
    parent = studio.get("parent_studio") or {}
    date = scene.get("date") or ""
    ids = [entry.get("stash_id") for entry in scene.get("stash_ids") or []
           if (entry.get("endpoint") or "").rstrip("/").casefold() in
           ("https://stashdb.org", "https://stashdb.org/graphql") and entry.get("stash_id")]
    fields = {"title": scene.get("title") or "", "studio_name": studio.get("name") or "",
              "studio_network": parent.get("name") or "", "date": date,
              "year": date[:4] if len(date) >= 4 else "",
              "stash_id": ids[0] if len(set(ids)) == 1 else ""}
    prefix = "movie" if kind == "movie" else "scene"
    directory = settings.get(prefix + "Directory") or "$title$"
    filename = settings.get(prefix + "Filename") or "$title$"
    root = "/data/movies" if kind == "movie" else "/data/scenes"
    results = []
    for file in scene.get("files") or []:
        source = file.get("path") or ""
        try:
            if not source.startswith("/"):
                raise ValueError("Source path must be absolute")
            destination = preview(root, directory, filename, fields, PurePosixPath(source).suffix)
            results.append((source, destination, None))
        except ValueError as exc:
            results.append((source, None, str(exc)))
    return kind, results


def run(payload, stash, logger):
    hook = (payload.get("args") or {}).get("hookContext") or {}
    if hook.get("type") != "Scene.Update.Post" or not hook.get("id"):
        return
    config = stash.call_GQL(CONFIG_QUERY)
    settings = ((config.get("configuration") or {}).get("plugins") or {}).get(PLUGIN_ID) or {}
    if settings.get("enabled") is not True:
        return
    scene = stash.call_GQL(SCENE_QUERY, {"id": str(hook["id"])}).get("findScene")
    if not scene:
        logger.warning("Preview skipped: scene no longer exists.")
        return
    kind, results = preview_scene(scene, settings)
    if not results:
        logger.warning("Preview skipped: scene has no files.")
    for source, destination, error in results:
        if error:
            logger.warning("Preview needs review: " + error)
        else:
            logger.info("Preview (" + kind + "): " + source + " -> " + destination)


def main():
    from stashapi import log
    from stashapi.stashapp import StashInterface

    try:
        payload = json.load(sys.stdin)
        run(payload, StashInterface(payload["server_connection"]), log)
        print(json.dumps({"output": "preview completed"}))
    except Exception:
        # Avoid logging server connection details or arbitrary API responses.
        log.error("Preview failed; check plugin configuration and compatibility.")
        print(json.dumps({"error": "preview failed"}))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

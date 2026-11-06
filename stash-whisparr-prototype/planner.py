"""Offline decision prototype. It never connects to services or moves files."""

import json
import sys


def plan(item, handoff_enabled):
    """Plan classification and handoff eligibility from synthetic input."""
    if not isinstance(item, dict) or not isinstance(handoff_enabled, bool):
        raise ValueError("Expected an item object and a boolean handoff toggle")
    tags = item.get("tags")
    if not isinstance(tags, list) or any(not isinstance(tag, str) for tag in tags):
        raise ValueError("tags must be a list of strings")
    organized = item.get("organized")
    if not isinstance(organized, bool):
        raise ValueError("organized must be a boolean")
    # Provisional: whole tag name only; no inherited tags or aliases.
    kind = "movie" if any(tag.strip().casefold() == "movie" for tag in tags) else "scene"
    result = {"kind": kind, "library": f"/data/{kind}s", "action": "none"}
    if not organized:
        result["reason"] = "not_organized"
    elif not handoff_enabled:
        result.update(action="organize", reason="handoff_disabled")
    elif kind == "movie":
        # Movie identifiers and their provider mapping have not been verified.
        result.update(action="organize", reason="movie_handoff_unverified")
    else:
        ids = item.get("stashdb_ids", [])
        if not isinstance(ids, list) or any(not isinstance(value, str) or not value.strip() for value in ids):
            raise ValueError("stashdb_ids must be a list of nonempty strings")
        if not ids:
            result.update(action="organize", reason="no_stashdb_id")
        elif len(set(ids)) != 1:
            result.update(action="organize", reason="ambiguous_stashdb_ids")
        else:
            result.update(action="organize_then_check_handoff", reason="candidate_only")
    return result


def main():
    try:
        payload = json.load(sys.stdin)
        if not isinstance(payload, dict):
            raise ValueError("Input must be an object")
        result = plan(payload.get("item"), payload.get("handoff_enabled"))
    except (ValueError, TypeError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

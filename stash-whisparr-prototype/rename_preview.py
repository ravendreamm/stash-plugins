"""Preview-only template renderer. No file, network, or application access."""

from pathlib import PurePosixPath
import re

TOKEN = re.compile(r"\$([a-z][a-z0-9_]*)\$")
OPTIONAL = re.compile(r"\{([^{}]*)\}")
UNSAFE = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
FIELDS = frozenset({"title", "studio_name", "studio_network", "date", "year",
                    "performers_female", "quality", "stash_id", "release_group"})


def _clean(value):
    if not isinstance(value, str):
        raise ValueError("Template values must be strings")
    return re.sub(r"\s+", " ", UNSAFE.sub("", value)).strip().rstrip(".")


def _render(template, fields):
    if not isinstance(template, str) or not template:
        raise ValueError("Template must be a nonempty string")
    tokens = set(TOKEN.findall(template))
    unknown = tokens - FIELDS
    if unknown:
        raise ValueError("Unknown template tokens: " + ", ".join(sorted(unknown)))
    values = {key: _clean(fields.get(key, "")) for key in tokens}

    def optional(match):
        part = match.group(1)
        part_tokens = TOKEN.findall(part)
        if not part_tokens:
            raise ValueError("Optional section must contain a token")
        return part if all(values[token] for token in part_tokens) else ""

    template = OPTIONAL.sub(optional, template)
    if "{" in template or "}" in template:
        raise ValueError("Invalid or nested optional section")
    remaining = TOKEN.findall(template)
    missing = sorted({token for token in remaining if not values[token]})
    if missing:
        raise ValueError("Missing required metadata: " + ", ".join(missing))
    output = TOKEN.sub(lambda match: values[match.group(1)], template)
    if "$" in output:
        raise ValueError("Invalid template token")
    return output


def preview(root, directory_template, filename_template, fields, extension):
    """Return a proposed destination; do not check the filesystem or move files."""
    if not isinstance(fields, dict):
        raise ValueError("Metadata must be an object")
    if not isinstance(root, str) or not root.startswith("/"):
        raise ValueError("Root must be an absolute POSIX path")
    root_path = PurePosixPath(root)
    if ".." in root_path.parts:
        raise ValueError("Root cannot contain parent traversal")
    if not isinstance(extension, str) or not re.fullmatch(r"\.[A-Za-z0-9]{1,10}", extension):
        raise ValueError("Expected the original media extension, such as .mp4")
    directory = _render(directory_template, fields)
    path = PurePosixPath(directory)
    if path.is_absolute() or not path.parts or any(part in (".", "..") for part in directory.split("/")):
        raise ValueError("Directory must be a relative path without traversal")
    # Reject unsafe characters in template literals as well as metadata values.
    if any(not part or _clean(part) != part for part in directory.split("/")):
        raise ValueError("Directory contains unsafe or empty components")
    filename = _render(filename_template, fields)
    if not filename or filename in (".", "..") or _clean(filename) != filename:
        raise ValueError("Filename contains unsafe characters or is empty")
    return str(root_path / path / (filename + extension))

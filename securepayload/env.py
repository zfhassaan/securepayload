"""Load environment variables from a .env file."""

from __future__ import annotations

import os
from pathlib import Path


def find_env_file(start: Path | None = None) -> Path | None:
    """Walk upward from ``start`` (default: cwd) looking for a ``.env`` file."""
    current = (start or Path.cwd()).resolve()
    for directory in (current, *current.parents):
        candidate = directory / ".env"
        if candidate.is_file():
            return candidate
    return None


def load_env(env_file: Path | str | None = None) -> bool:
    """
    Load variables from a ``.env`` file into ``os.environ``.

    Uses python-dotenv when installed; otherwise parses the file directly.
    When ``env_file`` is omitted, searches upward from the current working directory.
    Returns ``True`` if a file was found and loaded.
    """
    if env_file is not None:
        path = Path(env_file)
    else:
        found = find_env_file()
        if found is None:
            return False
        path = found

    if not path.is_file():
        return False

    try:
        from dotenv import load_dotenv

        load_dotenv(path)
        return True
    except ImportError:
        pass

    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, _, value = stripped.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            os.environ.setdefault(key, value)

    return True

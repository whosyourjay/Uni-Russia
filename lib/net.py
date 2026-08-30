"""Mirror a source document once and read it from disk afterwards."""

import os
import urllib.request

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; contest-research/1.0)"}


def get(url, timeout=60):
    """The bytes at a URL, with the headers the Russian hosts expect."""
    request = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read()


def mirror(url, path, force=False):
    """Save a source under `path` unless it is already there; return True if
    this call downloaded it."""
    if os.path.exists(path) and not force:
        return False
    os.makedirs(os.path.dirname(path), exist_ok=True)
    body = get(url)
    with open(path, "wb") as f:
        f.write(body)
    return True


def text(path):
    """A mirrored HTML page as text."""
    with open(path, encoding="utf-8") as f:
        return f.read()

"""
Auto-Updater Module
====================
How to Work:
    Test: latest, url = check_updates("0.9.0")
    Should return current v1.0.0 as newer.
    Handles offline gracefully (no crash).

Checks GitHub Releases for a newer version than the one currently
installed, using semantic versioning comparison.
"""

import requests
from packaging import version

CURRENT = "1.0.0"


def check_updates(current=CURRENT,
                  repo="Adityawaghma/ai-data-analytics-assistant"):
    """
    Check GitHub Releases for a version newer than `current`.

    Args:
        current: the currently installed version string (e.g. "1.0.0").
        repo: GitHub "owner/repo" to check releases for.

    Returns:
        (latest_version, download_url) if a newer version is available.
        (None, None) if already up to date, or if the check fails for
        any reason (offline, rate-limited, malformed response, etc.) —
        this function never raises.
    """
    try:
        r = requests.get(
            f"https://api.github.com/repos/{repo}/releases/latest",
            timeout=5,
        )
        r.raise_for_status()
        latest = r.json()["tag_name"].lstrip("v")

        if version.parse(latest) > version.parse(current):
            return latest, r.json()["html_url"]
    except Exception:
        pass

    return None, None


def prompt_if_update_available(
        current=CURRENT, repo="Adityawaghma/ai-data-analytics-assistant"):
    """
    Convenience wrapper: checks for updates and returns a user-facing
    message if one is available, or None if not (or check failed).
    """
    latest, url = check_updates(current, repo)
    if latest:
        return f"A new version (v{latest}) is available: {url}"
    return None


if __name__ == "__main__":
    latest, url = check_updates("0.9.0")
    print(f"latest={latest!r}, url={url!r}")
    print("Expected: current v1.0.0 reported as newer than 0.9.0")

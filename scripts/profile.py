"""Shared identity and profile copy used by every generated artifact."""

import os

USERNAME = os.environ.get("GH_PROFILE_USER", "Code-with-areeb")
HANDLE = os.environ.get("GH_PROFILE_HANDLE", USERNAME)
PROMPT = f"{HANDLE}@github"

DISPLAY_NAME = "Areeb"
ROLE = "Full-Stack Developer"
LOCATION = "Pakistan"

NOW = "Building polished full-stack experiences"
PREV = "Projects, experiments, and steady learning"
STACK = "React · Node.js · Python · JavaScript"
HIGHLIGHTS = [
    "React and Node.js apps, from interface to API",
    "Python automation and practical developer tools",
    "Clean UX, useful features, and continuous learning",
]

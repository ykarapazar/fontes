import os

# Tests never ask PyPI for updates (test_update_check.py switches it back on with a fake).
os.environ.setdefault("FONTES_NO_UPDATE_CHECK", "1")
# Usage counts stay off and nothing can reach the real relay from a test.
os.environ.pop("FONTES_STATS", None)
os.environ["FONTES_RELAY"] = "http://127.0.0.1:9"
# User-facing text in English whatever the machine's language (tests compare English strings).
os.environ["FONTES_LANG"] = "en"

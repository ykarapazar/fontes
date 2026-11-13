"""Bug reports: built locally, shown to the user, sent only after they confirm.

A report holds the Fontes version, the OS family, and the last failed tool call's
jurisdiction, tool name and error message (with that call's search text and ids cut out),
plus a note only if the user writes one. Sent to <relay>/v1/bug, a private inbox.

Two ways in, both with a real confirmation step:
- `fontes report-bug [--note TEXT]` in a terminal: prints the report, asks y/N.
- the `report_bug` MCP tool: asks the user in a dialog from their app (MCP elicitation).
  If the app cannot show that dialog, nothing is sent and the user gets the text and the
  two ways to send it themselves.

The last failure is kept in memory and in <cache dir>/last-error.json (overwritten each time,
never sent by itself) so the terminal command can report it.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import re
import time
from pathlib import Path
from urllib.parse import quote, quote_plus

import httpx
from pydantic import BaseModel, Field

from . import stats, update_check
from .i18n import t, yes

ISSUES_URL = "https://github.com/ykarapazar/fontes/issues"
TIMEOUT = 10.0
MAX_ERROR = 500
MAX_NOTE = 2000
_last: dict | None = None


def last_error_file() -> Path:
    return update_check.cache_file().parent / "last-error.json"


def redact(text: str, secrets) -> str:
    """Cut the call's own inputs (search text, ids, provision labels, as typed or URL-encoded)
    and every URL query string out of an error message."""
    forms = {f for s in secrets if isinstance(s, str) and len(s.strip()) >= 3
             for f in (s, s.strip(), quote(s.strip()), quote_plus(s.strip()))}
    for f in sorted(forms, key=len, reverse=True):
        text = text.replace(f, "[removed]")
    return re.sub(r"(https?://[^\s?'\"]*)\?[^\s'\"]*", r"\1?[removed]", text)[:MAX_ERROR]


def remember(jurisdiction: str, tool: str, error: str, secrets=()) -> None:
    """Note the latest failed call. Never raises."""
    global _last
    _last = {"jurisdiction": jurisdiction, "tool": tool, "error": redact(error, secrets),
             "time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    try:
        f = last_error_file()
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(json.dumps(_last), encoding="utf-8")
    except OSError:
        pass


def last_error() -> dict:
    if _last:
        return _last
    try:
        d = json.loads(last_error_file().read_text(encoding="utf-8"))
        return d if isinstance(d, dict) else {}
    except (OSError, ValueError):
        return {}


def build(note: str = "", last: dict | None = None) -> dict:
    """The exact JSON body that would be sent."""
    last = last_error() if last is None else last
    return {"schema": 1, "version": update_check.installed_version() or "dev",
            "os": stats.os_family(),
            "jurisdiction": str(last.get("jurisdiction", ""))[:10],
            "tool": str(last.get("tool", ""))[:40],
            "error": str(last.get("error", ""))[:MAX_ERROR],
            "note": (note or "").strip()[:MAX_NOTE]}


def render(report: dict) -> str:
    failed = (f"{report['tool']} ({report['jurisdiction']})" if report["tool"]
              else t("bug_none_recorded"))
    return "\n".join([
        t("bug_title"),
        t("bug_version", version=report["version"]),
        t("bug_os", os=report["os"]),
        t("bug_last_failed", call=failed),
        t("bug_error", error=report["error"] or "-"),
        t("bug_note", note=report["note"] or "-"),
    ])


def send(report: dict, post=httpx.post) -> str | None:
    """Post the report. None on success, else a short reason."""
    try:
        r = post(f"{stats.relay_url()}/v1/bug", json=report, timeout=TIMEOUT)
    except Exception as e:
        return t("bug_why_unreachable", error=type(e).__name__)
    return None if 200 <= r.status_code < 300 else t("bug_why_http", status=r.status_code)


def _not_sent(text: str, why: str) -> str:
    return f"{text}\n\n" + t("bug_not_sent_why", why=why, url=ISSUES_URL)


class Confirm(BaseModel):
    send: bool = Field(default=False, description=t("bug_ask_dialog"))


async def confirm_and_send(report: dict, elicit, post=httpx.post) -> str:
    """MCP path: the user, not the model, confirms in a dialog from their app."""
    if not (report["error"] or report["note"]):
        return t("bug_empty")
    text = render(report)
    try:
        answer = await elicit(message=f"{text}\n\n" + t("bug_ask_dialog"),
                              schema=Confirm)
    except Exception:
        return _not_sent(text, t("bug_why_no_dialog"))
    if answer.action != "accept" or not getattr(answer.data, "send", False):
        return f"{text}\n\n" + t("bug_declined")
    if err := await asyncio.to_thread(send, report, post):
        return _not_sent(text, err)
    return f"{text}\n\n" + t("bug_sent")


def cli(argv: list[str], ask=input, post=httpx.post) -> int:
    """`fontes report-bug`: show the report, send only on an explicit yes."""
    p = argparse.ArgumentParser(prog="fontes report-bug",
                                description="Send a bug report to the Fontes developers, after you confirm.")
    p.add_argument("--note", default="", help="what went wrong, in your words (sent as written)")
    report = build(p.parse_args(argv).note)
    if not (report["error"] or report["note"]):
        print(t("bug_empty"))
        return 1
    text = render(report)
    print(text, end="\n\n")
    try:
        ok = yes(ask(t("bug_ask_cli")))
    except EOFError:
        ok = False
    if not ok:
        print(t("bug_not_sent"))
        return 0
    if err := send(report, post):
        print(t("bug_not_sent_cli", why=err, url=ISSUES_URL))
        return 1
    print(t("bug_sent"))
    return 0

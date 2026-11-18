"""Shared async HTTP client, per-host throttle and small text helpers.

* One httpx.AsyncClient for the whole process.
* An honest User-Agent naming this project on every request, so sites can see
  (and block, via robots.txt or their firewall) who we are, with a contact email
  so a source operator can report a mistake. Checked 2026-11-10: all 191 source
  hosts answer it the same as without the email.
  Checked 2026-11-05: every live source answers it, including rechtspraak.nl,
  which nl-legal-mcp once found blocking non-browser clients.
* A per-host throttle: each adapter declares `min_interval = {host: seconds}`
  and the registry hands it to `set_min_interval`. Hosts nobody declared get
  DEFAULT_INTERVAL.
* Certificates are checked against the operating system's trust store (truststore),
  like a browser: macOS and Windows fetch missing intermediate certificates, which
  several court and gazette servers fail to send. Linux does not, so there we also load
  those intermediates from intermediates.pem (shipped with the package). Verification stays on.
* Size cap: a response body over MAX_BYTES (or a call's `max_bytes`) is refused
  with a SourceError instead of being read into memory.
* Rate limits: a 429/503 with Retry-After is waited out and retried once
  (max MAX_RETRY_WAIT s). Every host's requests, 429s and longest wait are
  counted in `stats` so we collect real limits; see rate_limit_report().
"""
from __future__ import annotations

import asyncio
import datetime
import io
import re
import ssl
import sys
import time
from pathlib import Path
from urllib.parse import urlsplit

import httpx
import truststore
from lxml import etree
from markdownify import markdownify as _md

try:
    from importlib.metadata import version as _version
    _VER = _version("fontes-mcp")  # the PyPI distribution name
except Exception:  # running from a source tree without install metadata
    _VER = "dev"
CONTACT = "fontesmcp@proton.me"   # for source operators: mistakes, blocks, permission questions
UA = f"Fontes/{_VER} (+https://github.com/ykarapazar/fontes; {CONTACT})"
DEFAULT_INTERVAL = 0.25
INTERMEDIATES = str(Path(__file__).with_name("intermediates.pem"))

_client: httpx.AsyncClient | None = None
_intervals: dict[str, float] = {}
_locks: dict[str, asyncio.Lock] = {}
_last_call: dict[str, float] = {}


def set_min_interval(host: str, seconds: float) -> None:
    _intervals[host.lower()] = seconds


def get_client() -> httpx.AsyncClient:
    global _client
    if _client is None:
        # OpenSSL DEFAULT ciphers also offer RSA key exchange, which some court servers
        # still require (www.sccourt.gov.eg). Certificates are verified as usual.
        ctx = truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ctx.set_ciphers("DEFAULT")
        if sys.platform.startswith("linux"):   # macOS/Windows fetch missing intermediates themselves
            ctx.load_verify_locations(INTERMEDIATES)
        _client = httpx.AsyncClient(
            timeout=httpx.Timeout(60.0, connect=15.0),
            follow_redirects=True,
            verify=ctx,
            headers={"User-Agent": UA, "Accept-Language": "en-GB,en;q=0.9,nl;q=0.8"},
        )
    return _client


async def _throttle(url: str) -> None:
    host = (urlsplit(url).hostname or "").lower()
    lock = _locks.setdefault(host, asyncio.Lock())
    async with lock:
        wait = _intervals.get(host, DEFAULT_INTERVAL) - (time.monotonic() - _last_call.get(host, 0.0))
        if wait > 0:
            await asyncio.sleep(wait)
        _last_call[host] = time.monotonic()


MAX_RETRY_WAIT = 30.0
MAX_BYTES = 50 * 2**20
stats: dict[str, dict[str, float]] = {}   # host -> {requests, limited, max_wait}


def _retry_after(r: httpx.Response) -> float:
    try:
        return max(1.0, float(r.headers.get("Retry-After", "")))
    except ValueError:
        return 5.0


async def _fetch(method: str, url: str, max_bytes: int, kw: dict) -> httpx.Response:
    """One request, reading at most max_bytes of (decoded) body."""
    from .base import SourceError
    client = get_client()
    send = {k: kw.pop(k) for k in ("follow_redirects", "auth") if k in kw}
    r = await client.send(client.build_request(method, url, **kw), stream=True, **send)
    try:
        size = r.headers.get("content-length", "")
        too_big = SourceError(f"Error ({r.url.host}): the file is too large to read here (over the "
                              f"{max_bytes // 2**20} MB limit); nothing was read. Open {url} directly.", 413)
        if size.isdigit() and int(size) > max_bytes and "content-encoding" not in r.headers:
            raise too_big
        buf = bytearray()
        async for chunk in r.aiter_bytes():
            buf += chunk
            if len(buf) > max_bytes:
                raise too_big
    finally:
        await r.aclose()
    # The body is already decoded: drop the encoding headers, and make Content-Length match
    # what we hold. A HEAD answer has no body, so its Content-Length (the file size adapters
    # check before downloading) is kept as sent.
    headers = r.headers.copy()
    for h in ("content-encoding", "transfer-encoding"):
        headers.pop(h, None)
    if method.upper() != "HEAD":
        headers["content-length"] = str(len(buf))
    return httpx.Response(r.status_code, headers=headers, content=bytes(buf), request=r.request,
                          history=r.history, extensions=r.extensions)


async def request(method: str, url: str, *, max_bytes: int = MAX_BYTES, **kw) -> httpx.Response:
    host = (urlsplit(url).hostname or "").lower()
    s = stats.setdefault(host, {"requests": 0, "limited": 0, "max_wait": 0.0})
    for attempt in (1, 2):
        await _throttle(url)
        s["requests"] += 1
        r = await _fetch(method, url, max_bytes, dict(kw))
        if r.status_code not in (429, 503) or attempt == 2:
            return r
        if r.status_code == 503 and "Retry-After" not in r.headers:
            return r
        s["limited"] += 1
        wait = _retry_after(r)
        s["max_wait"] = max(s["max_wait"], wait)
        if wait > MAX_RETRY_WAIT:
            return r
        await asyncio.sleep(wait)
    return r


async def get(url: str, **kw) -> httpx.Response:
    return await request("GET", url, **kw)


async def post(url: str, **kw) -> httpx.Response:
    return await request("POST", url, **kw)


def rate_limit_report() -> str:
    """One line per host: requests sent, how many were rate-limited, longest wait asked."""
    return "\n".join(f"{h}: {int(s['requests'])} requests, {int(s['limited'])} rate-limited, "
                     f"max Retry-After {s['max_wait']:.0f}s" for h, s in sorted(stats.items()))


def error(source: str, what: str, status: int | str, hint: str = "") -> str:
    """One consistent error line for adapters: `Error (source): what (HTTP n). hint`."""
    msg = f"Error ({source}): {what} (HTTP {status})."
    return f"{msg} {hint}".strip()


# --------------------------------------------------------------------------- #
# Text helpers shared by adapters
# --------------------------------------------------------------------------- #
def localname(el) -> str | None:
    return etree.QName(el).localname if isinstance(el.tag, str) else None


_NO_SPACE_BEFORE = set(",.;:!?)]}%»”’")
_NO_SPACE_AFTER = set("([{«“‘")


def text(el) -> str:
    """All descendant text of an element, whitespace-normalised.

    Adjacent text nodes are joined with a space (so block-ish children such as
    <Number>1</Number><Title>Foo</Title> don't run together), except where either
    side already has whitespace or the join is at punctuation: 'word<b>,</b>' stays
    'word,' and '(<i>x</i>)' stays '(x)'.
    """
    if el is None:
        return ""
    out = ""
    for t in el.itertext():
        if (out and t and not out[-1].isspace() and not t[0].isspace()
                and t[0] not in _NO_SPACE_BEFORE and out[-1] not in _NO_SPACE_AFTER):
            out += " "
        out += t
    return re.sub(r"\s+", " ", out).strip()


def page(body: str, offset: int, max_chars: int) -> str:
    """Return body[offset:offset+max_chars] with a continuation note."""
    total = len(body)
    offset = max(0, int(offset))
    end = min(total, offset + max(1000, int(max_chars)))
    chunk = body[offset:end]
    if offset:
        chunk = f"… [continuing from char {offset}]\n\n" + chunk
    if end < total:
        chunk += (f"\n\n… [truncated: showing chars {offset}–{end} of {total}. "
                  f"Call again with offset={end} for the next part.]")
    return chunk


def clean(s) -> str:
    """One line: whitespace collapsed (incl. non-breaking spaces), stripped."""
    return re.sub(r"\s+", " ", str(s or "").replace("\xa0", " ")).strip()


def html_paragraphs(html: str) -> list[str]:
    """HTML -> clean markdown paragraphs.

    Drops head/style/script/comments, links and images; a <br> becomes a markdown
    hard line break inside the paragraph (two <br> in a row end the paragraph);
    list items stay one per line; flattens one-column layout tables (common in
    Word-made HTML) into plain paragraphs and keeps real tables as markdown tables.
    """
    if not html:
        return []
    html = re.sub(r"(?is)<head\b.*?</head>|<style\b.*?</style>|<script\b.*?</script>|<!--.*?-->", "", html)
    html = re.sub(r"\s*\n\s*", " ", html)  # source newlines are plain whitespace in HTML
    md = _md(html, strip=["a", "img"], heading_style="ATX").replace("\xa0", " ")
    out = []
    for block in re.split(r"\n\s*\n", md):
        lines = [ln.strip() for ln in block.splitlines() if ln.strip()]
        if not lines:
            continue
        if lines[0].startswith("|"):
            cells = [ln.strip("| ") for ln in lines if not re.fullmatch(r"[|\s:-]*", ln)]
            if all("|" not in c for c in cells):  # one-column layout table
                out += cells
                continue
            p = "\n".join(lines)
        else:
            p, hard = "", False
            for raw in block.splitlines():
                ln = clean(raw)
                if not ln:
                    continue
                if p:  # markdownify ends a <br> line with two spaces
                    p += "  \n" if hard else "\n" if re.match(r"([*+-]|\d+[.)]) ", ln) else " "
                p += ln
                hard = raw.endswith("  ")
        if re.fullmatch(r"[#*_\-\s]*", p):
            continue
        out.append(p)
    return out


def html_to_md(html: str) -> str:
    """HTML -> clean markdown text (paragraphs separated by blank lines)."""
    return "\n\n".join(html_paragraphs(html))


def iso_date(s) -> str:
    """'27.01.2010', '27/1/2010' (day first) or '2010-01-27...' -> '2010-01-27'; else ''."""
    s = str(s or "").strip()
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})", s)
    if m:
        return m[0]
    m = re.match(r"^(\d{1,2})[./-](\d{1,2})[./-](\d{4})$", s)
    return f"{m[3]}-{int(m[2]):02d}-{int(m[1]):02d}" if m else ""


_EN_MONTHS = {m: i for i, m in enumerate(("january", "february", "march", "april", "may", "june", "july",
                                            "august", "september", "october", "november", "december"), 1)}


def en_date(s) -> str:
    """First 'July 8, 2016' (English month name) anywhere in s -> '2016-07-08'; else ''."""
    m = re.search(r"\b(" + "|".join(_EN_MONTHS) + r")\s+(\d{1,2}),\s*(\d{4})\b", str(s or ""), re.I)
    if not m:
        return ""
    try:
        return datetime.date(int(m[3]), _EN_MONTHS[m[1].lower()], int(m[2])).isoformat()
    except ValueError:
        return ""


def pdf_text(data: bytes) -> str:
    """Text of a text-layer PDF (no OCR): each line cleaned, empty lines dropped,
    pages separated by a blank line. '' when the PDF has no text layer."""
    from pypdf import PdfReader
    pages = []
    for p in PdfReader(io.BytesIO(data)).pages:
        lines = [clean(ln) for ln in (p.extract_text() or "").splitlines()]
        pages.append("\n".join(ln for ln in lines if ln))
    return re.sub(r"\n{3,}", "\n\n", "\n\n".join(p for p in pages if p)).strip()


def today() -> str:
    """Today's date as YYYY-MM-DD (the "as of" date for current consolidated texts)."""
    return datetime.date.today().isoformat()


def lru_put(cache: dict, key, value, size: int):
    """Store value in a plain dict used as a small bounded cache (oldest out first)."""
    cache[key] = value
    while len(cache) > size:
        cache.pop(next(iter(cache)))
    return value

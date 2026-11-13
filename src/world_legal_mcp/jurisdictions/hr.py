"""Croatia: legislation and Constitutional Court decisions from Narodne novine
(narodne-novine.nn.hr), the official gazette.

Gotchas this code encodes (verified 2026-11-05 from a UK IP):
  * Texts are the gazette text *as published*. There is no official consolidated
    database: amendments are separate acts ("Zakon o izmjenama i dopunama Zakona o ..."),
    and only a few laws get an official "(pročišćeni tekst)" act. zakon.hr is a private
    consolidation and is not used.
  * The id is the ELI path "{year}/{issue}/{act}" (eli/sluzbeni/2005/35/707). The ELI URL
    302-redirects to /clanci/sluzbeni/{year}_{month}_{issue}_{act}.html; a 404 redirects
    to /stranica404.aspx. We read the redirect ourselves so the target can be checked
    against robots.txt, which disallows ~100 individual gazette articles by path.
  * Search is GET search.aspx (qtype=3, kategorija=1 = službeni dio). naslovi=da searches
    titles only; without it the full text is searched. Words are matched as a phrase when
    possible, quotes force a phrase, AND/OR and prefix* work, Croatian morphology is
    handled. str is the 0-based page, rpp any page size. The result pages are ~600 KB
    (every issue of the year is listed in a side panel).
  * robots.txt disallows search.aspx with kategorija=3 (oglasni dio, notices): we only
    ever search kategorija=1.
  * Case law: odluke.sudovi.hr (all courts) and sljeme.usud.hr (Constitutional Court
    decision base) both have robots.txt "Disallow: /". The Constitutional Court's
    decisions that it orders published (all abstract-review U-I decisions and many
    U-III constitutional complaints) appear in the gazette; search_caselaw searches
    those only, by full text combined with the title phrase every such act carries.
  * Articles: "Članak 5." paragraphs; the short line before it is the article heading.
    Amending acts quote the new articles after „ so those are not mistaken for articles.
"""
from __future__ import annotations

import html
import re
from urllib.parse import quote_plus, urljoin, urlsplit

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import (Decision, DecisionHit, LawHit, LawText, Provision, Results, Toc,
                      TocEntry)

HOST = "narodne-novine.nn.hr"
NN = f"https://{HOST}"
USRH = "Ustavni sud Republike Hrvatske"
USRH_PHRASE = '"Ustavnog suda Republike Hrvatske broj"'
_MONTHS = {"siječnja": 1, "veljače": 2, "ožujka": 3, "travnja": 4, "svibnja": 5, "lipnja": 6,
           "srpnja": 7, "kolovoza": 8, "rujna": 9, "listopada": 10, "studenoga": 11,
           "studenog": 11, "prosinca": 12}
_ARTICLE = re.compile(r"^Članak\s+(\d+)\s*\.?\s*([a-z])?\s*\.?$")
_CASE_NO = re.compile(r"U-[IVX]+[A-Za-z]{0,3}-\s?\d+/\d{2,4}")

_docs: dict = {}
_robots: list[re.Pattern] | None = None


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def _parse_id(s: str) -> tuple[str, str, str]:
    """'2005/35/707', ELI URL, clanci URL/filename '2005_03_35_707' or 'NN 35/2005 (707)'."""
    s = _http.clean(s)
    m = re.search(r"(\d{4})_\d{2}_(\d{1,3})_(\d+)", s)
    if m:
        return m[1], str(int(m[2])), m[3]
    m = re.search(r"(?:^|/)(\d{4})/(\d{1,3})/(\d+)(?:/|$)", s)
    if m:
        return m[1], str(int(m[2])), m[3]
    m = re.search(r"NN\s*(\d{1,3})\s*/\s*(\d{4}|\d{2})(?!\d)\.?\s*,?\s*\(?\s*(\d+)\s*\)?", s, re.I)
    if m:
        y = m[2] if len(m[2]) == 4 else ("19" if int(m[2]) >= 90 else "20") + m[2]
        return y, str(int(m[1])), m[3]
    raise BadRequest(f"Bad Narodne novine id {s!r}. Use the ELI path year/issue/act, "
                     f"e.g. '2005/35/707' (NN 35/2005, act 707), or 'NN 35/2005 (707)'.")


def _eli(y: str, issue: str, act: str) -> str:
    return f"{NN}/eli/sluzbeni/{y}/{issue}/{act}"


def _hr_date(s: str) -> str:
    """'9. srpnja 2024' -> '2024-07-09'; else ''."""
    m = re.search(r"(\d{1,2})\.\s*([a-zčćšžđ]+)\s+(\d{4})", s or "", re.I)
    if m and m[2].lower() in _MONTHS:
        return f"{m[3]}-{_MONTHS[m[2].lower()]:02d}-{int(m[1]):02d}"
    return ""


async def _allowed(path: str) -> bool:
    """robots.txt (User-agent: *) check for one path; read once per process."""
    global _robots
    if _robots is None:
        r = await _http.get(f"{NN}/robots.txt")
        rules = []
        if r.status_code == 200:
            for line in r.text.splitlines():
                m = re.match(r"\s*Disallow:\s*(\S+)", line, re.I)
                if m:
                    pat = re.escape(m[1]).replace(r"\*", ".*")
                    if pat.endswith(r"\$"):
                        pat = pat[:-2] + "$"
                    rules.append(re.compile(pat))
        _robots = rules
    return not any(p.match(path) for p in _robots)


def _is_heading(p: str) -> bool:
    t = p.strip("*_ ")
    letters = [c for c in t if c.isalpha()]
    return bool(letters) and len(t) < 200 and sum(c.isupper() for c in letters) / len(letters) > 0.8


def _is_title(p: str) -> bool:
    t = p.strip("*_ ")
    return (0 < len(t) < 160 and not _ARTICLE.match(t) and t[-1] not in ".:;,"
            and not t.startswith(("(", "„", "\"", "-", "–")) and not re.match(r"^\d", t))


def _key(label: str) -> str:
    """'Članak 5.a', 'čl. 5a', 'art. 5', '5' -> '5a' / '5'. Keeps a '[n]' duplicate marker."""
    s = _http.clean(label).lower()
    dup = re.search(r"\[(\d+)\]", s)
    s = re.sub(r"\[\d+\]", "", s)
    s = re.sub(r"^(članak|clanak|član|clan|čl|cl|art|article)\.?\s*", "", s)
    m = re.fullmatch(r"(\d+)\s*\.?\s*([a-z])?\s*\.?", s.strip())
    if not m:
        return ""
    return m[1] + (m[2] or "") + (f"[{dup[1]}]" if dup else "")


# --------------------------------------------------------------------------- #
class Croatia(Jurisdiction):
    code = "hr"
    name = "Croatia"
    languages = ("hr",)
    aliases = ("croatia", "hrvatska", "hrv")
    sources = (
        Source(
            name="Narodne novine (official gazette of the Republic of Croatia)",
            url=NN,
            covers=("legislation", "caselaw"),
            licence=("No open licence stated; site terms say content is copyright and usable "
                     "'under the conditions of the law'. Laws, regulations and court decisions "
                     "are official texts excluded from copyright (Zakon o autorskom pravu, čl. 8)."),
            commercial_use=None,
            ai_use=True,   # robots.txt has no AI/TDM opt-out; its "Pristup podatcima" page invites crawlers and bots
            auth="none",
            rate_limit=("documented: 'configure scripts and bots to at most 3 requests per "
                        "second' (data_access_hr.aspx, read 2026-11-05); using 0.5 s spacing, "
                        "no 429 seen"),
            terms_url=f"{NN}/data_access_hr.aspx",
        ),
    )
    legislation_filters = {
        "fulltext": "'yes' searches the full text instead of titles only (default: titles)",
        "sort": "'relevance' (default) or 'date' (newest first)",
        "date_from": "gazette publication date from, YYYY-MM-DD",
        "date_to": "gazette publication date to, YYYY-MM-DD",
    }
    caselaw_filters = {
        "sort": "'relevance' (default) or 'date' (newest first)",
        "date_from": "gazette publication date from, YYYY-MM-DD",
        "date_to": "gazette publication date to, YYYY-MM-DD",
    }
    min_interval = {HOST: 0.5}
    notes = ("Legislation is the Narodne novine gazette text as published (no official "
             "consolidated text). Case law: only Constitutional Court decisions published in "
             "the gazette; the courts' own databases forbid robots.")
    gaps = (
        "Ordinary-court case law (odluke.sudovi.hr): robots.txt disallows",
        "Constitutional Court decisions not published in the gazette (sljeme.usud.hr): robots.txt disallows",
        "Consolidated legislation: not published online officially (only a few pročišćeni tekst acts); zakon.hr is private",
        "~100 individual gazette articles: robots.txt disallows",
        "International treaties part (Međunarodni ugovori): not searched (search uses kategorija=1, službeni dio, only)",
    )
    samples = {
        "caselaw_query": "najmoprimac",
        "decision_id": "2024/95/1740",
        "legislation_query": "Zakon o obveznim odnosima",
        "law_id": "2005/35/707",
        "provision": "Članak 8.",
    }

    # ------------------------------------------------------------------ search
    async def _search(self, query: str, *, limit: int, page: int, titles: bool, sort: str,
                      date_from: str = "", date_to: str = ""):
        if sort not in ("", "relevance", "date"):
            raise BadRequest("sort must be 'relevance' or 'date'.")
        params = [("upit", query)]
        if titles:
            params.append(("naslovi", "da"))
        params += [("sortiraj", "1" if sort == "date" else "0"), ("kategorija", "1"),
                   ("rpp", str(max(1, min(int(limit), 200)))), ("str", str(max(0, int(page) - 1))),
                   ("qtype", "3"), ("pretraga", "da")]
        for k, v in (("od", date_from), ("do", date_to)):
            if v:
                m = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", str(v).strip())
                if not m:
                    raise BadRequest(f"date_from/date_to must be YYYY-MM-DD, got {v!r}.")
                params.append((k, f"{m[3]}.{m[2]}.{m[1]}"))
        url = f"{NN}/search.aspx?" + "&".join(f"{k}={quote_plus(v)}" for k, v in params)
        r = await _http.get(url)
        if r.status_code != 200:
            raise SourceError(_http.error("Narodne novine", "search failed", r.status_code), r.status_code)
        h = r.text
        m = re.search(r"Ukupno (?:je|su) pronađen[oa]?\s*<span[^>]*>\s*([\d.]+)", h)
        total = int(m[1].replace(".", "")) if m else None
        hits = []
        for m in re.finditer(
                r'<div class="resultTitle">.*?<a href="(/clanci/sluzbeni/[^"]+)"[^>]*>\s*(.*?)<span'
                r'.*?official-number-and-date">([^<]*)</div>\s*(?:<span class="snippet">(.*?)</span>)?',
                h, re.S):
            fm = re.search(r"(\d{4})_\d{2}_(\d+)_(\d+)", m[1])
            if not fm:
                continue
            y, issue, act = fm[1], str(int(fm[2])), fm[3]
            meta = _http.clean(m[3])        # "NN 35/2005, (707),   zakon, 17.3.2005."
            parts = [p.strip() for p in meta.split(",")]
            hits.append({
                "id": f"{y}/{issue}/{act}",
                "title": _http.clean(html.unescape(re.sub(r"<[^>]+>", " ", m[2]))),
                "number": f"NN {issue}/{y} ({act})",
                "type": parts[2] if len(parts) > 2 else "",
                "date": _http.iso_date(parts[-1].rstrip(".")) if parts else "",
                "snippet": _http.clean(html.unescape(re.sub(r"<[^>]+>", " ", m[4] or "")))[:300],
                "url": _eli(y, issue, act),
            })
        return hits[:limit], (total if total is not None else (None if hits else 0))

    async def search_legislation(self, query, *, limit=10, page=1, filters=None):
        filters = filters or {}
        ft = str(filters.get("fulltext", "")).lower()
        if ft not in ("", "yes", "no", "true", "false"):
            raise BadRequest("fulltext must be 'yes' or 'no'.")
        rerank = str(filters.get("sort", "")).lower() != "date"
        # re-ranking needs a pool wider than one small page (a one-word query like 'radu'
        # buries the base law); page 1 only, later pages keep the source order
        pool = max(limit, 60) if rerank and page == 1 else limit
        hits, total = await self._search(query, limit=pool, page=page,
                                         titles=ft not in ("yes", "true"),
                                         sort=str(filters.get("sort", "")).lower(),
                                         date_from=filters.get("date_from", ""),
                                         date_to=filters.get("date_to", ""))
        if rerank:
            hits = self._rerank(hits, query)
        hits = hits[:limit]
        for x in hits:
            if re.search(r"izmjen\w*\s+(?:i\s+dopun\w*\s+)?(?:zakon|uredb|pravilnik|ustav)", x["title"], re.I):
                x["snippet"] = ("AMENDING act, not a consolidated text; the base law stays in force "
                                "unless this act repeals it. " + x["snippet"]).strip()
        return Results(
            [LawHit(id=x["id"], title=x["title"], type=x["type"], number=x["number"],
                    date=x["date"], snippet=x["snippet"], url=x["url"]) for x in hits],
            total=total,
            note=("Gazette texts as published, not consolidated: amendments are separate acts "
                  "(search 'izmjenama ... Zakona o ...'); some laws have an official "
                  "'(pročišćeni tekst)'. The source has no in-force flag and the default order is "
                  "by relevance (this page is re-ordered: whole-word title matches first, same-title acts "
                  "newest first; older ones are flagged): several acts can share a title (an older act is often "
                  "repealed by a newer one of the same title). Use filters sort='date' for "
                  "newest first and check the repeal provisions of the newest act."))

    @staticmethod
    def _rerank(hits: list[dict], query: str) -> list[dict]:
        """Whole-word title matches first; same-title acts newest first, older ones flagged."""
        words = re.findall(r"\w+", query.lower())
        groups: dict[str, list[dict]] = {}
        for x in hits:
            # an original and its '(pročišćeni tekst)' share a title
            groups.setdefault(re.sub(r"\s*\(pročišćeni tekst\)", "", x["title"].lower()), []).append(x)
        for g in groups.values():
            g.sort(key=lambda x: x["date"], reverse=True)
            for x in g[1:]:
                x["snippet"] = (f"Older act: a newer act with the same title is listed ({g[0]['number']}); "
                                "this one may be repealed (unverified). " + x["snippet"]).strip()
        # amending acts ('Zakon o izmjenama i dopuni Zakona o X') join the group of X, right after it
        gen = {"zakona": "zakon", "uredbe": "uredba", "pravilnika": "pravilnik", "ustava": "ustav"}
        moved: dict[str, list[dict]] = {}
        for k in list(groups):
            m = re.search(r"izmjen\w*\s+(?:i\s+dopun\w*\s+)?(zakona|uredbe|pravilnika|ustava)\s+(.*)", k)
            base = m and f"{gen[m[1]]} {m[2]}"
            if m and base in groups and base != k:
                moved.setdefault(base, []).extend(groups.pop(k))
        for base, am in moved.items():
            tgt = groups[base]
            newer = sorted((a for a in am if a["date"] > tgt[0]["date"]), key=lambda a: a["date"], reverse=True)
            if newer:
                tgt[0]["snippet"] = ("Newer amending act(s) exist ("
                                     + ", ".join(a["number"] for a in newer)
                                     + "; listed after this act, possibly on a later page): the current text may differ. " + tgt[0]["snippet"]).strip()
            tgt.extend(am)
        def exact(g):
            t = set(re.findall(r"\w+", g[0]["title"].lower()))
            return 0 if words and all(w in t for w in words) else 1
        return [x for g in sorted(groups.values(), key=lambda g: (exact(g), len(g[0]["title"]))) for x in g]

    async def search_caselaw(self, query, *, limit=10, page=1, filters=None):
        filters = filters or {}
        q = _http.clean(query)
        kw = dict(limit=limit, page=page, titles=False, sort=str(filters.get("sort", "")).lower(),
                  date_from=filters.get("date_from", ""), date_to=filters.get("date_to", ""))
        # bare words: require every word (the source ORs words inside parentheses, so a
        # labour query returned any decision containing 'radu' or 'ugovora')
        words = q.split()
        strict = bool(words) and not re.search(r'["()]|\b(?:AND|OR|NOT)\b', q)
        qa = f"{USRH_PHRASE} AND " + " AND ".join(words) if strict else (
            f"{USRH_PHRASE} AND ({q})" if q else USRH_PHRASE)
        hits, total = await self._search(qa, **kw)
        if strict and not total:
            hits, total = await self._search(f"{USRH_PHRASE} AND ({q})", **kw)
        out = []
        for x in hits:
            if "Ustavnog suda" not in x["title"]:
                continue    # full-text match elsewhere (strategies, other courts' acts), not a decision
            cn = _CASE_NO.search(x["title"])
            is_usrh = "Ustavnog suda" in x["title"]
            out.append(DecisionHit(
                id=x["id"], title=x["title"], court=USRH if is_usrh else "",
                date=_hr_date(x["title"]) if is_usrh else "",
                case_number=cn[0].replace(" ", "") if cn else "",
                snippet=x["snippet"], url=x["url"]))
        return Results(out, total=total, note=(
            "Only Constitutional Court (Ustavni sud) decisions published in Narodne novine; "
            "no Vrhovni sud or other court decisions (odluke.sudovi.hr) and not the Court's own "
            "base (sljeme.usud.hr): both forbid robots. The total counts gazette acts whose full "
            "text matches, so it can be higher than the decisions listed (non-decisions are "
            "dropped from the page, which may then show fewer than the page size), and "
            "court names in the query only match as words. Date range: date_from/date_to "
            "(gazette publication date)."))

    # ------------------------------------------------------------------ documents
    async def _doc(self, id: str) -> dict:
        y, issue, act = _parse_id(id)
        key = f"{y}/{issue}/{act}"
        if key in _docs:
            return _docs[key]
        eli = _eli(y, issue, act)
        r = await _http.get(eli, follow_redirects=False)
        if r.status_code in (301, 302, 303, 307, 308):
            target = urljoin(eli, r.headers.get("location", ""))
        elif r.status_code == 404:
            raise NotFound(f"No Narodne novine act {key} (NN {issue}/{y}, act {act}).")
        else:
            raise SourceError(_http.error("Narodne novine", f"ELI lookup for {key}", r.status_code),
                              r.status_code)
        path = urlsplit(target).path
        if "stranica404" in path or "/clanci/sluzbeni/" not in path:
            raise NotFound(f"No Narodne novine act {key} (NN {issue}/{y}, act {act}).")
        if not await _allowed(path):
            raise SourceError(f"Narodne novine robots.txt disallows {path}; not fetched. "
                              f"Open {eli} in a browser.", "robots")
        r = await _http.get(target)
        if r.status_code == 404:
            raise NotFound(f"No Narodne novine act {key}.")
        if r.status_code != 200:
            raise SourceError(_http.error("Narodne novine", f"fetching {key}", r.status_code), r.status_code)
        h = r.text
        tm = re.search(r'<div id="sticky" class="title">\s*<h2>(.*?)</h2>', h, re.S)
        title = _http.clean(html.unescape(re.sub(r"<[^>]+>", " ", tm[1]))) if tm else ""
        meta = {}
        for k, v in re.findall(r"<span class=['\"]key['\"]>([^<]+?):</span>(.*?)</td>", h, re.S):
            meta[_http.clean(k)] = _http.clean(html.unescape(re.sub(r"<[^>]+>", " ", v)))
        a = h.find('<div id="html-content-frame">')
        b = h.find('<div id="sticky-anchor2"', a)
        if a < 0:
            raise SourceError(f"Narodne novine page for {key} has no text block (layout changed?).")
        body = h[a:b if b > 0 else len(h)]
        body = re.sub(r'(?is)<span class="title-for-print">.*?</span>|<title\b.*?</title>', "", body)
        paras = [p for p in _http.html_paragraphs(body)
                 if p.strip("*_ ") != "if !supportEmptyParas endif"]
        if not title and paras:
            title = paras[0][:200]
        date = _http.iso_date(meta.get("Datum tiskanog izdanja", "").rstrip("."))
        doc = {"id": key, "title": title, "url": eli, "paras": paras, "meta": meta, "date": date,
               "number": f"NN {issue}/{y} ({act})"}
        return _http.lru_put(_docs, key, doc, 8)

    @staticmethod
    def _articles(paras: list[str]):
        """-> toc entries and {key: (label, start, end)} over paras."""
        entries, arts, idx = [], {}, []
        for i, p in enumerate(paras):
            m = _ARTICLE.match(p.strip("*_ "))
            if m:
                idx.append((i, m[1] + (m[2] or ""), f"Članak {m[1]}." + (m[2] or "")))
        starts = {}
        for i, k, label in idx:
            st = i - 1 if i > 0 and _is_title(paras[i - 1]) and not _is_heading(paras[i - 1]) else i
            starts[i] = st
        heads = {i for i, p in enumerate(paras) if _is_heading(p) and not _ARTICLE.match(p.strip("*_ "))}
        seen: dict[str, int] = {}
        for n in range(len(idx)):
            i, k, label = idx[n]
            st = starts[i]
            nxt = starts[idx[n + 1][0]] if n + 1 < len(idx) else len(paras)
            end = min((j for j in heads if i < j < nxt), default=nxt)
            seen[k] = seen.get(k, 0) + 1
            if seen[k] > 1:
                k, label = f"{k}[{seen[k]}]", f"{label} [{seen[k]}]"
            arts[k] = (label, st, end)
        # TOC in document order: headings + articles
        art_pos = {v[1]: (k, v[0]) for k, v in arts.items()}
        for j in range(len(paras)):
            if j in art_pos:
                k, label = art_pos[j]
                st = arts[k][1]
                ttl = paras[st].strip("*_ ") if not _ARTICLE.match(paras[st].strip("*_ ")) else ""
                entries.append(TocEntry(title=f"{label} – {ttl}" if ttl else label, level=1,
                                        provision=label))
            elif j in heads:
                entries.append(TocEntry(title=paras[j].strip("*_ "), level=0))
        return entries, arts

    @staticmethod
    def _status(d: dict) -> str:
        """Plain statement of which version of the act the text is."""
        if "pročišćeni tekst" in d["title"].lower():
            return (f"Official consolidated text (pročišćeni tekst) {d['number']}, current only up to "
                    f"{d['date']}: later amendments are separate acts (search 'izmjenama ... Zakona o ...').")
        msg = (f"ORIGINAL gazette text as published {d['number']} ({d['date']}), NOT the current "
               f"amended text: later amendments are separate acts (search 'izmjenama ... Zakona o ...') "
               f"and an official '(pročišćeni tekst)' may exist (search '{d['title']} pročišćeni tekst').")
        if d["title"].strip().lower() == "ustav republike hrvatske":
            msg += (" This server has no Constitution text current after 2014: the newest consolidated "
                    "text it can serve is id 2010/85/2422 (NN 85/2010), which predates the 2014 "
                    "amendment (NN 5/2014); the 1990 original is not current either.")
        if re.search(r"izmjen\w*\s+(?:i\s+dopun\w*\s+)?(?:zakon|uredb|pravilnik|ustav)", d["title"], re.I):
            rep = [p for p in d["paras"] if re.search(r"prestaj\w* važiti|stavlj\w* izvan snage", p, re.I)]
            msg += (" This is an AMENDING act, not a consolidated text: the base law stays in force "
                    "unless this act's repeal provisions say otherwise.")
            msg += (" Repeal wording found in this act: " + " | ".join(x[:300] for x in rep[:3])
                    if rep else " No repeal wording ('prestaje važiti', 'stavlja se izvan snage') "
                    "found in this act's text, so it does not appear to repeal the base law.")
        return msg

    async def get_legislation_toc(self, id):
        d = await self._doc(id)
        entries, _ = self._articles(d["paras"])
        if not entries:
            entries = [TocEntry(title=d["title"], level=0, provision="")]
        return Toc(id=d["id"], title=d["title"], url=d["url"], entries=entries)

    async def get_legislation_provision(self, id, provision):
        d = await self._doc(id)
        _, arts = self._articles(d["paras"])
        k = _key(provision)
        if not k:
            raise BadRequest(f"Bad provision {provision!r}. Use an article label such as "
                             f"'Članak 8.', 'čl. 8', '8' or '5.a'.")
        if k not in arts:
            raise NotFound(f"No {provision!r} in NN {d['number']} ({d['title']}).")
        label, st, end = arts[k]
        text = "\n\n".join(d["paras"][st:end])
        text = f"[{self._status(d)}]\n\n" + text
        return Provision(law_id=d["id"], law_title=d["title"], provision=label, text=text,
                         url=d["url"], as_of=d["date"])

    async def get_legislation_text(self, id):
        d = await self._doc(id)
        meta = {k: v for k, v in d["meta"].items() if k in
                ("Vrsta dokumenta", "Izdanje", "Broj dokumenta u izdanju", "Donositelj",
                 "Datum tiskanog izdanja")}
        meta["Version"] = self._status(d)
        return LawText(id=d["id"], title=d["title"], text="\n\n".join(d["paras"]), url=d["url"],
                       as_of=d["date"], metadata=meta)

    async def get_decision(self, id):
        d = await self._doc(id)
        t = d["title"]
        text = "\n\n".join(d["paras"])
        cn = _CASE_NO.search(t) or _CASE_NO.search(text)
        held = re.search(r"sjednici održanoj\s+(\d{1,2}\.\s*\w+\s+\d{4})", text)
        is_usrh = "Ustavnog suda" in t or any("USTAVNI SUD" in p.upper() for p in d["paras"][:3])
        meta = {k: v for k, v in d["meta"].items() if k in
                ("Vrsta dokumenta", "Izdanje", "Donositelj", "Datum tiskanog izdanja")}
        return Decision(id=d["id"], title=t, text=text, url=d["url"],
                        court=USRH if is_usrh else d["meta"].get("Donositelj", ""),
                        date=_hr_date(t) or _hr_date(held[1] if held else "") or d["date"],
                        case_number=cn[0].replace(" ", "") if cn else "",
                        metadata=meta)

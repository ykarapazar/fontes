"""The unified output format. Every adapter returns these records, never markdown.

The server renders them (render.py) so every country looks the same to the
model: same headings, same field order, same paging, same "how to cite" line.

Field rules (checked by tests/live/test_conformance.py):
  * `id` is what the next tool takes, exactly as the source uses it
    (ECLI, neutral citation, documentId, BWB-id, ...). Never invented.
  * `url` is a public https page a human can open to check the original.
  * dates are ISO "YYYY-MM-DD" (or "" when the source has none).
  * `text` is markdown. Full text, untruncated: the server pages it.
  * Strings are already cleaned (no HTML tags, whitespace collapsed).
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class DecisionHit:
    id: str                      # pass to get_decision
    title: str                   # case name, or court + case number when there is no name
    court: str = ""
    date: str = ""               # decision date, ISO
    case_number: str = ""        # docket / esas no / zaaknummer
    snippet: str = ""            # short plain-text excerpt, if the source gives one
    url: str = ""
    has_text: bool = True        # False: get_decision will not return a full judgment; the hit says so


@dataclass
class Decision:
    id: str
    title: str
    text: str                    # full text, markdown
    url: str
    court: str = ""
    date: str = ""
    case_number: str = ""
    summary: str = ""            # official headnote / samenvatting, if any
    metadata: dict[str, str] = field(default_factory=dict)  # extra labelled facts, source language ok
    note: str = ""               # one line about THIS result (e.g. "summary only"), shown under the title


@dataclass
class LawHit:
    id: str                      # pass to get_legislation_*
    title: str
    type: str = ""               # source's own type name: "Kanun", "ukpga", "wet"
    number: str = ""             # official number, e.g. "6098", "2006 c. 46"
    date: str = ""               # enactment / publication date, ISO
    status: str = ""             # "in force", "repealed", ... as the source says
    snippet: str = ""
    url: str = ""
    has_toc: bool = True         # False: get_legislation_toc will refuse this id; no Contents line


@dataclass
class TocEntry:
    title: str                   # heading text, e.g. "Madde 1 - Sözleşmenin kurulması"
    level: int = 0               # 0 = top level
    provision: str = ""          # label for get_legislation_provision; "" for pure headings


@dataclass
class Toc:
    id: str
    title: str
    url: str
    entries: list[TocEntry]
    note: str = ""               # always shown, never filtered by `keyword` (e.g. "no article split")


@dataclass
class Provision:
    law_id: str
    law_title: str
    provision: str               # normalised label, as get_legislation_toc shows it
    text: str                    # markdown, including the provision's own heading
    url: str
    as_of: str = ""              # version date of the consolidated text, ISO, if known
    note: str = ""               # one line about THIS result (e.g. "PDF extraction broke some words")


@dataclass
class LawText:
    id: str
    title: str
    text: str                    # full consolidated text, markdown
    url: str
    as_of: str = ""
    metadata: dict[str, str] = field(default_factory=dict)
    note: str = ""               # one line about THIS result, shown under the title


@dataclass
class Results:
    items: list                  # DecisionHit or LawHit
    total: int | None = None     # None when the source does not say
    note: str = ""               # one line the user should know (e.g. "data lags ~5 months")
    query_ignored: bool = False  # True: the source did not apply the search words; the header must not claim a match
    incomplete: bool = False     # True: only part of the source was searched; the count is a floor

# Translating Fontes

The language list and its rules are in `research/languages.json` and `research/languages.md`
(80 languages, all required; tier 1 first). English is the source for everything. Adding a
language means adding files: **no code changes**.

## Files for one language

Use the code exactly as written in `research/languages.json` (`tr`, `zh-Hans`, `sr-Latn`, `pt`...).
`pt` is Brazilian Portuguese and `pt-PT` European Portuguese (Portugal and the African and Asian
Portuguese-speaking countries): two separate sets of files.

| File | Translate from | Notes |
|---|---|---|
| `installer/locales/<code>.json` | `installer/locales/en.json` | Installer, Mac app dialogs, `fontes report-bug`, Claude Desktop extension text (`mcpb_*`). Same keys, same `{placeholders}`. `stats_privacy` keeps `{privacy}`: the installer fills in the link to your `PRIVACY.md` (English if yours is missing). |
| `docs/i18n/<code>/strings.json` | `docs/i18n/en/strings.json` | Translation notice, status page, COVERAGE.md summary and README table labels. Same keys, same `{placeholders}`. |
| `docs/i18n/<code>/README.md` | `README.md` | Keep the three marker pairs `<!-- languages:start/end -->`, `<!-- coverage:start/end -->`, `<!-- sources:start/end -->` with **nothing** between them; scripts fill them. The `languages` pair goes right under the title, as in English. Fix relative links (`docs/INSTALL.md` becomes `INSTALL.md`; English-only files such as `../../ADAPTER_SPEC.md`; `LICENSE` becomes `../../../LICENSE`). |
| `docs/i18n/<code>/INSTALL.md` | `docs/INSTALL.md` | |
| `docs/i18n/<code>/PRIVACY.md` | `docs/PRIVACY.md` | Strictly faithful; see the low-risk rule. |
| `docs/i18n/<code>/FAQ.md` | `docs/FAQ.md` | Links to `../README.md` become `README.md`, `../LICENSE` becomes `../../../LICENSE`, other root files `../../../`. |
| `docs/i18n/<code>/KEYS.md` | `docs/KEYS.md` | Strictly faithful, like PRIVACY.md: keys, accounts and terms. |
| `docs/i18n/<code>/index.html` | `docs/index.html` | `<html lang="<code>">`, plus `dir="rtl"` for ar, ur, fa, ps, he, ckb, dv. Keep the `<!-- languages:start/end -->` markers. Show the notice (below) under the header. Fix relative links (`status/` becomes `../../status/?lang=<code>`). |

Every translated `.md` file starts with the notice as a quote, in your language: the value of
`doc_notice` from your `strings.json`, which translates *"This is a machine-assisted translation.
The English version is authoritative."*:

```
> <doc_notice>
```

Do **not** create or edit: `COVERAGE.md` in your folder (a summary generated from your
`strings.json`), any English file, any `.py` / `.sh` / `.ps1` file, `docs/HEALTH.md`,
`docs/status/` or `docs/ADAPTER_SPEC.md` (English only; the status page
is one page that reads every `strings.json`).

Links to a heading (`#anchor`) use GitHub's slug of the heading as it reads **in your file**:
lower case, punctuation dropped, spaces become `-` (`## Ce dont vous avez besoin` →
`#ce-dont-vous-avez-besoin`). When you translate a heading, update every link to it, in the same
file and in your other files. Link to a file in your own folder when it exists (`INSTALL.md`,
`KEYS.md`, `FAQ.md`, `PRIVACY.md`), and to the English file otherwise.

After adding files, run only these, which change nothing:

```sh
uv run python scripts/i18n_check.py        # must say 0 errors for your files
uv run python scripts/linkcheck.py <code>  # links and anchors in your folder: 0 problems
uv run pytest -q tests --ignore=tests/live
```

Do **not** run `scripts/i18n_docs.py`, `scripts/readme_tables.py`, `scripts/catalogue.py` or
`scripts/status_page.py`: they rewrite every language's files, and several translators work at
the same time. The maintainer runs them once all translations are in.

## Needs native review

These languages were machine-translated on 2026-11-27 and the translator marked itself not confident:
ay, dv, dz, ps, qu, wo, zgh. A native reader should check them before anyone relies on the wording.

## Glossary rule: never translate

- **Fontes** (the product name), **MCP**, Model Context Protocol, Claude, Claude Desktop, Codex,
  uv, PyPI, GitHub.
- Tool names: `list_jurisdictions`, `search_caselaw`, `get_decision`, `search_legislation`,
  `get_legislation_toc`, `get_legislation_provision`, `get_legislation_text`, `report_bug`.
- Anything in `backticks` or code blocks, commands (`uvx fontes-mcp report-bug`), file names and paths,
  URLs, e-mail addresses, environment variables (`FONTES_LANG`, `FONTES_STATS`,
  `FONTES_NO_UPDATE_CHECK`, `WLM_PERMITTED`...), jurisdiction codes (`tr`, `gb`), JSON keys.
- `{placeholders}` stay exactly as they are; you may move them within the sentence.
- Source and court names stay in their own language as in English (`Bedesten`, `HUDOC`, `rechtspraak.nl`).
- The `yes` key: comma-separated words that mean "yes" in your language, lower case (English `y`
  and `yes` always work too). Keep `[y/N]`-style hints consistent with it.
- `mcpb_keywords`: comma-separated, no spaces after commas needed.

## Low-risk rule

Translate faithfully. **Never add, drop, soften or strengthen a claim**, especially about what
data is collected or sent, privacy, licences, official status of sources, or legal effect. If a
sentence says "never", "only", "opt-in", "unofficial", "not legal advice", keep exactly that
force. Do not add marketing, examples or explanations that are not in English. If a sentence
cannot be translated without changing its meaning, keep it closer to English and flag it in your
report. Privacy and licence text always carry the notice that the English version is
authoritative.

## Glossary seed

Use the term your country's lawyers and official sites use; record your choices at the top of
your report so later translators stay consistent.

| English | Meaning here |
|---|---|
| case law | court decisions as a body of law (not one "case") |
| court decision / judgment | one ruling of a court |
| legislation | laws and regulations together |
| law / act / statute | one legislative text |
| provision | one article or section of a law |
| jurisdiction | a country or international court Fontes covers (not "competence") |
| consolidated (text) | the current text with all amendments applied |
| as originally published | the text as first printed in the official gazette |
| official source | a publisher that is part of the state or court itself |
| unofficial (source / consolidation) | anything else; may differ from the binding text |
| source | the website or API a text comes from |
| robots.txt | untranslated |
| opt-in / off unless you say yes | never sent unless the user explicitly agrees |

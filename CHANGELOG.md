# Changelog

Plain-language notes for each release. Newest first.

## Unreleased

**New**

- Past versions of a law: `get_law_on_date` (a provision as in force on a date, also in the
  past, with the law that last changed it) and `get_law_history` (every law that changed a
  provision, or the word-by-word change between two dates). They work for any country in
  [Lexifina](https://github.com/lexifina/global-law)'s record. Fontes now has nine tools plus `report_bug`.
- 91 more countries and territories (for example South Africa, Kenya, Mexico, New Zealand,
  South Korea, Ukraine), legislation only, through the existing legislation tools. Coverage per
  country varies a lot; `list_jurisdictions` shows what each holds. The 125 jurisdictions with
  live official coverage are unchanged, except that India's Acts (legislation) now come from Lexifina's
  record too, since India Code's terms bar automated access; India's Supreme Court case law stays live.
- Both come from Lexifina's record of the law, which keeps about 200 countries as git history. Lexifina
  is not the official publisher and its record can lag it: every answer says so, links the official page and
  says how far the record goes. Lexifina's sourcing policy differs from Fontes's: in some countries
  it copies sites whose terms or robots.txt Fontes respects for its own fetching. Fontes is not
  affiliated with Lexifina, which built and maintains the record.
- Privacy: for these tools and countries, search words, citations and dates go to Lexifina's
  server (`global-law.lexifina.com`), which documents that it logs the tool called and how long
  it took, never what was asked. On by default; set `WLM_LEXIFINA=0` to turn it off.

## 0.1.3 (2026-11-27)

**New**

- US state courts (`us-states`): opinions of the supreme and appellate courts of all 50 states
  and DC, from CourtListener. CourtListener is run by Free Law Project, a non-profit, and is not
  an official source, so every answer says so and links the court's own copy when CourtListener
  has one. It needs your own free CourtListener API token (`WLM_US_COURTLISTENER_KEY`; the installers ask for it).
  State statutes are not covered yet. Asked for on Reddit.

**Fixed**

- Claude Code: a page of a long court decision or law (up to 60,000 characters) was saved to a
  file instead of reaching the conversation, so Claude saw only a short preview. These two tools
  now tell Claude Code to keep pages of up to 100,000 characters inline. Reported on Reddit.
- The website's page for France (and now US state courts) said "legislation" only when its key
  was not set where the page was built.

## 0.1.2 (2026-11-25)

**Fixed**

- Legislation search showed no id for hits without a table of contents, so they could not be
  opened: every Afghan law, Romanian laws other than the Constitution, and scanned Cabo Verde
  laws. These hits now show a `get_legislation_text` line with the id.
- Afghanistan: Official Gazettes whose PDF has no readable text (old fonts or scans, mostly
  before no. 1410) now return the law's record and where to read the PDF, instead of an error.
- Windows installer: the privacy notice now opens in your language, as on the Mac.

**Changed**

- Marked as beta on PyPI (was alpha), matching the rest of the project.
- Depends on plain `mcp` instead of `mcp[cli]`, so fewer packages are installed.

## 0.1.1 (2026-11-18)

**Fixed**

- Windows: jurisdictions from Latvia onwards (alphabetically, 47 of 124, among them the
  Netherlands and the US) did not load, because Windows has no time-zone database. Fontes now
  brings its own (tzdata), and one jurisdiction that fails to load no longer hides the others.
- Windows installer: the window now waits for Enter, so the summary can be read.
- Installer: if no AI app is found, it says so and points to Claude Desktop, instead of
  reporting success.

## 0.1.0 (2026-11-18)

The first public version.

**What you can search**

- Court decisions and legislation in 124 jurisdictions: 108 UN member states, Hong Kong,
  Kosovo, Palestine, Taiwan, the DIFC Courts, and 11 international courts and bodies (among them
  the European Court of Human Rights, the EU, the ICJ, ICSID, ITLOS, the WTO and the UN Treaty
  Collection).
- 72 of the 124 count as covered under a strict rule: the top general court's precedents, or
  the constitution and primary acts, reached completely. [docs/COVERAGE.md](docs/COVERAGE.md)
  lists what each jurisdiction reaches, what it doesn't, and why.
- France needs a free PISTE key; US case-law search works better with a free api.data.gov key.
  Every other jurisdiction needs no key.

**How it works**

- Seven research tools: `list_jurisdictions`, `search_caselaw`, `get_decision`,
  `search_legislation`, `get_legislation_toc`, `get_legislation_provision`,
  `get_legislation_text`. The jurisdiction is a parameter.
- Texts are fetched live from the publisher's website or API when you ask. No database, no bulk
  download, no account.
- Every result names its source and links to the original. Unofficial sources are flagged in
  the answer.
- Each source's licence, terms, robots.txt and rate limits are recorded. Sources whose terms
  need the publisher's permission are off by default (`WLM_PERMITTED`).
- Requests carry an honest User-Agent with a contact address and are spaced per website.
- `--only` limits the server to some jurisdictions. `nl-legal-mcp` and `uk-legal-mcp` remain as
  aliases for the Dutch and UK subsets.

**Install and updates**

- An installer for Mac and Windows that sets up Fontes in Claude Desktop, Codex, Claude Code,
  Cursor, VS Code (Copilot), Windsurf, Gemini CLI, Zed, LM Studio and Cline, in each one it
  finds. It updates Fontes once a day, falling back to the last version that worked. Tested on
  macOS; the Windows version has not yet been run on Windows.
- An optional keys step after installing, and an **Add or change keys** launcher, for the free
  France and US keys. See [docs/KEYS.md](docs/KEYS.md).
- A Claude Desktop extension (`.mcpb`) with optional key fields, and `uvx fontes-mcp` for developers.
- A once-a-day check for a newer version on PyPI (off with `FONTES_NO_UPDATE_CHECK=1`).

**Privacy and reports**

- Nothing is sent to the developer by default. Usage counts are opt-in; a bug report
  (`report_bug` tool, `fontes report-bug`) is sent only after you see it and confirm. See
  [docs/PRIVACY.md](docs/PRIVACY.md).

**Docs**

- README, install guide, privacy notice and landing page in 80 languages.
- A daily health check of the sources, with a public status page.
- [FAQ](docs/FAQ.md), [contributing guide](CONTRIBUTING.md), [code of conduct](CODE_OF_CONDUCT.md)
  and [security policy](SECURITY.md).

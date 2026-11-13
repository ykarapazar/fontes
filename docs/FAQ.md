# Fontes: questions and answers

## What is Fontes?

A free, open-source MCP server (Apache 2.0). It lets any app that speaks the Model Context
Protocol (Claude, Codex, Cursor, VS Code, Gemini CLI and others) search court decisions and
legislation live on court and government websites in 120+ jurisdictions and international
courts (124 adapters). Every result names its source and links to the original.

## Are the texts official?

Mostly, but not always.

- Most sources are run by a court, a ministry or an official gazette.
- Some consolidated texts are published by a government but are expressly unofficial: only
  the official gazette is authentic.
- A few sources are not government sites at all (for example LexiVox, LawPhil, Maqam,
  Wikisource).

Fontes adds an "Unofficial source" notice to every answer that comes from one of these. Before
you cite anything, check the official publication. The coverage table in the
[README](../README.md#coverage) and `list_jurisdictions` name the source for each jurisdiction.

## Which jurisdictions does it cover, and how well?

124 adapters: 108 UN member states, Hong Kong, Kosovo, Palestine, Taiwan, the DIFC Courts and
11 international courts and bodies (such as the European Court of Human Rights, the EU, the
ICJ and the WTO).

Coverage differs a lot. Under a strict rule (the top general court's precedents, or the
constitution and primary acts, reached completely), 72 of the 124 count as covered.
[COVERAGE.md](COVERAGE.md) lists, for each jurisdiction, what Fontes reaches, what it doesn't,
and why.

## Do I need an API key?

For almost every jurisdiction, no. Some sources need a free key: see [KEYS.md](KEYS.md).

- **France:** yes. France is off until you set `WLM_FR_PISTE_CLIENT_ID` and
  `WLM_FR_PISTE_CLIENT_SECRET`. These come from a free PISTE account (piste.gouv.fr) with an
  app subscribed to Judilibre and Légifrance.
- **United States:** optional. Case-law search works without a key, but the shared demo key
  allows only about 10 searches a day per IP address. A free api.data.gov key in
  `WLM_US_GOVINFO_KEY` raises it.

Set these as environment variables for the Fontes server in your app's MCP settings. Once the
installer is out, it will ask for them after installing, and its **Add or change keys** launcher
changes them later.

Separately, a few sources say in their terms that automated access needs the publisher's
permission. They are marked OFF and stay off. A key does not change that; only the
publisher's permission does (then set `WLM_PERMITTED=<codes>`).

## What leaves my computer?

Your searches go only to the source being searched. Fontes keeps no database and needs no
account.

Besides the sources, Fontes asks PyPI once a day whether a newer version exists (switch it off
with `FONTES_NO_UPDATE_CHECK=1`). Usage counts are off unless you turn them on, and a bug report
is sent only after you have seen it and confirmed. Your AI app sees your conversation under its
own terms.

Full details: [PRIVACY.md](PRIVACY.md).

## Is this legal advice?

No. Fontes is a research tool. It finds texts; it does not tell you what they mean for your
case, and using it does not create a lawyer–client relationship with anyone. The AI app can
misread a text, so read the full decision or provision before you rely on it. For advice, ask
a lawyer qualified where your question arises.

## Who maintains it? Will it keep working?

One person: Yüce Karapazar. There is no company behind Fontes, no support contract and no
service-level promise. No legal services are offered.

The sources are checked once a day and the results are published on the
[status page](https://ykarapazar.github.io/fontes/status/). Court and government websites
change without notice, so a source can break at any time. There is no guarantee that any source,
or Fontes itself, will keep working. Fontes is provided "as is", without warranty (sections 7
and 8 of the [LICENSE](../LICENSE)).

## A text is wrong, out of date or a source is broken. How do I report it?

- Open an issue with the "Broken or wrong source" form:
  <https://github.com/ykarapazar/fontes/issues/new/choose>. Say which jurisdiction, what you
  asked, what you got, and the official page that shows the right text.
- Or ask your AI app to "report a Fontes bug" (or run `fontes report-bug`). You see the report before
  anything is sent.
- Or email fontesmcp@proton.me.

Do not include client details or confidential facts in a report.

**If you run one of the sources** and something is wrong (your terms, your robots.txt, your rate
limits), email fontesmcp@proton.me. The source will be fixed or switched off.

## How is Fontes different from hosted legal-research tools?

- **It runs on your computer.** There is no Fontes server and no account. That also means it
  only works in apps that can start a local MCP server (Claude Desktop, Codex, Cursor, VS Code
  and similar), not in web-only apps that accept only hosted connectors.
- **It has no database.** Each search goes live to the publisher's own website or API, so
  results are as current as the source, and search quality is the source's own. There is no
  semantic search over a curated index.
- **It sets no usage limit.** Fontes has no monthly call cap. It spaces its requests to each
  website, and some sources limit how fast or how often they can be queried.
- **It is open source.** You can read every adapter and see exactly where each text comes from.
- **There is no vendor behind it.** No contract, support desk or uptime promise (see "Who
  maintains it?").

## Which apps and systems does it work with?

Any MCP app that can run a local (stdio) server, for example Claude Desktop, Claude Code,
Codex, Cursor, VS Code (GitHub Copilot), Gemini CLI, Windsurf, Zed, LM Studio and Cline. Fontes
runs on macOS, Windows and Linux, anywhere uv runs (Python 3.13+). Most apps need one
command or one config entry, and Claude Desktop takes a double-clicked `.mcpb` file. A one-click installer for Mac and Windows is on its way. It sets
up Claude Desktop, Codex, Claude Code, Cursor, VS Code, Windsurf, Gemini CLI, Zed, LM Studio and
Cline in one go. Steps for each app: [INSTALL.md](INSTALL.md).

## Can I contribute code?

Not at the moment. Issues, source reports and jurisdiction requests are welcome. See
[CONTRIBUTING.md](../CONTRIBUTING.md).

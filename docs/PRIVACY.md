# Fontes privacy notice

Fontes runs on your computer. Your searches and the documents you open stay
between your computer, the sources you search (official ones, plus CourtListener and Lexifina
where you use them, see below), and the AI app you use (under that
app's own terms). Fontes itself sends the Fontes developers **nothing by
default**.

## What can leave your computer, and when

**1. Update check (on by default).** Once a day Fontes asks PyPI, the public Python package
index, which version is the newest. The request carries nothing about you or your work; PyPI
sees your IP address, as with any download. To turn it off, set `FONTES_NO_UPDATE_CHECK=1`
(the in-app notice) and `FONTES_NO_AUTO_UPDATE=1` (the installer's automatic updates).

**2. Usage counts (off unless you turn them on).** If you opt in, once a day Fontes sends:

- the Fontes version and your OS family (macOS, Windows, Linux);
- per day, how many times each tool was used for each jurisdiction code, for example
  "2026-11-10, nl, search_caselaw, 12".

That is the whole message. It never includes your searches, document or case ids, document
text, your name, an account, or any id for you or your computer. Counts wait on your computer
(in Fontes's cache folder, `stats.json`) until they are sent; if sending fails they wait for
the next day.

- **Opt in**: answer "y" when the installer asks, or set `FONTES_STATS=1` for the Fontes server.
- **Opt out**: run the installer again and press Enter at that question, or remove
  `FONTES_STATS`. Deleting `stats.json` discards anything not yet sent.

**3. Bug reports (only when you send one).** When you ask for one (`fontes report-bug`, or ask
your AI app to report a Fontes bug), Fontes shows you the full report first and sends it only if
you confirm. It holds the Fontes version, your OS family, the last failed tool call's
jurisdiction code, tool name and error message (with your search words and ids cut out), and
a note if you write one. Do not put client details in the note. To support this, Fontes keeps
the last error on your computer (`last-error.json` in its cache folder, replaced each time);
it is never sent on its own.

**4. Lexifina (on by default).** `get_law_on_date`, `get_law_history`, the 91 countries and India's Acts
are read through Lexifina's record of the law, so they go to Lexifina as well as, or instead of, the official site. Your search words, citations and
dates go to Lexifina's free server, `global-law.lexifina.com`, which is run by Lexifina, not by the
Fontes developers. Lexifina documents that its server logs which tool was called and how long it
took, never what was asked; Fontes cannot check that, and Lexifina's own terms apply. Lexifina sees
your IP address, as any web server does. To turn Lexifina off completely, set `WLM_LEXIFINA=0`;
those two tools and countries then stop working and nothing is sent there.

## Where it goes and how long it is kept

Usage counts and bug reports go to a small server run by the Fontes developer
(`relay.kinetra.fit`). It stores no IP addresses: they are used only in memory, briefly, to
stop floods, and the web server keeps no access log for it. Counts are added into daily
totals; single submissions are not kept. Totals are kept up to 2 years, bug reports up to
1 year, then deleted. Nothing is sold or shared.

If that server cannot be reached, nothing is sent: counts stay on your computer and bug reports
point you to the issue tracker instead.

## Who is responsible, and on what basis

The data controller for usage counts and bug reports is Yüce Karapazar, the developer of
Fontes. Contact: fontesmcp@proton.me.

The lawful basis is your consent (Article 6(1)(a) of the UK GDPR and the EU GDPR). Usage counts
are sent only if you opt in, and a bug report only after you confirm it. You can withdraw
consent at any time by opting out as described above; this does not affect what was sent
before.

## Contact

Questions or requests: email fontesmcp@proton.me, or open an issue at
<https://github.com/ykarapazar/fontes/issues>.

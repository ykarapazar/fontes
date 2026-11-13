# Canada: CanLII API for Fontes

Researched 2026-11-10. Read-only. No key requested, no form submitted.

## Access limits of this research (important)
- canlii.org pages (terms of use, /en/api/, feedback, developer.canlii.org) return HTTP 403 with a DataDome bot challenge to automated fetchers. I could NOT read CanLII's own Terms of Use or any API terms/licence page. Everything about API terms beyond the GitHub doc is **unverified**.
- api.canlii.org/robots.txt returns `401 {"error": UNAUTHORIZED}` (no robots.txt; API needs a key). Nothing to read.
- Verified directly: https://www.canlii.org/robots.txt, and the official API doc at github.com/canlii/API_documentation (EN.md).

## 1. Key and terms
Official doc (raw.githubusercontent.com/canlii/API_documentation/master/EN.md):
- "CanLII maintains an API that allows **authorized developers** to programmatically access **metadata** about the CanLII collection."
- "To apply for an API key, please send a message with your contact information to the feedback form." (canlii.org/en/feedback/feedback.html)
- Keys are manually granted on application. Eligibility criteria: **not published** in the doc (unverified). Third parties say canlii.org/en/api/ and "free for research use" (secondary, unverified).
- Whether each self-hoster needs their own key: the doc implies a key per authorized developer; no redistribution-of-key language found. Fontes cannot ship a shared key (unverified, but a shared key would almost certainly breach "authorized developers" and per-key limits). Each user would have to apply individually, with no guarantee of approval.

## 2. API terms of use
NOT FOUND in any source I could read. The official doc contains no terms on commercial use, caching, redistribution, attribution, rate limits or AI/ML. The only limits stated:
- HTTPS only; "transfers larger than 10MB are not supported"; resultCount max 10,000.
- Third-party claims (unverified): 2 req/s, 1 concurrent, 5,000/day (Socket.dev listing for an npm canlii-mcp package); "daily limit" errors (MCP READMEs). Not from CanLII.
- CanLII's website Terms of Use reportedly prohibit "bulk and systematic download and scraping" (as characterised in CanLII's 2024 complaint against Caseway AI, per Canadian Lawyer / Law360). Quote is from the lawsuit allegation, not the terms text. Terms text unverified.

## 3. What the API returns
Verified from the official doc: **metadata only.** Endpoints: caseBrowse (courts/tribunals, case lists), case metadata (title, citation, url, docketNumber, decisionDate, keywords, language), caseCitator (cited cases, citing cases, cited legislation), legislationBrowse (lists; metadata with title, citation, type, startDate/endDate, repealed, "content" part list of partId/partName only). No judgment text, no statute text. The `url` field points to canlii.ca/t/... (the website).

Full text is reached only via the CanLII website (canlii.org/canlii.ca short links). Automated fetching:
- robots.txt (verified, 2516 lines): groups for Googlebot, Bingbot, MSNBot, Slurp, Teoma, Yandex, GPTBot (all with partial path disallows; Google/Bing `Allow: /` apart from search etc.), and finally:
  `User-agent: *` / `Disallow: /`
  So every unnamed crawler (ClaudeBot, CCBot, generic scripts, a Fontes user agent) is disallowed from the entire site. GPTBot has no blanket block but is blocked from many court/tribunal paths (scc-l, fca, onca, bcca, etc.).
- Site is behind DataDome bot protection (verified: 403 challenge to curl).
- Website ToU text unreadable by me; reported to bar bulk/systematic download. Conclusion: scraping full text from canlii.org with Fontes would breach robots.txt and, very likely, the ToU.

## 4. Public statements on AI/LLM use (2023-2026)
- No standalone CanLII AI-use policy found (unverified that none exists; the site was unreadable).
- Litigation: Nov 2024 CanLII sued Caseway AI (BC Supreme Court) alleging bulk scraping of ~3.5M records, ToU breach, copyright infringement. Defendant argued court decisions are public records. Settled, announced about 2026-03-20; terms undisclosed, parties proceed "independently" (The Logic, via WebFetch).
- Takeaway: CanLII actively enforces against AI-driven bulk extraction. No evidence either way on small, per-query, user-keyed use.

## Fit with Fontes
Even if a key is granted, the API gives metadata and citator links only: Fontes could offer case lookup by citation, citing/cited graph, and a link to the canlii.ca page, but could not give an assistant the text of a decision or statute. That makes it a weak Canadian source for answering legal questions. Full text would need other open sources (e.g. Justice Laws Website for federal statutes, court sites); not evaluated here.

## Verdict: usable with limits
Reason: the API is official, free-to-apply and legitimate for a key holder, so a metadata/citator-only tool with per-user keys is plausible. Limits: (a) keys are discretionary and each user must apply (criteria unverified); (b) API terms on commercial use, caching, AI use are unverified because CanLII pages were blocked to me, so Fontes should not ship until someone reads the terms in a browser or asks CanLII in writing; (c) no full text, and website scraping is barred by robots.txt (`User-agent: * Disallow: /`) and reportedly by ToU; (d) CanLII has sued over AI scraping. If the terms turn out to forbid AI/LLM use of API output, the verdict becomes not usable.

## Website Terms of Use, sections 4–5 (text as read 2026-11-10)

- 4.2: legal materials may be copied and used free of charge, provided CanLII is named as the source.
- 5.1 prohibits, among other things:
  - indexing by robots against robots.txt (which disallows all bots except named search engines);
  - "systematic downloading of published documents, including via programmatic means such as … crawlers, plug-ins, extensions, connectors, bots";
  - use for purposes other than the user's legal research or the practice, study or teaching of law.
- **Effect on Fontes:** fetching full text from canlii.org through an MCP server is a "connector" downloading by programmatic means, and robots.txt bars it, so it is **out**. The only open question is the API's own terms (metadata + links only), which are still unread. Verdict unchanged: low value, skip unless the owner wants a metadata-and-links-only Canada source.

## API documentation, read in full (github.com/canlii/API_documentation/blob/master/EN.md, 2026-11-10)

- **Endpoints:**
  - caseBrowse: list the databases; list the decisions in one database by date window, up to 10,000 per call; metadata for one case (title, citation, date, docket, keywords, canlii.ca URL).
  - caseCitator: citedCases, citingCases and citedLegislations; English only.
  - legislationBrowse: lists, plus metadata for one act.
- **No keyword search and no full text.** Fontes could do citation lookup and verification, the citator, and browsing by court and date, with links out to CanLII to read the text.
- **Limits:** HTTPS only; 10 MB per response. The docs state no terms of use, rate limits or licence: those come with the key (unverified).
- **Key:** by message through the canlii.org feedback form, at CanLII's discretion.
- **Possible use:** a "check this Canadian citation and see what cites it" tool. It is useful against hallucinated citations, but it is not search. Low priority.

# NL legislation search (BWB): may we keep using the SRU zoekservice?

Researched 2026-11-05. Read-only; a handful of test requests, no contact made.

## Recommendation

**Keep SRU (`zoekservice.overheid.nl/sru/Search`, x-connection=BWB) for search. Keep the
repository for the text.** No official alternative supports title search without a
blanket `Disallow: /` or a login. Odds that KOOP/Logius objects to low-volume,
user-triggered SRU queries from an honestly labelled client: low (my estimate, about 5–10%).
The service is published *for developers*, with a fair use policy. Odds that the
robots.txt reflects a deliberate ban on API clients: low, but **unverified**. No official
text explains it.

Do these:
1. Record the reasoning in the adapter or the spec. robots.txt on this host is a blanket
   default that KOOP also puts on its other API hosts. The service itself is officially
   documented for programmatic reuse under a fair use policy. Treat it as an API, not a
   crawl target.
2. Stay inside fair use. Send one search per user question, use a small `maximumRecords`
   (≤ 50), never page through the whole collection, and keep the honest User-Agent.
   Note: the UA points at a private GitHub repo URL, so a visitor would get a 404.
3. Optional: to make it airtight, email cup@koop.overheid.nl (named in
   the SRU 2.0 handbook as the address for questions about this service) and ask in writing.
   This is not required by any text found.

## Evidence

### 1. The SRU zoekservice is officially offered for programmatic use
- **"Handleiding SRU BWB"** (KOOP) is linked as a resource on the BWB dataset page,
  https://data.overheid.nl/dataset/basis-wetten-bestand (licence CC-0 1.0, contact
  wetten@overheid.nl). The PDF is
  https://data.overheid.nl/sites/default/files/dataset/ab78ba3f-bc07-49cc-95f2-0e23b8653181/resources/Handleiding%2BSRU%2BBWB.pdf.
  It says: "Dit document beschrijft de SRU-interface voor zoeken binnen het
  basiswettenbestand". The endpoint is `zoekservice.overheid.nl/sru/Search`,
  `x-connection=BWB`. The search field `titel` covers citeertitel, officiële titel and
  niet-officiële titel; operators are `=`, `adj`, `any`, `all`. The default is 50 records.
- **"Handleiding SRU 2.0"** (Logius|KOOP, v1.4, dated 24-06-2025):
  https://data.overheid.nl/sites/default/files/dataset/50aecb9c-75b0-41d9-ae38-dedfad4ad507/resources/HandleidingSRU2.0.pdf.
  It lists BWB on zoekservice.overheid.nl. It says the document is a "technische
  handleiding bedoeld voor ontwikkelaars van partijen die de data op overheid.nl willen
  ontsluiten", and that "Op het gebruik van deze dienst is een fair use policy van kracht."
  For contact it gives cup@koop.overheid.nl and https://www.koopoverheid.nl/contact.
  - The fair use policy text itself was **not found** online, so its limits are unknown.
- The overheid.nl help page "Een eigen kopie van het basiswettenbestand opbouwen",
  https://www.overheid.nl/help/wet-en-regelgeving/een-eigen-kopie-van-het-basiswettenbestand-opbouwen,
  gives example SRU calls used by IND, Belastingdienst and VWS. It says SRU replaces the old
  **BWBIdService** and **OPId2BWBIdService** ("De SRU interface kan deze oude webservice
  vervangen"). So those old services are gone, and SRU is the official successor.
- The dataset https://data.overheid.nl/dataset/open-data-overheid-nl describes the
  zoekdienst as a "technische koppeling (ook wel webservice of API genoemd)" for reuse.
- **No terms text mentions automated access or robots.txt.** None of the pages above say
  anything about it.

### robots.txt (fetched 2026-11-05)
| Host | robots.txt |
|---|---|
| zoekservice.overheid.nl | `User-agent: *` / `Disallow: /` |
| repository.overheid.nl (SRU for officiële publicaties, not BWB) | `User-agent: *` / `Disallow: /` |
| linkeddata.overheid.nl | `User-agent: *` / `Disallow: /` |
| open.overheid.nl | Googlebot allowed on a few pages; `*` Disallow / |
| repository.officiele-overheidspublicaties.nl | 404 (none) |
| zoekdienst.overheid.nl | 404 (none) |
| wetten.overheid.nl | Default allow for `*`, except `/zoeken/zoekresultaat`, `/service/`, `/*/informatie/xml`, etc. Blocks AI bots, **including user-triggered ones (`ChatGPT-User`, `MistralAI-User`, `Claude-Web`)**. Explicitly allows two legal-research bots (`AstralLaw`, `45weg-legal-research`) with Crawl-delay 30. |
| data.overheid.nl | Drupal default plus blocks for AI crawlers (ClaudeBot, GPTBot, …) |
| www.koopoverheid.nl | allows all |

**Is the Disallow aimed at search-engine indexing of an API host? Inference only.** The same
two-line file sits on several KOOP machine-interface hosts (zoekservice, repository.overheid.nl,
linkeddata). The only hosts with tailored files are the human-facing sites (wetten.overheid.nl,
open.overheid.nl), which suggests a default template for API hosts. Against that:
wetten.overheid.nl's file is carefully curated per user agent, so KOOP clearly thinks about
robots. No official text confirms either reading.

### 2. Alternatives checked
| Option | Host | robots | Title search? | Verdict |
|---|---|---|---|---|
| Repository service | repository.officiele-overheidspublicaties.nl/bwb | none (404) | **No.** It serves area/work/expression/manifest only (https://repository.officiele-overheidspublicaties.nl/uitleg_service_officielepublicaties.html) | Keep it for text fetch. It cannot search. |
| BWBIdService / OPId2BWBIdService | (retired) | n/a | n/a | Replaced by SRU, per overheid.nl |
| SRU 2.0 on repository.overheid.nl | repository.overheid.nl/sru | Disallow / | Covers officielepublicaties, sgd, vd, etc., **not BWB** | Same robots issue; wrong collection |
| LiDO linked data | linkeddata.overheid.nl/service/ | Disallow / | Only the deprecated `/regelingonderdeel?str=` searches titles; part of LiDO needs a username/password requested via feedback (https://linkeddata.overheid.nl/front/portal/services) | Worse: same robots, deprecated, partly login |
| wetten.overheid.nl site search | wetten.overheid.nl/zoeken/zoekresultaat | **explicitly Disallowed** | yes (HTML) | Forbidden, and HTML scraping |
| Basisset bulk dump | request via https://www.overheid.nl/contact?subject=wetten_overheid_nl | n/a | (local) | 160 GB, or 14 GB zipped. Bulk download plus a disk index, which breaks project rules |
| New KOOP/Logius BWB API | none found | n/a | n/a | None found. KOOP merges into Logius on 2027-01-01 (https://www.dutchitchannel.nl/news/761886/koop-gaat-per-2027-volledig-op-in-logius), so URLs and contacts may change |

None of these beats SRU on both robots and function.

### 3. Other open-source projects
- **wetsuite** (Dutch legal NLP toolkit) has a `koop_sru.BWB` class built on the KOOP SRU
  handbook, with a 0.5 s backoff "to avoid hammering a server"
  (https://wetsuite.knobs-dials.com/apidocs/wetsuite.datacollect.sru.SRUBase.html).
  It does not mention robots.txt.
- **nl-eli-mcp** (Apache-2.0, https://pypi.org/project/nl-eli-mcp/,
  repo github.com/matematicsolutions/nl-eli-mcp) uses `https://zoekservice.overheid.nl/sru/Search`
  and says it uses "KOOP's official SRU API". It does not mention robots.txt.
- **Ansvar-Systems/Dutch-law-mcp** (https://github.com/Ansvar-Systems/Dutch-law-mcp, now
  archived) bulk-ingests from the "Wetten.overheid.nl BWB API" into SQLite. It does not
  mention robots.txt, and it withholds its database, citing TDM constraints.
- No project I found discussed the zoekservice robots.txt. Coverage is limited: I did not
  inspect every repo's source.

### 4. Contact / registration routes (not used)
- cup@koop.overheid.nl: questions about the SRU service (Handleiding SRU 2.0, contact appendix)
- wetten@overheid.nl: BWB dataset contact (data.overheid.nl)
- servicedesk@koop.overheid.nl, +31 70 7000 526, https://www.koopoverheid.nl/contact
- LiDO credentials: via https://linkeddata.overheid.nl/front/portal/feedback
- No registration or API key exists for SRU. The test call worked without auth:
  `overheidbwb.titel="vreemdelingenwet"` returned 280 records, the first being BWBR0011823.

### Side note for `ai_use`
wetten.overheid.nl and data.overheid.nl opt out AI agents by name (wetten.overheid.nl even
blocks user-triggered agents). The adapter never fetches wetten.overheid.nl, so this does not
block it. But it is a signal for the adapter's `ai_use` field: KOOP does not welcome AI
use of its *websites*. The SRU and repository hosts carry no AI-specific terms.

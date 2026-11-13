# Cyprus (cy): no adapter (checked 2026-11-06)

No usable source, so no adapter was built. Every official host either forbids all robots or
sits behind a bot challenge, and the only full collection (CyLaw) is non-official and its terms
forbid reuse by other services. All checks used the project User-Agent
`world-legal-mcp/0.1.0 (+https://github.com/ykarapazar/fontes)`, through `_http`,
with about one request per host (robots.txt first).

| Host | Role | Result 2026-11-06 |
|---|---|---|
| www.supremecourt.gov.cy | Supreme Court (selected judgments since 2007, Greek) | robots.txt `User-agent: * / Disallow: /` (only Googlebot allowed) |
| www.supremeconstitutionalcourt.gov.cy | Supreme Constitutional Court | same gov.cy robots.txt (458 bytes, `Disallow: /` for `*`) |
| www.law.gov.cy | Law Office of the Republic | same robots.txt, `Disallow: /` |
| www.olc.gov.cy | Office of the Law Commissioner (English translations, partly consolidated) | same robots.txt, `Disallow: /` |
| www.mof.gov.cy | Printing Office / Official Gazette (`/mof/gpo`) | same robots.txt, `Disallow: /` |
| www.gov.cy (and www.cyprus.gov.cy) | Government portal | 403 "Azure WAF JS Challenge" on robots.txt itself |
| www.parliament.cy | House of Representatives (laws passed, as voted) | robots.txt allows `*` (Cloudflare Content-Signal `search=yes, ai-train=no, use=reference`), but `/el` returns 403 `cf-mitigated: challenge` |
| www.data.gov.cy | Open-data portal | robots.txt is a stock Drupal file; no legislation or case-law dataset known, not pursued |
| judiciary.gov.cy, courts.gov.cy, cylegislation.gov.cy, legislation.gov.cy, admincourt.gov.cy | guessed hosts | DNS: no such host |

## CyLaw (cylaw.org): forbidden without written consent

Run by KINOP/CyLII for the Cyprus Bar Association; non-official. robots.txt:
`Disallow: /apofaseis/ /apofaseised/ /clr/ /cgi-bin/` (all case law). `/nomoi/` (as-enacted
law PDFs) is not disallowed by robots, but the terms (`/terms.html`, read 2026-11-06) rule out
any use by this project:

> Το Cylaw δεν είναι μια πηγή άντλησης των σχετικών κειμένων, υπό την έννοια ότι δεν προσφέρει
> υπηρεσία σε εκδότες υλικού ή σε άλλες υπηρεσίες που κάνουν χρήση του πρωτογενούς και
> δευτερογενούς υλικού [...] Οι εκδότες αυτοί και οι διαχειριστές τέτοιων υπηρεσιών θα πρέπει
> να λάβουν τα κείμενα από την αρχική πηγή τους ή με άλλους κατάλληλους εγκεκριμένους τρόπους.

("CyLaw is not a source for drawing the texts, in the sense that it offers no service to
publishers or other services that use the primary and secondary material in its database [...]
Such publishers and operators of such services must obtain the texts from their original source
or by other appropriate approved means.")

> οι ακόλουθες χρήσεις του Ιστοτόπου απαγορεύονται, εκτός κατόπιν εκ των προτέρων γραπτής
> συναίνεσης του ΚΙΝΟΠ: Ενσωμάτωση σε άλλο ιστότοπο ή εφαρμογή (application) [...] μέσω
> [...] επαναχρησιμοποίησης αποτελεσμάτων ή διαδικασιών έρευνας [...]; Δημιουργία εξωτερικού
> ευρετηρίου (external indexing) [...] από διαδικτυακά ρομπότ; Μαζικό ή συστηματικό κατέβασμα
> [...] δια μέσου αυτοματοποιημένης επεξεργασίας

("The following uses are prohibited except with KINOP's prior written consent: incorporation
into another website or application [...] including by reusing search results or processes
[...]; external indexing by web robots; bulk or systematic downloading [...] through automated
processing.")

EU e-Justice (national case law, CY) confirms: "There is no official website on which judgments
are published"; only a selection appears on the Supreme Court site. N-Lex's Cyprus entry points
to CyLaw. Commercial: Leginet "Cyprus Legal Portal" (subscription; out of scope).

## What would unlock Cyprus

- Written consent from KINOP/CyLII (cylaw.org, contact page) for on-demand reading of judgments
  and laws: would give both case law (Supreme Court since 1997 and more) and legislation
  (as-enacted PDFs plus some consolidated HTML, windows-1253).
- Or the gov.cy hosts relaxing `Disallow: /` (Supreme Court, Law Office, Gazette).

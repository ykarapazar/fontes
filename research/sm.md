# San Marino (sm): no adapter (checked 2026-11-06)

No usable source. All requests went through `_http` (honest world-legal-mcp User-Agent).
robots.txt was fetched first on every host. Hosts that returned 403 were not contacted again.

| Host | What it holds | robots.txt (2026-11-06) | Verdict |
|---|---|---|---|
| www.consigliograndeegenerale.sm | Official legislation DB of the Consiglio Grande e Generale (laws, decrees, regulations) | **403 Forbidden** (Apache firewall page) | Blocked; not used |
| www.bollettinoufficiale.sm | Bollettino Ufficiale (official gazette) | **403 Forbidden** | Blocked; not used |
| www.collegiogarante.sm | Collegio Garante della Costituzionalità (constitutional court) decisions | **403 Forbidden** | Blocked; not used |
| www.consigliogiudiziario.sm | Consiglio Giudiziario (judicial reports) | **403 Forbidden** | Blocked; not used |
| www.tribunale.sm | Tribunale website: news, forms, organisational orders. **No decisions** | 404 (no file) | Nothing to build on |
| www.giustizia.sm, www.gov.sm, www.interni.sm | Government portals. **No legislation or case-law database** | 404 (no file) | Nothing to build on |
| www.giurisprudenzarsm.org | "Giurisprudenza Sammarinese": ~2,234 massime/judgments, run by the Istituto Giuridico Sammarinese (Università degli Studi della RSM) under a 2019 protocol with the Tribunale and the Segreterie di Stato | `User-agent: * / Disallow:` (allows everything) | **Login-gated**; not used |

## giurisprudenzarsm.org terms (the only case-law collection)

From https://www.giurisprudenzarsm.org/informazioni:

> "Profilo BASE: profilo di prima registrazione, permette di consultare le massime e il catalogo della biblioteca digitale"
> (BASE profile: a profile you get on first registration. It lets you read the headnotes and the digital library catalogue.)

> "Profilo AVANZATO … consente di consultare e scaricare tutti i contenuti … è riservato a chi vi sia interessato per motivi professionali o di studio … è richiesta la compilazione del modulo di iscrizione, allegando la certificazione"
> (ADVANCED profile: lets you read and download all content. It is only for people with a professional or study interest, and you must fill in a sign-up form with proof of eligibility.)

Even reading the headnotes needs a registered account, and full texts need vetted credentials.
The archive page loads its lists through a login/CSRF-token front end. Under the project rules
(no logins, no sign-ups) it can't be used. It is also non-official: a university institute, not a court.

## What would unlock San Marino
- Asking the Consiglio Grande e Generale and the Bollettino Ufficiale to unblock the
  world-legal-mcp User-Agent (or grant permission) would cover legislation. Collegio Garante
  would cover constitutional case law.
- giurisprudenzarsm.org needs a registered (and, for full texts, credentialed) account. That is a
  sign-up, so it is not done here.

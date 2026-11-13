# Sources that need a key, account or permission

Each item unlocks a source the code can use once the key or permission exists. Keys go in
`.env` (git-ignored).

## Free sign-ups / API keys

| Country | What to register | Where | Unlocks | Env var (to add) | Notes |
|---|---|---|---|---|---|
| France | PISTE account + app subscribed to Judilibre and Légifrance APIs (OAuth2 client credentials) | piste.gouv.fr | Case law (Cour de cassation, appeal courts) + legislation (Légifrance) | `WLM_FR_PISTE_CLIENT_ID` / `_SECRET` | Free. **Done 2026-11-11**: production app "Fontes" created, keys in the local .env, live tests pass. Each user needs their own PISTE app (credentials must not be published). Steps in research/fr.md. |
| New Zealand | Legislation API key, requested by email to the PCO | api.legislation.govt.nz | Legislation | `WLM_NZ_LEGISLATION_KEY` (planned) | Website is behind an AWS WAF challenge, so the API is the only route. |
| South Korea | law.go.kr Open API "OC" id, plus registering the server IP/domain | open.law.go.kr | Case law + legislation | `WLM_KR_LAW_OC` (planned) | IP registration means each self-hoster needs their own. Membership sign-up is open only to Korean citizens (checked 2026-11-11), so out of reach for now. |
| Australia (Queensland) | Queensland legislation API registration | api.legislation.qld.gov.au/api/signup | Queensland legislation | — | Free, CC BY 4.0. State level only. |
| Canada | CanLII API key (ask via the feedback form) | canlii.org/en/feedback/feedback.html (per CanLII's API docs on GitHub) | Case law of every Canadian court and province, plus provincial legislation (now only SCC + federal laws) | `WLM_CA_CANLII_KEY` (planned) | LOW VALUE: API gives metadata + links only, no full text; canlii.org robots.txt disallows all bots, and CanLII sued Caseway AI over scraping (2024). API terms unreadable (DataDome). See research/ca-canlii.md. |
| US | api.data.gov key | api.data.gov | govinfo search beyond DEMO_KEY | `WLM_US_GOVINFO_KEY` | Free. |

## Permissions (an email or application, not a sign-up)

| Source | Ask whom | Unlocks / why |
|---|---|---|
| gb Find Case Law | caselaw@nationalarchives.gov.uk (free computational-analysis licence) | Needed before hosting gb case law. |
| at RIS | announce use to ris.it@bka.gv.at | Anything beyond manual-scale use. |
| de NeuRIS | Federal Ministry of Justice / DigitalService | Turns on de case law (gated). |
| in India Code | Legislative Department, written authorization | Turns on in legislation (gated). |
| sg eLitigation | CrimsonLogic + Supreme Court of Singapore | Turns on sg case law (gated). |
| gr ET Gazette | Εθνικό Τυπογραφείο | Turns on gr legislation (gated). |
| difc | DIFC Courts | Turns on difc (gated). |
| dk Domsdatabasen | Domstolsstyrelsen API application | Danish case law (not built). |
| lv likumi.lv | Latvijas Vēstnesis written consent | Latvian legislation (not built). |
| ua Court register | State Judicial Administration written permission | Ukrainian case law (not built). |
| hu Nemzeti Jogszabálytár | written permission | Hungarian legislation (not built). |

## More permissions (checked 2026-11-06)

| Source | Ask whom | Unlocks / why |
|---|---|---|
| sa MoJ portal | Saudi Ministry of Justice, written approval (moj.gov.sa contact form) | ToS s.4 + linking clause. API works; nothing built. |
| lb legiliban | Université Libanaise CIJ, cij@ul.edu.lb | Full Lebanese legislation (now Constitution only). |
| rs Službeni glasnik | Službeni glasnik, written consent | Serbian legislation (not built). |
| cr Nexus PJ | Poder Judicial de Costa Rica | Costa Rican case law; terms ban robots/AI databases. |
| ph SC E-Library | libraryservices.sc@judiciary.gov.ph | Official Philippine text (now LawPhil, non-official). |
| co Gestor Normativo | Departamento Administrativo de la Función Pública, written consent | Consolidated Colombian legislation. Terms ban automated copying without written consent. Adapter built, OFF unless `WLM_PERMITTED=co`. |
| eg Court of Cassation | Court of Cassation: written approval + paid subscription | Egyptian Cassation case law. Paid, so low priority. |

Open questions (not sign-ups):
- az: e-qanun.az needs a Referer header (hotlink protection). Adapter built, OFF.
- bh: LLOC terms bar use "for other purposes". Adapter built, OFF.
- eaeu: courteurasian.org returns 403 to any User-Agent carrying a contact link (`Fontes/… (+https://…)`), 200 only without one (2026-11-06). We will not strip our contact link to pass a bot filter. Decision: not in the release.
- vn: precedents site sends an incomplete certificate chain; could pin the missing intermediate CA.

Skipped: Montenegro Regis (paid).

## More permissions (checked 2026-11-06, 2)

| Source | Ask whom | Unlocks / why |
|---|---|---|
| qa Al Meezan (MoJ) | Qatar Ministry of Justice, written permission | Qatari legislation + Court of Cassation rulings. JSON API endpoints already mapped in research/qa.md; nothing built. |
| qa QICDRC | Qatar International Court, written permission | English-language QICDRC judgments. Its robots.txt welcomes AI crawlers, so a yes looks likely (unverified). |
| itlos Reports | ITLOS Registrar (via the disclaimer page) | Text of ITLOS judgments/orders/advisory opinions. Adapter gives case records + PDF links only. About 30 lines to add once allowed. |
| jo lob.gov.jo | Legislation and Opinion Bureau | Jordanian legislation. The site encrypts its API on purpose; no route without their consent. |
| jo cco.gov.jo | info@cco.gov.jo (only if hosted commercially) | Constitutional Court terms allow non-commercial use only. |
| wto | WTO (inform them, per copyright page) | Not a permission, a notification required before public hosting. |

Open questions:
- dz: Constitutional Court site omits its intermediate certificate (same problem as vn). A working implementation is saved; it needs `_http` to use the OS trust store (truststore) or pin the cert.
- icj: every PDF sits behind a Cloudflare bot challenge, so ICJ gives records and links only. No sign-up exists.

## More permissions (checked 2026-11-06, 3)

| Source | Ask whom | Unlocks / why |
|---|---|---|
| my case law (ejudgment.kehakiman.gov.my) | Chief Registrar's Office, Federal Court of Malaysia (express prior written consent) | Malaysian case law. JSON search exists; full texts sit on an efs path robots.txt disallows. |
| my legislation (lom.agc.gov.my) | Attorney General's Chambers (contact.php) | Malaysian legislation. Responses are encrypted on purpose and robots.txt is unreachable (treat as disallow). |

Skipped (paid): ba csd.pravosudje.ba (ordinary-court case law), ba sluzbenilist.ba / slglasnik.org (state and Republika Srpska gazettes). ba parlament.ba state laws: robots.txt disallows the law pages.
- pk: Pakistan Code legislation is written but inactive. pakistancode.gov.pk sends the wrong intermediate certificate (needs "GoGetSSL RSA DV CA"). Same shared `_http` fix as vn/dz/ch: pin the intermediate or fetch missing ones.
- pk: Sindh High Court case law (caselaw.shc.gov.pk) needs a login; whether registration is public is unverified. Supreme Court site blocks automated clients (Akamai 403).

## More permissions (checked 2026-11-06, 4)

| Source | Ask whom | Unlocks / why |
|---|---|---|
| uz lex.uz | "Adolat" National Legal Information Centre (Ministry of Justice), written permission | Terms: "personal purposes only". Adapter built (case law + legislation), ON with a "personal use only" warning on every result (decided 2026-11-06). |
| kg cbd.minjust.gov.kg | Ministry of Justice of Kyrgyzstan: allow the project User-Agent | Kyrgyz legislation. Server drops the connection for our honest client; robots.txt allows everything. |
| li gerichtsentscheide.li | Liechtenstein courts (kontakt@stgh.li) | Liechtenstein case law. robots.txt `Disallow: /` on both decision sites. |
| do consultoria.gov.do | Consultoría Jurídica del Poder Ejecutivo | Dominican legislation (laws, decrees, Gaceta). Search API sits behind a Cloudflare challenge; terms ban scraping that degrades service. |
| do Tribunal Constitucional / Poder Judicial | each court's IT office: allow the project User-Agent | Dominican constitutional and ordinary case law. Azure WAFs return 406/403. |
| cy cylaw.org | KINOP / CyLII (Cyprus Bar Association), prior written consent via cylaw.org contact page | Cypriot case law (Supreme Court 1997–) + legislation. Non-official; every gov.cy host has robots `Disallow: /`. |
| bo TSJ Génesis API (apigenesis.tsj.bo) | Tribunal Supremo de Justicia: API access for the project | Bolivian Supreme Court case law. Public JS carries a hard-coded key; not used (would impersonate their client). |
| bo Tribunal Constitucional (buscador.tcpbolivia.bo) | TCP: explicit permission or an official API | Constitutional case law. Requests need app-computed hashes + captcha. |
| sv jurisprudencia.gob.sv | Corte Suprema, Centro de Documentación Judicial: allow the project User-Agent through Cloudflare | Salvadoran case law (and likely consolidated legislation). |
| gt Corte de Constitucionalidad (consultajur.cc.gob.gt) | CC: allow the project User-Agent through Cloudflare | Guatemalan constitutional case-law search (now fetch-by-id only). |
| gt Congreso / Organismo Judicial (CENADOJ) | each body's IT office: allowlist the project | Guatemalan legislation and Supreme Court case law (Incapsula / WAF / broken TLS). |
| pa Órgano Judicial | Panama judiciary IT: allow the project User-Agent | General Panamanian case law (now only Gazette-published Supreme Court rulings). |
| tm Adalat (law.minjust.gov.tm) | Account login on the Ministry of Justice legal database | Turkmen ministry-level regulations and more consolidated texts. |
| cv Boletim Oficial (boe.incv.cv) | Prior written authorisation from INCV (terms clause 6 forbids copying without it) | Cabo Verde's full national gazette (now only ~30 acts hosted by the Tribunal Constitucional). |
| bj CDIJ legis.cdij.bj | Written consent from the Centre de Documentation et d'Information Juridique (Ministry of Justice) | Benin's law database (search beyond SGG's promulgated texts). |
| mz MozLex (mozlex.ts.gov.mz) | Tribunal Supremo / CSM-ALTEC: written permission for automated access (robots.txt bans scraping) | Mozambique's best consolidated legislation database. |
| ad Portal Jurídic d'Andorra | BOPA service (Govern): permission for automated use | Consolidated Andorran laws and regulations. Adapter built, ON with a "personal use only" warning on every result (decided 2026-11-06) (terms: "Només està autoritzat l'ús personal", personal use only). |
| ad BOPA (bopa.ad) | BOPA: an official API key or open endpoint | Official gazette. Terms are permissive; the only route is an API keyed with function keys from its public JS, which we don't use. |
| kh moj.gov.kh / ccc.gov.kh / ocm.gov.kh / senate.gov.kh | each body: allow the project User-Agent (firewall "Request Rejected" on robots.txt) | Cambodian legislation beyond CDC business laws (Royal Gazette) and Constitutional Council decisions. |
| mu supremecourt.govmu.org | Supreme Court of Mauritius (Judiciary): confirm automated use is fine | Mauritian subordinate-court judgments (2020–) + Acts/GNs as enacted (2024–). Adapter built, ON with a "personal use only" warning on every result (decided 2026-11-06): disclaimer says "maintained for your personal use and viewing", though terms §3 allow free reproduction "in any format or medium" with attribution. |
| mu Attorney General Revised Laws | Solicitor General (sgo@govmu.org, unverified) | Consolidated Mauritian laws to 2017. Terms need prior approval for commercial use. |
| sm Consiglio Grande e Generale / Bollettino Ufficiale / Collegio Garante | each body: allow the project User-Agent (403 firewall on robots.txt) | San Marino legislation and constitutional case law. Only other case-law route, giurisprudenzarsm.org (university, non-official), needs an account; full texts need professional credentials. |
| tt Judiciary (ttlawcourts.org) | Judiciary of Trinidad and Tobago: permission for automated use | Trinidad and Tobago case law (~8,800 judgments). Adapter built, ON with a "personal use only" warning on every result (decided 2026-11-06) (terms: site "maintained for your personal use and viewing"). |
| by pravo.by | National Centre of Legal Information (НЦПИ): allow the project client | Consolidated Belarusian laws and codes. Firewall returned 403 on the first request (robots.txt). |

Open questions:
- mc: the gouv.mc portal CGU bans reuse without authorisation, but defines "Site" as that portal only. legimonaco.mc has no terms, so the adapter is ON. Confirm that reading before public hosting.
- li: gesetze.li sets a NetScaler cookie by script but serves full content without it; treated as not a challenge.
- mn: shuukh.mn returns a huge page (16–95 MB) instead of 404 for a non-existent decision id. Fixed 2026-11-06: `_http` size cap, mn stops reading at 5 MB and reports Not found.
- mn: legalinfo.mn (legislation) unreachable from a UK IP 2026-11-05/06; reachable again 2026-11-07, not built yet.
- pa: www.asamblea.gob.pa has the same missing-intermediate problem as vn/dz/ch/pk (not needed: legispan works).
- bo: Gaceta Oficial (gacetaoficialdebolivia.gob.bo) doesn't resolve on the local DNS; check robots/terms from another network. Would give fuller Bolivian legislation than the 2010–2023 Chamber of Deputies set.
- sv: asamblea.gob.sv (legislation) has the same missing-intermediate certificate problem (Sectigo OV R36). Fixable only by the shared TLS decision or on their side.
- jm: laws.moj.gov.jm (only consolidated Jamaican legislation) omits the DigiCert G2 intermediate: same shared TLS decision as vn/dz/ch/pk/sv.
- hn: poderjudicial.gob.hn / cedij (case law) timed out from the UK; retest from another network. congresonacional.hn certificate is for the wrong hostname.
- tt: rgd.legalaffairs.gov.tt fails TLS; not needed (laws.gov.tt works). Confirm the "personal use" reading (gated like uz) before deciding.
- by: court.gov.by, kc.gov.by, etalonline.by, house.gov.by, minjust.gov.by time out from the UK; retry from another network. government.gov.by certificate is for the wrong hostname.
- mu/tt/uz: decide one reading of "personal use" wording. Gated in all three now. mu is the weakest case (§3 allows reproduction in any format); under a lighter reading, mu and tt would get a warning only.
- ad: justicia.ad (ordinary courts) fails TLS (issuer certificate missing): same shared TLS decision.
- tj: adlia.tj (Ministry of Justice laws database), parlament.tj and sud.tj time out from the UK; retry from another network. minjust.tj has an expired certificate.
- sc: no Court of Appeal decisions online (judiciary.sc table empty); no consolidated laws (only SeyLII, excluded); legalaffairs.gov.sc does not resolve. Pre-2020 gazette items only by paid email request.
- gy: search on mola.gov.gy only answers with the `X-Requested-With: XMLHttpRequest` header its own page sends; the adapter sends it with the honest User-Agent. Open whether that is acceptable. supremecourt.gy has no judgments online; Official Gazette not yet checked.
- bt: case law hosts (judiciary.gov.bt) time out; nab.gov.bt wrong-host certificate (shared TLS decision).
- mv: all judgment hosts (dja.gov.mv, highcourt.gov.mv, old.supremecourt.mv) sit behind Cloudflare challenges. Only route would be asking the Department of Judicial Administration.
- bz: no decision dates in the source (only "posted on site").
- la: Gazette texts are image-only PDFs; full text would need OCR (not allowed by the brief). Metadata search only. moj.gov.la robots disallows all.
- mg: ordinary courts (Cour Suprême) have no online decisions; Journal Officiel scans need a login; justice.gov.mg wrong-host certificate (shared TLS decision).
- ci: sgg.gouv.ci (Journal officiel) and coursupreme.ci have expired certificates (shared TLS decision). Conseil constitutionnel decisions (robots allows, Crawl-delay 10) not yet wired in. One full party name unredacted in Cour de cassation arrêt 201/24 (source-side).
- cm: no Constitutional Council website found; many recent prc.cm acts are image-only scans (OCR not allowed). minjustice.gov.cm unreachable.

- mz: mozjuris.ts.gov.mz (case-law DB incl. Administrative Tribunal) behind an Anubis bot challenge; inm.gov.mz (Boletim da República) TLS chain incomplete (shared TLS decision). 2018 Constitution PDF has broken font encoding.
- sr: decided 2026-11-06 to follow dna.sr's lax auteursrechten page (copy with source link). Legislation is on with an attribution warning; commercial use still needs permission.
- cu: Tribunal Supremo Popular (tsp.gob.cu) terms forbid automated access, and it has no decision database anyway. gacetaoficial.gob.cu unreachable from the UK; retry from another network. Coverage is only the 64 Gazette issues MINJUS reposts.

- bj: Constitutional Court keyword search is broken at the source (Algolia 500); only number/applicant/type-year search works. Cour suprême publishes no decisions; Assemblée nationale in maintenance.
- cv: TC search returns at most 50 newest title matches (use a year filter); STJ only ~360 selected judgments 2021–26; legislation is BO PDF copies, not consolidated. kiosk.incv.cv has an expired certificate.
- et: legislation only (HoPR library, Amharic titles, Ethiopian-calendar years; English text inside PDFs). Federal Supreme Court cassation site (fsc.gov.et) unreachable; moj.gov.et expired certificate.
- ve: nothing built. TSJ refuses foreign connections; Asamblea Nacional page 2 returned 403; gacetaoficial.gob.ve stopped answering after ~9 requests. Retry Gaceta later from a fresh network with ≥3 s spacing.
- ht: legislation only, ~17 laws from the CSPJ library (6 are scans). Cour de cassation arrêts database is empty; parlementhaitien.ht certificate is for a different host. Re-check courdecassation.ht later.
- iq: Kurdistan Region legislation only (legislation.krd). Federal sources (iraqfsc.iq, parliament.iq, hjc.iq, iraqld) all behind Cloudflare challenges or 403; moj.gov.iq times out.
- af: legislation only (laws.moj.gov.af, de facto authority's site; warning set). Pre-2021 PDFs are legacy-font or scans, so no text. Supreme Court decisions page empty.
- ly: legislation only (Ministry of Justice selection, ~190 laws, not the Gazette). supremecourt.gov.ly behind a Sucuri error page; lawsociety.ly (private) terms page behind a Cloudflare challenge.
- mm: legislation only, 29 documents posted by the Supreme Court (CPC/CrPC in English). Court rulings sites (rcms/cjs/elib.usc.gov.mm) have incomplete certificate chains (the shared TLS issue); mlis.gov.mm times out. myanmar-law-library.org needs prior permission even to link.
- sn: built (Conseil constitutionnel 41 decisions + Constitution, primature.sn ~40 texts) but NOT merged: conseilconstitutionnel.sn has timed out on every request since 2026-11-06 ~10:07. Re-run tests later.
- ps: case law + legislation from Maqam (An-Najah University, NON-OFFICIAL academic; flagged). Official hosts (courts.gov.ps, lab.pna.ps, tscc.pna.ps) unreachable from the UK, maybe geo-filtered (unverified); retry from another network. Maqam advanced search is login-only (not used); its error pages run with Django debug on.
- tm: Mejlis laws/codes (tk + ru) + Constitution and 87 Supreme Court Plenum guiding resolutions (court.gov.tm). No individual judgments published. mejlis.gov.tm sometimes cuts off large pages (Civil Code). Adalat database needs a login.

# Serbia (rs): sources checked 2026-11-06

| Host | Use | robots.txt | Terms | Built |
|---|---|---|---|---|
| www.vrh.sud.rs (Supreme Court practice DB) | case law | `Crawl-delay: 10`; disallows `/search/` (Drupal search) only; Solr results + decision pages allowed | No terms page; footer: "Celokupan materijal dostupan na sajtu, zaštićen je autorskim pravima čiji je ekskluzivni nosilac Vrhovni kasacioni sud - Vrhovni sud." Silent on automation. | yes (`search_caselaw`, `get_decision`), 10 s spacing |
| pravno-informacioni-sistem.rs (state PIS, run by JP Službeni glasnik) | legislation | only `Allow: /eli/rep/*` lines | Terms (fp.pravno-informacioni-sistem.rs/api/prins/GetStaticPageByCode/TermsOfService): "Строго је забрањено коришћење било каквих аутоматизованих система, софтвера или процеса у сврху извлачења, индексирања или складиштења података са овог система. ... дозвољено је искључиво уз претходну изричиту писану сагласност Гласника." | no: needs written consent |
| www.ustavni.sud.rs/ustav-rs-i-propisi/ (Constitutional Court) | Constitution (consolidated, Amendments I-XXIX), 2006 Constitutional Law, Law on the Constitutional Court (unofficial consolidated) | `User-agent: *` disallows only /admin/, /account/, /upload/document/ etc.; law pages allowed | no terms page; footer "© Република Србија Уставни суд" (checked 2026-11-10) | yes (legislation methods), 1 s spacing |
| www.parlament.gov.rs (laws as adopted, PDF/DOC) | legislation (as passed) | PDFs under /upload/archive/files/*/pdf/ allowed | no terms page found | no: lists only the current convocation (14th, 2024-), no consolidation, no codes |
| sudskapraksa.sud.rs (unified case-law base) | case law | connection timed out | not read | no |
| paragraf.rs | commercial | - | - | not used |

# Fontes user-facing languages

`research/languages.json` is the list; `scripts/languages.py` rebuilds it (needs network: reads
CLDR from jsDelivr). `scripts/i18n_check.py` reports progress against it.

## Rule

Every language in the list is **required**: the 10 most-spoken languages in the world, plus
every official language of every jurisdiction Fontes covers. Tiers only set the order of work.

- **Tier 1 (12):** en, zh-Hans, hi, es, ar, fr, bn, pt, id, ur, tr, pt-PT. The 10 most-spoken
  languages, plus Turkish (installer text already existed) and European
  Portuguese (both Portuguese norms are required).
- **Tier 2 (68):** every other official or working language of a covered jurisdiction.
- **Total: 80.** Right-to-left: ar, ur, fa, ps, he, ckb, dv. Non-Latin scripts: 33 (see the
  `script` / `non_latin` fields).

## Sources

- **Official languages per jurisdiction:** Unicode CLDR 49 `supplemental/territoryInfo.json`
  (cldr-core 49.0.0), languages with `_officialStatus` `official` or `de_facto_official`.
  `official_regional` and unmarked languages are not included (exception below).
- **Supranational courts** (no CLDR territory): their working languages, written into
  `scripts/languages.py` with the basis for each (ECHR en/fr; ICJ en/fr; ITLOS en/fr; ICSID and
  WTO en/fr/es; ECOWAS Court en/fr/pt; EFTA Court and CCJ en; CJEU all 24 EU languages; UN Treaty
  Collection the six UN languages; DIFC en plus the UAE's ar). **Unverified:** the African Court's
  working languages (en/fr/ar/pt listed: the AU official languages; judgments seen mostly in
  en/fr).
- **Speaker ranking:** Ethnologue 2026 total speakers (L1+L2), as tabulated by Wikipedia's
  "List of languages by total number of speakers" (retrieved there 2026-03-08). **Unverified
  against Ethnologue itself** (paywalled). Top 10: English 1,493 M, Mandarin 1,183 M, Hindi 611 M,
  Spanish 561 M, Standard Arabic 335 M, French 334 M, Bengali 274 M, Portuguese 269 M,
  Indonesian 255 M, Urdu 246 M. Russian (210 M) is 11th. Mandarin is served as Simplified Chinese
  (zh-Hans); Standard Arabic as `ar`.
- **Tier 2 order:** CLDR population × percentage summed over territories (`cldr_speakers_estimate`),
  a rough figure used only for ordering.

## Codes and decisions

- Codes are BCP 47 as Fontes uses them for file names: `zh-Hans`, `zh-Hant`, `sr` (Cyrillic) and
  `sr-Latn`, `bs` and `bs-Cyrl`, `uz` and `uz-Cyrl`, `nb` and `nn` (CLDR's `no` is the
  macrolanguage), `zgh` for Morocco's Amazigh (CLDR `tzm`; the official standard is IRCAM's
  Standard Moroccan Tamazight in Tifinagh), `hak-Hant` and `nan-Hant` (Taiwanese Hakka and Hokkien, which CLDR marks de_facto_official for
  Taiwan; autonyms are Taiwan Ministry of Education names, not CLDR). Machine translation into
  these, `zgh`, `dz`, `dv`, `ay`, `gn`, `qu` and the second scripts (`uz-Cyrl`, `bs-Cyrl`) is
  likely weak (unverified); they need a human check.
- **Added outside CLDR's official set:** Central Kurdish (`ckb`) for Iraq: Constitution art. 4
  makes Arabic and Kurdish the two official languages and the `iq` adapter covers the Kurdistan
  Region; CLDR marks ckb only `official_regional`.
- **Dropped:** `gsw` (Swiss German; Switzerland and Liechtenstein write Standard German, no
  written standard to translate into); `az_Cyrl` (Azerbaijan moved to Latin script; nothing
  official is written in Cyrillic). Not added: Romansh (`rm`, CLDR `official_regional` in
  Switzerland) and Montenegrin (`cnr`, not in CLDR's official data for ME; me uses sr-Latn).
- **Two Portuguese files**: `pt` is Brazilian Portuguese (Brazil only), `pt-PT`
  European Portuguese (Portugal, Angola, Mozambique, Cabo Verde and every other CLDR territory
  with official Portuguese, plus the supranational courts that work in Portuguese: African Court,
  ECOWAS Court, CJEU). Fallbacks: pt-BR → pt; pt-PT, pt-AO, pt-MZ (any pt-XX but BR) → pt-PT → pt.
- One Spanish (`es`), one French (`fr`), one Arabic (`ar`): regional variants fall back to these.
- `fr` (France) is counted although its adapter is still being built (`PENDING`).

## What gets translated

Installer and `fontes report-bug` text (`installer/locales/<lang>.json`), the Claude Desktop
extension description (same file, `mcpb_*` keys), and for docs: README.md, INSTALL.md, PRIVACY.md,
the landing page, the status page (one page, `docs/status/index.html`, carrying every language's
strings; the browser picks the language, `?lang=<code>` forces one) and a COVERAGE.md summary
(counts and scorecard, linking to the full English file); the last two from string tables, data
rows as they are. **English only:** `docs/HEALTH.md` and `docs/ADAPTER_SPEC.md`
(developer and maintainer documents). Details: `docs/i18n/TRANSLATING.md`.

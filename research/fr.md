# France (fr): PISTE / Judilibre + Légifrance

Adapter: `src/world_legal_mcp/jurisdictions/fr.py`. It stays **inactive** (no tools, no coverage, and a
"needs free PISTE account" note in `list_jurisdictions`) until both `WLM_FR_PISTE_CLIENT_ID` and
`WLM_FR_PISTE_CLIENT_SECRET` are set. `WLM_FR_PISTE_SANDBOX=1` switches to the sandbox hosts.
Tested against the live production API on 2026-11-11: `tests/live/test_fr.py` (7) and the
France conformance checks (6) pass. Run `scripts/catalogue.py` with the keys loaded
(`set -a && . ./.env && set +a`), otherwise France drops out of docs/COVERAGE.md.

## Sources

| | Judilibre (Cour de cassation) | Légifrance (DILA) |
|---|---|---|
| Covers | Cour de cassation, cours d'appel, and some tribunaux judiciaires / de commerce / CPH | Codes (LEGI), laws and decrees (LODA), Journal officiel (JORF); case law: Conseil d'État, CAA, TA selection, Tribunal des conflits (CETAT), Conseil constitutionnel (CONSTIT) |
| Spec | OpenAPI 3.0.2 v1.2.5, `github.com/Cour-de-cassation/judilibre-search/blob/dev/public/JUDILIBRE-public.json` | Swagger 2.0 v1.6.2.5, `raw.githubusercontent.com/betagouv/api_gouv_swaggers/main/swaggers/api-legifrance-v2.json` (linked from the data.gouv.fr dataservice) |
| Prod base | `https://api.piste.gouv.fr/cassation/judilibre/v1.0` | `https://api.piste.gouv.fr/dila/legifrance/lf-engine-app` |
| Sandbox base | `https://sandbox-api.piste.gouv.fr/cassation/judilibre/v1.0` | `https://sandbox-api.piste.gouv.fr/dila/legifrance/lf-engine-app` |
| Endpoints used | `GET /search`, `GET /decision?id=` | `POST /search`, `POST /consult/legiPart`, `POST /consult/getArticleWithIdAndNum`, `POST /consult/juri`, `POST /consult/jorf` |
| Auth | PISTE OAuth2 client credentials | same |

Token: `POST https://oauth.piste.gouv.fr/api/oauth/token` (sandbox: `sandbox-oauth.piste.gouv.fr`) with form fields
`grant_type=client_credentials`, `client_id`, `client_secret`, `scope=openid`. This comes from the PISTE user guide
(`piste.gouv.fr/images/com_apiportal/documentation/UserGuide_navigation_EN.pdf`). The token is cached until
`expires_in - 60 s` and refreshed once on a 401.

## Terms (checked)

- **Licence Ouverte / Etalab 2.0** covers the data of both APIs. Reuse, including commercial reuse, is allowed with attribution.
- **Légifrance API CGU** (DILA, v1.1, 04/08/2020; `piste.gouv.fr/images/cgu/DILA_Legifrance_Beta_v2.pdf`), read in full:
  - Free. Accepted in two steps: the PISTE CGU at sign-up, then these CGU when the API is chosen.
  - OAuth 2.0. Credentials must not be published, and compromised credentials must be reported.
  - Beta service with no availability guarantee. DILA can suspend an account.
  - Quotas per second, minute and day, visible in PISTE under "API Sélectionnées > Actions > Consulter les quotas".
  - Commercial use is allowed under Etalab 2.0 at the user's own risk.
  - The data are **not authentic or opposable**: only the signed JO PDF is. The adapter shows this as a source warning.
  - Contact: retours-legifrance-modernise@dila.gouv.fr.
- **Judilibre**:
  - The repo README states Licence Ouverte 2.0 plus the PISTE CGU and the Cour de cassation reuse CGU. Quotas are listed as "prochainement sur PISTE".
  - justice.gouv.fr (`/documentation/open-data-decisions-justice`) adds two conditions:
    - Judges' and clerks' identity data may not be reused to evaluate, analyse, compare or predict their professional practice. This is COJ art. L111-13, a criminal offence.
    - Reusers must comply with GDPR and must not re-identify the pseudonymised parties.
  - The adapter shows both conditions as a source warning.
- **Not read (blocked):**
  - The PISTE portal CGU PDF (`developer.aife.economie.gouv.fr/.../cgu_portal_FR.pdf`) did not resolve.
  - The Cour de cassation reuse CGU page on courdecassation.fr needs JavaScript, and that site's HTML is not to be scraped.
  - The GitHub `CGU.md` link from justice.gouv.fr returns 404.
  - Whoever subscribes sees and accepts these texts on PISTE. Read them then.
- `ai_use` is left as `None` (unknown): none of the texts read mentions AI or ML use.

## Verified

Verified live on 2026-11-11 (production app):
- Judilibre accepts the OAuth `Authorization: Bearer` token.
- Sample decision `5fca7d162a251e6bf9c78514` exists in prod; fetching it by id and by its
  `courdecassation.fr/decision/{id}` URL gives the same text.
- Appeal-court filter (`jurisdiction=ca`) with `date_start`.
- Légifrance search for codes and LODA texts, and Code civil article 1240 via `getArticleWithIdAndNum`.

Verified from the specs:
- Judilibre `/search` parameters:
  - `query`, `jurisdiction`, `chamber`, `date_start`, `date_end`, `sort`, `operator`, `resolve_references`.
  - `page` (0-based) and `page_size`.
  - The tutorial gives 25 as the per-page maximum and 10,000 as the overall results cap.
- Judilibre response fields: `total`, `results[].id/number/ecli/decision_date/summary/highlights`, `/decision` `text`/`visa`/`zones`.
- Légifrance request and response schemas: SearchRequestDTO, ConsultTextResponse, and the article response.
- OAuth token URLs and form body.
- The prod Légifrance path `/dila/legifrance/lf-engine-app`, which differs from the swagger's `legifrance-beta` sandbox basePath. The prod path is confirmed by SocialGouv/dila-api-client.

Still unverified:
- Légifrance search details beyond what the tests check:
  - the `DATE_VERSION` facet with epoch-ms `singleDate`;
  - `sort: "PERTINENCE"`;
  - the `sections[].extracts[]` snippet shape.
  These come from DILA's usage examples, read through a third-party transcription, because legifrance.gouv.fr returned 403.
- legiPart response size and timing for very large codes such as the Code civil.
- Public URL patterns: `legifrance.gouv.fr/codes/texte_lc|article_lc/…`, `/loda/id/…`, `/jorf/id/…`.
- Actual quotas. `min_interval` is set to 1 s per host to be safe.

## Légifrance case law and JORF (added 2026-11-11, verified live)

- `search_caselaw` with `jurisdiction` = `ce`, `caa`, `ta`, `tc` searches fond CETAT; `constit` searches fond CONSTIT.
  These cannot be mixed with the Judilibre codes in one call.
- Court filter: the Swagger's `JURIDICTION_NATURE` facet returns HTTP 500 for plain `valeurs` (tried
  CONSEIL_ETAT, COURS_APPEL, TRIBUNAL_ADMINISTATIF/-TRATIF, TRIBUNAL_CONFLIT). It does work with
  `multiValeurs` (e.g. `{"COURS_APPEL": ["Lyon"]}`), but the adapter uses an exact `TITLE` phrase instead
  ("Conseil d'État"; "CAA" or "Cour administrative d'appel"; "Tribunal administratif"; "Tribunal des conflits").
  Title matching ignores accents and case.
- Dates: facet `DATE_DECISION` with `dates: {start, end}`. Sort: `DATE_DESC` or `PERTINENCE`.
  Operators: `TOUS_LES_MOTS_DANS_UN_CHAMP` (and, default), `UN_DES_MOTS` (or), `EXACTE`.
- Decisions: `POST /consult/juri {"textId": "CETATEXT…|CONSTEXT…|JURITEXT…"}`. Search hits have no
  date or number, so both are parsed from the title.
- Counts on 2026-11-11 (title filter only): CE 174,277 (from 1875), CAA 390,805 (from 1989),
  TA 6,514 (1965–2009 only, a selection), TC 1,838 (from 1873), CONSTIT 7,423 (from 1958).
  The full TA output since 2022 is only in the bulk XML at opendata.justice-administrative.fr (not built).
- JORF: `search_legislation` with `fond=jorf` (no `DATE_VERSION` filter: it does not apply). For a
  JORF-only text, `consult/legiPart` answers 400, so `_text` falls back to `POST /consult/jorf
  {"textCid": …}` (the version as published). `getArticleWithIdAndNum` returns `article: null` for
  JORFTEXT ids, so article lookup in those texts walks the text instead.
- Unverified: the public URL patterns `/ceta/id/`, `/cons/id/`, `/juri/id/`, `/jorf/article_jo/`.

## Steps on piste.gouv.fr

1. Create an account at piste.gouv.fr. This means accepting the **PISTE CGU**.
2. Under API > **Consentement CGU API**, accept the CGU for **JUDILIBRE** and **Légifrance**, production and also sandbox if wanted. These are the **Judilibre CGU** (with the Cour de cassation reuse terms) and the **DILA Légifrance API CGU v1.1**. Both data sets are under Licence Ouverte 2.0.
3. Create a **production application**. The auto-created APP_SANDBOX has no production rights. Under "Modifier l'application", tick **JUDILIBRE (production)** and **Légifrance (production)**, then apply.
4. On the app's **Authentification** tab, copy the OAuth `client_id` and `client_secret` into `.env` as
   `WLM_FR_PISTE_CLIENT_ID` and `WLM_FR_PISTE_CLIENT_SECRET`. For a sandbox app, add `WLM_FR_PISTE_SANDBOX=1`.
5. Check the limits under API Sélectionnées > Actions > Consulter les quotas, then run `uv run pytest tests/live/test_fr.py`.

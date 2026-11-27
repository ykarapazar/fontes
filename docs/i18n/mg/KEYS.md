> Fandikan-teny natao tamin'ny fanampian'ny milina ity. Ny dikan-teny anglisy no manan-kery.

# Fanalahidy API

Mandeha tsy misy fanalahidy ny saika loharano rehetra ao amin'ny Fontes. Telo no mila fanalahidy maimaim-poana:

| Fanalahidy | Manokatra | Raha tsy misy azy |
|---|---|---|
| `WLM_FR_PISTE_CLIENT_ID` + `WLM_FR_PISTE_CLIENT_SECRET` | Frantsa: Judilibre (didim-pitsarana) sy Légifrance (lalàna) | Maty i Frantsa. Asehon'ny `list_jurisdictions` ho tsy mavitrika izy. |
| `WLM_US_GOVINFO_KEY` | Etazonia: fikarohana govinfo (heviny navoakan'ny fitsarana federaly, Statutes at Large, public laws) | Mampiasa ny `DEMO_KEY` iombonana ny Fontes: fikarohana 10 eo ho eo isan'andro isaky ny adiresy IP. Tsy ilaina ny fanalahidy hanokafana didim-pitsarana fantatra sy ny US Code. |
| `WLM_US_COURTLISTENER_KEY` | Fitsarana ao amin'ny fanjakana Amerikana (`us-states`): didim-pitsarana avy amin'ny fitsarana tampony sy fitsarana ambony ao amin'ny fanjakana 50 sy DC rehetra, avy amin'ny CourtListener | Maty ny jurisprudence an'ny fitsarana ao amin'ny fanjakana Amerikana. Aseho ho tsy mavitrika ao amin'ny `list_jurisdictions` izy. |

Tsy voatery ireo fanalahidy. Azonao ampiana any aoriana izy ireo.

## Fanampiana fanalahidy

**Amin'ny mpametraka.** Rehefa voapetraka ny Fontes, manolotra ny hanampy fanalahidy ny mpametraka. Amin'ny
Mac, tsindrio ny **Hanampy fanalahidy**, na ny **Vita** handinganana; amin'ny Windows, valio ilay fanontaniana
(tsindrio ny Enter handinganana). Raha hanampy na hanova fanalahidy any aoriana, alefaso ny
**Add or change keys**:

- Mac: sokafy indray ny rindranasa Fontes Installer ary safidio ny **Hanampy na hanova fanalahidy**.
- Windows: sokafy ny menu Start, avy eo **Fontes** → **Hanampy na hanova fanalahidy**.

Tsy aseho ny soratanao. Ho an'ny fanalahidy tsirairay: apetaho izy, tsindrio ny Enter hitazonana izay efa
eo, na soraty ny `-` hanesorana azy. Miditra ao amin'ny rindranasa rehetra efa manana ny Fontes ireo
fanalahidy.

**Amin'ny fanitarana Claude Desktop (.mcpb).** Sokafy ny Claude > Settings > Extensions > Fontes ary fenoy
ireo saha. Tsy voatery avokoa izy rehetra.

**Amin'ny tanana.** Ampio ireo variables ao amin'ny bloc `env` an'ny fidirana `fontes` ao amin'ny
fandrindrana MCP an'ny rindranasanao:

```json
"fontes": {
  "command": "...",
  "args": ["..."],
  "env": { "WLM_US_GOVINFO_KEY": "your-key" }
}
```

Akatony ary sokafy indray ilay rindranasa aorian'ny fanovana rehetra.

## Frantsa: PISTE (maimaim-poana)

1. Mamorona kaonty ao amin'ny [piste.gouv.fr](https://piste.gouv.fr). Midika izany fa manaiky ny fepetran'ny
   PISTE (CGU) ianao.
2. Mandehana any amin'ny API > **Consentement CGU API**. Ekeo ny fepetra ho an'ny **JUDILIBRE** sy
   **Légifrance** (production).
3. Mamorona **production application**. Tsy afaka mahatratra ny production ny `APP_SANDBOX` noforonina ho
   anao. Ao amin'ny "Modifier l'application", marihio ny **JUDILIBRE (production)** sy
   **Légifrance (production)**, dia ampiharo.
4. Sokafy ny tabilao **Authentification** an'ilay rindranasa. Adikao ny `client_id` sy ny `client_secret`.
5. Alefaso ny **Add or change keys** ary apetaho ireo.

Ny fepetra, raha fintinina:

- Angona: Licence Ouverte / Etalab 2.0. Avela ny fampiasana indray, anisan'izany ny fampiasana indray ara-barotra,
  raha tononina ny loharano.
- Aza avoaka na zaraina ny mari-pamantaranao (credentials). Ampahafantaro ny PISTE raha niparitaka izy ireo.
- Tolotra beta ny API Légifrance. Mety hampiatoina izy, ary manana quota (isan-tsegondra, isa-minitra ary
  isan'andro).
- Tsy ny dika tena marina ny lahatsoratra Légifrance. Ny PDF nosoniavina an'ny Journal officiel ihany no
  tena marina.
- Judilibre: aza ampiasaina ny anaran'ny mpitsara na ny mpiraki-draharaha hanombanana, hampitahana na
  haminavina ny asany (Code de l'organisation judiciaire art. L111-13; heloka bevava).
- Judilibre: ankatoavy ny GDPR. Aza miezaka ny hamantatra indray ny mombamomba ireo mpifanolana.

Ao amin'ny PISTE ny quota-nao ao amin'ny API Sélectionnées > Actions > Consulter les quotas.

## Etazonia: api.data.gov (maimaim-poana)

1. Mandehana any amin'ny [govinfo.gov/api-signup](https://www.govinfo.gov/api-signup) (aseho eo amin'ny
   efijery ny fanalahidy) na [api.data.gov/signup](https://api.data.gov/signup/) (alefa aminao amin'ny
   mailaka ny fanalahidy).
2. Ampidiro ny anaranao sy ny mailakao. Tsy voatery ny saha "how will you use it".
3. Adikao ilay fanalahidy misy litera 40.
4. Alefaso ny **Add or change keys** ary apetaho ho fanalahidy US izy.

Ny fepetra, raha fintinina:

- Amin'ny fanalahidinao manokana, mamela fangatahana hatramin'ny 36,000 isan'ora ny govinfo.
- Tsy nahita fepetra fampiasana manokana ho an'ny API izahay (tsy misy ny api.data.gov/terms/). Tsy voamarina.
  Jereo ny [politikan'ny govinfo](https://www.govinfo.gov/about/policies) sy ny
  [politikan'ny fiainana manokana an'ny data.gov](https://data.gov/privacy-policy/).
- Tehirizo ho anao irery ny fanalahidy.

## Fitsarana ao amin'ny fanjakana Amerikana: CourtListener (maimaim-poana)

Ny CourtListener dia tantanan'ny [Free Law Project](https://free.law), fikambanana tsy mitady tombony izay nanangona didim-pitsaran'ny fitsarana Amerikana nanomboka tamin'ny 2010 ary mamela azy ho maimaim-poana ho an'ny rehetra. Araka ny kajiny manokana, manana didim-pitsarana mihoatra ny sivy tapitrisa izy. Tsy loharano ofisialy izy: ny fitsarana no mamoaka ny didim-pitsarany, ary ny CourtListener no manangona azy avy amin'ny tranonkalan'ny fitsarana sy ny tatitra ara-dalàna nodinihina (scan). Milaza izany ny valin'ny Fontes rehetra avy aminy. Tsy misy ifandraisany amin'ny Free Law Project ny Fontes.

1. Mamorona kaonty maimaim-poana ao amin'ny [courtlistener.com](https://www.courtlistener.com/sign-in/).
2. Sokafy ny mombamomba anao ary adikao ny API token-nao.
3. Alefaso ny **Add or change keys** ary apetaho ho fanalahidy CourtListener izy.

Ny fepetra, raha fintinina ([fepetra feno](https://wiki.free.law/c/terms/courtlistener/courtlistenercom-terms-of-service-and-policies)):

- Anao irery ny token: aza zaraina, aza atambatra ary aza amidy indray, ary aza mampiasa kaonty maromaro.
- Ianao no tompon'andraikitra amin'ny zavatra ataon'ny rindranasa AI amin'ny token-nao.
- Aza asehoy ho novokarin'ny Free Law Project, ankatoavin'ny Free Law Project na hamarinin'ny Free Law Project ny famakafakana nataon'ny AI momba ny angona nataon'izy ireo.
- Ny kaonty maimaim-poana dia mamela fangatahana 5 isaky ny minitra, 50 isaky ny ora ary 125 isan'andro. Fangatahana iray ny fikarohana; roa ny fanokafana didim-pitsarana. Ny fahefana mpikambana ao amin'ny Free Law Project dia mampiakatra ireo fetra ireo.
- Tsy manome antoka ny fahamarinan'ny angona ny CourtListener. Ampitahao amin'ny kopian'ny fitsarana ny didim-pitsarana alohan'ny hianaranao azy.

## Aiza no itahirizana ireo fanalahidy

- **Mpametraka na amin'ny tanana:** ho lahatsoratra tsotra ao amin'ny rakitra fandrindrana MCP an'ny
  rindranasa tsirairay, ao amin'ny bloc `env` an'ny fidirana `fontes`. Afaka mamaky ireo fanalahidy izay
  rehetra afaka mamaky ny rakitrao.
  - Claude Desktop: `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac),
    `%APPDATA%\Claude\claude_desktop_config.json` (Windows)
  - Claude Code: `~/.claude.json`
  - Codex: `~/.codex/config.toml`
  - Cursor: `~/.cursor/mcp.json`
  - VS Code (Copilot): `~/.copilot/mcp-config.json`
  - Windsurf: `~/.config/devin/mcp_config.json` na `~/.codeium/windsurf/mcp_config.json`
    (Windows: `%APPDATA%\devin\mcp_config.json`)
  - Gemini CLI: `~/.gemini/settings.json`
  - Zed: `~/.config/zed/settings.json` (Windows: `%APPDATA%\Zed\settings.json`)
  - LM Studio: `~/.lmstudio/mcp.json`
  - Cline: `~/.cline/data/settings/cline_mcp_settings.json`
- **Fanitarana Claude Desktop (.mcpb):** tehirizin'ny Claude ao amin'ny fandrindrany ireo saha ireo ary
  arovany amin'ny fitehirizana voaaro an'ny rafitrao (Keychain amin'ny Mac, Credential Manager amin'ny
  Windows).

Alohan'ny fanovana tsirairay, mitahiry dika amin'ny rakitra fandrindrana eo akaikiny ny mpametraka
(`<file>.fontes-backup-<time>`). Misy fanalahidy koa ireo dika natao taorian'ny nanampianao fanalahidy. Fafao
ireo dika taloha tsy ilainao.

## Fanovana na fanesorana fanalahidy

- Alefaso ny **Add or change keys**. Apetaho fanalahidy vaovao hanoloana azy, na soraty ny `-` hanesorana azy.
- Na ovay amin'ny tanana ny bloc `env` ary akatony sy sokafy indray ilay rindranasa.
- Ny fanesorana ny Fontes dia manala ny fidirany manontolo, anisan'izany ny fanalahidy. Tsy mamafa ireo dika
  fiarovana izany.
- Raha niparitaka ny fanalahidy iray, soloy koa ao amin'ny loharano izy: ao amin'ny PISTE, mamorona
  mari-pamantarana vaovao ho an'ny rindranasanao; ho an'ny api.data.gov, misoratra anarana ho an'ny
  fanalahidy vaovao.

## Hafatra mety ho hitanao

| Hafatra | Dikany |
|---|---|
| `France needs a free PISTE key: set WLM_FR_PISTE_CLIENT_ID and WLM_FR_PISTE_CLIENT_SECRET.` | Tsy misy fanalahidy ho an'i Frantsa. Ampio iray. |
| `Inactive: needs a free PISTE account. ...` (ao amin'ny `list_jurisdictions`) | Mitovy amin'izany. |
| `PISTE refused the client credentials ...` | Diso na tsy manan-kery intsony ny ID na ny secret. Adikao indray avy ao amin'ny tabilao Authentification izy roa. |
| `PISTE denied access to the ... API: subscribe the application to ... and accept its CGU on piste.gouv.fr.` | Tsy misoratra anarana amin'io API io ny rindranasanao, na mbola tsy nanaiky ny fepetrany ianao. Jereo ny dingana 2 sy 3. |
| `Using govinfo DEMO_KEY (about 10 searches/day per IP) ...` | Tsy misy fanalahidy US. Mandeha ho an'ny antso vitsivitsy isan'andro ny fikarohana. |
| `govinfo rate limit reached (Retry-After ...). DEMO_KEY allows only about 10 searches a day per IP ...` | Lany ny fanalahidy demo. Ampio ny fanalahidinao manokana. |
| `govinfo refused the API key (WLM_US_GOVINFO_KEY).` | Diso ny fanalahidy, na mbola tsy nohamafisina tamin'ny mailaka. |

Ny sanda foana dia raisina ho tsy misy fanalahidy.

## Fahazoan-dalana (WLM_PERMITTED)

Tsy fanalahidy API ity, ary tsy apetraky ny mpametraka. **Apetraho ihany raha ianao mihitsy no manana io
fahazoan-dalana io.**

Maty raha tsy misy fanovana ny loharano sasany satria mandrara ny fampiasana mandeha ho azy tsy misy
fahazoan-dalana ny fepetrany na ny robots.txt-ny. Raha manana fahazoan-dalana avy amin'ny mpamoaka ianao,
alefaso ny loharano iray amin'ny fanampiana ny kaodiny ao amin'ny `WLM_PERMITTED`, sarahina faingo, ao
amin'ny bloc `env`: `"WLM_PERMITTED": "in,de"`.

| Kaody | Loharano |
|---|---|
| `az` | Azerbaijan: e-qanun.az (Ministry of Justice) |
| `bh` | Bahrain: Legislation and Legal Opinion Commission (lloc.gov.bh) |
| `co` | Kolombia: Función Pública, Gestor Normativo (lalàna natambatra) |
| `de` | Alemaina: NeuRIS (vavahadin-tserasera federaly momba ny fampahalalana ara-dalàna, tolotra andrana) |
| `difc` | Dubai International Financial Centre Courts (difccourts.ae) |
| `gr` | Grisia: National Printing Office, fikarohana ao amin'ny Government Gazette (search.et.gr) |
| `mu` | Maorisy: Supreme Court (supremecourt.govmu.org) |
| `sg` | Singapore: didim-pitsarana (elitigation.sg) |

Raha tsy misy fahazoan-dalana, hoy ny Fontes: `Off by default (<code>): the terms or robots.txt of ... forbid
automated use without the operator's permission.`

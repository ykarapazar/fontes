> Sa a se yon tradiksyon ki fèt avèk èd machin. Se vèsyon angle a ki fè lafwa.

# Kle API

Prèske tout sous nan Fontes mache san kle. Twa bezwen yon kle gratis:

| Kle | Sa li debloke | San li |
|---|---|---|
| `WLM_FR_PISTE_CLIENT_ID` + `WLM_FR_PISTE_CLIENT_SECRET` | Lafrans: Judilibre (desizyon tribinal) ak Légifrance (lejislasyon) | Lafrans etenn. `list_jurisdictions` montre l kòm inaktif. |
| `WLM_US_GOVINFO_KEY` | Etazini: rechèch govinfo (opinyon tribinal federal yo, Statutes at Large, lwa piblik) | Fontes sèvi ak kle pataje `DEMO_KEY` la: anviwon 10 rechèch pa jou pou chak adrès IP. Pou louvri yon desizyon ou deja konnen ak US Code, ou pa bezwen kle. |
| `WLM_US_COURTLISTENER_KEY` | Tribinal eta Etazini yo (`us-states`): opinyon tribinal siprèm ak tribinal apèl tout 50 eta yo ak DC, soti nan CourtListener | Jirisprudans eta Etazini yo etenn. `list_jurisdictions` montre l kòm inaktif. |

Kle yo opsyonèl. Ou ka ajoute yo pita.

## Ajoute yon kle

**Ak enstalatè a.** Lè Fontes fin konfigire, enstalatè a ofri w pou ajoute kle. Sou Mac, klike sou
**Ajoute kle**, oswa sou **Fini** pou sote sa; sou Windows, reponn kesyon an (peze Enter pou sote sa).
Pou ajoute oswa chanje kle pita, lanse **Ajoute oswa chanje kle**:

- Mac: louvri aplikasyon Fontes Installer la ankò epi chwazi **Ajoute oswa chanje kle**.
- Windows: ouvri Start menu, apre sa **Fontes** → **Ajoute oswa chanje kle**.

Sa ou tape a kache. Pou chak kle: kole l, peze Enter pou kenbe sa ki la deja, oswa tape `-` pou retire l.
Kle yo ale nan chak aplikasyon ki deja gen Fontes.

**Ak ekstansyon Claude Desktop la (.mcpb).** Louvri Claude > Settings > Extensions > Fontes epi ranpli
chan yo. Yo tout opsyonèl.

**Alamen.** Ajoute varyab yo nan blòk `env` antre `fontes` la nan konfigirasyon MCP aplikasyon ou:

```json
"fontes": {
  "command": "...",
  "args": ["..."],
  "env": { "WLM_US_GOVINFO_KEY": "your-key" }
}
```

Relanse aplikasyon an apre nenpòt chanjman.

## Lafrans: PISTE (gratis)

1. Kreye yon kont sou [piste.gouv.fr](https://piste.gouv.fr). Sa vle di ou aksepte kondisyon PISTE yo (CGU).
2. Ale nan API > **Consentement CGU API**. Aksepte kondisyon yo pou **JUDILIBRE** ak **Légifrance** (pwodiksyon).
3. Kreye yon **aplikasyon pwodiksyon**. `APP_SANDBOX` yo kreye pou ou a pa ka rive nan pwodiksyon.
   Anba "Modifier l'application", tcheke **JUDILIBRE (production)** ak **Légifrance (production)**, epi aplike.
4. Louvri onglè **Authentification** aplikasyon an. Kopye `client_id` ak `client_secret`.
5. Lanse **Ajoute oswa chanje kle** epi kole yo.

Kondisyon yo, an kout:

- Done: Licence Ouverte / Etalab 2.0. Ou gen dwa reitilize yo, ladan l itilizasyon komèsyal, si ou site sous la.
- Pa pibliye ni pataje idantifyan ou yo. Avèti PISTE si yo koule.
- API Légifrance la se yon sèvis beta. Li ka sispann, e li gen kota (pa segonn, pa minit ak pa jou).
- Tèks Légifrance yo pa vèsyon otantik la. Se sèlman PDF siyen Journal officiel la ki otantik.
- Judilibre: pa sèvi ak non jij oswa grefye pou evalye, konpare oswa predi travay yo
  (Code de l'organisation judiciaire art. L111-13; se yon enfraksyon penal).
- Judilibre: respekte GDPR. Pa eseye re-idantifye pati yo.

Kota ou yo sou PISTE anba API Sélectionnées > Actions > Consulter les quotas.

## Etazini: api.data.gov (gratis)

1. Ale sou [govinfo.gov/api-signup](https://www.govinfo.gov/api-signup) (kle a parèt sou ekran an)
   oswa sou [api.data.gov/signup](https://api.data.gov/signup/) (yo voye kle a ba ou pa imèl).
2. Antre non ou ak imèl ou. Chan "how will you use it" la opsyonèl.
3. Kopye kle 40 karaktè a.
4. Lanse **Ajoute oswa chanje kle** epi kole l kòm kle Etazini an.

Kondisyon yo, an kout:

- Ak pwòp kle ou, govinfo pèmèt jiska 36,000 demann pa èdtan.
- Nou pa jwenn okenn kondisyon itilizasyon espesyal pou API a (api.data.gov/terms/ pa egziste). Pa verifye.
  Gade [politik govinfo yo](https://www.govinfo.gov/about/policies) ak
  [politik vi prive data.gov la](https://data.gov/privacy-policy/).
- Kenbe kle a pou ou sèl.

## Tribinal eta Etazini yo: CourtListener (gratis)

[Free Law Project](https://free.law), yon òganizasyon san bi likratif, fè CourtListener mache. Depi 2010, li ap rasanble opinyon tribinal Etazini yo epi li ofri yo gratis bay tout moun. Dapre pwòp konte li, li gen plis pase nèf milyon desizyon. Se pa yon sous ofisyèl: tribinal yo menm piblye opinyon yo, epi CourtListener ranmase yo sou sit entènèt tribinal yo ak nan rapò jiridik eskane. Chak repons Fontes ki soti ladan l di sa. Fontes pa gen okenn rapò ak Free Law Project.

1. Kreye yon kont gratis sou [courtlistener.com](https://www.courtlistener.com/sign-in/).
2. Louvri pwofil ou epi kopye token API ou.
3. Lanse **Ajoute oswa chanje kle** epi kole l kòm kle CourtListener la.

Kondisyon yo, an kout ([kondisyon konplè yo](https://wiki.free.law/c/terms/courtlistener/courtlistenercom-terms-of-service-and-policies)):

- Token an se pou ou sèl: pa pataje l, pa mete l ansanm ak lòt moun, pa revann li, epi pa itilize plizyè kont.
- Ou responsab sa yon aplikasyon AI fè ak token ou a.
- Pa prezante yon analiz yon AI fè sou done yo kòm si Free Law Project te pwodui l, apiye l oswa verifye l.
- Yon kont gratis pèmèt 5 demann pa minit, 50 pa èdtan ak 125 pa jou. Yon rechèch se yon demann; louvri yon desizyon se de. Yon manm Free Law Project jwenn limit ki pi wo.
- CourtListener pa garanti egzaktitid. Verifye yon opinyon ak kopi tribinal la anvan ou konte sou li.

## Ki kote kle yo estoke

- **Ak enstalatè a oswa alamen:** an tèks klè nan fichye konfigirasyon MCP chak aplikasyon, nan blòk `env`
  antre `fontes` la. Nenpòt moun ki ka li fichye itilizatè ou yo ka li kle yo.
  - Claude Desktop: `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac),
    `%APPDATA%\Claude\claude_desktop_config.json` (Windows)
  - Claude Code: `~/.claude.json`
  - Codex: `~/.codex/config.toml`
  - Cursor: `~/.cursor/mcp.json`
  - VS Code (Copilot): `~/.copilot/mcp-config.json`
  - Windsurf: `~/.config/devin/mcp_config.json` oswa `~/.codeium/windsurf/mcp_config.json`
    (Windows: `%APPDATA%\devin\mcp_config.json`)
  - Gemini CLI: `~/.gemini/settings.json`
  - Zed: `~/.config/zed/settings.json` (Windows: `%APPDATA%\Zed\settings.json`)
  - LM Studio: `~/.lmstudio/mcp.json`
  - Cline: `~/.cline/data/settings/cline_mcp_settings.json`
- **Ekstansyon Claude Desktop la (.mcpb):** Claude kenbe chan sa yo nan paramèt li epi li pwoteje yo ak
  estokaj sekirize sistèm ou (Keychain sou Mac, Credential Manager sou Windows).

Anvan chak chanjman, enstalatè a sove yon kopi fichye konfigirasyon an akote l
(`<file>.fontes-backup-<time>`). Kopi ki fèt apre ou ajoute kle yo gen kle yo ladan yo tou. Efase ansyen
kopi ou pa bezwen yo.

## Chanje oswa retire yon kle

- Lanse **Ajoute oswa chanje kle**. Kole yon nouvo kle pou ranplase l, oswa tape `-` pou retire l.
- Oswa modifye blòk `env` la alamen epi relanse aplikasyon an.
- Lè ou dezenstale Fontes, sa retire tout antre li a, ansanm ak kle yo. Li pa efase kopi sekou yo.
- Si yon kle koule, ranplase l tou nan sous la: sou PISTE, fè nouvo idantifyan pou aplikasyon ou;
  pou api.data.gov, enskri pou yon nouvo kle.

## Mesaj ou ka wè

| Mesaj | Sa sa vle di |
|---|---|
| `France needs a free PISTE key: set WLM_FR_PISTE_CLIENT_ID and WLM_FR_PISTE_CLIENT_SECRET.` | Pa gen kle pou Lafrans. Ajoute youn. |
| `Inactive: needs a free PISTE account. ...` (nan `list_jurisdictions`) | Menm bagay. |
| `PISTE refused the client credentials ...` | ID a oswa secret la pa bon oswa li pa valab ankò. Kopye toude ankò nan onglè Authentification la. |
| `PISTE denied access to the ... API: subscribe the application to ... and accept its CGU on piste.gouv.fr.` | Aplikasyon ou pa abòne ak API sa a, oswa ou poko aksepte kondisyon li yo. Gade etap 2 ak 3. |
| `Using govinfo DEMO_KEY (about 10 searches/day per IP) ...` | Pa gen kle pou Etazini. Rechèch la mache pou kèk apèl pa jou. |
| `govinfo rate limit reached (Retry-After ...). DEMO_KEY allows only about 10 searches a day per IP ...` | Kle demo a fini. Ajoute pwòp kle ou. |
| `govinfo refused the API key (WLM_US_GOVINFO_KEY).` | Kle a pa bon, oswa ou poko konfime l nan imèl la. |

Yon valè vid konte kòm pa gen kle.

## Pèmisyon (WLM_PERMITTED)

Sa a se pa yon kle API, e enstalatè a pa mete l. **Mete l sèlman si ou menm ou gen pèmisyon sa a.**

Kèk sous etenn pa defo paske kondisyon yo oswa robots.txt yo entèdi itilizasyon otomatik san pèmisyon. Si
ou gen pèmisyon piblikatè a, limen yon sous lè ou ajoute kòd li nan `WLM_PERMITTED`, separe ak vigil, nan
blòk `env` la: `"WLM_PERMITTED": "in,de"`.

| Kòd | Sous |
|---|---|
| `az` | Azèbayjan: e-qanun.az (Ministè Jistis) |
| `bh` | Bahreyn: Legislation and Legal Opinion Commission (lloc.gov.bh) |
| `co` | Kolonbi: Función Pública, Gestor Normativo (lejislasyon konsolide) |
| `de` | Almay: NeuRIS (pòtay federal enfòmasyon jiridik, sèvis esè) |
| `difc` | Dubai International Financial Centre Courts (difccourts.ae) |
| `gr` | Grès: Enprimri Nasyonal, rechèch nan Jounal Ofisyèl la (search.et.gr) |
| `in` | Lend: India Code (indiacode.gov.in) |
| `mu` | Moris: Tribinal Siprèm (supremecourt.govmu.org) |
| `sg` | Singapou: jijman tribinal (elitigation.sg) |

San pèmisyon, Fontes di: `Off by default (<code>): the terms or robots.txt of ... forbid
automated use without the operator's permission.`

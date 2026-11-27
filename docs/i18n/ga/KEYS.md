> Aistriúchán é seo a rinneadh le cúnamh ó mheaisín. Is é an leagan Béarla an leagan údarásach.

# Eochracha API

Oibríonn beagnach gach foinse in Fontes gan eochair. Teastaíonn eochair saor in aisce ó thrí cinn:

| Eochair | Díghlasálann | Gan í |
|---|---|---|
| `WLM_FR_PISTE_CLIENT_ID` + `WLM_FR_PISTE_CLIENT_SECRET` | An Fhrainc: Judilibre (breithiúnais chúirte) agus Légifrance (reachtaíocht) | Tá an Fhrainc múchta. Taispeánann `list_jurisdictions` í mar neamhghníomhach. |
| `WLM_US_GOVINFO_KEY` | Na Stáit Aontaithe: cuardach govinfo (tuairimí cúirteanna feidearálacha, Statutes at Large, public laws) | Úsáideann Fontes an `DEMO_KEY` comhroinnte: thart ar 10 gcuardach sa lá in aghaidh an tseolta IP. Ní theastaíonn eochair chun breithiúnas aitheanta a oscailt ná don US Code. |
| `WLM_US_COURTLISTENER_KEY` | Cúirteanna stáit na SA (`us-states`): tuairimí na gcúirteanna uachtaracha agus achomhairc i ngach ceann den 50 stát agus i DC, ó CourtListener | Tá cásdlí stáit na SA múchta. Taispeánann `list_jurisdictions` í mar neamhghníomhach. |

Tá eochracha roghnach. Is féidir leat iad a chur leis níos déanaí.

## Eochair a chur leis

**Leis an suiteálaí.** Nuair atá Fontes socraithe, tairgeann an suiteálaí eochracha a chur leis. Ar
Mac, cliceáil **Cuir eochracha leis**, nó **Déanta** chun scipeáil; ar Windows, freagair an cheist
(brúigh Enter chun scipeáil). Chun eochracha a chur leis nó a athrú níos déanaí, rith
**Add or change keys**:

- Mac: oscail aip Fontes Installer arís agus roghnaigh **Cuir eochracha leis nó athraigh iad**.
- Windows: oscail an roghchlár Start, ansin **Fontes** → **Cuir eochracha leis nó athraigh iad**.

Tá an clóscríobh folaithe. Do gach eochair: greamaigh í, brúigh Enter chun an méid atá ann a
choinneáil, nó clóscríobh `-` chun í a bhaint. Téann na heochracha isteach i ngach aip a bhfuil
Fontes inti cheana.

**Le síneadh Claude Desktop (.mcpb).** Oscail Claude > Settings > Extensions > Fontes agus líon
isteach na réimsí. Tá siad ar fad roghnach.

**De láimh.** Cuir na hathróga leis an mbloc `env` den iontráil `fontes` i gcumraíocht MCP d'aipe:

```json
"fontes": {
  "command": "...",
  "args": ["..."],
  "env": { "WLM_US_GOVINFO_KEY": "your-key" }
}
```

Atosaigh an aip tar éis aon athraithe.

## An Fhrainc: PISTE (saor in aisce)

1. Cruthaigh cuntas ag [piste.gouv.fr](https://piste.gouv.fr). Ciallaíonn sé seo glacadh le téarmaí
   PISTE (CGU).
2. Téigh go API > **Consentement CGU API**. Glac leis na téarmaí do **JUDILIBRE** agus
   **Légifrance** (production).
3. Cruthaigh **production application**. Ní féidir leis an `APP_SANDBOX` a rinneadh duit production
   a shroicheadh. Faoi "Modifier l'application", ticeáil **JUDILIBRE (production)** agus
   **Légifrance (production)**, ansin cuir i bhfeidhm.
4. Oscail cluaisín **Authentification** na haipe. Cóipeáil an `client_id` agus an `client_secret`.
5. Rith **Add or change keys** agus greamaigh iad.

Na téarmaí, go hachomair:

- Sonraí: Licence Ouverte / Etalab 2.0. Ceadaítear athúsáid, athúsáid tráchtála san áireamh, le
  sannadh.
- Ná foilsigh ná ná roinn do dhintiúir. Inis do PISTE má sceitheann siad.
- Seirbhís béite is ea API Légifrance. D'fhéadfaí í a chur ar fionraí, agus tá cuótaí aici (in
  aghaidh an tsoicind, an nóiméid agus an lae).
- Ní hiad téacsanna Légifrance an leagan barántúil. Níl barántúil ach PDF sínithe an Journal
  officiel.
- Judilibre: ná húsáid ainmneacha breithiúna ná cléireach chun a gcuid oibre a mheas, a chur i
  gcomparáid ná a thuar (Code de l'organisation judiciaire art. L111-13; cion coiriúil).
- Judilibre: lean an GDPR. Ná déan iarracht na páirtithe a athaithint.

Tá do chuótaí ar PISTE faoi API Sélectionnées > Actions > Consulter les quotas.

## Na Stáit Aontaithe: api.data.gov (saor in aisce)

1. Téigh go [govinfo.gov/api-signup](https://www.govinfo.gov/api-signup) (taispeántar an eochair ar
   an scáileán) nó [api.data.gov/signup](https://api.data.gov/signup/) (seoltar an eochair chugat
   trí ríomhphost).
2. Iontráil d'ainm agus do ríomhphost. Tá an réimse "how will you use it" roghnach.
3. Cóipeáil an eochair 40 carachtar.
4. Rith **Add or change keys** agus greamaigh í mar eochair na SA.

Na téarmaí, go hachomair:

- Le d'eochair féin, ceadaíonn govinfo suas le 36,000 iarratas san uair.
- Níor aimsíomar aon téarmaí seirbhíse a bhaineann go sonrach leis an API (níl api.data.gov/terms/
  ann). Gan fíorú. Féach [beartais govinfo](https://www.govinfo.gov/about/policies) agus
  [beartas príobháideachta data.gov](https://data.gov/privacy-policy/).
- Coinnigh an eochair agat féin.

## Cúirteanna stáit na SA: CourtListener (saor in aisce)

Is é [Free Law Project](https://free.law) a reáchtálann CourtListener, eagraíocht neamhbhrabúis a bhailigh tuairimí cúirteanna na SA ó 2010 agus a chuireann saor in aisce ar fáil do chách iad. De réir a chomhaireamh féin, tá breis agus naoi milliún breithiúnas aici. Ní foinse oifigiúil í: foilsíonn na cúirteanna a dtuairimí féin, agus bailíonn CourtListener iad ó shuíomhanna gréasáin cúirteanna agus ó thuarascálacha dlí scanta. Deir gach freagra ó Fontes uaithi sin. Níl Fontes cleamhnaithe le Free Law Project.

1. Cruthaigh cuntas saor in aisce ag [courtlistener.com](https://www.courtlistener.com/sign-in/).
2. Oscail do phróifíl agus cóipeáil do chomhartha API.
3. Rith **Add or change keys** agus greamaigh é mar eochair CourtListener.

Na téarmaí, go hachomair ([téarmaí iomlána](https://wiki.free.law/c/terms/courtlistener/courtlistenercom-terms-of-service-and-policies)):

- Is leatsa amháin an comhartha: ná roinn, ná cuir i gcomhthiomsú ná athdhíol é, agus ná húsáid cuntais iolracha.
- Tá tú freagrach as an méid a dhéanann aip AI le do chomhartha.
- Ná cuir anailís AI ar a gcuid sonraí i láthair mar rud a tháirg, a thacaigh Free Law Project leis nó a sheiceáil sé.
- Ceadaíonn cuntas saor in aisce 5 iarratas sa nóiméad, 50 san uair agus 125 sa lá. Is iarratas amháin é cuardach; is dhá iarratas é breithiúnas a oscailt. Ardaíonn ballraíocht de chuid Free Law Project na teorainneacha.
- Ní ráthaíonn CourtListener cruinneas. Seiceáil tuairim i gcoinne chóip na cúirte sula mbíonn muinín agat as.

## Cá stóráiltear eochracha

- **Suiteálaí nó de láimh:** mar ghnáth-théacs i gcomhad cumraíochta MCP gach aipe, sa bhloc `env`
  den iontráil `fontes`. Is féidir le duine ar bith ar féidir leis do chomhaid úsáideora a léamh na
  heochracha a léamh.
  - Claude Desktop: `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac),
    `%APPDATA%\Claude\claude_desktop_config.json` (Windows)
  - Claude Code: `~/.claude.json`
  - Codex: `~/.codex/config.toml`
  - Cursor: `~/.cursor/mcp.json`
  - VS Code (Copilot): `~/.copilot/mcp-config.json`
  - Windsurf: `~/.config/devin/mcp_config.json` nó `~/.codeium/windsurf/mcp_config.json`
    (Windows: `%APPDATA%\devin\mcp_config.json`)
  - Gemini CLI: `~/.gemini/settings.json`
  - Zed: `~/.config/zed/settings.json` (Windows: `%APPDATA%\Zed\settings.json`)
  - LM Studio: `~/.lmstudio/mcp.json`
  - Cline: `~/.cline/data/settings/cline_mcp_settings.json`
- **Síneadh Claude Desktop (.mcpb):** coinníonn Claude na réimsí seo ina shocruithe agus cosnaíonn
  sé iad le stóráil shlán do chórais (Keychain ar Mac, Credential Manager ar Windows).

Roimh gach athrú, sábhálann an suiteálaí cóip den chomhad cumraíochta in aice leis
(`<file>.fontes-backup-<time>`). Tá na heochracha freisin i gcóipeanna a rinneadh tar éis duit
eochracha a chur leis. Scrios seanchóipeanna nach bhfuil uait.

## Eochair a athrú nó a bhaint

- Rith **Add or change keys**. Greamaigh eochair nua chun í a athsholáthar, nó clóscríobh `-` chun
  í a bhaint.
- Nó cuir an bloc `env` in eagar de láimh agus atosaigh an aip.
- Nuair a dhíshuiteáiltear Fontes baintear a iontráil iomlán, eochracha san áireamh. Ní scriostar
  na cóipeanna cúltaca.
- Má sceith eochair, athsholáthair í ag an bhfoinse freisin: ar PISTE, déan dintiúir nua do d'aip;
  do api.data.gov, cláraigh le haghaidh eochair nua.

## Teachtaireachtaí a d'fhéadfá a fheiceáil

| Teachtaireacht | Brí |
|---|---|
| `France needs a free PISTE key: set WLM_FR_PISTE_CLIENT_ID and WLM_FR_PISTE_CLIENT_SECRET.` | Níl eochair don Fhrainc ann. Cuir ceann leis. |
| `Inactive: needs a free PISTE account. ...` (in `list_jurisdictions`) | Mar an gcéanna. |
| `PISTE refused the client credentials ...` | Tá an ID nó an secret mícheart nó níl sé bailí a thuilleadh. Cóipeáil an dá cheann arís ón gcluaisín Authentification. |
| `PISTE denied access to the ... API: subscribe the application to ... and accept its CGU on piste.gouv.fr.` | Níl d'aip liostáilte leis an API sin, nó níor ghlac tú lena théarmaí. Féach céimeanna 2 agus 3. |
| `Using govinfo DEMO_KEY (about 10 searches/day per IP) ...` | Níl eochair SA ann. Oibríonn cuardach do roinnt glaonna sa lá. |
| `govinfo rate limit reached (Retry-After ...). DEMO_KEY allows only about 10 searches a day per IP ...` | Tá an eochair taispeána ídithe. Cuir d'eochair féin leis. |
| `govinfo refused the API key (WLM_US_GOVINFO_KEY).` | Tá an eochair mícheart, nó níor deimhníodh fós í ón ríomhphost. |

Áirítear luach folamh mar easpa eochrach.

## Ceadanna (WLM_PERMITTED)

Ní eochair API é seo, agus ní shocraíonn an suiteálaí é. **Ná socraigh é ach amháin má tá an cead
sin agat féin.**

Tá roinnt foinsí múchta de réir réamhshocraithe toisc go dtoirmisceann a dtéarmaí nó a robots.txt
úsáid uathoibrithe gan chead. Má tá cead agat ón bhfoilsitheoir, cas foinse air trína cód a chur le
`WLM_PERMITTED`, scartha le camóga, sa bhloc `env`: `"WLM_PERMITTED": "in,de"`.

| Cód | Foinse |
|---|---|
| `az` | An Asarbaiseáin: e-qanun.az (Aireacht Dlí agus Cirt) |
| `bh` | Bairéin: Legislation and Legal Opinion Commission (lloc.gov.bh) |
| `co` | An Cholóim: Función Pública, Gestor Normativo (reachtaíocht chomhdhlúite) |
| `de` | An Ghearmáin: NeuRIS (tairseach faisnéise dlí feidearálach, seirbhís trialach) |
| `difc` | Dubai International Financial Centre Courts (difccourts.ae) |
| `gr` | An Ghréig: Oifig Náisiúnta Priontála, cuardach na hIrise Rialtais (search.et.gr) |
| `mu` | Oileán Mhuirís: an Chúirt Uachtarach (supremecourt.govmu.org) |
| `sg` | Singeapór: breithiúnais chúirte (elitigation.sg) |

Gan chead, deir Fontes: `Off by default (<code>): the terms or robots.txt of ... forbid
automated use without the operator's permission.`

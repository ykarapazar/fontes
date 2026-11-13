> Tämä on konekäännöksen avulla tehty käännös. Englanninkielinen versio on määräävä.

# API-avaimet

Lähes kaikki Fontesin lähteet toimivat ilman avainta. Kaksi tarvitsee maksuttoman avaimen:

| Avain | Avaa | Ilman sitä |
|---|---|---|
| `WLM_FR_PISTE_CLIENT_ID` + `WLM_FR_PISTE_CLIENT_SECRET` | Ranska: Judilibre (tuomioistuinten ratkaisut) ja Légifrance (lainsäädäntö) | Ranska on pois päältä. `list_jurisdictions` näyttää sen ei-aktiivisena. |
| `WLM_US_GOVINFO_KEY` | Yhdysvallat: govinfo-haku (liittovaltion tuomioistuinten ratkaisut, Statutes at Large, public laws) | Fontes käyttää jaettua `DEMO_KEY`-avainta: noin 10 hakua päivässä IP-osoitetta kohden. Tunnetun ratkaisun avaaminen ja US Code eivät tarvitse avainta. |

Avaimet ovat valinnaisia. Voit lisätä ne myöhemmin.

## Avaimen lisääminen

**Asennusohjelmalla.** Asennuksen aikana asennusohjelma kysyy, haluatko lisätä avaimia. Valitse
**Not now** (tai paina Enter) ohittaaksesi. Lisää tai muuta avaimia myöhemmin ajamalla **Add or change keys**:

- Mac: avaa Fontes Installer -sovellus uudelleen ja valitse **Add or change keys**, tai kaksoisnapsauta
  `Add or change keys.command` asennuskansiossa.
- Windows: kaksoisnapsauta `Add or change keys.cmd` asennuskansiossa. Windowsin asennusohjelma
  lisää sen myös, kun se on saatavilla, Käynnistä-valikkoon > Fontes.

Kirjoittamasi teksti on piilotettu. Kunkin avaimen kohdalla: liitä se, paina Enter säilyttääksesi nykyisen arvon tai kirjoita `-`
poistaaksesi sen. Avaimet lisätään jokaiseen sovellukseen, jossa Fontes jo on.

**Claude Desktop -laajennuksella (.mcpb).** Avaa Claude > Settings > Extensions > Fontes ja
täytä kentät. Ne ovat kaikki valinnaisia.

**Käsin.** Lisää muuttujat sovelluksesi MCP-asetusten `fontes`-merkinnän `env`-lohkoon:

```json
"fontes": {
  "command": "...",
  "args": ["..."],
  "env": { "WLM_US_GOVINFO_KEY": "your-key" }
}
```

Käynnistä sovellus uudelleen jokaisen muutoksen jälkeen.

## Ranska: PISTE (maksuton)

1. Luo tili osoitteessa [piste.gouv.fr](https://piste.gouv.fr). Tämä tarkoittaa PISTEn käyttöehtojen (CGU) hyväksymistä.
2. Siirry kohtaan API > **Consentement CGU API**. Hyväksy **JUDILIBREn** ja **Légifrancen** käyttöehdot (tuotanto).
3. Luo **tuotantosovellus** (production application). Sinulle luotu `APP_SANDBOX` ei pääse tuotantoympäristöön.
   Valitse kohdassa ”Modifier l'application” **JUDILIBRE (production)** ja **Légifrance (production)** ja tallenna.
4. Avaa sovelluksen **Authentification**-välilehti. Kopioi `client_id` ja `client_secret`.
5. Aja **Add or change keys** ja liitä ne.

Käyttöehdot lyhyesti:

- Aineisto: Licence Ouverte / Etalab 2.0. Uudelleenkäyttö, myös kaupallinen, on sallittu lähde mainiten.
- Älä julkaise tai jaa tunnuksiasi. Ilmoita PISTElle, jos ne vuotavat.
- Légifrancen API on beta-palvelu. Se voidaan keskeyttää, ja sillä on kiintiöt (sekunnissa, minuutissa ja päivässä).
- Légifrancen tekstit eivät ole todistusvoimainen versio. Vain allekirjoitettu Journal officiel -PDF on.
- Judilibre: älä käytä tuomareiden tai kirjaajien nimiä heidän työnsä arviointiin, vertailuun tai ennustamiseen
  (Code de l'organisation judiciaire art. L111-13; rikos).
- Judilibre: noudata GDPR:ää. Älä yritä tunnistaa asianosaisia uudelleen.

Kiintiösi näet PISTEssä kohdassa API Sélectionnées > Actions > Consulter les quotas.

## Yhdysvallat: api.data.gov (maksuton)

1. Siirry osoitteeseen [govinfo.gov/api-signup](https://www.govinfo.gov/api-signup) (avain näytetään näytöllä)
   tai [api.data.gov/signup](https://api.data.gov/signup/) (avain lähetetään sinulle sähköpostitse).
2. Anna nimesi ja sähköpostiosoitteesi. Kenttä ”how will you use it” on valinnainen.
3. Kopioi 40-merkkinen avain.
4. Aja **Add or change keys** ja liitä se Yhdysvaltojen avaimeksi.

Käyttöehdot lyhyesti:

- Omalla avaimella govinfo sallii enintään 36 000 pyyntöä tunnissa.
- Emme löytäneet API:lle omia käyttöehtoja (api.data.gov/terms/ ei ole olemassa). Vahvistamaton.
  Katso [govinfon käytännöt](https://www.govinfo.gov/about/policies) ja
  [data.govin tietosuojakäytäntö](https://data.gov/privacy-policy/).
- Pidä avain omana tietonasi.

## Missä avaimet säilytetään

- **Asennusohjelma tai käsin:** pelkkänä tekstinä kunkin sovelluksen MCP-asetustiedostossa, `fontes`-merkinnän
  `env`-lohkossa. Kuka tahansa, joka voi lukea käyttäjätiedostojasi, voi lukea avaimet.
  - Claude Desktop: `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac),
    `%APPDATA%\Claude\claude_desktop_config.json` (Windows)
  - Claude Code: `~/.claude.json`
  - Codex: `~/.codex/config.toml`
  - Cursor: `~/.cursor/mcp.json`
  - VS Code (Copilot): `~/.copilot/mcp-config.json`
  - Windsurf: `~/.config/devin/mcp_config.json` tai `~/.codeium/windsurf/mcp_config.json`
    (Windows: `%APPDATA%\devin\mcp_config.json`)
  - Gemini CLI: `~/.gemini/settings.json`
  - Zed: `~/.config/zed/settings.json` (Windows: `%APPDATA%\Zed\settings.json`)
  - LM Studio: `~/.lmstudio/mcp.json`
  - Cline: `~/.cline/data/settings/cline_mcp_settings.json`
- **Claude Desktop -laajennus (.mcpb):** Claude säilyttää nämä kentät asetuksissaan ja suojaa ne
  järjestelmäsi suojatulla tallennustilalla (Keychain Macissa, Credential Manager Windowsissa).

Ennen jokaista muutosta asennusohjelma tallentaa asetustiedostosta kopion sen viereen
(`<file>.fontes-backup-<time>`). Kopiot, jotka on tehty avainten lisäämisen jälkeen, sisältävät myös avaimet. Poista vanhat
kopiot, joita et tarvitse.

## Avaimen muuttaminen tai poistaminen

- Aja **Add or change keys**. Liitä uusi avain korvataksesi vanhan tai kirjoita `-` poistaaksesi sen.
- Tai muokkaa `env`-lohkoa käsin ja käynnistä sovellus uudelleen.
- Fontesin poistaminen poistaa sen koko merkinnän avaimineen. Varmuuskopioita se ei poista.
- Jos avain on vuotanut, vaihda se myös lähteessä: PISTEssä luo sovelluksellesi uudet tunnukset;
  api.data.govissa rekisteröidy uutta avainta varten.

## Ilmoitukset, joita saatat nähdä

| Ilmoitus | Merkitys |
|---|---|
| `France needs a free PISTE key: set WLM_FR_PISTE_CLIENT_ID and WLM_FR_PISTE_CLIENT_SECRET.` | Ranskan avainta ei ole. Lisää se. |
| `Inactive: needs a free PISTE account. ...` (`list_jurisdictions`-tuloksessa) | Sama. |
| `PISTE refused the client credentials ...` | Tunnus tai salaisuus on väärä tai ei enää voimassa. Kopioi molemmat uudelleen Authentification-välilehdeltä. |
| `PISTE denied access to the ... API: subscribe the application to ... and accept its CGU on piste.gouv.fr.` | Sovelluksesi ei ole tilannut kyseistä API:a, tai et ole hyväksynyt sen käyttöehtoja. Katso vaiheet 2 ja 3. |
| `Using govinfo DEMO_KEY (about 10 searches/day per IP) ...` | Yhdysvaltojen avainta ei ole. Haku toimii muutaman kutsun päivässä. |
| `govinfo rate limit reached (Retry-After ...). DEMO_KEY allows only about 10 searches a day per IP ...` | Demoavain on käytetty loppuun. Lisää oma avain. |
| `govinfo refused the API key (WLM_US_GOVINFO_KEY).` | Avain on väärä tai sitä ei ole vielä vahvistettu sähköpostista. |

Tyhjä arvo tarkoittaa, ettei avainta ole.

## Luvat (WLM_PERMITTED)

Tämä ei ole API-avain, eikä asennusohjelma aseta sitä. **Aseta se vain, jos sinulla itselläsi on
tämä lupa.**

Jotkin lähteet ovat oletuksena pois päältä, koska niiden käyttöehdot tai robots.txt kieltävät automaattisen käytön ilman
lupaa. Jos sinulla on julkaisijan lupa, ota lähde käyttöön lisäämällä sen koodi
muuttujaan `WLM_PERMITTED` pilkuilla erotettuna `env`-lohkossa: `"WLM_PERMITTED": "in,de"`.

| Koodi | Lähde |
|---|---|
| `az` | Azerbaidžan: e-qanun.az (oikeusministeriö) |
| `bh` | Bahrain: Legislation and Legal Opinion Commission (lloc.gov.bh) |
| `co` | Kolumbia: Función Pública, Gestor Normativo (ajantasainen lainsäädäntö) |
| `de` | Saksa: NeuRIS (liittovaltion oikeudellisen tiedon portaali, kokeilupalvelu) |
| `difc` | Dubai International Financial Centre Courts (difccourts.ae) |
| `gr` | Kreikka: National Printing Office, Government Gazette -haku (search.et.gr) |
| `in` | Intia: India Code (indiacode.gov.in) |
| `mu` | Mauritius: Supreme Court (supremecourt.govmu.org) |
| `sg` | Singapore: tuomioistuinten tuomiot (elitigation.sg) |

Ilman lupaa Fontes sanoo: `Off by default (<code>): the terms or robots.txt of ... forbid
automated use without the operator's permission.`

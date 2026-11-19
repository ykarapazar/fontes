> Tämä on konekäännöksen avulla tehty käännös. Englanninkielinen versio on määräävä.

# Fontesin asentaminen

Fontesin avulla tekoälysovelluksesi voi hakea tuomioistuinten ratkaisuja ja lainsäädäntöä reaaliajassa tuomioistuinten ja viranomaisten
verkkosivustoilta yli 120 lainkäyttöalueelta. Jokaisessa tuloksessa on linkki alkuperäiseen. Se on tavallinen MCP-palvelin,
joten se toimii missä tahansa sovelluksessa, joka voi ajaa paikallista MCP-palvelinta: Claude Desktop, Codex, Claude
Code, Cursor, VS Code (GitHub Copilot), Gemini CLI, Windsurf, Zed, LM Studio, Cline ja muut.

Valitse sovelluksesi, noudata sen vaiheita ja [tarkista sitten, että se toimii](#tarkista-että-se-toimii).

## Claude Desktop

1. Lataa Fontesin `.mcpb`-tiedosto
   [uusimmasta julkaisusta](https://github.com/ykarapazar/fontes/releases/latest).
2. Kaksoisnapsauta sitä. Claude Desktop avaa sen.
3. Napsauta **Install**.

## Codex

Päätteessä (terminal):

```bash
codex mcp add fontes -- uvx fontes-mcp
```

Codex CLI ja Codexin IDE-laajennus jakavat tämän asetuksen (`~/.codex/config.toml`).
Tarvitset [uv-työkalun](#tarvitset-uv-työkalun).

## Claude Code

Päätteessä (terminal):

```bash
claude mcp add fontes -- uvx fontes-mcp
```

Tarvitset [uv-työkalun](#tarvitset-uv-työkalun).

## Muut sovellukset

Jokainen näistä tarvitsee [uv-työkalun](#tarvitset-uv-työkalun). Lisää merkintä, tallenna, sulje sitten sovellus ja avaa se uudelleen.

**Cursor:** tiedostossa `~/.cursor/mcp.json` (kaikki projektit) tai `.cursor/mcp.json` (yksi projekti):

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**VS Code (GitHub Copilot):** suorita **MCP: Add Server** Command Palettesta, valitse
**Command (stdio)**, kirjoita `uvx fontes-mcp` ja anna palvelimen nimeksi `fontes`. Tai lisää tämä tiedostoon
`~/.copilot/mcp-config.json`:

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

Vanhemmat VS Code -asetukset käyttävät tiedostoa `.vscode/mcp.json`, jossa ylimmän tason avain on `servers` eikä
`mcpServers`.

**Gemini CLI:** päätteessä `gemini mcp add -s user fontes uvx fontes-mcp`. Tai lisää tämä tiedostoon
`~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Zed:** avaa asetustiedostosi (**zed: open settings file**) ja lisää:

```json
{
  "context_servers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**LM Studio:** avaa oikeanpuoleisessa sivupalkissa **Program**-välilehti, napsauta **Install → Edit
mcp.json** ja lisää:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Cline:** napsauta **MCP Servers** -kuvaketta, avaa **Configure**-välilehti, napsauta **Configure MCP
Servers** ja lisää sama `mcpServers`-merkintä kuin LM Studiolle.

**Claude Desktop, käsin** (`.mcpb`-tiedoston sijaan): lisää sama `mcpServers`-merkintä tiedostoon
`claude_desktop_config.json` (macOS: `~/Library/Application Support/Claude/`, Windows:
`%APPDATA%\Claude\`).

**Mikä tahansa muu MCP-sovellus** (Windsurf ja muut): sovelluksen oma dokumentaatio kertoo, minne se tallentaa MCP-palvelimensa.
Useimmat käyttävät samaa merkintää: komento `uvx`, argumentit `fontes`.

Jos sovellus ei löydä komentoa `uvx`, käytä sen koko polkua (macOS:ssä ja Linuxissa `which uvx` tulostaa sen).

## Tarvitset uv-työkalun

Codex, Claude Code ja muut sovellukset käynnistävät Fontesin komennolla `uvx`, joka tulee **uv**:n mukana. uv on Astralin pieni
maksuton työkalu. Asenna se
[Astralin ohjeen](https://docs.astral.sh/uv/getting-started/installation/) mukaan tai aja:

- macOS tai Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Windows (PowerShell): `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

## Avaimet

Jotkin lähteet tarvitsevat maksuttoman avaimen: katso [KEYS.md](KEYS.md).

## Tarkista, että se toimii

Kysy uudessa keskustelussa: *”Mistä lainkäyttöalueista Fontes voi hakea?”* Sovelluksen pitäisi vastata
luettelolla maista. Jos se ei vastaa, sulje sovellus ja avaa se vielä kerran.

## Yhden napsautuksen asennusohjelma (Mac ja Windows)

Asennusohjelma ottaa Fontesin käyttöön kaikissa sovelluksissasi kerralla: Claude Desktopissa,
Codexissa, Claude Codessa, Cursorissa, VS Codessa (GitHub Copilot), Windsurfissa, Gemini CLI:ssä,
Zedissä, LM Studiossa ja Clinessä.

**Ennen kuin aloitat:** sulje jokainen näistä sovelluksista kokonaan. Tämä on tärkeintä Claude Coden kohdalla:
käynnissä ollessaan se kirjoittaa tiedoston `~/.claude.json` uudelleen ja voi kumota asennusohjelman muutoksen. Jos et voi
sulkea Claude Codea, lisää Fontes siihen sen sijaan komennolla `claude mcp add` (katso [Claude Code](#claude-code)).

**Mac**

1. Lataa Macin asennusohjelma (`Fontes-Installer-…-mac.zip`) [uusimmasta
   julkaisusta](https://github.com/ykarapazar/fontes/releases/latest) ja pura se
   kaksoisnapsauttamalla.
2. Kaksoisnapsauta **Fontes Installer**. Jos Mac kysyy, haluatko avata internetistä ladatun
   sovelluksen, napsauta **Open**.
3. Valitse **Asenna** ja napsauta **OK**. Käyttöönotto kestää noin minuutin.
4. Ilmoitus luettelee sovellukset, jotka se otti käyttöön. Napsauta **Valmis** ja avaa sitten nämä
   sovellukset uudelleen. Jos haluat lisätä valinnaiset ilmaiset avaimet ensin, napsauta sen sijaan
   **Lisää avaimet**; katso [Avainvaihe](#avainvaihe).

**Windows**

1. Lataa Windowsin asennusohjelma (`Fontes-Setup-….exe`) [uusimmasta julkaisusta](https://github.com/ykarapazar/fontes/releases/latest) ja kaksoisnapsauta sitä.
   - Jos Windows näyttää ilmoituksen ”Windows protected your PC”: napsauta **More info** ja sitten **Run anyway**.
2. Napsauta **Asenna**. Ikkuna avautuu ja asentaa Fontesin.
3. Kun sinulta kysytään, lähetetäänkö nimettömiä käyttömääriä, paina Enter vastataksesi ei.
4. Se kysyy, lisätäänkö avaimet nyt. Paina Enter ohittaaksesi; katso [Avainvaihe](#avainvaihe).
5. Kun näkyy **Done**, avaa tekoälysovelluksesi uudelleen. Jos jokin oli yhä käynnissä, sulje se
   kokonaan (myös ilmoitusalueelta kellon vierestä) ja avaa se uudelleen.

Lopuksi asennusohjelma luettelee sovellukset, jotka se otti käyttöön.

### Mitkä sovellukset se ottaa käyttöön

Se ottaa sovelluksen käyttöön vain, jos sovelluksen asetuskansio on jo tietokoneellasi. Claude Code
otetaan käyttöön vain, jos `~/.claude.json` on olemassa. Claude Desktop otetaan aina käyttöön. Jokainen sovellus saa yhden
merkinnän, `fontes`, tähän tiedostoon:

| Sovellus | Tiedosto (Mac ja Linux) | Tiedosto (Windows) |
|---|---|---|
| Claude Desktop | `~/Library/Application Support/Claude/claude_desktop_config.json` (Linux: `~/.config/Claude/`) | `%APPDATA%\Claude\claude_desktop_config.json` sekä Microsoft Store -version oma kopio |
| Codex | `~/.codex/config.toml` | `%USERPROFILE%\.codex\config.toml` |
| Claude Code | `~/.claude.json` | `%USERPROFILE%\.claude.json` |
| Cursor | `~/.cursor/mcp.json` | `%USERPROFILE%\.cursor\mcp.json` |
| VS Code (Copilot) | `~/.copilot/mcp-config.json` | `%USERPROFILE%\.copilot\mcp-config.json` |
| Windsurf | `~/.config/devin/mcp_config.json` tai vanhemmissa versioissa `~/.codeium/windsurf/mcp_config.json` | `%APPDATA%\devin\mcp_config.json` tai `%USERPROFILE%\.codeium\windsurf\mcp_config.json` |
| Gemini CLI | `~/.gemini/settings.json` | `%USERPROFILE%\.gemini\settings.json` |
| Zed | `~/.config/zed/settings.json` | `%APPDATA%\Zed\settings.json` |
| LM Studio | `~/.lmstudio/mcp.json` | `%USERPROFILE%\.lmstudio\mcp.json` |
| Cline | `~/.cline/data/settings/cline_mcp_settings.json` | `%USERPROFILE%\.cline\data\settings\cline_mcp_settings.json` |

VS Code otetaan käyttöön, jos `~/.copilot` tai VS Coden oma asetuskansio on olemassa.

Kaksi sovellusta tarvitsee yhden lisävaiheen:

- **Windsurf:** kun olet avannut sen uudelleen, paina päivityspainiketta Cascadessa.
- **Cline vanhemmassa VS Code -laajennuksessa:** lisää Fontes käsin (katso [Cline](#muut-sovellukset)).

### Avainvaihe

Heti asennuksen jälkeen asennusohjelma tarjoutuu lisäämään maksuttomat avaimet Ranskaa ja Yhdysvaltoja varten. Avainten lisääminen tai
muuttaminen myöhemmin:

- **Mac:** avaa **Fontes Installer** uudelleen ja valitse **Lisää tai vaihda avaimia**.
- **Windows:** avaa Käynnistä-valikko ja valitse **Fontes** → **Lisää tai vaihda avaimia**.

Kirjoittamasi teksti on piilotettu. Avaimet lisätään jokaiseen sovellukseen, jossa Fontes jo on. Sulje sovellukset ja avaa ne
uudelleen sen jälkeen. Mistä avaimet saa ja mitä ne avaavat: [KEYS.md](KEYS.md).

### Varmuuskopiot, uudelleenajot ja poistaminen

Asennusohjelma muuttaa vain `fontes`-merkintää. Kaikki muut asetukset ja kommentit säilyvät ennallaan.
Ennen tiedoston muuttamista se tallentaa sen viereen kopion nimeltä `<file>.fontes-backup-<date>`. Kopiot,
jotka on tehty avainten lisäämisen jälkeen, sisältävät nuo avaimet: poista ne, joita et enää tarvitse. Se
asentaa myös uv:n. Sen voi turvallisesti ajaa uudelleen: se korjaa asetukset eikä muuta mitään muuta.

Poista Fontes avaamalla **Fontes Installer** ja valitsemalla **Poista** (Mac) tai poista **Fontes** kohdasta Asetukset → Sovellukset (Windows). Se poistaa `fontes`-merkinnän avaimineen jokaisesta sovelluksesta. Muut asetuksesi
ja varmuuskopiot säilyvät.

## Päivitykset

- **Asennusohjelma ja `.mcpb`-tiedosto:** sinun ei tarvitse tehdä mitään. Kerran päivässä, kun sovellus
  käynnistyy, Fontes tarkistaa taustalla, onko uudempaa versiota, ja valmistelee sen; seuraavalla kerralla
  sovellus käyttää sitä. Jos päivitystä ei voida ladata tai se ei toimi, Fontes jatkaa
  toimivan version käyttämistä.
- **`uvx`:** Fontes kertoo sinulle, kun uudempi versio on olemassa, lainkäyttöalueiden luettelonsa
  alussa. Jos haluat aina ajaa uusinta versiota, käytä `fontes-mcp@latest` eikä `fontes-mcp`.

Tätä varten ei lähetetä minnekään mitään tietoja sinusta tai hauistasi.

## Tietosuoja

Fontes ei oletuksena lähetä mitään sinusta tai hauistasi. Käyttömäärät ovat vapaaehtoisia (opt-in), ja virheraportti
lähetetään vasta, kun olet nähnyt sen ja vahvistanut. Lisätietoja: [PRIVACY.md](PRIVACY.md).

## Poistaminen

Poista `fontes`-merkintä sovelluksen MCP-asetuksista (Claude Codessa:
`claude mcp remove fontes`), sulje sitten sovellus ja avaa se uudelleen.

## Hyvä tietää

Fontes lukee julkisia lähteitä, enimmäkseen tuomioistuinten ja viranomaisten verkkosivustoja. Se merkitsee epäviralliset lähteet
vastauksissaan. Avaa aina lähdelinkki ennen kuin luotat ratkaisuun tai säännökseen.

Jos jokin menee vikaan, kerro sähköpostitse osoitteeseen fontesmcp@proton.me, mitä teit ja minkä virheen sait.

## Ennen kuin luotat siihen

- Fontes on tiedonhakutyökalu, ei oikeudellista neuvontaa. Sen käyttäminen ei tee kenestäkään asianajajaasi.
- Se tarjotaan ”sellaisenaan”, ilman takuuta, eivätkä sen tekijät ole vastuussa siitä, miten sitä käytetään,
  siinä määrin kuin laki sallii. Täydelliset ehdot ovat [lisenssissä](../../../LICENSE) (Apache 2.0).

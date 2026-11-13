> See on masinabil tehtud tõlge. Autoriteetne on ingliskeelne versioon.

# Fontese paigaldamine

Fontes võimaldab teie tehisintellekti rakendusel otsida kohtulahendeid ja õigusakte reaalajas kohtute ja valitsuste
veebisaitidelt enam kui 120 jurisdiktsioonis. Iga tulemus sisaldab linki originaalile. See on tavaline MCP-server,
nii et see töötab igas rakenduses, mis suudab käivitada kohalikku MCP-serverit: Claude Desktop, Codex, Claude
Code, Cursor, VS Code (GitHub Copilot), Gemini CLI, Windsurf, Zed, LM Studio, Cline ja teised.

**Fontes ei ole veel PyPI-s.** Allolevad sammud toimivad pärast esimese versiooni avaldamist.

Valige oma rakendus, järgige selle samme ja seejärel [kontrollige, et see töötab](#kontrollige-et-see-töötab).

## Claude Desktop

1. Laadige Fontese `.mcpb`-fail alla
   [viimasest väljalaskest](https://github.com/ykarapazar/fontes/releases/latest).
2. Tehke sellel topeltklõps. Claude Desktop avab selle.
3. Klõpsake **Install**.

## Codex

Terminalis:

```bash
codex mcp add fontes -- uvx fontes-mcp
```

Codex CLI ja Codexi IDE-laiendus jagavad seda seadistust (`~/.codex/config.toml`).
Vajate [uv-d](#vajate-uv-d).

## Claude Code

Terminalis:

```bash
claude mcp add fontes -- uvx fontes-mcp
```

Vajate [uv-d](#vajate-uv-d).

## Muud rakendused

Igaüks neist vajab [uv-d](#vajate-uv-d). Lisage kirje, salvestage, seejärel sulgege rakendus ja avage see uuesti.

**Cursor:** failis `~/.cursor/mcp.json` (kõik projektid) või `.cursor/mcp.json` (üks projekt):

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**VS Code (GitHub Copilot):** käivitage Command Palette'ist **MCP: Add Server**, valige
**Command (stdio)**, sisestage `uvx fontes-mcp` ja andke serverile nimi `fontes`. Või lisage see faili
`~/.copilot/mcp-config.json`:

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

Vanemad VS Code'i seadistused kasutavad faili `.vscode/mcp.json`, mille ülemise taseme võti on `servers`, mitte
`mcpServers`.

**Gemini CLI:** terminalis `gemini mcp add -s user fontes uvx fontes-mcp`. Või lisage see faili
`~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Zed:** avage oma seadete fail (**zed: open settings file**) ja lisage:

```json
{
  "context_servers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**LM Studio:** avage parempoolsel külgribal vahekaart **Program**, klõpsake **Install → Edit
mcp.json** ja lisage:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Cline:** klõpsake ikooni **MCP Servers**, avage vahekaart **Configure**, klõpsake **Configure MCP
Servers** ja lisage sama `mcpServers`-kirje nagu LM Studio puhul.

**Claude Desktop, käsitsi** (`.mcpb`-faili asemel): lisage sama `mcpServers`-kirje faili
`claude_desktop_config.json` (macOS: `~/Library/Application Support/Claude/`, Windows:
`%APPDATA%\Claude\`).

**Mis tahes muu MCP-rakendus** (Windsurf ja teised): rakenduse enda dokumentatsioon ütleb, kuhu see oma MCP-serverid salvestab.
Enamik kasutab sama kirjet: käsk `uvx`, argumendid `fontes`.

Kui rakendus ei leia käsku `uvx`, kasutage selle täielikku teed (macOS-is ja Linuxis väljastab selle `which uvx`).

## Vajate uv-d

Codex, Claude Code ja muud rakendused käivitavad Fontese käsuga `uvx`, mis tuleb koos tööriistaga **uv**: Astrali väike
tasuta tööriist. Paigaldage see
[Astrali juhendi](https://docs.astral.sh/uv/getting-started/installation/) järgi või käivitage:

- macOS või Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Windows (PowerShell): `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

## Võtmed

Mõni allikas vajab tasuta võtit: vt [KEYS.md](KEYS.md).

## Kontrollige, et see töötab

Küsige uues vestluses: *„Millistes jurisdiktsioonides saab Fontes otsida?“* Rakendus peaks vastama
riikide loeteluga. Kui ei vasta, sulgege rakendus ja avage see veel kord.

## Ühe klõpsuga paigaldaja (tulekul)

Maci ja Windowsi paigaldaja, mis seadistab Fontese korraga kõigis teie rakendustes, on tulekul. See
seadistab Claude Desktopi, Codexi, Claude Code'i, Cursori, VS Code'i (GitHub Copilot), Windsurfi, Gemini CLI,
Zedi, LM Studio ja Cline'i. Kui see on avaldatud:

**Enne alustamist:** sulgege kõik need rakendused täielikult. See on kõige olulisem Claude Code'i puhul:
töötamise ajal kirjutab see faili `~/.claude.json` üle ja võib paigaldaja muudatuse tagasi võtta. Kui te ei saa
Claude Code'i sulgeda, lisage Fontes sellesse hoopis käsuga `claude mcp add` (vt [Claude Code](#claude-code)).

**Mac**

1. Avage allalaaditud kaust **Fontes Installer**.
2. Tehke topeltklõps failil **Install Fontes.command**.
   - Kui Mac ütleb, et seda ei saa avada ("cannot be opened because it is from an unidentified developer"):
     paremklõpsake faili (või Control-klõps), valige **Open** ja seejärel uuesti **Open**. Seda on vaja teha
     ainult üks kord.
3. Avaneb aken, mis küsib, kas saata anonüümseid kasutuskordade arve; vajutage Enter, et vastata ei.
4. See küsib, kas lisada võtmed kohe. Vahelejätmiseks vajutage Enter; vt [Võtmete samm](#võtmete-samm).
5. Kui näete **Done**, avage oma tehisintellekti rakendus uuesti.

**Windows**

1. Pakkige allalaaditud **Fontes Installer** lahti (paremklõps → Extract All).
2. Tehke topeltklõps failil **Install Fontes.cmd**.
   - Kui Windows näitab teadet „Windows protected your PC“: klõpsake **More info** ja seejärel **Run anyway**.
3. Kui teilt küsitakse, kas saata anonüümseid kasutuskordade arve, vajutage Enter, et vastata ei.
4. See küsib, kas lisada võtmed kohe. Vahelejätmiseks vajutage Enter; vt [Võtmete samm](#võtmete-samm).
5. Kui näete **Done**, avage oma tehisintellekti rakendus uuesti. Kui midagi veel töötas, sulgege see
   täielikult (ka teavitusalalt kella kõrval) ja avage uuesti.

Lõpus loetleb paigaldaja rakendused, mille ta seadistas.

### Milliseid rakendusi see seadistab

See seadistab rakenduse ainult siis, kui rakenduse seadete kaust on teie arvutis juba olemas. Claude Code
seadistatakse ainult siis, kui `~/.claude.json` on olemas. Claude Desktop seadistatakse alati. Iga rakendus saab ühe
kirje, `fontes`, sellesse faili:

| Rakendus | Fail (Mac ja Linux) | Fail (Windows) |
|---|---|---|
| Claude Desktop | `~/Library/Application Support/Claude/claude_desktop_config.json` (Linux: `~/.config/Claude/`) | `%APPDATA%\Claude\claude_desktop_config.json` ning Microsoft Store'i versiooni enda koopia |
| Codex | `~/.codex/config.toml` | `%USERPROFILE%\.codex\config.toml` |
| Claude Code | `~/.claude.json` | `%USERPROFILE%\.claude.json` |
| Cursor | `~/.cursor/mcp.json` | `%USERPROFILE%\.cursor\mcp.json` |
| VS Code (Copilot) | `~/.copilot/mcp-config.json` | `%USERPROFILE%\.copilot\mcp-config.json` |
| Windsurf | `~/.config/devin/mcp_config.json` või vanemates versioonides `~/.codeium/windsurf/mcp_config.json` | `%APPDATA%\devin\mcp_config.json` või `%USERPROFILE%\.codeium\windsurf\mcp_config.json` |
| Gemini CLI | `~/.gemini/settings.json` | `%USERPROFILE%\.gemini\settings.json` |
| Zed | `~/.config/zed/settings.json` | `%APPDATA%\Zed\settings.json` |
| LM Studio | `~/.lmstudio/mcp.json` | `%USERPROFILE%\.lmstudio\mcp.json` |
| Cline | `~/.cline/data/settings/cline_mcp_settings.json` | `%USERPROFILE%\.cline\data\settings\cline_mcp_settings.json` |

VS Code seadistatakse, kui `~/.copilot` või VS Code'i enda seadete kaust on olemas.

Kaks rakendust vajavad ühte lisasammu:

- **Windsurf:** pärast uuesti avamist vajutage Cascade'is värskendamisnuppu.
- **Cline vanemas VS Code'i laienduses:** lisage Fontes käsitsi (vt [Cline](#muud-rakendused)).

### Võtmete samm

Kohe pärast paigaldamist pakub paigaldaja Prantsusmaa ja USA tasuta võtmete lisamist. Võtmete lisamiseks või
muutmiseks hiljem:

- **Mac:** tehke paigaldaja kaustas topeltklõps failil **Add or change keys.command** või avage
  rakendus Fontes Installer uuesti ja valige **Add or change keys**.
- **Windows:** tehke paigaldaja kaustas topeltklõps failil **Add or change keys.cmd**.

Sisestatav tekst on peidetud. Võtmed lisatakse igasse rakendusse, kus Fontes juba on. Seejärel sulgege rakendused ja avage
need uuesti. Kust võtmed saada ja mida need avavad: [KEYS.md](KEYS.md).

### Varukoopiad, uuesti käivitamine ja eemaldamine

Paigaldaja muudab ainult `fontes`-kirjet. Kõik muud seaded ja kommentaarid jäävad samaks.
Enne faili muutmist salvestab see selle kõrvale koopia nimega `<file>.fontes-backup-<date>`. Koopiad,
mis on tehtud pärast võtmete lisamist, sisaldavad neid võtmeid: kustutage need, mida te enam ei vaja. See
paigaldab ka uv. Seda on ohutu uuesti käivitada: see parandab seadistuse ega muuda midagi muud.

Fontese eemaldamiseks tehke topeltklõps failil **Uninstall Fontes.command** (Mac) või **Uninstall Fontes.cmd**
(Windows). See eemaldab `fontes`-kirje koos võtmetega igast rakendusest. Teie muud seaded
ja varukoopiad jäävad alles.

## Uuendused

- **Paigaldaja ja `.mcpb`-fail:** te ei pea midagi tegema. Kord päevas, kui rakendus
  käivitub, kontrollib Fontes taustal, kas on olemas uuem versioon, ja valmistab selle ette; järgmisel korral
  kasutab rakendus seda. Kui uuendust ei õnnestu alla laadida või see ei tööta, jätkab Fontes
  töötava versiooni kasutamist.
- **`uvx`:** Fontes annab teile teada, kui uuem versioon on olemas, oma jurisdiktsioonide loendi
  alguses. Et alati käivitada uusimat versiooni, kasutage `fontes-mcp` asemel `fontes-mcp@latest`.

Selleks ei saadeta kuhugi mingeid andmeid teie ega teie otsingute kohta.

## Privaatsus

Fontes ei saada vaikimisi midagi teie ega teie otsingute kohta. Kasutuskordade arvud on vabatahtlikud (opt-in) ja veateade
saadetakse alles siis, kui olete seda näinud ja kinnitanud. Üksikasjad: [PRIVACY.md](PRIVACY.md).

## Eemaldamine

Eemaldage `fontes`-kirje rakenduse MCP-seadetest (Claude Code'is:
`claude mcp remove fontes`), seejärel sulgege rakendus ja avage see uuesti.

## Hea teada

Fontes loeb avalikke allikaid, peamiselt kohtute ja valitsuste veebisaite. See märgib mitteametlikud allikad
oma vastustes. Avage alati allika link, enne kui lahendile või sättele tuginete.

Kui midagi läheb valesti, kirjutage aadressile fontesmcp@proton.me, mida te tegite ja millise vea saite.

## Enne kui sellele tuginete

- Fontes on uurimistööriist, mitte õigusnõu. Selle kasutamine ei tee kedagi teie advokaadiks.
- See antakse „nagu on“, ilma garantiita, ja selle autorid ei vastuta selle kasutamise eest,
  seadusega lubatud ulatuses. Täielikud tingimused on [litsentsis](../../../LICENSE) (Apache 2.0).

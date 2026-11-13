> Aistriúchán é seo a rinneadh le cúnamh ó mheaisín. Is é an leagan Béarla an leagan údarásach.

# Fontes a shuiteáil

Ligeann Fontes do d'aip IS breithiúnais chúirte agus reachtaíocht a chuardach beo ar shuíomhanna
gréasáin cúirteanna agus rialtais i níos mó ná 120 dlínse. Tá nasc chuig an mbunleagan i ngach
toradh. Is freastalaí MCP caighdeánach é, mar sin oibríonn sé in aon aip ar féidir léi freastalaí
MCP áitiúil a rith: Claude Desktop, Codex, Claude Code, Cursor, VS Code (GitHub Copilot), Gemini
CLI, Windsurf, Zed, LM Studio, Cline agus aipeanna eile.

Roghnaigh d'aip, lean a céimeanna, ansin [seiceáil go n-oibríonn sé](#seiceáil-go-n-oibríonn-sé).

## Claude Desktop

1. Íoslódáil an comhad Fontes `.mcpb` ón
   [eisiúint is déanaí](https://github.com/ykarapazar/fontes/releases/latest).
2. Déchliceáil é. Osclaíonn Claude Desktop é.
3. Cliceáil **Install**.

## Codex

I dteirminéal:

```bash
codex mcp add fontes -- uvx fontes-mcp
```

Roinneann Codex CLI agus síneadh IDE Codex an socrú seo (`~/.codex/config.toml`).
Teastaíonn [uv](#teastaíonn-uv-uait) uait.

## Claude Code

I dteirminéal:

```bash
claude mcp add fontes -- uvx fontes-mcp
```

Teastaíonn [uv](#teastaíonn-uv-uait) uait.

## Aipeanna eile

Teastaíonn [uv](#teastaíonn-uv-uait) ó gach ceann díobh seo. Cuir an iontráil leis, sábháil,
ansin scoir den aip agus oscail arís í.

**Cursor:** in `~/.cursor/mcp.json` (gach tionscadal) nó `.cursor/mcp.json` (tionscadal amháin):

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**VS Code (GitHub Copilot):** rith **MCP: Add Server** ón Command Palette, roghnaigh
**Command (stdio)**, iontráil `uvx fontes-mcp` agus tabhair `fontes` mar ainm ar an bhfreastalaí. Nó
cuir é seo le `~/.copilot/mcp-config.json`:

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

Úsáideann socruithe VS Code níos sine `.vscode/mcp.json`, áit arb í `servers` an eochair
barrleibhéil in ionad `mcpServers`.

**Gemini CLI:** i dteirminéal, `gemini mcp add -s user fontes uvx fontes-mcp`. Nó cuir é seo le
`~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Zed:** oscail do chomhad socruithe (**zed: open settings file**) agus cuir leis:

```json
{
  "context_servers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**LM Studio:** sa bharra taoibh ar dheis, oscail an cluaisín **Program**, cliceáil **Install → Edit
mcp.json**, agus cuir leis:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Cline:** cliceáil an deilbhín **MCP Servers**, oscail an cluaisín **Configure**, cliceáil
**Configure MCP Servers**, agus cuir leis an iontráil `mcpServers` chéanna agus a bhí do LM Studio.

**Claude Desktop, de láimh** (in ionad an chomhaid `.mcpb`): cuir an iontráil `mcpServers` chéanna
le `claude_desktop_config.json` (macOS: `~/Library/Application Support/Claude/`, Windows:
`%APPDATA%\Claude\`).

**Aon aip MCP eile** (Windsurf agus aipeanna eile): insíonn a doiciméadacht féin cá gcoinníonn sí a
freastalaithe MCP. Glacann formhór acu leis an iontráil chéanna: ordú `uvx`, argóint `fontes`.

Mura féidir leis an aip `uvx` a aimsiú, úsáid a chonair iomlán (ar macOS agus Linux, priontálann
`which uvx` í).

## Teastaíonn uv uait

Tosaíonn Codex, Claude Code agus na haipeanna eile Fontes le `uvx`, a thagann le **uv**, uirlis
bheag saor in aisce ó Astral. Chun é a shuiteáil, féach
[treoir Astral](https://docs.astral.sh/uv/getting-started/installation/), nó rith:

- macOS nó Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Windows (PowerShell): `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

## Eochracha

Teastaíonn eochair saor in aisce ó roinnt foinsí: féach [KEYS.md](KEYS.md).

## Seiceáil go n-oibríonn sé

I gcomhrá nua, fiafraigh: *"Cé na dlínsí ar féidir le Fontes a chuardach?"* Ba cheart don aip
liosta tíortha a thabhairt mar fhreagra. Mura dtugann, scoir den aip agus oscail arís í uair
amháin eile.

## Suiteálaí aon chliceáil (ar an mbealach)

Tá suiteálaí Mac agus Windows ar an mbealach a shocraíonn Fontes i do chuid aipeanna go léir in
éineacht. Socraíonn sé Claude Desktop, Codex, Claude Code, Cursor, VS Code (GitHub Copilot),
Windsurf, Gemini CLI, Zed, LM Studio agus Cline. Nuair a bheidh sé eisithe:

**Sula dtosaíonn tú:** scoir go hiomlán de gach ceann de na haipeanna seo. Is tábhachtaí é seo i
gcás Claude Code: fad atá sé ag rith, athscríobhann sé `~/.claude.json` agus féadann sé athrú an
tsuiteálaí a chealú. Mura féidir leat scor de Claude Code, cuir Fontes leis le `claude mcp add` ina
ionad sin (féach [Claude Code](#claude-code)).

**Mac**

1. Oscail an fillteán **Fontes Installer** a d'íoslódáil tú.
2. Déchliceáil **Install Fontes.command**.
   - Má deir do Mac nach féidir é a oscailt "because it is from an unidentified developer":
     deaschliceáil (nó Control-cliceáil) an comhad, roghnaigh **Open**, ansin **Open** arís. Ní
     dhéanann tú é seo ach uair amháin.
3. Osclaítear fuinneog agus fiafraíonn sé ar cheart comhairimh úsáide gan ainm a sheoladh; brúigh
   Enter le haghaidh "ní hea".
4. Fiafraíonn sé ar mhaith leat eochracha a chur leis anois. Brúigh Enter chun scipeáil; féach
   [Céim na n-eochracha](#céim-na-n-eochracha).
5. Nuair a deir sé **Done**, oscail do chuid aipeanna IS arís.

**Windows**

1. Dízipeáil an **Fontes Installer** a d'íoslódáil tú (deaschliceáil → Extract All).
2. Déchliceáil **Install Fontes.cmd**.
   - Má thaispeánann Windows "Windows protected your PC": cliceáil **More info**, ansin **Run anyway**.
3. Nuair a fhiafraítear díot ar cheart comhairimh úsáide gan ainm a sheoladh, brúigh Enter le
   haghaidh "ní hea".
4. Fiafraíonn sé ar mhaith leat eochracha a chur leis anois. Brúigh Enter chun scipeáil; féach
   [Céim na n-eochracha](#céim-na-n-eochracha).
5. Nuair a deir sé **Done**, oscail do chuid aipeanna IS arís. Má bhí ceann acu fós ag rith, dún go
   hiomlán é (ón tráidire córais freisin, in aice leis an gclog) agus oscail arís é.

Ag an deireadh liostaíonn an suiteálaí na haipeanna a shocraigh sé.

### Na haipeanna a shocraíonn sé

Ní shocraíonn sé aip ach amháin má tá fillteán socruithe na haipe sin ar do ríomhaire cheana.
Ní shocraítear Claude Code ach amháin má tá `~/.claude.json` ann. Socraítear Claude Desktop i
gcónaí. Faigheann gach aip iontráil amháin, `fontes`, sa chomhad seo:

| Aip | Comhad (Mac agus Linux) | Comhad (Windows) |
|---|---|---|
| Claude Desktop | `~/Library/Application Support/Claude/claude_desktop_config.json` (Linux: `~/.config/Claude/`) | `%APPDATA%\Claude\claude_desktop_config.json`, agus cóip féin an leagain Microsoft Store |
| Codex | `~/.codex/config.toml` | `%USERPROFILE%\.codex\config.toml` |
| Claude Code | `~/.claude.json` | `%USERPROFILE%\.claude.json` |
| Cursor | `~/.cursor/mcp.json` | `%USERPROFILE%\.cursor\mcp.json` |
| VS Code (Copilot) | `~/.copilot/mcp-config.json` | `%USERPROFILE%\.copilot\mcp-config.json` |
| Windsurf | `~/.config/devin/mcp_config.json`, nó `~/.codeium/windsurf/mcp_config.json` ar leaganacha níos sine | `%APPDATA%\devin\mcp_config.json`, nó `%USERPROFILE%\.codeium\windsurf\mcp_config.json` |
| Gemini CLI | `~/.gemini/settings.json` | `%USERPROFILE%\.gemini\settings.json` |
| Zed | `~/.config/zed/settings.json` | `%APPDATA%\Zed\settings.json` |
| LM Studio | `~/.lmstudio/mcp.json` | `%USERPROFILE%\.lmstudio\mcp.json` |
| Cline | `~/.cline/data/settings/cline_mcp_settings.json` | `%USERPROFILE%\.cline\data\settings\cline_mcp_settings.json` |

Socraítear VS Code má tá `~/.copilot` nó fillteán socruithe VS Code féin ann.

Teastaíonn céim amháin eile ó dhá aip:

- **Windsurf:** tar éis é a athoscailt, brúigh athnuaigh in Cascade.
- **Cline laistigh den seanshíneadh VS Code:** cuir Fontes leis de láimh (féach [Cline](#aipeanna-eile)).

### Céim na n-eochracha

Díreach tar éis na suiteála, tairgeann an suiteálaí na heochracha saor in aisce don Fhrainc agus
do na SA a chur leis. Chun iad a chur leis nó a athrú níos déanaí:

- **Mac:** déchliceáil **Add or change keys.command** i bhfillteán an tsuiteálaí, nó oscail aip
  Fontes Installer arís agus roghnaigh **Add or change keys**.
- **Windows:** déchliceáil **Add or change keys.cmd** i bhfillteán an tsuiteálaí.

Tá an clóscríobh folaithe. Téann na heochracha isteach i ngach aip a bhfuil Fontes inti cheana.
Scoir de na haipeanna agus oscail arís iad ina dhiaidh sin. Cá bhfaighidh tú na heochracha agus cad
a dhíghlasálann siad: [KEYS.md](KEYS.md).

### Cúltacaí, athrith agus baint

Ní athraíonn an suiteálaí ach an iontráil `fontes`. Fanann gach socrú agus nóta tráchta eile mar a
bhí. Sula n-athraíonn sé comhad, sábhálann sé cóip in aice leis, darb ainm
`<file>.fontes-backup-<date>`. Tá na heochracha i gcóipeanna a rinneadh tar éis duit eochracha a
chur leis: scrios na cinn nach bhfuil uait a thuilleadh. Suiteálann sé uv freisin. Is sábháilte é a
rith arís: deisíonn sé an socrú agus ní athraíonn sé aon rud eile.

Chun Fontes a bhaint, déchliceáil **Uninstall Fontes.command** (Mac) nó **Uninstall Fontes.cmd**
(Windows). Baineann sé an iontráil `fontes`, eochracha san áireamh, de gach aip. Fanann do
shocruithe eile agus na cóipeanna cúltaca.

## Nuashonruithe

- **Suiteálaí agus comhad `.mcpb`:** ní gá duit aon rud a dhéanamh. Uair sa lá, nuair a thosaíonn
  an aip, seiceálann Fontes sa chúlra an bhfuil leagan níos nuaí ann agus ullmhaíonn sé é; úsáidtear
  é an chéad uair eile a thosaíonn an aip. Mura féidir nuashonrú a íoslódáil nó mura n-oibríonn sé,
  leanann Fontes ag úsáid an leagain a d'oibrigh.
- **`uvx`:** insíonn Fontes duit nuair atá leagan níos nuaí ar fáil, ag barr a liosta dlínsí. Chun
  an leagan is nuaí a rith i gcónaí, úsáid `fontes-mcp@latest` in ionad `fontes-mcp`.

Ní sheoltar aon fhaisnéis fút ná faoi do chuardaigh áit ar bith chuige seo.

## Príobháideacht

Ní sheolann Fontes aon rud fút ná faoi do chuardaigh de réir réamhshocraithe. Is ar bhonn roghnach
(opt-in) atá comhairimh úsáide, agus ní sheoltar tuairisc ar fhabht ach tar éis duit í a fheiceáil
agus a dheimhniú. Sonraí: [PRIVACY.md](PRIVACY.md).

## Fontes a bhaint

Bain an iontráil `fontes` de shocruithe MCP d'aipe (in Claude Code: `claude mcp remove fontes`),
ansin scoir den aip agus oscail arís í.

## Eolas úsáideach

Léann Fontes foinsí poiblí, suíomhanna gréasáin cúirteanna agus rialtais den chuid is mó. Marcálann
sé na cinn neamhoifigiúla ina chuid freagraí. Oscail nasc na foinse i gcónaí sula mbraitheann tú ar
bhreithiúnas nó ar fhoráil.

Má théann rud éigin mícheart, seol ríomhphost chuig fontesmcp@proton.me ag insint cad a rinne tú
agus an earráid a chonaic tú.

## Sula mbraitheann tú air

- Uirlis taighde é Fontes, ní comhairle dlí. Ní dhéanann a úsáid dlíodóir duit d'aon duine.
- Soláthraítear é "mar atá", gan bharántas, agus níl a údair faoi dhliteanas as an gcaoi a
  n-úsáidtear é, a mhéid a cheadaíonn an dlí. Tá na téarmaí iomlána sa [cheadúnas](../../../LICENSE)
  (Apache 2.0).

> Aceasta este o traducere asistată automat. Versiunea în limba engleză este cea care prevalează.

# Instalarea Fontes

Fontes permite aplicației dumneavoastră de IA să caute hotărâri judecătorești și legislație în timp real pe
site-urile instanțelor și ale autorităților publice, în peste 120 de jurisdicții. Fiecare rezultat are un
link către original. Este un server MCP standard, deci funcționează în orice aplicație care poate rula un
server MCP local: Claude Desktop, Codex, Claude Code, Cursor, VS Code (GitHub Copilot), Gemini CLI, Windsurf,
Zed, LM Studio, Cline și altele.

Alegeți aplicația, urmați pașii pentru ea, apoi [verificați că funcționează](#verificarea-funcționării).

## Claude Desktop

1. Descărcați fișierul `.mcpb` al Fontes din
   [cea mai recentă versiune](https://github.com/ykarapazar/fontes/releases/latest).
2. Faceți dublu clic pe el. Claude Desktop îl deschide.
3. Faceți clic pe **Install**.

## Codex

Într-un terminal:

```bash
codex mcp add fontes -- uvx fontes-mcp
```

Codex CLI și extensia Codex pentru IDE folosesc în comun această setare (`~/.codex/config.toml`).
Aveți nevoie de [uv](#aveți-nevoie-de-uv).

## Claude Code

Într-un terminal:

```bash
claude mcp add fontes -- uvx fontes-mcp
```

Aveți nevoie de [uv](#aveți-nevoie-de-uv).

## Alte aplicații

Fiecare dintre acestea are nevoie de [uv](#aveți-nevoie-de-uv). Adăugați intrarea, salvați, apoi închideți
și redeschideți aplicația.

**Cursor:** în `~/.cursor/mcp.json` (toate proiectele) sau `.cursor/mcp.json` (un singur proiect):

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**VS Code (GitHub Copilot):** rulați **MCP: Add Server** din Command Palette, alegeți **Command (stdio)**,
introduceți `uvx fontes-mcp` și denumiți serverul `fontes`. Sau adăugați următoarele în
`~/.copilot/mcp-config.json`:

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

Configurațiile VS Code mai vechi folosesc `.vscode/mcp.json`, unde cheia de nivel superior este `servers`
în loc de `mcpServers`.

**Gemini CLI:** într-un terminal, `gemini mcp add -s user fontes uvx fontes-mcp`. Sau adăugați următoarele în
`~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Zed:** deschideți fișierul de setări (**zed: open settings file**) și adăugați:

```json
{
  "context_servers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**LM Studio:** în bara laterală din dreapta, deschideți fila **Program**, faceți clic pe **Install → Edit
mcp.json** și adăugați:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Cline:** faceți clic pe pictograma **MCP Servers**, deschideți fila **Configure**, faceți clic pe
**Configure MCP Servers** și adăugați aceeași intrare `mcpServers` ca pentru LM Studio.

**Claude Desktop, manual** (în loc de fișierul `.mcpb`): adăugați aceeași intrare `mcpServers` în
`claude_desktop_config.json` (macOS: `~/Library/Application Support/Claude/`, Windows:
`%APPDATA%\Claude\`).

**Orice altă aplicație MCP** (Windsurf și altele): propria documentație spune unde își păstrează serverele
MCP. Majoritatea acceptă aceeași intrare: comanda `uvx`, argumentul `fontes-mcp`.

Dacă aplicația nu găsește `uvx`, folosiți calea completă (pe macOS și Linux, `which uvx` o afișează).

## Aveți nevoie de uv

Codex, Claude Code și celelalte aplicații pornesc Fontes cu `uvx`, care vine împreună cu **uv**, un mic
instrument gratuit de la Astral. Pentru a-l instala, consultați
[ghidul Astral](https://docs.astral.sh/uv/getting-started/installation/) sau rulați:

- macOS sau Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Windows (PowerShell): `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

## Chei

Unele surse necesită o cheie gratuită: vedeți [KEYS.md](KEYS.md).

## Verificarea funcționării

Într-o conversație nouă, întrebați: *„În ce jurisdicții poate căuta Fontes?”* Aplicația ar trebui să
răspundă cu o listă de țări. Dacă nu, închideți și redeschideți aplicația încă o dată.

## Program de instalare cu un clic (Mac și Windows)

Programul de instalare configurează Fontes în toate aplicațiile dumneavoastră deodată: Claude
Desktop, Codex, Claude Code, Cursor, VS Code (GitHub Copilot), Windsurf, Gemini CLI, Zed, LM Studio și
Cline.

**Înainte de a începe:** închideți complet fiecare dintre aceste aplicații. Acest lucru contează cel mai
mult pentru Claude Code: cât timp rulează, rescrie `~/.claude.json` și poate anula modificarea făcută de
programul de instalare. Dacă nu puteți închide Claude Code, adăugați Fontes în el cu `claude mcp add`
(vedeți [Claude Code](#claude-code)).

**Mac**

1. Descărcați programul de instalare pentru Mac (`Fontes-Installer-…-mac.zip`) din
   [cea mai recentă versiune](https://github.com/ykarapazar/fontes/releases/latest) și faceți dublu clic pe el pentru a-l dezarhiva.
2. Faceți dublu clic pe **Fontes Installer**. Dacă Mac-ul vă întreabă dacă doriți să deschideți o aplicație
   descărcată de pe internet, faceți clic pe **Deschide**.
3. Alegeți **Instalare** și faceți clic pe **OK**. Configurarea durează aproximativ un minut.
4. Un mesaj afișează aplicațiile configurate. Faceți clic pe **Gata**, apoi deschideți din nou acele
   aplicații. Pentru a adăuga mai întâi cheile gratuite opționale, faceți clic în schimb pe **Adăugare chei**;
   vedeți [Pasul pentru chei](#pasul-pentru-chei).

**Windows**

1. Descărcați programul de instalare pentru Windows (`Fontes-Setup-….exe`) din
   [cea mai recentă versiune](https://github.com/ykarapazar/fontes/releases/latest) și faceți dublu clic pe el.
   - Dacă Windows afișează „Windows a protejat PC-ul”: faceți clic pe **Mai multe informații**, apoi pe
     **Executare oricum**.
2. Faceți clic pe **Instalare**. Se deschide o fereastră care configurează Fontes.
3. La întrebarea dacă doriți să trimiteți contorizări anonime de utilizare, apăsați Enter pentru nu.
4. Vă întreabă dacă doriți să adăugați chei acum. Apăsați Enter pentru a sări peste acest pas; vedeți
   [Pasul pentru chei](#pasul-pentru-chei).
5. Când apare **Gata**, deschideți din nou aplicațiile de IA. Dacă una dintre ele încă rula, închideți-o
   complet (inclusiv din zona de notificare, lângă ceas) și deschideți-o din nou.

La final, programul de instalare afișează lista aplicațiilor pe care le-a configurat.

### Ce aplicații configurează

Configurează o aplicație doar dacă folderul de setări al acesteia există deja pe computer. Claude Code este
configurat doar dacă există `~/.claude.json`. Claude Desktop este configurat întotdeauna. Fiecare aplicație
primește o singură intrare, `fontes`, în acest fișier:

| Aplicație | Fișier (Mac și Linux) | Fișier (Windows) |
|---|---|---|
| Claude Desktop | `~/Library/Application Support/Claude/claude_desktop_config.json` (Linux: `~/.config/Claude/`) | `%APPDATA%\Claude\claude_desktop_config.json` și copia proprie a versiunii din Microsoft Store |
| Codex | `~/.codex/config.toml` | `%USERPROFILE%\.codex\config.toml` |
| Claude Code | `~/.claude.json` | `%USERPROFILE%\.claude.json` |
| Cursor | `~/.cursor/mcp.json` | `%USERPROFILE%\.cursor\mcp.json` |
| VS Code (Copilot) | `~/.copilot/mcp-config.json` | `%USERPROFILE%\.copilot\mcp-config.json` |
| Windsurf | `~/.config/devin/mcp_config.json` sau, la versiunile mai vechi, `~/.codeium/windsurf/mcp_config.json` | `%APPDATA%\devin\mcp_config.json` sau `%USERPROFILE%\.codeium\windsurf\mcp_config.json` |
| Gemini CLI | `~/.gemini/settings.json` | `%USERPROFILE%\.gemini\settings.json` |
| Zed | `~/.config/zed/settings.json` | `%APPDATA%\Zed\settings.json` |
| LM Studio | `~/.lmstudio/mcp.json` | `%USERPROFILE%\.lmstudio\mcp.json` |
| Cline | `~/.cline/data/settings/cline_mcp_settings.json` | `%USERPROFILE%\.cline\data\settings\cline_mcp_settings.json` |

VS Code este configurat dacă există `~/.copilot` sau folderul de setări propriu al VS Code.

Două aplicații necesită un pas în plus:

- **Windsurf:** după ce o redeschideți, apăsați reîmprospătare în Cascade.
- **Cline în extensia VS Code mai veche:** adăugați Fontes manual (vedeți [Cline](#alte-aplicații)).

### Pasul pentru chei

Imediat după instalare, programul de instalare se oferă să adauge cheile gratuite pentru Franța și SUA.
Pentru a le adăuga sau modifica mai târziu:

- **Mac:** deschideți din nou **Fontes Installer** și alegeți **Adăugați sau modificați cheile**.
- **Windows:** deschideți meniul Start, apoi alegeți **Fontes** → **Adăugați sau modificați cheile**.

Textul tastat este ascuns. Cheile ajung în fiecare aplicație care are deja Fontes. Închideți și
redeschideți apoi aplicațiile. De unde obțineți cheile și ce deblochează: [KEYS.md](KEYS.md).

### Copii de rezervă, rulări repetate și eliminare

Programul de instalare modifică doar intrarea `fontes`. Toate celelalte setări și comentarii rămân așa cum
erau. Înainte de a modifica un fișier, salvează o copie lângă el, numită `<file>.fontes-backup-<date>`.
Copiile făcute după ce ați adăugat chei conțin acele chei: ștergeți-le pe cele de care nu mai aveți nevoie.
De asemenea, instalează uv. Rularea lui din nou este sigură: repară configurația și nu modifică nimic
altceva.

Pentru a elimina Fontes, deschideți **Fontes Installer** și alegeți **Eliminare** (Mac) sau dezinstalați
**Fontes** din Setări → Aplicații (Windows). Acesta elimină intrarea `fontes`, inclusiv cheile, din fiecare aplicație. Celelalte
setări și copiile de rezervă rămân.

## Actualizări

- **Programul de instalare și fișierul `.mcpb`:** nu trebuie să faceți nimic. O dată pe zi, la pornirea
  aplicației, Fontes verifică în fundal dacă există o versiune mai nouă și o pregătește; la următoarea
  pornire a aplicației o folosește. Dacă o actualizare nu poate fi descărcată sau nu funcționează, Fontes
  continuă să folosească versiunea care funcționa.
- **`uvx`:** Fontes vă anunță când este disponibilă o versiune mai nouă, în partea de sus a listei sale de
  jurisdicții. Pentru a rula întotdeauna cea mai nouă versiune, folosiți `fontes-mcp@latest` în loc de `fontes-mcp`.

Pentru aceasta nu se trimite nicăieri nicio informație despre dumneavoastră sau despre căutările
dumneavoastră.

## Confidențialitate

În mod implicit, Fontes nu trimite nimic despre dumneavoastră sau despre căutările dumneavoastră.
Contorizările de utilizare sunt opționale (opt-in), iar un raport de eroare este trimis doar după ce l-ați
văzut și l-ați confirmat. Detalii: [PRIVACY.md](PRIVACY.md).

## Eliminare

Eliminați intrarea `fontes` din setările MCP ale aplicației (în Claude Code: `claude mcp remove fontes`),
apoi închideți și redeschideți aplicația.

## Bine de știut

Fontes citește surse publice, în principal site-uri ale instanțelor și ale autorităților publice. Marchează
sursele neoficiale în răspunsurile sale. Deschideți întotdeauna linkul către sursă înainte de a vă baza pe o
hotărâre sau pe o dispoziție.

Dacă ceva nu merge, trimiteți un e-mail la fontesmcp@proton.me cu ce ați făcut și eroarea pe care ați
văzut-o.

## Înainte de a vă baza pe el

- Fontes este un instrument de cercetare, nu consultanță juridică. Folosirea lui nu face pe nimeni avocatul
  dumneavoastră.
- Este furnizat „ca atare”, fără garanție, iar autorii săi nu răspund pentru modul în care este folosit, în
  măsura permisă de lege. Condițiile complete se află în [licență](../../../LICENSE) (Apache 2.0).

> Questa è una traduzione assistita da macchina. Fa fede la versione inglese.

# Installare Fontes

Fontes consente alla Sua app di IA di consultare decisioni giudiziarie e normativa in tempo reale dai
siti web giudiziari e istituzionali di oltre 120 giurisdizioni. Ogni risultato rimanda all'originale.
È un server MCP standard, quindi funziona in qualsiasi app in grado di eseguire un server MCP locale:
Claude Desktop, Codex, Claude Code, Cursor, VS Code (GitHub Copilot), Gemini CLI, Windsurf, Zed,
LM Studio, Cline e altre.

Scelga la Sua app, segua i relativi passaggi e poi [verifichi che funzioni](#verificare-che-funzioni).

## Claude Desktop

1. Scarichi il file `.mcpb` di Fontes dall'
   [ultima versione](https://github.com/ykarapazar/fontes/releases/latest).
2. Vi faccia doppio clic. Claude Desktop lo apre.
3. Faccia clic su **Install**.

## Codex

In un terminale:

```bash
codex mcp add fontes -- uvx fontes-mcp
```

La CLI di Codex e l'estensione di Codex per IDE condividono questa configurazione
(`~/.codex/config.toml`). Le serve [uv](#le-serve-uv).

## Claude Code

In un terminale:

```bash
claude mcp add fontes -- uvx fontes-mcp
```

Le serve [uv](#le-serve-uv).

## Altre app

Ciascuna di queste richiede [uv](#le-serve-uv). Aggiunga la voce, salvi, poi chiuda e riapra l'app.

**Cursor:** in `~/.cursor/mcp.json` (tutti i progetti) o `.cursor/mcp.json` (un progetto):

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**VS Code (GitHub Copilot):** esegua **MCP: Add Server** dalla Command Palette, scelga
**Command (stdio)**, inserisca `uvx fontes-mcp` e chiami il server `fontes`. Oppure aggiunga questo a
`~/.copilot/mcp-config.json`:

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

Le configurazioni più vecchie di VS Code usano `.vscode/mcp.json`, dove la chiave di primo livello è
`servers` anziché `mcpServers`.

**Gemini CLI:** in un terminale, `gemini mcp add -s user fontes uvx fontes-mcp`. Oppure aggiunga questo a
`~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Zed:** apra il file delle impostazioni (**zed: open settings file**) e aggiunga:

```json
{
  "context_servers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**LM Studio:** nella barra laterale destra, apra la scheda **Program**, faccia clic su
**Install → Edit mcp.json** e aggiunga:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Cline:** faccia clic sull'icona **MCP Servers**, apra la scheda **Configure**, faccia clic su
**Configure MCP Servers** e aggiunga la stessa voce `mcpServers` di LM Studio.

**Claude Desktop, manualmente** (invece del file `.mcpb`): aggiunga la stessa voce `mcpServers` a
`claude_desktop_config.json` (macOS: `~/Library/Application Support/Claude/`, Windows:
`%APPDATA%\Claude\`).

**Qualsiasi altra app MCP** (Windsurf e altre): la documentazione dell'app indica dove salva i suoi
server MCP. La maggior parte accetta la stessa voce: comando `uvx`, argomento `fontes`.

Se l'app non trova `uvx`, usi il suo percorso completo (su macOS e Linux, `which uvx` lo mostra).

## Le serve uv

Codex, Claude Code e le altre app avviano Fontes con `uvx`, incluso in **uv**, un piccolo strumento
gratuito di Astral. Per installarlo, veda la
[guida di Astral](https://docs.astral.sh/uv/getting-started/installation/) oppure esegua:

- macOS o Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Windows (PowerShell): `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

## Chiavi

Alcune fonti richiedono una chiave gratuita: veda [KEYS.md](KEYS.md).

## Verificare che funzioni

In una nuova chat, chieda: *«In quali giurisdizioni può cercare Fontes?»* L'app dovrebbe rispondere
con un elenco di paesi. In caso contrario, chiuda e riapra l'app ancora una volta.

## Programma di installazione con un clic (in arrivo)

È in arrivo un programma di installazione per Mac e Windows che configura Fontes in tutte le Sue app
in una volta sola. Configura Claude Desktop, Codex, Claude Code, Cursor, VS Code (GitHub Copilot),
Windsurf, Gemini CLI, Zed, LM Studio e Cline. Quando uscirà:

**Prima di iniziare:** chiuda completamente ciascuna di queste app. È più importante per Claude Code:
mentre è in esecuzione riscrive `~/.claude.json` e può annullare la modifica del programma di
installazione. Se non può chiudere Claude Code, vi aggiunga Fontes con `claude mcp add` (veda
[Claude Code](#claude-code)).

**Mac**

1. Apra la cartella **Fontes Installer** scaricata.
2. Faccia doppio clic su **Install Fontes.command**.
   - Se il Mac dice che "cannot be opened because it is from an unidentified developer" (non può
     essere aperto perché proviene da uno sviluppatore non identificato): faccia clic destro (o
     Control-clic) sul file, scelga **Open**, poi di nuovo **Open**. Deve farlo una sola volta.
3. Si apre una finestra che chiede se inviare conteggi di utilizzo anonimi; prema Invio per
   rispondere di no.
4. Chiede se aggiungere chiavi ora. Prema Invio per saltare; veda
   [Il passaggio delle chiavi](#il-passaggio-delle-chiavi).
5. Quando compare **Fatto**, riapra le Sue app di IA.

**Windows**

1. Decomprima il **Fontes Installer** scaricato (clic destro → Extract All).
2. Faccia doppio clic su **Install Fontes.cmd**.
   - Se Windows mostra "Windows protected your PC": faccia clic su **More info**, poi su
     **Run anyway**.
3. Quando chiede se inviare conteggi di utilizzo anonimi, prema Invio per rispondere di no.
4. Chiede se aggiungere chiavi ora. Prema Invio per saltare; veda
   [Il passaggio delle chiavi](#il-passaggio-delle-chiavi).
5. Quando compare **Fatto**, riapra le Sue app di IA. Se una era ancora in esecuzione, la chiuda
   completamente (anche dall'area di notifica, vicino all'orologio) e la riapra.

Alla fine, il programma di installazione elenca le app che ha configurato.

### Quali app configura

Configura un'app solo se la cartella di configurazione di quell'app esiste già sul computer. Claude
Code viene configurato solo se esiste `~/.claude.json`. Claude Desktop viene configurato sempre. Ogni
app riceve una voce, `fontes`, in questo file:

| App | File (Mac e Linux) | File (Windows) |
|---|---|---|
| Claude Desktop | `~/Library/Application Support/Claude/claude_desktop_config.json` (Linux: `~/.config/Claude/`) | `%APPDATA%\Claude\claude_desktop_config.json`, e la copia propria della versione Microsoft Store |
| Codex | `~/.codex/config.toml` | `%USERPROFILE%\.codex\config.toml` |
| Claude Code | `~/.claude.json` | `%USERPROFILE%\.claude.json` |
| Cursor | `~/.cursor/mcp.json` | `%USERPROFILE%\.cursor\mcp.json` |
| VS Code (Copilot) | `~/.copilot/mcp-config.json` | `%USERPROFILE%\.copilot\mcp-config.json` |
| Windsurf | `~/.config/devin/mcp_config.json`, o `~/.codeium/windsurf/mcp_config.json` nelle versioni più vecchie | `%APPDATA%\devin\mcp_config.json`, o `%USERPROFILE%\.codeium\windsurf\mcp_config.json` |
| Gemini CLI | `~/.gemini/settings.json` | `%USERPROFILE%\.gemini\settings.json` |
| Zed | `~/.config/zed/settings.json` | `%APPDATA%\Zed\settings.json` |
| LM Studio | `~/.lmstudio/mcp.json` | `%USERPROFILE%\.lmstudio\mcp.json` |
| Cline | `~/.cline/data/settings/cline_mcp_settings.json` | `%USERPROFILE%\.cline\data\settings\cline_mcp_settings.json` |

VS Code viene configurato se esiste `~/.copilot` o la cartella delle impostazioni di VS Code stesso.

Due app richiedono un passaggio in più:

- **Windsurf:** dopo averlo riaperto, faccia clic su aggiorna (refresh) in Cascade.
- **Cline all'interno della vecchia estensione di VS Code:** vi aggiunga Fontes manualmente (veda
  [Cline](#altre-app)).

### Il passaggio delle chiavi

Subito dopo l'installazione, il programma di installazione Le propone di aggiungere le chiavi gratuite
per la Francia e gli Stati Uniti. Per aggiungerle o modificarle in seguito:

- **Mac:** faccia doppio clic su **Add or change keys.command** nella cartella del programma di
  installazione, oppure riapra l'app Fontes Installer e scelga **Aggiungi o modifica chiavi**.
- **Windows:** faccia doppio clic su **Add or change keys.cmd** nella cartella del programma di
  installazione.

Ciò che digita non viene mostrato. Le chiavi vanno a tutte le app che hanno già Fontes. Poi chiuda e
riapra le app. Dove ottenere le chiavi e che cosa sbloccano: [KEYS.md](KEYS.md).

### Copie di backup, nuove esecuzioni e rimozione

Il programma di installazione modifica solo la voce `fontes`. Tutte le altre impostazioni e i
commenti restano come erano. Prima di modificare un file, ne salva una copia accanto, denominata
`<file>.fontes-backup-<date>`. Le copie fatte dopo aver aggiunto chiavi contengono tali chiavi:
elimini quelle che non Le servono più. Installa anche uv. Eseguirlo di nuovo è sicuro: ripara la
configurazione e non modifica nient'altro.

Per rimuovere Fontes, faccia doppio clic su **Uninstall Fontes.command** (Mac) o
**Uninstall Fontes.cmd** (Windows). Rimuove la voce `fontes`, chiavi comprese, da ogni app. Le altre
impostazioni e le copie di backup restano.

## Aggiornamenti

- **Programma di installazione e file `.mcpb`:** non deve fare nulla. Una volta al giorno, all'avvio
  dell'app, Fontes controlla in background se esiste una versione più recente e la prepara; al
  successivo avvio dell'app viene usata. Se un aggiornamento non può essere scaricato o non funziona,
  Fontes continua a usare la versione funzionante.
- **`uvx`:** Fontes La avvisa quando esiste una versione più recente, in cima all'elenco delle
  giurisdizioni. Per eseguire sempre la versione più recente, usi `fontes-mcp@latest` invece di `fontes-mcp`.

Per questo non viene inviata da nessuna parte alcuna informazione su di Lei o sulle Sue ricerche.

## Privacy

Per impostazione predefinita, Fontes non invia nulla su di Lei o sulle Sue ricerche. I conteggi di
utilizzo sono facoltativi (opt-in) e una segnalazione di errore viene inviata solo dopo che Lei l'ha
vista e confermata. Dettagli: [PRIVACY.md](PRIVACY.md).

## Rimuoverlo

Rimuova la voce `fontes` dalla configurazione MCP dell'app (in Claude Code:
`claude mcp remove fontes`), poi chiuda e riapra l'app.

## Buono a sapersi

Fontes legge fonti pubbliche, soprattutto siti web giudiziari e istituzionali. Segnala quelle non
ufficiali nelle risposte. Apra sempre il link alla fonte prima di fare affidamento su una decisione o
una disposizione.

Se qualcosa non funziona, scriva a fontesmcp@proton.me indicando che cosa ha fatto e l'errore ottenuto.

## Prima di farvi affidamento

- Fontes è uno strumento di ricerca, non consulenza legale. Usarlo non rende nessuno il Suo avvocato.
- È fornito "così com'è", senza garanzia, e i suoi autori non sono responsabili dell'uso che se ne
  fa, nei limiti consentiti dalla legge. I termini completi sono nella [licenza](../../../LICENSE)
  (Apache 2.0).

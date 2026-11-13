> Questa è una traduzione assistita da macchina. Fa fede la versione inglese.

# Chiavi API

Quasi tutte le fonti di Fontes funzionano senza chiave. Due richiedono una chiave gratuita:

| Chiave | Sblocca | Senza la chiave |
|---|---|---|
| `WLM_FR_PISTE_CLIENT_ID` + `WLM_FR_PISTE_CLIENT_SECRET` | Francia: Judilibre (decisioni giudiziarie) e Légifrance (normativa) | La Francia è disattivata. `list_jurisdictions` la mostra come inattiva. |
| `WLM_US_GOVINFO_KEY` | Stati Uniti: ricerca su govinfo (decisioni dei tribunali federali, Statutes at Large, public laws) | Fontes usa la `DEMO_KEY` condivisa: circa 10 ricerche al giorno per indirizzo IP. Aprire una decisione nota e lo US Code non richiede chiave. |

Le chiavi sono facoltative. Può aggiungerle in seguito.

## Aggiungere una chiave

**Con il programma di installazione.** Durante l'installazione, il programma chiede se aggiungere
chiavi. Scelga **Non ora** (o prema Invio) per saltare. Per aggiungere o modificare chiavi in seguito,
esegua **Add or change keys**:

- Mac: riapra l'app Fontes Installer e scelga **Aggiungi o modifica chiavi**, oppure faccia doppio
  clic su `Add or change keys.command` nella cartella del programma di installazione.
- Windows: faccia doppio clic su `Add or change keys.cmd` nella cartella del programma di
  installazione. Il programma di setup per Windows, quando sarà disponibile, lo inserisce anche in
  Start menu > Fontes.

Ciò che digita non viene mostrato. Per ogni chiave: la incolli, prema Invio per mantenere quella
attuale o digiti `-` per rimuoverla. Le chiavi vanno a tutte le app che hanno già Fontes.

**Con l'estensione di Claude Desktop (.mcpb).** Apra Claude > Settings > Extensions > Fontes e
compili i campi. Sono tutti facoltativi.

**Manualmente.** Aggiunga le variabili al blocco `env` della voce `fontes` nella configurazione MCP
della Sua app:

```json
"fontes": {
  "command": "...",
  "args": ["..."],
  "env": { "WLM_US_GOVINFO_KEY": "your-key" }
}
```

Riavvii l'app dopo ogni modifica.

## Francia: PISTE (gratuito)

1. Crei un account su [piste.gouv.fr](https://piste.gouv.fr). Ciò comporta l'accettazione delle
   condizioni di PISTE (CGU).
2. Vada su API > **Consentement CGU API**. Accetti le condizioni di **JUDILIBRE** e **Légifrance**
   (produzione).
3. Crei un'**applicazione di produzione**. L'`APP_SANDBOX` creata per Lei non può accedere alla
   produzione. In "Modifier l'application", selezioni **JUDILIBRE (production)** e
   **Légifrance (production)** e applichi.
4. Apra la scheda **Authentification** dell'applicazione. Copi `client_id` e `client_secret`.
5. Esegua **Add or change keys** e li incolli.

Condizioni, in breve:

- Dati: Licence Ouverte / Etalab 2.0. Il riutilizzo, anche commerciale, è consentito con
  attribuzione.
- Non pubblichi né condivida le Sue credenziali. Avvisi PISTE se vengono divulgate.
- L'API di Légifrance è un servizio beta. Può essere sospesa e ha quote (per secondo, minuto e
  giorno).
- I testi di Légifrance non sono la versione autentica. Lo è solo il PDF firmato del Journal officiel.
- Judilibre: non usi i nomi di giudici o cancellieri per valutare, confrontare o prevedere il loro
  lavoro (Code de l'organisation judiciaire, art. L111-13; è un reato).
- Judilibre: rispetti il GDPR. Non tenti di reidentificare le parti.

Le Sue quote si trovano in PISTE, in API Sélectionnées > Actions > Consulter les quotas.

## Stati Uniti: api.data.gov (gratuito)

1. Vada su [govinfo.gov/api-signup](https://www.govinfo.gov/api-signup) (la chiave viene mostrata
   sullo schermo) o su [api.data.gov/signup](https://api.data.gov/signup/) (la chiave viene inviata
   per e-mail).
2. Inserisca nome ed e-mail. Il campo "how will you use it" è facoltativo.
3. Copi la chiave di 40 caratteri.
4. Esegua **Add or change keys** e la incolli come chiave per gli Stati Uniti.

Condizioni, in breve:

- Con la Sua chiave, govinfo consente fino a 36.000 richieste all'ora.
- Non abbiamo trovato condizioni di servizio specifiche per l'API (api.data.gov/terms/ non esiste).
  Non verificato. Veda le [policy di govinfo](https://www.govinfo.gov/about/policies) e
  l'[informativa sulla privacy di data.gov](https://data.gov/privacy-policy/).
- Non condivida la chiave.

## Dove vengono salvate le chiavi

- **Programma di installazione o manualmente:** in testo semplice nel file di configurazione MCP di
  ciascuna app, nel blocco `env` della voce `fontes`. Chiunque possa leggere i Suoi file utente può
  leggere le chiavi.
  - Claude Desktop: `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac),
    `%APPDATA%\Claude\claude_desktop_config.json` (Windows)
  - Claude Code: `~/.claude.json`
  - Codex: `~/.codex/config.toml`
  - Cursor: `~/.cursor/mcp.json`
  - VS Code (Copilot): `~/.copilot/mcp-config.json`
  - Windsurf: `~/.config/devin/mcp_config.json` o `~/.codeium/windsurf/mcp_config.json`
    (Windows: `%APPDATA%\devin\mcp_config.json`)
  - Gemini CLI: `~/.gemini/settings.json`
  - Zed: `~/.config/zed/settings.json` (Windows: `%APPDATA%\Zed\settings.json`)
  - LM Studio: `~/.lmstudio/mcp.json`
  - Cline: `~/.cline/data/settings/cline_mcp_settings.json`
- **Estensione di Claude Desktop (.mcpb):** Claude salva questi campi nelle sue impostazioni e li
  protegge con l'archivio sicuro del Suo sistema (Keychain su Mac, Credential Manager su Windows).

Prima di ogni modifica, il programma di installazione salva una copia del file di configurazione
accanto a esso (`<file>.fontes-backup-<time>`). Le copie fatte dopo aver aggiunto chiavi contengono
anche le chiavi. Elimini le copie vecchie che non Le servono.

## Modificare o rimuovere una chiave

- Esegua **Add or change keys**. Incolli una nuova chiave per sostituirla o digiti `-` per rimuoverla.
- Oppure modifichi manualmente il blocco `env` e riavvii l'app.
- Disinstallare Fontes rimuove l'intera voce, chiavi comprese. Le copie di backup non vengono
  eliminate.
- Se una chiave è stata divulgata, la sostituisca anche all'origine: in PISTE, generi nuove
  credenziali per la Sua applicazione; su api.data.gov, si registri per una nuova chiave.

## Messaggi che può vedere

| Messaggio | Significato |
|---|---|
| `France needs a free PISTE key: set WLM_FR_PISTE_CLIENT_ID and WLM_FR_PISTE_CLIENT_SECRET.` | Nessuna chiave per la Francia. Ne aggiunga una. |
| `Inactive: needs a free PISTE account. ...` (in `list_jurisdictions`) | Lo stesso. |
| `PISTE refused the client credentials ...` | L'ID o il segreto è errato o non è più valido. Copi di nuovo entrambi dalla scheda Authentification. |
| `PISTE denied access to the ... API: subscribe the application to ... and accept its CGU on piste.gouv.fr.` | La Sua applicazione non è abbonata a quell'API, o non ne ha accettato le condizioni. Veda i passaggi 2 e 3. |
| `Using govinfo DEMO_KEY (about 10 searches/day per IP) ...` | Nessuna chiave per gli Stati Uniti. La ricerca funziona per alcune chiamate al giorno. |
| `govinfo rate limit reached (Retry-After ...). DEMO_KEY allows only about 10 searches a day per IP ...` | La chiave dimostrativa è esaurita. Aggiunga la Sua chiave. |
| `govinfo refused the API key (WLM_US_GOVINFO_KEY).` | La chiave è errata o non è ancora stata confermata via e-mail. |

Un valore vuoto equivale all'assenza di chiave.

## Autorizzazioni (WLM_PERMITTED)

Questa non è una chiave API, e il programma di installazione non la imposta. **La imposti solo se
dispone Lei stesso di tale autorizzazione.**

Alcune fonti sono disattivate per impostazione predefinita perché le loro condizioni o il loro
robots.txt vietano l'uso automatizzato senza autorizzazione. Se dispone dell'autorizzazione
dell'editore, attivi una fonte aggiungendo il suo codice a `WLM_PERMITTED`, separato da virgole, nel
blocco `env`: `"WLM_PERMITTED": "in,de"`.

| Codice | Fonte |
|---|---|
| `az` | Azerbaigian: e-qanun.az (Ministero della Giustizia) |
| `bh` | Bahrein: Legislation and Legal Opinion Commission (lloc.gov.bh) |
| `co` | Colombia: Función Pública, Gestor Normativo (normativa consolidata) |
| `de` | Germania: NeuRIS (portale federale di informazione giuridica, servizio di prova) |
| `difc` | Dubai International Financial Centre Courts (difccourts.ae) |
| `gr` | Grecia: Poligrafico nazionale, ricerca nella Gazzetta ufficiale del governo (search.et.gr) |
| `in` | India: India Code (indiacode.gov.in) |
| `mu` | Mauritius: Supreme Court (supremecourt.govmu.org) |
| `sg` | Singapore: decisioni giudiziarie (elitigation.sg) |

Senza autorizzazione, Fontes dice: `Off by default (<code>): the terms or robots.txt of ... forbid
automated use without the operator's permission.`

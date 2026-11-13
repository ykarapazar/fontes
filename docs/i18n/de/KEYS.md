> Dies ist eine maschinengestützte Übersetzung. Maßgeblich ist die englische Fassung.

# API-Schlüssel

Fast jede Quelle in Fontes funktioniert ohne Schlüssel. Zwei benötigen einen kostenlosen:

| Schlüssel | Schaltet frei | Ohne ihn |
|---|---|---|
| `WLM_FR_PISTE_CLIENT_ID` + `WLM_FR_PISTE_CLIENT_SECRET` | Frankreich: Judilibre (Gerichtsentscheidungen) und Légifrance (Rechtsvorschriften) | Frankreich ist aus. `list_jurisdictions` zeigt es als inaktiv an. |
| `WLM_US_GOVINFO_KEY` | Vereinigte Staaten: govinfo-Suche (Entscheidungen der Bundesgerichte, Statutes at Large, public laws) | Fontes verwendet den gemeinsamen `DEMO_KEY`: etwa 10 Suchen pro Tag und IP-Adresse. Das Öffnen einer bekannten Entscheidung und der US Code benötigen keinen Schlüssel. |

Schlüssel sind optional. Sie können sie später hinzufügen.

## Einen Schlüssel hinzufügen

**Mit dem Installationsprogramm.** Während der Installation fragt das Installationsprogramm, ob Sie
Schlüssel hinzufügen möchten. Wählen Sie **Nicht jetzt** (oder drücken Sie Enter), um das zu
überspringen. Um Schlüssel später hinzuzufügen oder zu ändern, führen Sie **Add or change keys** aus:

- Mac: Öffnen Sie die App Fontes Installer erneut und wählen Sie **Schlüssel hinzufügen oder
  ändern**, oder doppelklicken Sie im Ordner des Installationsprogramms auf
  `Add or change keys.command`.
- Windows: Doppelklicken Sie im Ordner des Installationsprogramms auf `Add or change keys.cmd`. Das
  Windows-Setupprogramm legt es, sobald es verfügbar ist, außerdem unter Startmenü > Fontes ab.

Die Eingabe wird nicht angezeigt. Für jeden Schlüssel: Fügen Sie ihn ein, drücken Sie Enter, um den
vorhandenen zu behalten, oder geben Sie `-` ein, um ihn zu entfernen. Die Schlüssel werden in jede App
eingetragen, die Fontes bereits hat.

**Mit der Claude-Desktop-Erweiterung (.mcpb).** Öffnen Sie Claude > Settings > Extensions > Fontes und
füllen Sie die Felder aus. Alle sind optional.

**Von Hand.** Fügen Sie die Variablen in den `env`-Block des Eintrags `fontes` in der MCP-Konfiguration
Ihrer App ein:

```json
"fontes": {
  "command": "...",
  "args": ["..."],
  "env": { "WLM_US_GOVINFO_KEY": "your-key" }
}
```

Starten Sie die App nach jeder Änderung neu.

## Frankreich: PISTE (kostenlos)

1. Legen Sie ein Konto auf [piste.gouv.fr](https://piste.gouv.fr) an. Dabei akzeptieren Sie die
   Nutzungsbedingungen von PISTE (CGU).
2. Gehen Sie zu API > **Consentement CGU API**. Akzeptieren Sie die Bedingungen für **JUDILIBRE** und
   **Légifrance** (Produktion).
3. Legen Sie eine **Produktionsanwendung** an. Die für Sie angelegte `APP_SANDBOX` kann die Produktion
   nicht erreichen. Kreuzen Sie unter „Modifier l'application“ **JUDILIBRE (production)** und
   **Légifrance (production)** an und übernehmen Sie die Änderung.
4. Öffnen Sie den Reiter **Authentification** der Anwendung. Kopieren Sie `client_id` und
   `client_secret`.
5. Führen Sie **Add or change keys** aus und fügen Sie beide ein.

Die Bedingungen in Kürze:

- Daten: Licence Ouverte / Etalab 2.0. Die Weiterverwendung, auch die kommerzielle, ist mit
  Quellenangabe erlaubt.
- Veröffentlichen oder teilen Sie Ihre Zugangsdaten nicht. Informieren Sie PISTE, wenn sie
  bekannt werden.
- Die Légifrance-API ist ein Beta-Dienst. Er kann ausgesetzt werden und hat Kontingente (pro
  Sekunde, Minute und Tag).
- Die Texte auf Légifrance sind nicht die authentische Fassung. Authentisch ist nur das signierte
  PDF des Journal officiel.
- Judilibre: Verwenden Sie die Namen von Richterinnen und Richtern oder von Urkundsbeamten nicht, um
  deren Arbeit zu bewerten, zu vergleichen oder vorherzusagen (Code de l'organisation judiciaire
  Art. L111-13; eine Straftat).
- Judilibre: Halten Sie die DSGVO ein. Versuchen Sie nicht, die Parteien wieder zu identifizieren.

Ihre Kontingente finden Sie auf PISTE unter API Sélectionnées > Actions > Consulter les quotas.

## Vereinigte Staaten: api.data.gov (kostenlos)

1. Gehen Sie zu [govinfo.gov/api-signup](https://www.govinfo.gov/api-signup) (der Schlüssel wird auf
   dem Bildschirm angezeigt) oder zu [api.data.gov/signup](https://api.data.gov/signup/) (der
   Schlüssel wird Ihnen per E-Mail zugesandt).
2. Geben Sie Ihren Namen und Ihre E-Mail-Adresse ein. Das Feld „how will you use it“ ist optional.
3. Kopieren Sie den 40-stelligen Schlüssel.
4. Führen Sie **Add or change keys** aus und fügen Sie ihn als US-Schlüssel ein.

Die Bedingungen in Kürze:

- Mit Ihrem eigenen Schlüssel erlaubt govinfo bis zu 36.000 Anfragen pro Stunde.
- Wir haben keine API-spezifischen Nutzungsbedingungen gefunden (api.data.gov/terms/ existiert
  nicht). Nicht verifiziert. Siehe die [Richtlinien von govinfo](https://www.govinfo.gov/about/policies)
  und die [Datenschutzrichtlinie von data.gov](https://data.gov/privacy-policy/).
- Behalten Sie den Schlüssel für sich.

## Wo die Schlüssel gespeichert werden

- **Mit dem Installationsprogramm oder von Hand:** als Klartext in der MCP-Konfigurationsdatei jeder
  App, im `env`-Block des Eintrags `fontes`. Wer Ihre Benutzerdateien lesen kann, kann die Schlüssel
  lesen.
  - Claude Desktop: `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac),
    `%APPDATA%\Claude\claude_desktop_config.json` (Windows)
  - Claude Code: `~/.claude.json`
  - Codex: `~/.codex/config.toml`
  - Cursor: `~/.cursor/mcp.json`
  - VS Code (Copilot): `~/.copilot/mcp-config.json`
  - Windsurf: `~/.config/devin/mcp_config.json` oder `~/.codeium/windsurf/mcp_config.json`
    (Windows: `%APPDATA%\devin\mcp_config.json`)
  - Gemini CLI: `~/.gemini/settings.json`
  - Zed: `~/.config/zed/settings.json` (Windows: `%APPDATA%\Zed\settings.json`)
  - LM Studio: `~/.lmstudio/mcp.json`
  - Cline: `~/.cline/data/settings/cline_mcp_settings.json`
- **Claude-Desktop-Erweiterung (.mcpb):** Claude speichert diese Felder in seinen Einstellungen und
  schützt sie mit dem sicheren Speicher Ihres Systems (Schlüsselbund auf dem Mac,
  Anmeldeinformationsverwaltung unter Windows).

Vor jeder Änderung speichert das Installationsprogramm eine Kopie der Konfigurationsdatei daneben
(`<file>.fontes-backup-<time>`). Kopien, die erstellt wurden, nachdem Sie Schlüssel hinzugefügt
haben, enthalten ebenfalls die Schlüssel. Löschen Sie alte Kopien, die Sie nicht brauchen.

## Einen Schlüssel ändern oder entfernen

- Führen Sie **Add or change keys** aus. Fügen Sie einen neuen Schlüssel ein, um ihn zu ersetzen, oder
  geben Sie `-` ein, um ihn zu entfernen.
- Oder bearbeiten Sie den `env`-Block von Hand und starten Sie die App neu.
- Die Deinstallation von Fontes entfernt seinen gesamten Eintrag, einschließlich der Schlüssel. Die
  Sicherungskopien löscht sie nicht.
- Wenn ein Schlüssel bekannt geworden ist, ersetzen Sie ihn auch bei der Quelle: Erstellen Sie auf
  PISTE neue Zugangsdaten für Ihre Anwendung; registrieren Sie sich bei api.data.gov für einen neuen
  Schlüssel.

## Meldungen, die Sie sehen können

| Meldung | Bedeutung |
|---|---|
| `France needs a free PISTE key: set WLM_FR_PISTE_CLIENT_ID and WLM_FR_PISTE_CLIENT_SECRET.` | Kein Schlüssel für Frankreich. Fügen Sie einen hinzu. |
| `Inactive: needs a free PISTE account. ...` (in `list_jurisdictions`) | Dasselbe. |
| `PISTE refused the client credentials ...` | Die ID oder das Secret ist falsch oder nicht mehr gültig. Kopieren Sie beide erneut aus dem Reiter Authentification. |
| `PISTE denied access to the ... API: subscribe the application to ... and accept its CGU on piste.gouv.fr.` | Ihre Anwendung hat diese API nicht abonniert, oder Sie haben deren Bedingungen nicht akzeptiert. Siehe Schritte 2 und 3. |
| `Using govinfo DEMO_KEY (about 10 searches/day per IP) ...` | Kein US-Schlüssel. Die Suche funktioniert für einige Aufrufe pro Tag. |
| `govinfo rate limit reached (Retry-After ...). DEMO_KEY allows only about 10 searches a day per IP ...` | Der Demo-Schlüssel ist aufgebraucht. Fügen Sie Ihren eigenen Schlüssel hinzu. |
| `govinfo refused the API key (WLM_US_GOVINFO_KEY).` | Der Schlüssel ist falsch oder noch nicht über die E-Mail bestätigt. |

Ein leerer Wert gilt als kein Schlüssel.

## Erlaubnisse (WLM_PERMITTED)

Dies ist kein API-Schlüssel, und das Installationsprogramm setzt ihn nicht. **Setzen Sie ihn nur,
wenn Sie diese Erlaubnis selbst haben.**

Einige Quellen sind standardmäßig aus, weil ihre Nutzungsbedingungen oder ihre robots.txt die
automatisierte Nutzung ohne Erlaubnis verbieten. Wenn Sie die Erlaubnis des Herausgebers haben,
schalten Sie eine Quelle ein, indem Sie ihren Code durch Kommas getrennt zu `WLM_PERMITTED` im
`env`-Block hinzufügen: `"WLM_PERMITTED": "in,de"`.

| Code | Quelle |
|---|---|
| `az` | Aserbaidschan: e-qanun.az (Justizministerium) |
| `bh` | Bahrain: Legislation and Legal Opinion Commission (lloc.gov.bh) |
| `co` | Kolumbien: Función Pública, Gestor Normativo (konsolidierte Rechtsvorschriften) |
| `de` | Deutschland: NeuRIS (Rechtsinformationsportal des Bundes, Testbetrieb) |
| `difc` | Dubai International Financial Centre Courts (difccourts.ae) |
| `gr` | Griechenland: Nationale Druckerei, Suche im Regierungsanzeiger (search.et.gr) |
| `in` | Indien: India Code (indiacode.gov.in) |
| `mu` | Mauritius: Supreme Court (supremecourt.govmu.org) |
| `sg` | Singapur: Gerichtsentscheidungen (elitigation.sg) |

Ohne Erlaubnis meldet Fontes: `Off by default (<code>): the terms or robots.txt of ... forbid
automated use without the operator's permission.`

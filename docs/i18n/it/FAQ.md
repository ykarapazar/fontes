> Questa è una traduzione assistita da macchina. Fa fede la versione inglese.

# Fontes: domande e risposte

## Che cos'è Fontes?

Un server MCP gratuito e open source (Apache 2.0). Consente a qualsiasi app che parli il Model
Context Protocol (Claude, Codex, Cursor, VS Code, Gemini CLI e altre) di cercare decisioni
giudiziarie e normativa in tempo reale dai siti web giudiziari e istituzionali di oltre 120
giurisdizioni e corti internazionali (124 adattatori). Ogni risultato indica la sua fonte e rimanda
all'originale.

## I testi sono ufficiali?

Per lo più, ma non sempre.

- La maggior parte delle fonti è gestita da un organo giurisdizionale, un ministero o una gazzetta
  ufficiale.
- Alcuni testi consolidati sono pubblicati da un governo ma sono espressamente non ufficiali: solo la
  gazzetta ufficiale è autentica.
- Alcune fonti non sono nemmeno siti istituzionali (ad esempio LexiVox, LawPhil, Maqam, Wikisource).

Fontes aggiunge un avviso "Unofficial source" (fonte non ufficiale) a ogni risposta che proviene da
una di queste. Prima di citare qualcosa, verifichi la pubblicazione ufficiale. La tabella di
copertura nel [README](README.md#copertura) e `list_jurisdictions` indicano la fonte di ogni
giurisdizione.

## Quali giurisdizioni copre, e in che misura?

124 adattatori: 108 Stati membri dell'ONU, Hong Kong, Kosovo, Palestina, Taiwan, le DIFC Courts e 11
corti e organismi internazionali (come la Corte europea dei diritti dell'uomo, l'UE, la CIG e l'OMC).

La copertura varia molto. Secondo un criterio rigoroso (la giurisprudenza della corte suprema della
giurisdizione ordinaria, oppure la costituzione e le leggi, coperte integralmente), 72 su 124 risultano
coperte. [COVERAGE.md](../../COVERAGE.md) indica, per ogni giurisdizione, che cosa Fontes copre, che
cosa non copre e perché.

## Mi serve una chiave API?

Per quasi tutte le giurisdizioni, no. Alcune fonti richiedono una chiave gratuita: veda
[KEYS.md](KEYS.md).

- **Francia:** sì. La Francia è disattivata finché non imposta `WLM_FR_PISTE_CLIENT_ID` e
  `WLM_FR_PISTE_CLIENT_SECRET`. Si ottengono da un account PISTE gratuito (piste.gouv.fr) con
  un'applicazione abbonata a Judilibre e Légifrance.
- **Stati Uniti:** facoltativa. La ricerca nella giurisprudenza funziona senza chiave, ma la chiave
  dimostrativa condivisa consente solo circa 10 ricerche al giorno per indirizzo IP. Una chiave
  gratuita di api.data.gov in `WLM_US_GOVINFO_KEY` aumenta questo limite.

Le imposti come variabili d'ambiente per il server Fontes nella configurazione MCP della Sua app.
Quando uscirà il programma di installazione, Le chiederà le chiavi dopo l'installazione, e il suo
collegamento **Add or change keys** consente di modificarle in seguito.

A parte questo, alcune fonti dichiarano nelle loro condizioni che l'accesso automatizzato richiede
l'autorizzazione dell'editore. Sono indicate come OFF e restano disattivate. Una chiave non cambia
questa situazione; solo l'autorizzazione dell'editore la cambia (poi imposti
`WLM_PERMITTED=<codes>`).

## Che cosa lascia il mio computer?

Le Sue ricerche vanno solo alla fonte in cui si cerca. Fontes non mantiene alcuna banca dati e non
richiede alcun account.

Oltre alle fonti, Fontes chiede a PyPI una volta al giorno se esiste una versione più recente (la
disattivi con `FONTES_NO_UPDATE_CHECK=1`). I conteggi di utilizzo sono disattivati a meno che Lei non
li attivi, e una segnalazione di errore viene inviata solo dopo che Lei l'ha vista e confermata. La
Sua app di IA vede la Sua conversazione secondo le proprie condizioni.

Tutti i dettagli: [PRIVACY.md](PRIVACY.md).

## È consulenza legale?

No. Fontes è uno strumento di ricerca. Trova testi; non Le dice che cosa significano per il Suo caso,
e il suo uso non crea alcun rapporto avvocato-cliente con nessuno. L'app di IA può leggere male un
testo, quindi legga la decisione o la disposizione completa prima di farvi affidamento. Per una
consulenza, si rivolga a un avvocato abilitato nel luogo in cui sorge la Sua questione.

## Chi lo mantiene? Continuerà a funzionare?

Una persona: Yüce Karapazar. Non c'è alcuna società dietro Fontes, nessun contratto di assistenza,
nessun accordo sul livello di servizio. Non vengono offerti servizi legali.

Le fonti vengono verificate una volta al giorno e i risultati sono pubblicati nella
[pagina di stato](https://ykarapazar.github.io/fontes/status/?lang=it). I siti web giudiziari e
istituzionali cambiano senza preavviso, quindi una fonte può smettere di funzionare in qualsiasi
momento. Non c'è alcuna garanzia che una fonte, o Fontes stesso, continui a funzionare. Fontes è
fornito "così com'è", senza garanzia (sezioni 7 e 8 della [LICENSE](../../../LICENSE)).

## Un testo è errato, non aggiornato o una fonte non funziona. Come lo segnalo?

- Apra una issue con il modulo "Broken or wrong source":
  <https://github.com/ykarapazar/fontes/issues/new/choose>. Indichi quale giurisdizione, che cosa ha
  chiesto, che cosa ha ottenuto e la pagina ufficiale che mostra il testo corretto.
- Oppure chieda alla Sua app di IA di "segnalare un errore di Fontes" (o esegua
  `fontes report-bug`). Vede la segnalazione prima che venga inviato qualsiasi cosa.
- Oppure scriva a fontesmcp@proton.me.

Non includa dati dei clienti né fatti riservati in una segnalazione.

**Se gestisce una delle fonti** e qualcosa non è corretto (le Sue condizioni, robots.txt, i limiti di
richieste), scriva a fontesmcp@proton.me. La fonte verrà corretta o disattivata.

## In che cosa Fontes differisce dagli strumenti di ricerca giuridica ospitati?

- **Viene eseguito sul Suo computer.** Non c'è alcun server Fontes né alcun account. Ciò significa
  anche che funziona solo nelle app in grado di avviare un server MCP locale (Claude Desktop, Codex,
  Cursor, VS Code e simili), non nelle app solo web che accettano soltanto connettori ospitati.
- **Non ha una banca dati.** Ogni ricerca va in tempo reale al sito web o all'API dell'editore
  stesso, quindi i risultati sono aggiornati quanto la fonte e la qualità della ricerca è quella della
  fonte stessa. Non c'è ricerca semantica su un indice curato.
- **Non impone limiti di utilizzo.** Fontes non ha un tetto mensile di chiamate. Distanzia le
  richieste a ciascun sito, e alcune fonti limitano la velocità o la frequenza con cui possono essere
  interrogate.
- **È open source.** Può leggere ogni adattatore e vedere esattamente da dove proviene ogni testo.
- **Non c'è alcun fornitore dietro.** Nessun contratto, servizio di assistenza o impegno di
  disponibilità (veda "Chi lo mantiene?").

## Con quali app e sistemi funziona?

Con qualsiasi app MCP in grado di eseguire un server locale (stdio), ad esempio Claude Desktop,
Claude Code, Codex, Cursor, VS Code (GitHub Copilot), Gemini CLI, Windsurf, Zed, LM Studio e Cline.
Fontes funziona su macOS, Windows e Linux, ovunque funzioni uv (Python 3.13+). È in arrivo un programma di
installazione con un clic per Mac e Windows. Configura Claude Desktop, Codex, Claude Code, Cursor,
VS Code, Windsurf, Gemini CLI, Zed, LM Studio e Cline in una volta sola. Passaggi per ogni app:
[INSTALL.md](INSTALL.md).

## Posso contribuire con codice?

Per ora no. Issue, segnalazioni sulle fonti e richieste di giurisdizioni sono benvenute. Veda
[CONTRIBUTING.md](../../../CONTRIBUTING.md).

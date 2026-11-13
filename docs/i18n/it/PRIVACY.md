> Questa è una traduzione assistita da macchina. Fa fede la versione inglese.

# Informativa sulla privacy di Fontes

Fontes viene eseguito sul Suo computer. Le Sue ricerche e i documenti che apre restano tra il Suo
computer, le fonti ufficiali in cui cerca e l'app di IA che usa (secondo le condizioni di tale app).
Fontes stesso **per impostazione predefinita non invia nulla** agli sviluppatori di Fontes.

## Che cosa può lasciare il Suo computer, e quando

**1. Controllo degli aggiornamenti (attivo per impostazione predefinita).** Una volta al giorno,
Fontes chiede a PyPI, l'indice pubblico dei pacchetti Python, quale sia la versione più recente. La
richiesta non contiene nulla su di Lei o sul Suo lavoro; PyPI vede il Suo indirizzo IP, come per
qualsiasi download. Per disattivarlo, imposti `FONTES_NO_UPDATE_CHECK=1` (l'avviso nell'app) e
`FONTES_NO_AUTO_UPDATE=1` (gli aggiornamenti automatici del programma di installazione).

**2. Conteggi di utilizzo (disattivati a meno che Lei non li attivi).** Se acconsente (opt-in), una
volta al giorno Fontes invia:

- la versione di Fontes e la famiglia del Suo sistema operativo (macOS, Windows, Linux);
- per giorno, quante volte ciascuno strumento è stato usato per ciascun codice di giurisdizione, ad
  esempio "2026-11-10, nl, search_caselaw, 12".

Questo è il messaggio completo. Non include mai le Sue ricerche, identificativi di documenti o di
pratiche, il testo di documenti, il Suo nome, un account o alcun identificativo Suo o del Suo
computer. I conteggi restano in attesa sul Suo computer (nella cartella della cache di Fontes,
`stats.json`) finché non vengono inviati; se l'invio non riesce, attendono il giorno successivo.

- **Attivarli**: risponda "y" quando il programma di installazione lo chiede, oppure imposti
  `FONTES_STATS=1` per il server Fontes.
- **Disattivarli**: esegua di nuovo il programma di installazione e prema Invio a quella domanda,
  oppure rimuova `FONTES_STATS`. Eliminare `stats.json` scarta tutto ciò che non è ancora stato
  inviato.

**3. Segnalazioni di errore (solo quando ne invia una).** Quando ne richiede una (`fontes report-bug`,
oppure chiedendo alla Sua app di IA di segnalare un errore di Fontes), Fontes Le mostra prima la
segnalazione completa e la invia solo se Lei conferma. Contiene la versione di Fontes, la famiglia
del Suo sistema operativo, il codice di giurisdizione, il nome dello strumento e il messaggio di
errore dell'ultima chiamata non riuscita (con le Sue parole di ricerca e gli identificativi rimossi),
più una nota se ne scrive una. Non inserisca dati dei clienti nella nota. A tale scopo, Fontes
conserva l'ultimo errore sul Suo computer (`last-error.json` nella cartella della cache, sostituito
ogni volta); non viene mai inviato da solo.

## Dove vanno i dati e per quanto tempo sono conservati

I conteggi di utilizzo e le segnalazioni di errore vanno a un piccolo server gestito dallo
sviluppatore di Fontes (`relay.kinetra.fit`). Non memorizza indirizzi IP: sono usati solo in memoria,
brevemente, per limitare gli abusi di richieste, e il server web non conserva alcun registro di
accesso per questo server. I conteggi vengono sommati in totali giornalieri; i singoli invii non
vengono conservati. I totali sono conservati fino a 2 anni e le segnalazioni di errore fino a 1 anno;
poi vengono eliminati. Nulla viene venduto o condiviso.

Se il server non è raggiungibile, non viene inviato nulla: i conteggi restano sul Suo computer e le
segnalazioni di errore rimandano al sistema di tracciamento delle issue (issue tracker).

## Chi ne è responsabile, e su quale base

Il titolare del trattamento dei dati dei conteggi di utilizzo e delle segnalazioni di errore è Yüce
Karapazar, lo sviluppatore di Fontes. Contatto: fontesmcp@proton.me.

La base giuridica è il Suo consenso (articolo 6(1)(a) dello UK GDPR e del GDPR dell'UE). I conteggi
di utilizzo vengono inviati solo se Lei acconsente, e una segnalazione di errore solo dopo che Lei
l'ha confermata. Può revocare il consenso in qualsiasi momento disattivandoli come descritto sopra;
ciò non incide su quanto inviato in precedenza.

## Contatti

Domande o richieste: scriva a fontesmcp@proton.me o apra una issue su
<https://github.com/ykarapazar/fontes/issues>.

> Dies ist eine maschinengestützte Übersetzung. Maßgeblich ist die englische Fassung.

# Datenschutzhinweis zu Fontes

Fontes läuft auf Ihrem Computer. Ihre Suchen und die Dokumente, die Sie öffnen, bleiben zwischen
Ihrem Computer, den Quellen, die Sie durchsuchen (amtliche, dazu CourtListener und Lexifina, wo Sie sie
nutzen, siehe unten), und der KI-App, die Sie verwenden (nach deren eigenen Bedingungen). Fontes selbst sendet den Fontes-Entwicklern **standardmäßig nichts**.

## Was Ihren Computer verlassen kann, und wann

**1. Update-Prüfung (standardmäßig an).** Einmal täglich fragt Fontes bei PyPI, dem öffentlichen
Python-Paketverzeichnis, welche Version die neueste ist. Die Anfrage enthält nichts über Sie oder
Ihre Arbeit; PyPI sieht Ihre IP-Adresse, wie bei jedem Download. Zum Abschalten setzen Sie
`FONTES_NO_UPDATE_CHECK=1` (der Hinweis in der App) und `FONTES_NO_AUTO_UPDATE=1` (die automatischen
Updates des Installationsprogramms).

**2. Nutzungszahlen (aus, außer Sie schalten sie ein).** Wenn Sie einwilligen (Opt-in), sendet Fontes
einmal täglich:

- die Fontes-Version und Ihre Betriebssystemfamilie (macOS, Windows, Linux);
- pro Tag, wie oft jedes Tool für jeden Code einer Rechtsordnung verwendet wurde, zum Beispiel
  „2026-11-10, nl, search_caselaw, 12“.

Das ist die gesamte Nachricht. Sie enthält nie Ihre Suchen, Dokument- oder Aktenkennungen,
Dokumenttext, Ihren Namen, ein Konto oder irgendeine Kennung für Sie oder Ihren Computer. Die Zahlen
warten auf Ihrem Computer (im Cache-Ordner von Fontes, `stats.json`), bis sie gesendet werden; wenn
das Senden fehlschlägt, warten sie bis zum nächsten Tag.

- **Opt-in**: Antworten Sie mit „j“, wenn das Installationsprogramm fragt, oder setzen Sie
  `FONTES_STATS=1` für den Fontes-Server.
- **Opt-out**: Führen Sie das Installationsprogramm erneut aus und drücken Sie bei dieser Frage
  Enter, oder entfernen Sie `FONTES_STATS`. Das Löschen von `stats.json` verwirft alles noch nicht
  Gesendete.

**3. Fehlerberichte (nur wenn Sie einen senden).** Wenn Sie einen anfordern (`fontes report-bug`,
oder Sie bitten Ihre KI-App, einen Fontes-Fehler zu melden), zeigt Fontes Ihnen zuerst den
vollständigen Bericht und sendet ihn nur, wenn Sie bestätigen. Er enthält die Fontes-Version, Ihre
Betriebssystemfamilie, den Code der Rechtsordnung, den Tool-Namen und die Fehlermeldung des letzten
fehlgeschlagenen Tool-Aufrufs (wobei Ihre Suchbegriffe und Kennungen entfernt werden) sowie eine
Notiz, wenn Sie eine schreiben. Schreiben Sie keine Mandantendaten in die Notiz. Dafür speichert
Fontes den letzten Fehler auf Ihrem Computer (`last-error.json` in seinem Cache-Ordner, jedes Mal
ersetzt); er wird nie für sich allein gesendet.

**4. Lexifina (standardmäßig an).** `get_law_on_date`, `get_law_history` die 91 Länder und Indiens Gesetze werden über
Lexifinas Rechtsbestand gelesen; sie gehen daher an Lexifina, je nach Fall zusätzlich zur amtlichen Website oder statt ihr. Ihre Suchbegriffe, Zitate
und Daten gehen an den kostenlosen Server von Lexifina, `global-law.lexifina.com`, der von Lexifina
betrieben wird, nicht von den Fontes-Entwicklern. Lexifina dokumentiert, dass sein Server protokolliert,
welches Tool aufgerufen wurde und wie lange es dauerte, aber nie, was gefragt wurde; Fontes kann das
nicht prüfen, und es gelten Lexifinas eigene Bedingungen. Lexifina sieht Ihre IP-Adresse, wie jeder
Webserver. Um Lexifina vollständig abzuschalten, setzen Sie `WLM_LEXIFINA=0`; diese beiden Tools und
Länder funktionieren dann nicht mehr, und dorthin wird nichts gesendet.

## Wohin die Daten gehen und wie lange sie aufbewahrt werden

Nutzungszahlen und Fehlerberichte gehen an einen kleinen Server, den der Fontes-Entwickler betreibt
(`relay.kinetra.fit`). Er speichert keine IP-Adressen: Sie werden nur kurz im Arbeitsspeicher
verwendet, um Überflutungen abzuwehren, und der Webserver führt dafür kein Zugriffsprotokoll. Die
Zahlen werden zu Tagessummen addiert; einzelne Übermittlungen werden nicht aufbewahrt. Summen werden
bis zu 2 Jahre, Fehlerberichte bis zu 1 Jahr aufbewahrt und dann gelöscht. Nichts wird verkauft oder
weitergegeben.

Wenn dieser Server nicht erreichbar ist, wird nichts gesendet: Die Zahlen bleiben auf Ihrem Computer,
und Fehlerberichte verweisen Sie stattdessen auf den Issue-Tracker.

## Wer verantwortlich ist und auf welcher Grundlage

Verantwortlicher für Nutzungszahlen und Fehlerberichte ist Yüce Karapazar, der Entwickler von Fontes.
Kontakt: fontesmcp@proton.me.

Rechtsgrundlage ist Ihre Einwilligung (Artikel 6 Absatz 1 Buchstabe a der UK GDPR und der EU-DSGVO).
Nutzungszahlen werden nur gesendet, wenn Sie einwilligen (Opt-in), und ein Fehlerbericht nur, nachdem
Sie ihn bestätigt haben. Sie können Ihre Einwilligung jederzeit widerrufen, indem Sie wie oben
beschrieben das Opt-out wählen; das berührt nicht, was zuvor gesendet wurde.

## Kontakt

Fragen oder Anliegen: Schreiben Sie an fontesmcp@proton.me, oder eröffnen Sie ein Issue unter
<https://github.com/ykarapazar/fontes/issues>.

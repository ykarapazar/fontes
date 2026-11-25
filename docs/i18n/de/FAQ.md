> Dies ist eine maschinengestützte Übersetzung. Maßgeblich ist die englische Fassung.

# Fontes: Fragen und Antworten

## Was ist Fontes?

Ein kostenloser Open-Source-MCP-Server (Apache 2.0). Mit ihm kann jede App, die das Model Context
Protocol spricht (Claude, Codex, Cursor, VS Code, Gemini CLI und andere), Gerichtsentscheidungen und
Rechtsvorschriften live auf Websites von Gerichten und Behörden durchsuchen, in über 120
Rechtsordnungen und internationalen Gerichten (124 Adapter). Jedes Ergebnis nennt seine Quelle und
verlinkt auf das Original.

## Sind die Texte amtlich?

Meistens, aber nicht immer.

- Die meisten Quellen werden von einem Gericht, einem Ministerium oder einem Amtsblatt betrieben.
- Manche konsolidierten Texte werden von einer Regierung veröffentlicht, sind aber ausdrücklich
  nichtamtlich: Nur das Amtsblatt ist authentisch.
- Einige wenige Quellen sind überhaupt keine staatlichen Websites (zum Beispiel LexiVox, LawPhil,
  Maqam, Wikisource).

Fontes versieht jede Antwort, die aus einer dieser Quellen stammt, mit dem Hinweis „Nichtamtliche
Quelle“. Prüfen Sie die amtliche Veröffentlichung, bevor Sie etwas zitieren. Die Abdeckungstabelle in
der [README](README.md#abdeckung) und `list_jurisdictions` nennen die Quelle für jede Rechtsordnung.

## Welche Rechtsordnungen deckt es ab, und wie gut?

124 Adapter: 108 UN-Mitgliedstaaten, Hongkong, Kosovo, Palästina, Taiwan, die DIFC Courts und
11 internationale Gerichte und Gremien (etwa der Europäische Gerichtshof für Menschenrechte, die EU,
der IGH und die WTO).

Die Abdeckung unterscheidet sich stark. Nach einer strengen Regel (die Präjudizien des obersten
ordentlichen Gerichts oder die Verfassung und die Parlamentsgesetze, jeweils vollständig erreicht)
gelten 72 der 124 als abgedeckt. [COVERAGE.md](COVERAGE.md) gibt für jede Rechtsordnung an, was Fontes
erreicht, was nicht, und warum.

## Brauche ich einen API-Schlüssel?

Für fast jede Rechtsordnung nicht. Einige Quellen benötigen einen kostenlosen Schlüssel: siehe
[KEYS.md](KEYS.md).

- **Frankreich:** ja. Frankreich ist aus, bis Sie `WLM_FR_PISTE_CLIENT_ID` und
  `WLM_FR_PISTE_CLIENT_SECRET` setzen. Diese erhalten Sie über ein kostenloses PISTE-Konto
  (piste.gouv.fr) mit einer Anwendung, die Judilibre und Légifrance abonniert hat.
- **Vereinigte Staaten:** optional. Die Suche in der Rechtsprechung funktioniert ohne Schlüssel, aber
  der gemeinsame Demo-Schlüssel erlaubt nur etwa 10 Suchen pro Tag und IP-Adresse. Ein kostenloser
  api.data.gov-Schlüssel in `WLM_US_GOVINFO_KEY` erhöht diese Grenze.

Setzen Sie diese als Umgebungsvariablen für den Fontes-Server in den MCP-Einstellungen Ihrer App.
Die Installationsprogramme fragen nach der Installation danach, und ihr Starter
**Add or change keys** ändert sie später.

Unabhängig davon sagen einige Quellen in ihren Nutzungsbedingungen, dass der automatisierte Zugriff
die Erlaubnis des Herausgebers erfordert. Sie sind mit OFF markiert und bleiben aus. Ein Schlüssel
ändert daran nichts; nur die Erlaubnis des Herausgebers tut das (setzen Sie dann
`WLM_PERMITTED=<codes>`).

## Was verlässt meinen Computer?

Ihre Suchen gehen nur an die durchsuchte Quelle. Fontes führt keine Datenbank und braucht kein Konto.

Neben den Quellen fragt Fontes einmal täglich bei PyPI, ob es eine neuere Version gibt (abschaltbar
mit `FONTES_NO_UPDATE_CHECK=1`). Nutzungszahlen sind aus, außer Sie schalten sie ein, und ein
Fehlerbericht wird erst gesendet, nachdem Sie ihn gesehen und bestätigt haben. Ihre KI-App sieht Ihr
Gespräch nach ihren eigenen Bedingungen.

Alle Einzelheiten: [PRIVACY.md](PRIVACY.md).

## Ist das Rechtsberatung?

Nein. Fontes ist ein Recherchewerkzeug. Es findet Texte; es sagt Ihnen nicht, was sie für Ihren Fall
bedeuten, und seine Nutzung begründet mit niemandem ein Mandatsverhältnis. Die KI-App kann einen Text
falsch lesen; lesen Sie daher die vollständige Entscheidung oder Vorschrift, bevor Sie sich darauf
verlassen. Für eine Beratung wenden Sie sich an eine Rechtsanwältin oder einen Rechtsanwalt, die oder
der dort zugelassen ist, wo sich Ihre Frage stellt.

## Wer pflegt es? Wird es weiter funktionieren?

Eine Person: Yüce Karapazar. Hinter Fontes steht kein Unternehmen, es gibt keinen Supportvertrag und
keine Zusage zur Dienstgüte. Es werden keine Rechtsdienstleistungen angeboten.

Die Quellen werden einmal täglich geprüft, und die Ergebnisse werden auf der
[Statusseite](https://ykarapazar.github.io/fontes/status/?lang=de) veröffentlicht. Websites von
Gerichten und Behörden ändern sich ohne Vorankündigung, daher kann eine Quelle jederzeit ausfallen.
Es gibt keine Garantie, dass irgendeine Quelle oder Fontes selbst weiter funktioniert. Fontes wird
„wie besehen“ bereitgestellt, ohne Gewährleistung (Abschnitte 7 und 8 der [LICENSE](../../../LICENSE)).

## Ein Text ist falsch oder veraltet, oder eine Quelle funktioniert nicht. Wie melde ich das?

- Eröffnen Sie ein Issue mit dem Formular „Broken or wrong source“:
  <https://github.com/ykarapazar/fontes/issues/new/choose>. Geben Sie an, welche Rechtsordnung, was
  Sie gefragt haben, was Sie erhalten haben und die amtliche Seite, die den richtigen Text zeigt.
- Oder bitten Sie Ihre KI-App, „einen Fontes-Fehler zu melden“ (oder führen Sie `fontes report-bug`
  aus). Sie sehen den Bericht, bevor etwas gesendet wird.
- Oder schreiben Sie an fontesmcp@proton.me.

Nehmen Sie keine Mandantendaten oder vertraulichen Tatsachen in einen Bericht auf.

**Wenn Sie eine der Quellen betreiben** und etwas nicht stimmt (Ihre Nutzungsbedingungen, Ihre
robots.txt, Ihre Ratenbegrenzungen), schreiben Sie an fontesmcp@proton.me. Die Quelle wird korrigiert
oder abgeschaltet.

## Worin unterscheidet sich Fontes von gehosteten Werkzeugen für die juristische Recherche?

- **Es läuft auf Ihrem Computer.** Es gibt keinen Fontes-Server und kein Konto. Das bedeutet auch,
  dass es nur in Apps funktioniert, die einen lokalen MCP-Server starten können (Claude Desktop,
  Codex, Cursor, VS Code und ähnliche), nicht in reinen Web-Apps, die nur gehostete Connectoren
  akzeptieren.
- **Es hat keine Datenbank.** Jede Suche geht live an die eigene Website oder API des Herausgebers,
  daher sind die Ergebnisse so aktuell wie die Quelle, und die Suchqualität ist die der Quelle selbst.
  Es gibt keine semantische Suche über einen kuratierten Index.
- **Es setzt keine Nutzungsgrenze.** Fontes hat keine monatliche Obergrenze für Aufrufe. Es verteilt
  seine Anfragen an jede Website zeitlich, und manche Quellen begrenzen, wie schnell oder wie oft sie
  abgefragt werden können.
- **Es ist Open Source.** Sie können jeden Adapter lesen und genau sehen, woher jeder Text stammt.
- **Es steht kein Anbieter dahinter.** Kein Vertrag, kein Support, keine Verfügbarkeitszusage (siehe
  „Wer pflegt es?“).

## Mit welchen Apps und Systemen funktioniert es?

Mit jeder MCP-App, die einen lokalen (stdio-)Server ausführen kann, zum Beispiel Claude Desktop,
Claude Code, Codex, Cursor, VS Code (GitHub Copilot), Gemini CLI, Windsurf, Zed, LM Studio und Cline.
Fontes läuft unter macOS, Windows und Linux, überall dort, wo uv läuft (Python 3.13+). Auf einem Mac oder
Windows-PC richtet ein Ein-Klick-Installationsprogramm Claude Desktop, Codex, Claude Code, Cursor, VS Code,
Windsurf, Gemini CLI, Zed, LM Studio und Cline in einem Durchgang ein. Schritte für jede App: [INSTALL.md](INSTALL.md).

## Kann ich Code beitragen?

Derzeit nicht. Issues, Meldungen zu Quellen und Wünsche nach Rechtsordnungen sind willkommen. Siehe
[CONTRIBUTING.md](../../../CONTRIBUTING.md).

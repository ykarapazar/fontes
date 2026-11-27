> Detta är en maskinstödd översättning. Den engelska versionen gäller.

# Fontes: frågor och svar

## Vad är Fontes?

En kostnadsfri MCP-server med öppen källkod (Apache 2.0). Den låter alla appar som talar Model Context
Protocol (Claude, Codex, Cursor, VS Code, Gemini CLI med flera) söka i domstolsavgöranden och
lagstiftning direkt på domstolars och myndigheters webbplatser i fler än 120 jurisdiktioner och internationella
domstolar (125 adaptrar). Varje resultat anger sin källa och länkar till originalet.

## Är texterna officiella?

För det mesta, men inte alltid.

- De flesta källor drivs av en domstol, ett ministerium eller en officiell kungörelsetidning.
- Vissa konsoliderade texter publiceras av en myndighet men är uttryckligen inofficiella: endast
  den officiella kungörelsetidningen är autentisk.
- Några få källor är inte myndigheters webbplatser alls (till exempel LexiVox, LawPhil, Maqam,
  Wikisource).

Fontes lägger till ett meddelande om ”inofficiell källa” i varje svar som kommer från en av dessa. Innan
du citerar något, kontrollera den officiella publiceringen. Täckningstabellen i
[README](README.md#täckning) och `list_jurisdictions` anger källan för varje jurisdiktion.

## Vilka jurisdiktioner täcker det, och hur väl?

125 adaptrar: 108 FN-medlemsstater, Hongkong, Kosovo, Palestina, Taiwan, DIFC Courts, de amerikanska delstatsdomstolarna och 11 internationella domstolar och organ (som Europeiska domstolen för de mänskliga rättigheterna, EU,
ICJ och WTO).

Täckningen skiljer sig mycket. Enligt en strikt regel (den högsta allmänna domstolens prejudikat, eller
grundlagen och de primära lagarna, nådda fullständigt) räknas 72 av de 125 som täckta.
[COVERAGE.md](../../COVERAGE.md) anger för varje jurisdiktion vad Fontes når, vad det inte når
och varför.

## Behöver jag en API-nyckel?

För nästan alla jurisdiktioner, nej. Vissa källor kräver en kostnadsfri nyckel: se [KEYS.md](KEYS.md).

- **Frankrike:** ja. Frankrike är avstängt tills du anger `WLM_FR_PISTE_CLIENT_ID` och
  `WLM_FR_PISTE_CLIENT_SECRET`. Dessa får du från ett kostnadsfritt PISTE-konto (piste.gouv.fr) med en
  app som abonnerar på Judilibre och Légifrance.
- **USA:** valfritt. Sökning i rättspraxis fungerar utan nyckel, men den delade demonyckeln
  tillåter bara omkring 10 sökningar om dagen per IP-adress. En kostnadsfri api.data.gov-nyckel i
  `WLM_US_GOVINFO_KEY` höjer gränsen.
- **USA:s delstatsdomstolar:** ja. Delstaternas rättspraxis (`us-states`) är avstängd tills du anger din egen kostnadsfria CourtListener-API-token i `WLM_US_COURTLISTENER_KEY`. CourtListener drivs av den ideella organisationen Free Law Project; det är ingen officiell källa, och varje svar anger detta.

Ange dessa som miljövariabler för Fontes-servern i appens MCP-inställningar. Installationsprogrammen
frågar efter dem efter installationen, och deras startfil **Add or change keys** ändrar dem
senare.

Därutöver anger några få källor i sina villkor att automatiserad åtkomst kräver utgivarens
tillstånd. De är markerade OFF och förblir avstängda. En nyckel ändrar inte det; endast
utgivarens tillstånd gör det (ange då `WLM_PERMITTED=<codes>`).

## Vad lämnar min dator?

Dina sökningar går endast till den källa som genomsöks. Fontes för ingen databas och kräver inget
konto.

Utöver källorna frågar Fontes PyPI en gång om dagen om det finns en nyare version (stängs av
med `FONTES_NO_UPDATE_CHECK=1`). Användningssiffror är avstängda om du inte slår på dem, och en felrapport
skickas endast efter att du har sett den och bekräftat. Din AI-app ser din konversation enligt sina
egna villkor.

Alla detaljer: [PRIVACY.md](PRIVACY.md).

## Är detta juridisk rådgivning?

Nej. Fontes är ett researchverktyg. Det hittar texter; det säger inte vad de betyder för ditt
ärende, och att använda det skapar inte något klientförhållande med en advokat för någon. AI-appen kan
läsa fel i en text, så läs hela avgörandet eller hela bestämmelsen innan du förlitar dig på det. För rådgivning, fråga
en advokat som är behörig där din fråga uppstår.

## Vem underhåller det? Kommer det att fortsätta fungera?

En person: Yüce Karapazar. Det finns inget företag bakom Fontes, inget supportavtal och inget
löfte om servicenivå. Inga juridiska tjänster erbjuds.

Källorna kontrolleras en gång om dagen och resultaten publiceras på
[statussidan](https://ykarapazar.github.io/fontes/status/?lang=sv). Domstolars och myndigheters webbplatser
ändras utan förvarning, så en källa kan sluta fungera när som helst. Det finns ingen garanti för att någon källa,
eller Fontes självt, fortsätter att fungera. Fontes tillhandahålls ”i befintligt skick”, utan garanti (avsnitt 7
och 8 i [LICENSE](../../../LICENSE)).

## En text är fel eller inaktuell, eller en källa fungerar inte. Hur rapporterar jag det?

- Öppna ett ärende (issue) med formuläret ”Broken or wrong source”:
  <https://github.com/ykarapazar/fontes/issues/new/choose>. Ange vilken jurisdiktion, vad du
  frågade, vad du fick och den officiella sida som visar rätt text.
- Eller be din AI-app att ”rapportera ett fel i Fontes” (eller kör `fontes report-bug`). Du ser rapporten innan
  något skickas.
- Eller mejla fontesmcp@proton.me.

Ta inte med klientuppgifter eller konfidentiella fakta i en rapport.

**Om du driver en av källorna** och något är fel (dina villkor, din robots.txt, dina
anropsgränser), mejla fontesmcp@proton.me. Källan rättas eller stängs av.

## Hur skiljer sig Fontes från webbaserade verktyg för juridisk research?

- **Det körs på din dator.** Det finns ingen Fontes-server och inget konto. Det betyder också att det
  bara fungerar i appar som kan starta en lokal MCP-server (Claude Desktop, Codex, Cursor, VS Code
  och liknande), inte i rena webbappar som bara tar emot värdbaserade anslutningar (hosted connectors).
- **Det har ingen databas.** Varje sökning går direkt till utgivarens egen webbplats eller API, så
  resultaten är lika aktuella som källan, och sökkvaliteten är källans egen. Det finns ingen
  semantisk sökning i ett kurerat index.
- **Det sätter ingen användningsgräns.** Fontes har inget månatligt tak för anrop. Det glesar ut sina förfrågningar till varje
  webbplats, och vissa källor begränsar hur snabbt eller hur ofta de kan frågas.
- **Det har öppen källkod.** Du kan läsa varje adapter och se exakt varifrån varje text kommer.
- **Det finns ingen leverantör bakom det.** Inget avtal, ingen supportfunktion och inget löfte om drifttid (se ”Vem
  underhåller det?”).

## Vilka appar och system fungerar det med?

Alla MCP-appar som kan köra en lokal server (stdio), till exempel Claude Desktop, Claude Code,
Codex, Cursor, VS Code (GitHub Copilot), Gemini CLI, Windsurf, Zed, LM Studio och Cline. Fontes
körs på macOS, Windows och Linux, överallt där uv körs (Python 3.13+). På en Mac eller Windows-dator konfigurerar ett installationsprogram med ett klick
Claude Desktop, Codex, Claude Code, Cursor, VS Code, Windsurf, Gemini CLI, Zed, LM Studio och
Cline på en gång. Steg för varje app: [INSTALL.md](INSTALL.md).

## Kan jag bidra med kod?

Inte för närvarande. Ärenden, rapporter om källor och önskemål om jurisdiktioner är välkomna. Se
[CONTRIBUTING.md](../../../CONTRIBUTING.md).

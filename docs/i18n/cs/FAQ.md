> Toto je strojově asistovaný překlad. Závazná je anglická verze.

# Fontes: otázky a odpovědi

## Co je Fontes?

Bezplatný server MCP s otevřeným zdrojovým kódem (Apache 2.0). Umožňuje každé aplikaci, která
používá Model Context Protocol (Claude, Codex, Cursor, VS Code, Gemini CLI a další), živě
vyhledávat soudní rozhodnutí a právní předpisy na webech soudů a státních orgánů ve více než
120 jurisdikcích a u mezinárodních soudů (124 adaptérů). Každý výsledek uvádí svůj zdroj a
odkazuje na originál.

## Jsou texty oficiální?

Většinou ano, ale ne vždy.

- Většinu zdrojů provozuje soud, ministerstvo nebo úřední věstník.
- Některá úplná znění zveřejňuje stát, ale jsou výslovně neoficiální: autentický je pouze
  úřední věstník.
- Několik zdrojů vůbec nejsou weby státních orgánů (například LexiVox, LawPhil, Maqam,
  Wikisource).

Fontes ke každé odpovědi, která pochází z jednoho z těchto zdrojů, přidá upozornění
„Unofficial source“. Než cokoli citujete, ověřte si oficiální publikaci. Tabulka pokrytí v
[README](README.md#pokrytí) a `list_jurisdictions` uvádějí zdroj pro každou jurisdikci.

## Které jurisdikce pokrývá a jak dobře?

124 adaptérů: 108 členských států OSN, Hongkong, Kosovo, Palestina, Tchaj-wan, soudy DIFC a 11
mezinárodních soudů a orgánů (například Evropský soud pro lidská práva, EU, Mezinárodní soudní
dvůr a WTO).

Pokrytí se velmi liší. Podle přísného pravidla (precedenty nejvyššího obecného soudu nebo
ústava a základní zákony, dostupné v úplnosti) se 72 ze 124 počítá jako pokryté.
[COVERAGE.md](COVERAGE.md) pro každou jurisdikci uvádí, co Fontes zpřístupní, co ne a proč.

## Potřebuji klíč API?

U téměř každé jurisdikce ne. Některé zdroje vyžadují bezplatný klíč: viz [KEYS.md](KEYS.md).

- **Francie:** ano. Francie je vypnutá, dokud nenastavíte `WLM_FR_PISTE_CLIENT_ID` a
  `WLM_FR_PISTE_CLIENT_SECRET`. Získáte je z bezplatného účtu PISTE (piste.gouv.fr) s
  aplikací přihlášenou k odběru Judilibre a Légifrance.
- **Spojené státy:** volitelné. Vyhledávání judikatury funguje bez klíče, ale sdílený demo klíč
  povoluje jen přibližně 10 hledání denně na IP adresu. Bezplatný klíč api.data.gov v
  `WLM_US_GOVINFO_KEY` tento limit zvýší.

Nastavte je jako proměnné prostředí pro server Fontes v nastavení MCP své aplikace. Až bude
instalátor vydán, po instalaci se na ně zeptá a jeho spouštěč **Add or change keys** je později
změní.

Nezávisle na tom několik zdrojů ve svých podmínkách uvádí, že automatizovaný přístup vyžaduje
povolení vydavatele. Jsou označeny OFF a zůstávají vypnuté. Klíč na tom nic nemění; změní to
jen povolení vydavatele (pak nastavte `WLM_PERMITTED=<codes>`).

## Co opouští můj počítač?

Vaše vyhledávání jdou pouze ke zdroji, který prohledáváte. Fontes nevede žádnou databázi a
nevyžaduje účet.

Kromě zdrojů se Fontes jednou denně zeptá PyPI, zda existuje novější verze (vypnete to pomocí
`FONTES_NO_UPDATE_CHECK=1`). Počty použití jsou vypnuté, pokud je nezapnete, a hlášení chyby se
odešle teprve poté, co ho uvidíte a potvrdíte. Vaše aplikace s AI vidí váš rozhovor podle
vlastních podmínek.

Všechny podrobnosti: [PRIVACY.md](PRIVACY.md).

## Je to právní poradenství?

Ne. Fontes je nástroj pro rešerše. Vyhledává texty; neříká vám, co znamenají pro váš případ, a
jeho používáním nevzniká s nikým vztah advokáta a klienta. Aplikace s AI může text špatně
vyložit, proto si celé rozhodnutí nebo ustanovení přečtěte dříve, než se na ně spolehnete.
S žádostí o radu se obraťte na advokáta s kvalifikací v místě, kde vaše otázka vzniká.

## Kdo ho udržuje? Bude dál fungovat?

Jedna osoba: Yüce Karapazar. Za Fontes nestojí žádná společnost, neexistuje smlouva o podpoře
ani příslib úrovně služeb. Neposkytují se žádné právní služby.

Zdroje se kontrolují jednou denně a výsledky se zveřejňují na
[stránce stavu](https://ykarapazar.github.io/fontes/status/?lang=cs). Weby soudů a státních
orgánů se mění bez upozornění, takže zdroj může kdykoli přestat fungovat. Neexistuje záruka,
že jakýkoli zdroj nebo samotný Fontes bude dál fungovat. Fontes se poskytuje „tak, jak je“, bez
záruky (oddíly 7 a 8 [LICENSE](../../../LICENSE)).

## Text je chybný nebo zastaralý, nebo zdroj nefunguje. Jak to nahlásím?

- Založte issue pomocí formuláře "Broken or wrong source":
  <https://github.com/ykarapazar/fontes/issues/new/choose>. Uveďte jurisdikci, na co jste se
  ptali, co jste dostali, a oficiální stránku, která ukazuje správný text.
- Nebo požádejte svou aplikaci s AI, aby „nahlásila chybu Fontes“ (nebo spusťte
  `fontes report-bug`). Hlášení uvidíte dříve, než se cokoli odešle.
- Nebo napište na fontesmcp@proton.me.

Do hlášení neuvádějte údaje o klientech ani důvěrné skutečnosti.

**Pokud provozujete některý ze zdrojů** a něco není v pořádku (vaše podmínky, váš robots.txt,
vaše limity počtu požadavků), napište na fontesmcp@proton.me. Zdroj bude opraven nebo vypnut.

## Čím se Fontes liší od hostovaných nástrojů pro právní rešerše?

- **Běží ve vašem počítači.** Neexistuje žádný server Fontes ani účet. To také znamená, že
  funguje jen v aplikacích, které dokážou spustit lokální server MCP (Claude Desktop, Codex,
  Cursor, VS Code a podobné), ne v čistě webových aplikacích, které přijímají jen hostované
  konektory.
- **Nemá databázi.** Každé vyhledávání jde živě na web nebo API vydavatele, takže výsledky jsou
  tak aktuální jako zdroj a kvalita vyhledávání je kvalitou samotného zdroje. Neexistuje
  sémantické vyhledávání v kurátorovaném indexu.
- **Nestanoví limit použití.** Fontes nemá měsíční limit volání. Své požadavky na každý web
  rozkládá v čase a některé zdroje omezují, jak rychle nebo jak často se na ně lze dotazovat.
- **Má otevřený zdrojový kód.** Můžete si přečíst každý adaptér a přesně vidět, odkud každý text
  pochází.
- **Nestojí za ním žádný dodavatel.** Žádná smlouva, podpora ani příslib dostupnosti (viz „Kdo
  ho udržuje?“).

## S jakými aplikacemi a systémy funguje?

S každou aplikací MCP, která dokáže spustit lokální (stdio) server, například Claude Desktop,
Claude Code, Codex, Cursor, VS Code (GitHub Copilot), Gemini CLI, Windsurf, Zed, LM Studio a
Cline. Fontes běží na macOS, Windows a Linuxu, všude, kde běží uv (Python 3.13+). Zatím není na
PyPI; až bude, většině aplikací postačí jeden příkaz nebo jedna položka v konfiguraci a Claude
Desktop přijme soubor `.mcpb`, na který dvakrát kliknete. Instalátor na jedno kliknutí pro Mac a
Windows připravujeme. Najednou nastaví Claude Desktop, Codex, Claude Code, Cursor, VS Code,
Windsurf, Gemini CLI, Zed, LM Studio a Cline. Postup pro každou aplikaci:
[INSTALL.md](INSTALL.md).

## Mohu přispět kódem?

V tuto chvíli ne. Hlášení problémů, hlášení zdrojů a žádosti o jurisdikce jsou vítány. Viz
[CONTRIBUTING.md](../../../CONTRIBUTING.md).

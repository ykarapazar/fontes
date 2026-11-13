> Toto je strojově asistovaný překlad. Závazná je anglická verze.

# Informace o ochraně soukromí ve Fontes

Fontes běží ve vašem počítači. Vaše vyhledávání a dokumenty, které otevřete, zůstávají mezi vaším
počítačem, oficiálními zdroji, které prohledáváte, a aplikací s AI, kterou používáte (podle
vlastních podmínek této aplikace). Samotný Fontes vývojářům Fontes **ve výchozím stavu neposílá
nic**.

## Co může opustit váš počítač a kdy

**1. Kontrola aktualizací (ve výchozím stavu zapnutá).** Jednou denně se Fontes zeptá PyPI,
veřejného rejstříku balíčků Pythonu, která verze je nejnovější. Požadavek neobsahuje nic o vás
ani o vaší práci; PyPI vidí vaši IP adresu, jako při každém stahování. Chcete-li ji vypnout,
nastavte `FONTES_NO_UPDATE_CHECK=1` (upozornění v aplikaci) a `FONTES_NO_AUTO_UPDATE=1`
(automatické aktualizace instalátoru).

**2. Počty použití (vypnuté, pokud je nezapnete).** Pokud udělíte souhlas (opt-in), Fontes
jednou denně odešle:

- verzi Fontes a rodinu vašeho operačního systému (macOS, Windows, Linux);
- za každý den, kolikrát byl každý nástroj použit pro každý kód jurisdikce, například
  „2026-11-10, nl, search_caselaw, 12“.

To je celá zpráva. Nikdy neobsahuje vaše vyhledávání, identifikátory dokumentů ani věcí, text
dokumentů, vaše jméno, účet ani žádný identifikátor vás nebo vašeho počítače. Počty čekají ve
vašem počítači (ve složce mezipaměti Fontes, `stats.json`), dokud nejsou odeslány; pokud
odeslání selže, počkají na další den.

- **Souhlas (opt-in)**: odpovězte „y“, když se instalátor zeptá, nebo nastavte `FONTES_STATS=1`
  pro server Fontes.
- **Odvolání (opt-out)**: spusťte instalátor znovu a u této otázky stiskněte Enter, nebo
  odeberte `FONTES_STATS`. Smazáním `stats.json` zahodíte vše, co ještě nebylo odesláno.

**3. Hlášení chyb (pouze když nějaké odešlete).** Když o něj požádáte (`fontes report-bug` nebo
požádáte svou aplikaci s AI, aby nahlásila chybu Fontes), Fontes vám nejprve ukáže celé hlášení
a odešle ho pouze, pokud potvrdíte. Obsahuje verzi Fontes, rodinu vašeho operačního systému a u
posledního neúspěšného volání nástroje kód jurisdikce, název nástroje a chybovou zprávu (s
vystřiženými hledanými slovy a identifikátory) a poznámku, pokud ji napíšete. Do poznámky
neuvádějte údaje o klientech. Kvůli tomu Fontes uchovává poslední chybu ve vašem počítači
(`last-error.json` ve své složce mezipaměti, pokaždé nahrazen); nikdy se neodesílá sám od sebe.

## Kam data putují a jak dlouho se uchovávají

Počty použití a hlášení chyb putují na malý server provozovaný vývojářem Fontes
(`relay.kinetra.fit`). Ten neukládá IP adresy: používají se pouze v paměti, krátce, k zastavení
zahlcení, a webový server pro něj nevede žádný přístupový log. Počty se sčítají do denních
souhrnů; jednotlivá odeslání se neuchovávají. Souhrny se uchovávají až 2 roky, hlášení chyb až
1 rok, poté se smažou. Nic se neprodává ani nesdílí.

Pokud tento server není dostupný, nic se neodešle: počty zůstanou ve vašem počítači a hlášení
chyb vás místo toho odkáže na systém pro sledování problémů (issue tracker).

## Kdo odpovídá a na jakém základě

Správcem údajů pro počty použití a hlášení chyb je Yüce Karapazar, vývojář Fontes. Kontakt:
fontesmcp@proton.me.

Právním základem je váš souhlas (čl. 6 odst. 1 písm. a) UK GDPR a GDPR EU). Počty použití se
posílají pouze, pokud udělíte souhlas (opt-in), a hlášení chyby teprve poté, co ho potvrdíte.
Souhlas můžete kdykoli odvolat výše popsaným způsobem; to nemá vliv na to, co bylo odesláno
dříve.

## Kontakt

Dotazy nebo žádosti: napište na fontesmcp@proton.me nebo založte issue na
<https://github.com/ykarapazar/fontes/issues>.

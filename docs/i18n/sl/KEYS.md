> To je strojno podprt prevod. Merodajna je angleška različica.

# Ključi API

Skoraj vsak vir v orodju Fontes deluje brez ključa. Dva vira potrebujeta brezplačen ključ:

| Ključ | Odklene | Brez njega |
|---|---|---|
| `WLM_FR_PISTE_CLIENT_ID` + `WLM_FR_PISTE_CLIENT_SECRET` | Francija: Judilibre (sodne odločbe) in Légifrance (predpisi) | Francija je izklopljena. `list_jurisdictions` jo prikaže kot neaktivno. |
| `WLM_US_GOVINFO_KEY` | Združene države Amerike: iskanje govinfo (mnenja zveznih sodišč, Statutes at Large, public laws) | Fontes uporablja skupni `DEMO_KEY`: približno 10 iskanj na dan na naslov IP. Za odpiranje znane odločbe in za US Code ključ ni potreben. |

Ključi niso obvezni. Dodate jih lahko tudi pozneje.

## Dodajanje ključa

**Z namestitvenim programom.** Med namestitvijo vas namestitveni program vpraša, ali želite
dodati ključe. Izberite **Ne zdaj** (ali pritisnite Enter), da to preskočite. Če želite ključe
dodati ali spremeniti pozneje, zaženite **Add or change keys**:

- Mac: znova odprite aplikacijo Fontes Installer in izberite **Dodaj ali spremeni ključe**
  ali dvakrat kliknite `Add or change keys.command` v mapi namestitvenega programa.
- Windows: dvakrat kliknite `Add or change keys.cmd` v mapi namestitvenega programa.
  Namestitveni program za Windows ga bo, ko bo na voljo, dodal tudi v Start menu > Fontes.

Vnos se ne prikazuje. Za vsak ključ: prilepite ga, pritisnite Enter, da obdržite obstoječega,
ali vpišite `-`, da ga odstranite. Ključi se zapišejo v vsako aplikacijo, ki že ima Fontes.

**Z razširitvijo za Claude Desktop (.mcpb).** Odprite Claude > Settings > Extensions > Fontes
in izpolnite polja. Nobeno ni obvezno.

**Ročno.** Dodajte spremenljivke v blok `env` vnosa `fontes` v konfiguraciji MCP svoje aplikacije:

```json
"fontes": {
  "command": "...",
  "args": ["..."],
  "env": { "WLM_US_GOVINFO_KEY": "your-key" }
}
```

Po vsaki spremembi znova zaženite aplikacijo.

## Francija: PISTE (brezplačno)

1. Odprite račun na [piste.gouv.fr](https://piste.gouv.fr). To pomeni, da sprejmete pogoje PISTE (CGU).
2. Pojdite na API > **Consentement CGU API**. Sprejmite pogoje za **JUDILIBRE** in **Légifrance** (production).
3. Ustvarite **production application**. `APP_SANDBOX`, ki je bil ustvarjen za vas, ne more dostopati do produkcije.
   Pod "Modifier l'application" označite **JUDILIBRE (production)** in **Légifrance (production)**, nato uveljavite spremembe.
4. Odprite zavihek **Authentification** aplikacije. Kopirajte `client_id` in `client_secret`.
5. Zaženite **Add or change keys** in ju prilepite.

Pogoji na kratko:

- Podatki: Licence Ouverte / Etalab 2.0. Ponovna uporaba, tudi komercialna, je dovoljena z navedbo vira.
- Svojih poverilnic ne objavljajte in ne delite. Če uidejo v javnost, obvestite PISTE.
- API Légifrance je storitev beta. Lahko je prekinjena in ima kvote (na sekundo, minuto in dan).
- Besedila na Légifrance niso verodostojna različica. Verodostojen je le podpisani PDF Journal officiel.
- Judilibre: imen sodnikov ali sodnega osebja ne uporabljajte za ocenjevanje, primerjanje ali
  napovedovanje njihovega dela (Code de l'organisation judiciaire, člen L111-13; kaznivo dejanje).
- Judilibre: spoštujte GDPR. Ne poskušajte ponovno identificirati strank.

Svoje kvote vidite na PISTE pod API Sélectionnées > Actions > Consulter les quotas.

## Združene države Amerike: api.data.gov (brezplačno)

1. Pojdite na [govinfo.gov/api-signup](https://www.govinfo.gov/api-signup) (ključ se prikaže na zaslonu)
   ali [api.data.gov/signup](https://api.data.gov/signup/) (ključ prejmete po e-pošti).
2. Vpišite svoje ime in e-poštni naslov. Polje "how will you use it" ni obvezno.
3. Kopirajte 40-mestni ključ.
4. Zaženite **Add or change keys** in ga prilepite kot ključ za ZDA.

Pogoji na kratko:

- Z lastnim ključem govinfo dovoli do 36.000 zahtev na uro.
- Pogojev uporabe, specifičnih za API, nismo našli (api.data.gov/terms/ ne obstaja). Nepreverjeno.
  Glejte [pravila govinfo](https://www.govinfo.gov/about/policies) in
  [politiko zasebnosti data.gov](https://data.gov/privacy-policy/).
- Ključ obdržite zase.

## Kje so ključi shranjeni

- **Namestitveni program ali ročno:** kot navadno besedilo v konfiguracijski datoteki MCP vsake
  aplikacije, v bloku `env` vnosa `fontes`. Kdor lahko bere vaše uporabniške datoteke, lahko
  prebere tudi ključe.
  - Claude Desktop: `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac),
    `%APPDATA%\Claude\claude_desktop_config.json` (Windows)
  - Claude Code: `~/.claude.json`
  - Codex: `~/.codex/config.toml`
  - Cursor: `~/.cursor/mcp.json`
  - VS Code (Copilot): `~/.copilot/mcp-config.json`
  - Windsurf: `~/.config/devin/mcp_config.json` ali `~/.codeium/windsurf/mcp_config.json`
    (Windows: `%APPDATA%\devin\mcp_config.json`)
  - Gemini CLI: `~/.gemini/settings.json`
  - Zed: `~/.config/zed/settings.json` (Windows: `%APPDATA%\Zed\settings.json`)
  - LM Studio: `~/.lmstudio/mcp.json`
  - Cline: `~/.cline/data/settings/cline_mcp_settings.json`
- **Razširitev za Claude Desktop (.mcpb):** Claude ta polja hrani v svojih nastavitvah in jih
  ščiti z varno shrambo vašega sistema (Keychain na Macu, Credential Manager v sistemu Windows).

Pred vsako spremembo namestitveni program shrani kopijo konfiguracijske datoteke poleg nje
(`<file>.fontes-backup-<time>`). Kopije, ustvarjene potem, ko ste dodali ključe, prav tako
vsebujejo ključe. Izbrišite stare kopije, ki jih ne potrebujete.

## Spreminjanje ali odstranjevanje ključa

- Zaženite **Add or change keys**. Prilepite nov ključ, da zamenjate obstoječega, ali vpišite
  `-`, da ga odstranite.
- Ali ročno uredite blok `env` in znova zaženite aplikacijo.
- Odstranitev orodja Fontes odstrani celoten njegov vnos, skupaj s ključi. Varnostnih kopij ne
  izbriše.
- Če je ključ ušel v javnost, ga zamenjajte tudi pri viru: na PISTE ustvarite nove poverilnice
  za svojo aplikacijo; pri api.data.gov se prijavite za nov ključ.

## Sporočila, ki jih lahko vidite

| Sporočilo | Pomen |
|---|---|
| `France needs a free PISTE key: set WLM_FR_PISTE_CLIENT_ID and WLM_FR_PISTE_CLIENT_SECRET.` | Ni ključa za Francijo. Dodajte ga. |
| `Inactive: needs a free PISTE account. ...` (v `list_jurisdictions`) | Enako. |
| `PISTE refused the client credentials ...` | ID ali secret je napačen ali ne velja več. Znova kopirajte oba z zavihka Authentification. |
| `PISTE denied access to the ... API: subscribe the application to ... and accept its CGU on piste.gouv.fr.` | Vaša aplikacija ni naročena na ta API ali niste sprejeli njegovih pogojev. Glejte koraka 2 in 3. |
| `Using govinfo DEMO_KEY (about 10 searches/day per IP) ...` | Ni ključa za ZDA. Iskanje deluje za nekaj klicev na dan. |
| `govinfo rate limit reached (Retry-After ...). DEMO_KEY allows only about 10 searches a day per IP ...` | Demo ključ je porabljen. Dodajte lasten ključ. |
| `govinfo refused the API key (WLM_US_GOVINFO_KEY).` | Ključ je napačen ali še ni potrjen po e-pošti. |

Prazna vrednost šteje, kot da ključa ni.

## Dovoljenja (WLM_PERMITTED)

To ni ključ API in namestitveni program ga ne nastavi. **Nastavite ga le, če to dovoljenje
imate vi osebno.**

Nekateri viri so privzeto izklopljeni, ker njihovi pogoji ali robots.txt prepovedujejo
avtomatizirano uporabo brez dovoljenja. Če imate dovoljenje izdajatelja, vir vklopite tako, da
njegovo kodo dodate v `WLM_PERMITTED`, ločeno z vejicami, v bloku `env`: `"WLM_PERMITTED": "in,de"`.

| Koda | Vir |
|---|---|
| `az` | Azerbajdžan: e-qanun.az (Ministrstvo za pravosodje) |
| `bh` | Bahrajn: Legislation and Legal Opinion Commission (lloc.gov.bh) |
| `co` | Kolumbija: Función Pública, Gestor Normativo (prečiščeni predpisi) |
| `de` | Nemčija: NeuRIS (zvezni portal pravnih informacij, poskusna storitev) |
| `difc` | Dubai International Financial Centre Courts (difccourts.ae) |
| `gr` | Grčija: National Printing Office, iskanje Government Gazette (search.et.gr) |
| `in` | Indija: India Code (indiacode.gov.in) |
| `mu` | Mavricij: Supreme Court (supremecourt.govmu.org) |
| `sg` | Singapur: sodne sodbe (elitigation.sg) |

Brez dovoljenja Fontes sporoči: `Off by default (<code>): the terms or robots.txt of ... forbid
automated use without the operator's permission.`

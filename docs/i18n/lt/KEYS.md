> Tai vertimas, parengtas padedant mašininiam vertimui. Autentiška yra versija anglų kalba.

# API raktai

Beveik kiekvienas Fontes šaltinis veikia be rakto. Trims reikia nemokamo rakto:

| Raktas | Ką atveria | Be jo |
|---|---|---|
| `WLM_FR_PISTE_CLIENT_ID` + `WLM_FR_PISTE_CLIENT_SECRET` | Prancūzija: Judilibre (teismų sprendimai) ir Légifrance (teisės aktai) | Prancūzija išjungta. `list_jurisdictions` rodo ją kaip neaktyvią. |
| `WLM_US_GOVINFO_KEY` | Jungtinės Valstijos: govinfo paieška (federalinių teismų sprendimai, Statutes at Large, public laws) | Fontes naudoja bendrą `DEMO_KEY`: apie 10 paieškų per dieną vienam IP adresui. Žinomam sprendimui atidaryti ir US Code raktas nereikalingas. |
| `WLM_US_COURTLISTENER_KEY` | JAV valstijų teismai (`us-states`): visų 50 valstijų ir Kolumbijos apygardos aukščiausiųjų bei apeliacinių teismų sprendimai iš CourtListener | JAV valstijų teismų praktika išjungta. `list_jurisdictions` rodo ją kaip neaktyvią. |

Raktai neprivalomi. Galite juos pridėti vėliau.

## Rakto pridėjimas

**Su diegimo programa.** Kai Fontes nustatyta, diegimo programa pasiūlo pridėti raktus.
Mac kompiuteryje spustelėkite **Pridėti raktus** arba, norėdami praleisti, **Baigta**; Windows
sistemoje atsakykite į klausimą (norėdami praleisti, paspauskite Enter). Norėdami pridėti arba
pakeisti raktus vėliau, paleiskite **Add or change keys**:

- Mac: vėl atidarykite programą Fontes Installer ir pasirinkite **Pridėti arba keisti raktus**.
- Windows: atidarykite Start menu, tada **Fontes** → **Pridėti arba keisti raktus**.

Įvedami simboliai nerodomi. Kiekvienam raktui: įklijuokite jį, paspauskite Enter, kad
paliktumėte esamą, arba įveskite `-`, kad jį pašalintumėte. Raktai įrašomi į kiekvieną programą,
kurioje jau yra Fontes.

**Su Claude Desktop plėtiniu (.mcpb).** Atidarykite Claude > Settings > Extensions > Fontes ir
užpildykite laukus. Visi jie neprivalomi.

**Rankiniu būdu.** Pridėkite kintamuosius į `fontes` įrašo bloką `env` savo programos MCP
konfigūracijoje:

```json
"fontes": {
  "command": "...",
  "args": ["..."],
  "env": { "WLM_US_GOVINFO_KEY": "your-key" }
}
```

Po bet kokio pakeitimo paleiskite programą iš naujo.

## Prancūzija: PISTE (nemokamai)

1. Susikurkite paskyrą [piste.gouv.fr](https://piste.gouv.fr). Tam reikia sutikti su PISTE
   sąlygomis (CGU).
2. Eikite į API > **Consentement CGU API**. Sutikite su **JUDILIBRE** ir **Légifrance**
   (production) sąlygomis.
3. Sukurkite **gamybinę programą (production application)**. Jums sukurta `APP_SANDBOX` negali
   pasiekti gamybinės aplinkos. Skiltyje „Modifier l'application“ pažymėkite **JUDILIBRE
   (production)** ir **Légifrance (production)**, tada pritaikykite.
4. Atidarykite programos skirtuką **Authentification**. Nukopijuokite `client_id` ir
   `client_secret`.
5. Paleiskite **Add or change keys** ir juos įklijuokite.

Sąlygos trumpai:

- Duomenys: Licence Ouverte / Etalab 2.0. Pakartotinis naudojimas, įskaitant komercinį, leidžiamas
  nurodant šaltinį.
- Neskelbkite ir niekam neperduokite savo prisijungimo duomenų. Jei jie nutekėjo, praneškite
  PISTE.
- Légifrance API yra beta paslauga. Ji gali būti sustabdyta, ir jai taikomos kvotos (per
  sekundę, minutę ir dieną).
- Légifrance tekstai nėra autentiška versija. Autentiškas tik pasirašytas Journal officiel PDF.
- Judilibre: nenaudokite teisėjų ar teismo kanceliarijos darbuotojų vardų jų darbui vertinti,
  lyginti ar prognozuoti (Code de l'organisation judiciaire art. L111-13; tai nusikalstama
  veika).
- Judilibre: laikykitės BDAR. Nebandykite iš naujo nustatyti šalių tapatybės.

Savo kvotas rasite PISTE skiltyje API Sélectionnées > Actions > Consulter les quotas.

## Jungtinės Valstijos: api.data.gov (nemokamai)

1. Eikite į [govinfo.gov/api-signup](https://www.govinfo.gov/api-signup) (raktas rodomas ekrane)
   arba [api.data.gov/signup](https://api.data.gov/signup/) (raktas atsiunčiamas el. paštu).
2. Įveskite savo vardą ir el. pašto adresą. Laukas „how will you use it“ neprivalomas.
3. Nukopijuokite 40 simbolių raktą.
4. Paleiskite **Add or change keys** ir įklijuokite jį kaip JAV raktą.

Sąlygos trumpai:

- Su savo raktu govinfo leidžia iki 36,000 užklausų per valandą.
- Neradome jokių konkrečiai API taikomų naudojimo sąlygų (api.data.gov/terms/ neegzistuoja).
  Nepatikrinta. Žr. [govinfo politiką](https://www.govinfo.gov/about/policies) ir
  [data.gov privatumo politiką](https://data.gov/privacy-policy/).
- Laikykite raktą tik sau.

## JAV valstijų teismai: CourtListener (nemokamai)

CourtListener valdo [Free Law Project](https://free.law) – ne pelno siekianti organizacija, nuo 2010 m. renkanti JAV teismų sprendimus ir teikianti juos nemokamai visiems. Pagal jos pačios duomenis, joje yra daugiau kaip devyni milijonai sprendimų. Tai nėra oficialus šaltinis: teismai savo sprendimus skelbia patys, o CourtListener surenka juos iš teismų svetainių ir nuskenuotų įstatymų ataskaitų. Kiekvienas Fontes atsakymas iš jos tai nurodo. Fontes neturi jokių ryšių su Free Law Project.

1. Susikurkite nemokamą paskyrą adresu [courtlistener.com](https://www.courtlistener.com/sign-in/).
2. Atidarykite savo profilį ir nukopijuokite savo API žetoną (token).
3. Paleiskite **Add or change keys** ir įklijuokite jį kaip CourtListener raktą.

Sąlygos trumpai ([visos sąlygos](https://wiki.free.law/c/terms/courtlistener/courtlistenercom-terms-of-service-and-policies)):

- Žetonas skirtas tik jums: nesidalykite juo, nejunkite jo į bendrą rinkinį ir neperparduokite, nenaudokite kelių paskyrų.
- Jūs atsakote už tai, ką DI programa daro su jūsų žetonu.
- Nepateikite DI atlikto jų duomenų analizės kaip parengtos, patvirtintos ar patikrintos Free Law Project.
- Nemokama paskyra leidžia 5 užklausas per minutę, 50 per valandą ir 125 per dieną. Paieška yra viena užklausa; sprendimo atidarymas – dvi. Free Law Project narystė šias ribas padidina.
- CourtListener negarantuoja tikslumo. Prieš pasikliaudami sprendimu, palyginkite jį su teismo egzemplioriumi.

## Kur saugomi raktai

- **Diegimo programa arba rankiniu būdu:** kaip paprastas tekstas kiekvienos programos MCP
  konfigūracijos faile, `fontes` įrašo bloke `env`. Kiekvienas, galintis skaityti jūsų naudotojo
  failus, gali perskaityti ir raktus.
  - Claude Desktop: `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac),
    `%APPDATA%\Claude\claude_desktop_config.json` (Windows)
  - Claude Code: `~/.claude.json`
  - Codex: `~/.codex/config.toml`
  - Cursor: `~/.cursor/mcp.json`
  - VS Code (Copilot): `~/.copilot/mcp-config.json`
  - Windsurf: `~/.config/devin/mcp_config.json` arba `~/.codeium/windsurf/mcp_config.json`
    (Windows: `%APPDATA%\devin\mcp_config.json`)
  - Gemini CLI: `~/.gemini/settings.json`
  - Zed: `~/.config/zed/settings.json` (Windows: `%APPDATA%\Zed\settings.json`)
  - LM Studio: `~/.lmstudio/mcp.json`
  - Cline: `~/.cline/data/settings/cline_mcp_settings.json`
- **Claude Desktop plėtinys (.mcpb):** Claude šiuos laukus laiko savo nustatymuose ir apsaugo
  jūsų sistemos saugia saugykla (Mac – Keychain, Windows – Credential Manager).

Prieš kiekvieną pakeitimą diegimo programa šalia konfigūracijos failo išsaugo jo kopiją
(`<file>.fontes-backup-<time>`). Kopijose, padarytose pridėjus raktus, taip pat yra raktai.
Ištrinkite senas kopijas, kurių jums nereikia.

## Rakto keitimas arba pašalinimas

- Paleiskite **Add or change keys**. Įklijuokite naują raktą, kad jį pakeistumėte, arba
  įveskite `-`, kad jį pašalintumėte.
- Arba rankiniu būdu redaguokite bloką `env` ir paleiskite programą iš naujo.
- Pašalinus Fontes, pašalinamas visas jo įrašas kartu su raktais. Atsarginės kopijos
  neištrinamos.
- Jei raktas nutekėjo, pakeiskite jį ir šaltinyje: PISTE sukurkite naujus savo programos
  prisijungimo duomenis; api.data.gov užsiregistruokite naujam raktui.

## Pranešimai, kuriuos galite matyti

| Pranešimas | Reikšmė |
|---|---|
| `France needs a free PISTE key: set WLM_FR_PISTE_CLIENT_ID and WLM_FR_PISTE_CLIENT_SECRET.` | Nėra Prancūzijos rakto. Pridėkite jį. |
| `Inactive: needs a free PISTE account. ...` (`list_jurisdictions` išvestyje) | Tas pats. |
| `PISTE refused the client credentials ...` | ID arba slaptasis raktas neteisingas arba nebegalioja. Dar kartą nukopijuokite abu iš skirtuko Authentification. |
| `PISTE denied access to the ... API: subscribe the application to ... and accept its CGU on piste.gouv.fr.` | Jūsų programa neužsiprenumeravusi tos API arba nesutikote su jos sąlygomis. Žr. 2 ir 3 veiksmus. |
| `Using govinfo DEMO_KEY (about 10 searches/day per IP) ...` | Nėra JAV rakto. Paieška veikia kelis kartus per dieną. |
| `govinfo rate limit reached (Retry-After ...). DEMO_KEY allows only about 10 searches a day per IP ...` | Demonstracinis raktas išnaudotas. Pridėkite savo raktą. |
| `govinfo refused the API key (WLM_US_GOVINFO_KEY).` | Raktas neteisingas arba dar nepatvirtintas el. laiške. |

Tuščia reikšmė laikoma rakto nebuvimu.

## Leidimai (WLM_PERMITTED)

Tai nėra API raktas, ir diegimo programa jo nenustato. **Nustatykite jį tik tada, jei patys
turite tą leidimą.**

Kai kurie šaltiniai pagal numatytuosius nustatymus išjungti, nes jų sąlygos arba robots.txt
draudžia automatizuotą naudojimą be leidimo. Jei turite leidėjo leidimą, įjunkite šaltinį
pridėdami jo kodą prie `WLM_PERMITTED`, atskirdami kableliais, bloke `env`:
`"WLM_PERMITTED": "in,de"`.

| Kodas | Šaltinis |
|---|---|
| `az` | Azerbaidžanas: e-qanun.az (Teisingumo ministerija) |
| `bh` | Bahreinas: Legislation and Legal Opinion Commission (lloc.gov.bh) |
| `co` | Kolumbija: Función Pública, Gestor Normativo (suvestinės redakcijos teisės aktai) |
| `de` | Vokietija: NeuRIS (federalinis teisinės informacijos portalas, bandomoji paslauga) |
| `difc` | Dubai International Financial Centre Courts (difccourts.ae) |
| `gr` | Graikija: Nacionalinė spaustuvė, Vyriausybės žinių paieška (search.et.gr) |
| `in` | Indija: India Code (indiacode.gov.in) |
| `mu` | Mauricijus: Aukščiausiasis Teismas (supremecourt.govmu.org) |
| `sg` | Singapūras: teismų sprendimai (elitigation.sg) |

Be leidimo Fontes praneša: `Off by default (<code>): the terms or robots.txt of ... forbid
automated use without the operator's permission.`

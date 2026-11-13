> Ez gépi segítséggel készült fordítás. Az angol változat az irányadó.

# API-kulcsok

A Fontes szinte minden forrása kulcs nélkül működik. Kettőhöz ingyenes kulcs kell:

| Kulcs | Mit tesz elérhetővé | Nélküle |
|---|---|---|
| `WLM_FR_PISTE_CLIENT_ID` + `WLM_FR_PISTE_CLIENT_SECRET` | Franciaország: Judilibre (bírósági határozatok) és Légifrance (jogszabályok) | Franciaország ki van kapcsolva. A `list_jurisdictions` inaktívként mutatja. |
| `WLM_US_GOVINFO_KEY` | Egyesült Államok: govinfo-keresés (szövetségi bírósági határozatok, Statutes at Large, public laws) | A Fontes a közös `DEMO_KEY` kulcsot használja: IP-címenként naponta körülbelül 10 keresés. Egy ismert határozat megnyitásához és a US Code-hoz nem kell kulcs. |

A kulcsok opcionálisak. Később is hozzáadhatja őket.

## Kulcs hozzáadása

**A telepítővel.** Telepítés közben a telepítő megkérdezi, szeretne-e kulcsokat hozzáadni. A
kihagyáshoz válassza a **Not now** lehetőséget (vagy nyomja meg az Entert). A kulcsok későbbi
hozzáadásához vagy módosításához futtassa az **Add or change keys** elemet:

- Mac: nyissa meg újra a Fontes Installer alkalmazást, és válassza az **Add or change keys**
  lehetőséget, vagy kattintson duplán az `Add or change keys.command` fájlra a telepítő
  mappájában.
- Windows: kattintson duplán az `Add or change keys.cmd` fájlra a telepítő mappájában. A
  Windows-telepítőprogram, amint elérhető lesz, a Start menu > Fontes alá is elhelyezi.

A begépelt szöveg rejtve marad. Minden kulcsnál: illessze be, nyomja meg az Entert a meglévő
érték megtartásához, vagy írjon be `-` jelet az eltávolításához. A kulcsok minden olyan
alkalmazásba bekerülnek, amelyben már megvan a Fontes.

**A Claude Desktop-bővítménnyel (.mcpb).** Nyissa meg a Claude > Settings > Extensions > Fontes
menüt, és töltse ki a mezőket. Mindegyik opcionális.

**Kézzel.** Adja hozzá a változókat a `fontes` bejegyzés `env` blokkjához az alkalmazása
MCP-konfigurációjában:

```json
"fontes": {
  "command": "...",
  "args": ["..."],
  "env": { "WLM_US_GOVINFO_KEY": "your-key" }
}
```

Minden módosítás után indítsa újra az alkalmazást.

## Franciaország: PISTE (ingyenes)

1. Hozzon létre fiókot a [piste.gouv.fr](https://piste.gouv.fr) oldalon. Ehhez el kell fogadnia
   a PISTE feltételeit (CGU).
2. Lépjen az API > **Consentement CGU API** menüpontra. Fogadja el a **JUDILIBRE** és a
   **Légifrance** (production) feltételeit.
3. Hozzon létre egy **éles (production) alkalmazást**. Az Ön számára létrehozott `APP_SANDBOX`
   nem éri el az éles környezetet. A „Modifier l'application” alatt jelölje be a **JUDILIBRE
   (production)** és a **Légifrance (production)** elemet, majd alkalmazza.
4. Nyissa meg az alkalmazás **Authentification** fülét. Másolja ki a `client_id` és a
   `client_secret` értéket.
5. Futtassa az **Add or change keys** elemet, és illessze be őket.

A feltételek röviden:

- Adatok: Licence Ouverte / Etalab 2.0. Az újrafelhasználás, a kereskedelmi újrafelhasználást is
  beleértve, forrásmegjelöléssel megengedett.
- Ne tegye közzé és ne ossza meg a hitelesítő adatait. Ha kiszivárognak, értesítse a PISTE-t.
- A Légifrance API béta szolgáltatás. Felfüggeszthetik, és kvóták vonatkoznak rá (másodpercenként,
  percenként és naponként).
- A Légifrance szövegei nem a hiteles változatok. Csak az aláírt Journal officiel PDF hiteles.
- Judilibre: ne használja a bírák vagy a bírósági tisztviselők nevét a munkájuk értékelésére,
  összehasonlítására vagy előrejelzésére (Code de l'organisation judiciaire art. L111-13;
  bűncselekmény).
- Judilibre: tartsa be a GDPR-t. Ne próbálja újra azonosítani a feleket.

A kvótáit a PISTE-n találja: API Sélectionnées > Actions > Consulter les quotas.

## Egyesült Államok: api.data.gov (ingyenes)

1. Látogasson el a [govinfo.gov/api-signup](https://www.govinfo.gov/api-signup) oldalra (a kulcs
   a képernyőn jelenik meg) vagy az [api.data.gov/signup](https://api.data.gov/signup/) oldalra (a
   kulcsot e-mailben kapja meg).
2. Adja meg a nevét és az e-mail-címét. A „how will you use it” mező opcionális.
3. Másolja ki a 40 karakteres kulcsot.
4. Futtassa az **Add or change keys** elemet, és illessze be egyesült államokbeli kulcsként.

A feltételek röviden:

- Saját kulccsal a govinfo óránként legfeljebb 36,000 kérést enged.
- Nem találtunk az API-ra vonatkozó külön felhasználási feltételeket (az api.data.gov/terms/
  nem létezik). Nem ellenőrzött. Lásd [a govinfo szabályzatait](https://www.govinfo.gov/about/policies)
  és [a data.gov adatvédelmi szabályzatát](https://data.gov/privacy-policy/).
- A kulcsot tartsa meg magának.

## Hol tárolódnak a kulcsok

- **Telepítővel vagy kézzel:** egyszerű szövegként az egyes alkalmazások MCP-konfigurációs
  fájljában, a `fontes` bejegyzés `env` blokkjában. Aki olvashatja a felhasználói fájljait, a
  kulcsokat is olvashatja.
  - Claude Desktop: `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac),
    `%APPDATA%\Claude\claude_desktop_config.json` (Windows)
  - Claude Code: `~/.claude.json`
  - Codex: `~/.codex/config.toml`
  - Cursor: `~/.cursor/mcp.json`
  - VS Code (Copilot): `~/.copilot/mcp-config.json`
  - Windsurf: `~/.config/devin/mcp_config.json` vagy `~/.codeium/windsurf/mcp_config.json`
    (Windows: `%APPDATA%\devin\mcp_config.json`)
  - Gemini CLI: `~/.gemini/settings.json`
  - Zed: `~/.config/zed/settings.json` (Windows: `%APPDATA%\Zed\settings.json`)
  - LM Studio: `~/.lmstudio/mcp.json`
  - Cline: `~/.cline/data/settings/cline_mcp_settings.json`
- **Claude Desktop-bővítmény (.mcpb):** a Claude ezeket a mezőket a beállításaiban tárolja, és a
  rendszer biztonságos tárolójával védi (Macen Keychain, Windowson Credential Manager).

Minden módosítás előtt a telepítő másolatot ment a konfigurációs fájlról mellé
(`<file>.fontes-backup-<time>`). A kulcsok hozzáadása után készült másolatok a kulcsokat is
tartalmazzák. Törölje a régi másolatokat, amelyekre nincs szüksége.

## Kulcs módosítása vagy eltávolítása

- Futtassa az **Add or change keys** elemet. Illesszen be egy új kulcsot a cseréhez, vagy írjon
  be `-` jelet az eltávolításhoz.
- Vagy szerkessze kézzel az `env` blokkot, és indítsa újra az alkalmazást.
- A Fontes eltávolítása a teljes bejegyzését törli, a kulcsokkal együtt. A biztonsági
  másolatokat nem törli.
- Ha egy kulcs kiszivárgott, a forrásnál is cserélje le: a PISTE-n hozzon létre új hitelesítő
  adatokat az alkalmazásához; az api.data.gov esetében regisztráljon új kulcsért.

## Üzenetek, amelyeket láthat

| Üzenet | Jelentés |
|---|---|
| `France needs a free PISTE key: set WLM_FR_PISTE_CLIENT_ID and WLM_FR_PISTE_CLIENT_SECRET.` | Nincs francia kulcs. Adjon hozzá egyet. |
| `Inactive: needs a free PISTE account. ...` (a `list_jurisdictions` kimenetében) | Ugyanaz. |
| `PISTE refused the client credentials ...` | Az azonosító vagy a titkos kulcs hibás, vagy már nem érvényes. Másolja ki mindkettőt újra az Authentification fülről. |
| `PISTE denied access to the ... API: subscribe the application to ... and accept its CGU on piste.gouv.fr.` | Az alkalmazása nem fizetett elő arra az API-ra, vagy nem fogadta el a feltételeit. Lásd a 2. és 3. lépést. |
| `Using govinfo DEMO_KEY (about 10 searches/day per IP) ...` | Nincs egyesült államokbeli kulcs. A keresés naponta néhány hívásig működik. |
| `govinfo rate limit reached (Retry-After ...). DEMO_KEY allows only about 10 searches a day per IP ...` | A demókulcs elfogyott. Adja hozzá a saját kulcsát. |
| `govinfo refused the API key (WLM_US_GOVINFO_KEY).` | A kulcs hibás, vagy még nem erősítette meg az e-mailből. |

Az üres érték kulcs hiányának számít.

## Engedélyek (WLM_PERMITTED)

Ez nem API-kulcs, és a telepítő nem állítja be. **Csak akkor állítsa be, ha Ön maga rendelkezik
ezzel az engedéllyel.**

Egyes források alapértelmezés szerint ki vannak kapcsolva, mert a feltételeik vagy a
robots.txt-jük engedély nélkül tiltja az automatizált felhasználást. Ha a kiadó engedélyével
rendelkezik, kapcsolja be a forrást úgy, hogy a kódját vesszővel elválasztva hozzáadja a
`WLM_PERMITTED` változóhoz az `env` blokkban: `"WLM_PERMITTED": "in,de"`.

| Kód | Forrás |
|---|---|
| `az` | Azerbajdzsán: e-qanun.az (Igazságügyi Minisztérium) |
| `bh` | Bahrein: Legislation and Legal Opinion Commission (lloc.gov.bh) |
| `co` | Kolumbia: Función Pública, Gestor Normativo (egységes szerkezetbe foglalt jogszabályok) |
| `de` | Németország: NeuRIS (szövetségi jogi információs portál, próbaüzem) |
| `difc` | Dubai International Financial Centre Courts (difccourts.ae) |
| `gr` | Görögország: Nemzeti Nyomda, a Kormányzati Közlöny keresője (search.et.gr) |
| `in` | India: India Code (indiacode.gov.in) |
| `mu` | Mauritius: Legfelsőbb Bíróság (supremecourt.govmu.org) |
| `sg` | Szingapúr: bírósági ítéletek (elitigation.sg) |

Engedély nélkül a Fontes ezt írja ki: `Off by default (<code>): the terms or robots.txt of ...
forbid automated use without the operator's permission.`

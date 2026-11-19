> Tai vertimas, parengtas padedant mašininiam vertimui. Autentiška yra versija anglų kalba.

# Fontes diegimas

Fontes leidžia jūsų DI programai tiesiogiai ieškoti teismų sprendimų ir teisės aktų teismų ir
valstybės institucijų svetainėse daugiau nei 120 jurisdikcijų. Kiekvienas rezultatas pateikia
nuorodą į originalą. Tai standartinis MCP serveris, todėl jis veikia bet kurioje programoje,
galinčioje paleisti vietinį MCP serverį: Claude Desktop, Codex, Claude Code, Cursor, VS Code
(GitHub Copilot), Gemini CLI, Windsurf, Zed, LM Studio, Cline ir kitose.

Pasirinkite savo programą, atlikite jos veiksmus, tada
[patikrinkite, ar veikia](#kaip-patikrinti-ar-veikia).

## Claude Desktop

1. Atsisiųskite Fontes `.mcpb` failą iš
   [naujausios versijos](https://github.com/ykarapazar/fontes/releases/latest).
2. Dukart jį spustelėkite. Claude Desktop jį atidarys.
3. Spustelėkite **Install**.

## Codex

Terminale:

```bash
codex mcp add fontes -- uvx fontes-mcp
```

Codex CLI ir Codex IDE plėtinys naudoja tą patį nustatymą (`~/.codex/config.toml`).
Jums reikės [uv](#jums-reikės-uv).

## Claude Code

Terminale:

```bash
claude mcp add fontes -- uvx fontes-mcp
```

Jums reikės [uv](#jums-reikės-uv).

## Kitos programos

Kiekvienai iš jų reikia [uv](#jums-reikės-uv). Pridėkite įrašą, išsaugokite, tada uždarykite
programą ir vėl ją atidarykite.

**Cursor:** faile `~/.cursor/mcp.json` (visiems projektams) arba `.cursor/mcp.json` (vienam
projektui):

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**VS Code (GitHub Copilot):** komandų paletėje (Command Palette) paleiskite **MCP: Add Server**,
pasirinkite **Command (stdio)**, įveskite `uvx fontes-mcp` ir pavadinkite serverį `fontes`. Arba
pridėkite tai į `~/.copilot/mcp-config.json`:

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

Senesnėse VS Code sąrankose naudojamas `.vscode/mcp.json`, kuriame aukščiausio lygio raktas yra
`servers`, o ne `mcpServers`.

**Gemini CLI:** terminale `gemini mcp add -s user fontes uvx fontes-mcp`. Arba pridėkite tai į
`~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Zed:** atidarykite nustatymų failą (**zed: open settings file**) ir pridėkite:

```json
{
  "context_servers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**LM Studio:** dešinėje šoninėje juostoje atidarykite skirtuką **Program**, spustelėkite
**Install → Edit mcp.json** ir pridėkite:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Cline:** spustelėkite piktogramą **MCP Servers**, atidarykite skirtuką **Configure**,
spustelėkite **Configure MCP Servers** ir pridėkite tą patį `mcpServers` įrašą kaip LM Studio.

**Claude Desktop rankiniu būdu** (vietoj `.mcpb` failo): pridėkite tą patį `mcpServers` įrašą į
`claude_desktop_config.json` (macOS: `~/Library/Application Support/Claude/`, Windows:
`%APPDATA%\Claude\`).

**Bet kuri kita MCP programa** (Windsurf ir kitos): jos dokumentacijoje nurodyta, kur ji laiko
savo MCP serverius. Dauguma priima tą patį įrašą: komanda `uvx`, argumentas `fontes`.

Jei programa neranda `uvx`, naudokite visą jo kelią (macOS ir Linux sistemose jį parodo
`which uvx`).

## Jums reikės uv

Codex, Claude Code ir kitos programos paleidžia Fontes naudodamos `uvx`, kuris pateikiamas kartu
su **uv** – nedideliu nemokamu Astral įrankiu. Norėdami jį įdiegti, žr.
[Astral vadovą](https://docs.astral.sh/uv/getting-started/installation/) arba paleiskite:

- macOS arba Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Windows (PowerShell): `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

## Raktai

Kai kuriems šaltiniams reikia nemokamo rakto: žr. [KEYS.md](KEYS.md).

## Kaip patikrinti, ar veikia

Naujame pokalbyje paklauskite: *„Kuriose jurisdikcijose gali ieškoti Fontes?“* Programa turėtų
atsakyti šalių sąrašu. Jei taip neatsitinka, dar kartą uždarykite programą ir vėl ją
atidarykite.

## Diegimo programa vienu spustelėjimu (Mac ir Windows)

Diegimo programa iš karto nustato Fontes visose jūsų programose: Claude Desktop, Codex, Claude
Code, Cursor, VS Code (GitHub Copilot), Windsurf, Gemini CLI, Zed, LM Studio ir Cline.

**Prieš pradėdami:** visiškai uždarykite kiekvieną iš šių programų. Labiausiai tai svarbu Claude
Code: veikdama ji perrašo `~/.claude.json` ir gali atšaukti diegimo programos pakeitimą. Jei
negalite uždaryti Claude Code, verčiau pridėkite Fontes į ją komanda `claude mcp add` (žr.
[Claude Code](#claude-code)).

**Mac**

1. Atsisiųskite Mac diegimo programą (`Fontes-Installer-…-mac.zip`) iš [naujausios
   laidos](https://github.com/ykarapazar/fontes/releases/latest) ir dukart ją spustelėkite, kad
   išskleistumėte.
2. Dukart spustelėkite **Fontes Installer**. Jei jūsų Mac klausia, ar atidaryti iš interneto
   atsisiųstą programą, spustelėkite **Open**.
3. Pasirinkite **Įdiegti** ir spustelėkite **Gerai**. Nustatymas trunka maždaug minutę.
4. Pranešime išvardijamos programos, kurias ji nustatė. Spustelėkite **Baigta**, tada vėl
   atidarykite tas programas. Jei pirmiau norite pridėti neprivalomus nemokamus raktus, verčiau
   spustelėkite **Pridėti raktus**; žr. [Raktų žingsnis](#raktų-žingsnis).

**Windows**

1. Atsisiųskite Windows diegimo programą (`Fontes-Setup-….exe`) iš
   [naujausios laidos](https://github.com/ykarapazar/fontes/releases/latest) ir dukart ją spustelėkite.
   - Jei Windows rodo „Windows protected your PC“: spustelėkite **More info**, tada **Run
     anyway**.
2. Spustelėkite **Įdiegti**. Atsidaro langas ir nustato Fontes.
3. Paklausti, ar siųsti anoniminius naudojimo skaičius, norėdami atsakyti „ne“, paspauskite
   Enter.
4. Jis klausia, ar pridėti raktus dabar. Norėdami praleisti, paspauskite Enter; žr.
   [Raktų žingsnis](#raktų-žingsnis).
5. Kai parodomas užrašas **Done**, vėl atidarykite savo DI programas. Jei kuri nors dar veikė,
   visiškai ją uždarykite (taip pat ir sistemos dėkle, šalia laikrodžio) ir vėl atidarykite.

Pabaigoje diegimo programa išvardija programas, kurias nustatė.

### Kurias programas ji nustato

Ji nustato programą tik tada, jei tos programos nustatymų aplankas jau yra jūsų kompiuteryje.
Claude Code nustatoma tik tada, jei yra `~/.claude.json`. Claude Desktop nustatoma visada.
Kiekviena programa gauna vieną įrašą `fontes` šiame faile:

| Programa | Failas (Mac ir Linux) | Failas (Windows) |
|---|---|---|
| Claude Desktop | `~/Library/Application Support/Claude/claude_desktop_config.json` (Linux: `~/.config/Claude/`) | `%APPDATA%\Claude\claude_desktop_config.json` ir atskira Microsoft Store versijos kopija |
| Codex | `~/.codex/config.toml` | `%USERPROFILE%\.codex\config.toml` |
| Claude Code | `~/.claude.json` | `%USERPROFILE%\.claude.json` |
| Cursor | `~/.cursor/mcp.json` | `%USERPROFILE%\.cursor\mcp.json` |
| VS Code (Copilot) | `~/.copilot/mcp-config.json` | `%USERPROFILE%\.copilot\mcp-config.json` |
| Windsurf | `~/.config/devin/mcp_config.json` arba senesnėse versijose `~/.codeium/windsurf/mcp_config.json` | `%APPDATA%\devin\mcp_config.json` arba `%USERPROFILE%\.codeium\windsurf\mcp_config.json` |
| Gemini CLI | `~/.gemini/settings.json` | `%USERPROFILE%\.gemini\settings.json` |
| Zed | `~/.config/zed/settings.json` | `%APPDATA%\Zed\settings.json` |
| LM Studio | `~/.lmstudio/mcp.json` | `%USERPROFILE%\.lmstudio\mcp.json` |
| Cline | `~/.cline/data/settings/cline_mcp_settings.json` | `%USERPROFILE%\.cline\data\settings\cline_mcp_settings.json` |

VS Code nustatoma, jei yra `~/.copilot` arba paties VS Code nustatymų aplankas.

Dviem programoms reikia dar vieno veiksmo:

- **Windsurf:** vėl ją atidarę, Cascade paspauskite atnaujinimą (refresh).
- **Cline senesniame VS Code plėtinyje:** pridėkite Fontes rankiniu būdu (žr.
  [Cline](#kitos-programos)).

### Raktų žingsnis

Iškart po diegimo diegimo programa pasiūlo pridėti nemokamus Prancūzijos ir JAV raktus. Norėdami
juos pridėti arba pakeisti vėliau:

- **Mac:** vėl atidarykite **Fontes Installer** ir pasirinkite **Pridėti arba keisti raktus**.
- **Windows:** pradžios meniu atidarykite **Fontes** → **Pridėti arba keisti raktus**.

Įvedami simboliai nerodomi. Raktai įrašomi į kiekvieną programą, kurioje jau yra Fontes. Po to
uždarykite programas ir vėl jas atidarykite. Kur gauti raktus ir ką jie atveria:
[KEYS.md](KEYS.md).

### Atsarginės kopijos, pakartotinis paleidimas ir pašalinimas

Diegimo programa keičia tik įrašą `fontes`. Visi kiti nustatymai ir komentarai lieka tokie, kokie
buvo. Prieš keisdama failą, ji šalia jo išsaugo kopiją pavadinimu `<file>.fontes-backup-<date>`.
Kopijose, padarytose pridėjus raktus, yra tie raktai: ištrinkite tas, kurių nebereikia. Ji taip
pat įdiegia uv. Paleisti ją dar kartą saugu: ji sutvarko sąranką ir nieko kito nekeičia.

Norėdami pašalinti Fontes, atidarykite **Fontes Installer** ir pasirinkite **Pašalinti** (Mac) arba
pašalinkite **Fontes** per Settings → Apps (Windows). Tai pašalina įrašą `fontes` kartu su raktais iš visų
programų. Kiti jūsų nustatymai ir atsarginės kopijos lieka.

## Atnaujinimai

- **Diegimo programa ir `.mcpb` failas:** nieko daryti nereikia. Kartą per dieną, kai programa
  paleidžiama, Fontes fone patikrina, ar yra naujesnė versija, ir ją paruošia; kitą kartą
  paleidus programą, ji naudojama. Jei atnaujinimo nepavyksta atsisiųsti arba jis neveikia,
  Fontes toliau naudoja veikusią versiją.
- **`uvx`:** Fontes praneša, kai yra naujesnė versija, savo jurisdikcijų sąrašo viršuje. Norėdami
  visada naudoti naujausią versiją, vietoj `fontes-mcp` naudokite `fontes-mcp@latest`.

Tam jokia informacija apie jus ar jūsų paieškas niekur nesiunčiama.

## Privatumas

Pagal numatytuosius nustatymus Fontes nesiunčia nieko apie jus ar jūsų paieškas. Naudojimo
skaičiai siunčiami tik jums sutikus (opt-in), o klaidos ataskaita siunčiama tik jums ją
pamačius ir patvirtinus. Išsamiau: [PRIVACY.md](PRIVACY.md).

## Kaip pašalinti

Pašalinkite įrašą `fontes` iš savo programos MCP nustatymų (Claude Code:
`claude mcp remove fontes`), tada uždarykite programą ir vėl ją atidarykite.

## Naudinga žinoti

Fontes skaito viešus šaltinius, daugiausia teismų ir valstybės institucijų svetaines. Savo
atsakymuose jis pažymi neoficialius šaltinius. Prieš remdamiesi sprendimu ar nuostata, visada
atidarykite šaltinio nuorodą.

Jei kas nors nepavyksta, parašykite, ką darėte ir kokią klaidą matėte, adresu
fontesmcp@proton.me.

## Prieš remdamiesi

- Fontes yra tyrimų įrankis, o ne teisinė konsultacija. Jo naudojimas niekieno nepadaro jūsų
  advokatu.
- Jis teikiamas „tokia, kokia yra“ („as is“), be jokių garantijų, o jo autoriai, kiek leidžia
  įstatymai, neatsako už tai, kaip jis naudojamas. Visos sąlygos pateiktos
  [licencijoje](../../../LICENSE) (Apache 2.0).

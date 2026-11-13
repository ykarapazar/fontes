> ນີ້ແມ່ນການແປໂດຍມີເຄື່ອງຈັກຊ່ວຍ. ສະບັບພາສາອັງກິດແມ່ນສະບັບທີ່ມີຜົນບັງຄັບ.

# ກະແຈ API

ເກືອບທຸກແຫຼ່ງໃນ Fontes ເຮັດວຽກໄດ້ໂດຍບໍ່ມີກະແຈ. ມີສອງແຫຼ່ງທີ່ຕ້ອງການກະແຈຟຣີ:

| ກະແຈ | ເປີດໃຫ້ໃຊ້ | ຖ້າບໍ່ມີມັນ |
|---|---|---|
| `WLM_FR_PISTE_CLIENT_ID` + `WLM_FR_PISTE_CLIENT_SECRET` | ຝຣັ່ງ: Judilibre (ຄຳຕັດສິນຂອງສານ) ແລະ Légifrance (ນິຕິກຳ) | ຝຣັ່ງຖືກປິດ. `list_jurisdictions` ສະແດງມັນວ່າບໍ່ເຮັດວຽກ. |
| `WLM_US_GOVINFO_KEY` | ສະຫະລັດ: ການຄົ້ນຫາ govinfo (ຄຳພິພາກສາຂອງສານລັດຖະບານກາງ, Statutes at Large, public laws) | Fontes ໃຊ້ `DEMO_KEY` ທີ່ໃຊ້ຮ່ວມກັນ: ປະມານ 10 ການຄົ້ນຫາຕໍ່ມື້ ຕໍ່ທີ່ຢູ່ IP. ການເປີດຄຳຕັດສິນທີ່ຮູ້ຈັກແລ້ວ ແລະ US Code ບໍ່ຕ້ອງການກະແຈ. |

ກະແຈເປັນທາງເລືອກ. ທ່ານສາມາດເພີ່ມພວກມັນໃນພາຍຫຼັງ.

## ການເພີ່ມກະແຈ

**ດ້ວຍໂປຣແກຣມຕິດຕັ້ງ.** ໃນຂະນະທີ່ມັນຕິດຕັ້ງ, ໂປຣແກຣມຕິດຕັ້ງຖາມວ່າທ່ານຕ້ອງການເພີ່ມກະແຈຫຼືບໍ່. ເລືອກ
**Not now** (ຫຼື ກົດ Enter) ເພື່ອຂ້າມ. ເພື່ອເພີ່ມ ຫຼື ປ່ຽນກະແຈໃນພາຍຫຼັງ, ແລ່ນ **Add or change keys**:

- Mac: ເປີດແອັບ Fontes Installer ອີກຄັ້ງ ແລ້ວເລືອກ **Add or change keys**, ຫຼື ຄລິກສອງເທື່ອໃສ່
  `Add or change keys.command` ໃນໂຟນເດີໂປຣແກຣມຕິດຕັ້ງ.
- Windows: ຄລິກສອງເທື່ອໃສ່ `Add or change keys.cmd` ໃນໂຟນເດີໂປຣແກຣມຕິດຕັ້ງ. ໂປຣແກຣມຕິດຕັ້ງ Windows
  (setup program), ເມື່ອມີແລ້ວ, ຍັງໃສ່ມັນໄວ້ໃນ Start menu > Fontes ນຳ.

ສິ່ງທີ່ທ່ານພິມຈະຖືກເຊື່ອງໄວ້. ສຳລັບແຕ່ລະກະແຈ: ວາງມັນ, ກົດ Enter ເພື່ອຮັກສາຄ່າທີ່ມີຢູ່, ຫຼື ພິມ `-` ເພື່ອ
ລຶບມັນອອກ. ກະແຈຈະເຂົ້າໄປໃນທຸກແອັບທີ່ມີ Fontes ແລ້ວ.

**ດ້ວຍສ່ວນຂະຫຍາຍ Claude Desktop (.mcpb).** ເປີດ Claude > Settings > Extensions > Fontes ແລະ
ຕື່ມຂໍ້ມູນໃສ່ຊ່ອງຕ່າງໆ. ທຸກຊ່ອງເປັນທາງເລືອກ.

**ດ້ວຍມື.** ເພີ່ມຕົວແປໃສ່ບລັອກ `env` ຂອງລາຍການ `fontes` ໃນການຕັ້ງຄ່າ MCP ຂອງແອັບທ່ານ:

```json
"fontes": {
  "command": "...",
  "args": ["..."],
  "env": { "WLM_US_GOVINFO_KEY": "your-key" }
}
```

ເລີ່ມແອັບຄືນໃໝ່ ຫຼັງຈາກການປ່ຽນແປງໃດໆ.

## ຝຣັ່ງ: PISTE (ຟຣີ)

1. ສ້າງບັນຊີທີ່ [piste.gouv.fr](https://piste.gouv.fr). ນີ້ໝາຍເຖິງການຍອມຮັບເງື່ອນໄຂຂອງ PISTE (CGU).
2. ໄປທີ່ API > **Consentement CGU API**. ຍອມຮັບເງື່ອນໄຂສຳລັບ **JUDILIBRE** ແລະ **Légifrance** (production).
3. ສ້າງ **production application**. `APP_SANDBOX` ທີ່ຖືກສ້າງໃຫ້ທ່ານ ບໍ່ສາມາດເຂົ້າເຖິງ production ໄດ້.
   ພາຍໃຕ້ "Modifier l'application", ໝາຍຕິກ **JUDILIBRE (production)** ແລະ **Légifrance (production)**, ແລ້ວນຳໃຊ້.
4. ເປີດແຖບ **Authentification** ຂອງແອັບ. ສຳເນົາ `client_id` ແລະ `client_secret`.
5. ແລ່ນ **Add or change keys** ແລ້ວວາງພວກມັນ.

ເງື່ອນໄຂ, ໂດຍຫຍໍ້:

- ຂໍ້ມູນ: Licence Ouverte / Etalab 2.0. ອະນຸຍາດໃຫ້ນຳໃຊ້ຄືນ, ລວມທັງການນຳໃຊ້ຄືນເພື່ອການຄ້າ, ໂດຍມີການລະບຸແຫຼ່ງທີ່ມາ.
- ຢ່າເຜີຍແຜ່ ຫຼື ແບ່ງປັນຂໍ້ມູນປະຈຳຕົວຂອງທ່ານ. ແຈ້ງ PISTE ຖ້າພວກມັນຮົ່ວໄຫຼ.
- API ຂອງ Légifrance ເປັນບໍລິການເບຕ້າ. ມັນອາດຖືກໂຈະ, ແລະ ມັນມີໂຄຕ້າ (ຕໍ່ວິນາທີ, ນາທີ ແລະ ມື້).
- ເນື້ອໃນຂອງ Légifrance ບໍ່ແມ່ນສະບັບທີ່ແທ້ຈິງ. ມີພຽງ PDF ຂອງ Journal officiel ທີ່ມີລາຍເຊັນເທົ່ານັ້ນທີ່ແທ້ຈິງ.
- Judilibre: ຢ່າໃຊ້ຊື່ຂອງຜູ້ພິພາກສາ ຫຼື ເລຂາສານ ເພື່ອປະເມີນ, ປຽບທຽບ ຫຼື ຄາດຄະເນວຽກຂອງພວກເຂົາ
  (Code de l'organisation judiciaire art. L111-13; ເປັນການກະທຳຜິດທາງອາຍາ).
- Judilibre: ປະຕິບັດຕາມ GDPR. ຢ່າພະຍາຍາມລະບຸຕົວຕົນຂອງຄູ່ຄວາມຄືນ.

ໂຄຕ້າຂອງທ່ານຢູ່ໃນ PISTE ພາຍໃຕ້ API Sélectionnées > Actions > Consulter les quotas.

## ສະຫະລັດ: api.data.gov (ຟຣີ)

1. ໄປທີ່ [govinfo.gov/api-signup](https://www.govinfo.gov/api-signup) (ກະແຈສະແດງເທິງໜ້າຈໍ)
   ຫຼື [api.data.gov/signup](https://api.data.gov/signup/) (ກະແຈຖືກສົ່ງທາງອີເມວໃຫ້ທ່ານ).
2. ໃສ່ຊື່ ແລະ ອີເມວຂອງທ່ານ. ຊ່ອງ "how will you use it" ເປັນທາງເລືອກ.
3. ສຳເນົາກະແຈ 40 ຕົວອັກສອນ.
4. ແລ່ນ **Add or change keys** ແລ້ວວາງມັນເປັນກະແຈຂອງສະຫະລັດ.

ເງື່ອນໄຂ, ໂດຍຫຍໍ້:

- ດ້ວຍກະແຈຂອງທ່ານເອງ, govinfo ອະນຸຍາດເຖິງ 36,000 ຄຳຂໍຕໍ່ຊົ່ວໂມງ.
- ພວກເຮົາບໍ່ພົບເງື່ອນໄຂການບໍລິການສະເພາະຂອງ API (api.data.gov/terms/ ບໍ່ມີຢູ່). ຍັງບໍ່ໄດ້ຢືນຢັນ.
  ເບິ່ງ [ນະໂຍບາຍຂອງ govinfo](https://www.govinfo.gov/about/policies) ແລະ
  [ນະໂຍບາຍຄວາມເປັນສ່ວນຕົວຂອງ data.gov](https://data.gov/privacy-policy/).
- ເກັບກະແຈໄວ້ກັບຕົວທ່ານເອງ.

## ກະແຈຖືກເກັບໄວ້ຢູ່ໃສ

- **ໂປຣແກຣມຕິດຕັ້ງ ຫຼື ດ້ວຍມື:** ເປັນຂໍ້ຄວາມທຳມະດາ ໃນໄຟລ໌ການຕັ້ງຄ່າ MCP ຂອງແຕ່ລະແອັບ, ໃນບລັອກ `env` ຂອງ
  ລາຍການ `fontes`. ຜູ້ໃດກໍຕາມທີ່ສາມາດອ່ານໄຟລ໌ຜູ້ໃຊ້ຂອງທ່ານ ກໍສາມາດອ່ານກະແຈໄດ້.
  - Claude Desktop: `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac),
    `%APPDATA%\Claude\claude_desktop_config.json` (Windows)
  - Claude Code: `~/.claude.json`
  - Codex: `~/.codex/config.toml`
  - Cursor: `~/.cursor/mcp.json`
  - VS Code (Copilot): `~/.copilot/mcp-config.json`
  - Windsurf: `~/.config/devin/mcp_config.json` ຫຼື `~/.codeium/windsurf/mcp_config.json`
    (Windows: `%APPDATA%\devin\mcp_config.json`)
  - Gemini CLI: `~/.gemini/settings.json`
  - Zed: `~/.config/zed/settings.json` (Windows: `%APPDATA%\Zed\settings.json`)
  - LM Studio: `~/.lmstudio/mcp.json`
  - Cline: `~/.cline/data/settings/cline_mcp_settings.json`
- **ສ່ວນຂະຫຍາຍ Claude Desktop (.mcpb):** Claude ເກັບຊ່ອງເຫຼົ່ານີ້ໄວ້ໃນການຕັ້ງຄ່າຂອງມັນ ແລະ ປົກປ້ອງພວກມັນ
  ດ້ວຍບ່ອນເກັບຂໍ້ມູນທີ່ປອດໄພຂອງລະບົບທ່ານ (Keychain ໃນ Mac, Credential Manager ໃນ Windows).

ກ່ອນການປ່ຽນແປງແຕ່ລະຄັ້ງ, ໂປຣແກຣມຕິດຕັ້ງບັນທຶກສຳເນົາຂອງໄຟລ໌ການຕັ້ງຄ່າໄວ້ຂ້າງໆ
(`<file>.fontes-backup-<time>`). ສຳເນົາທີ່ສ້າງຂຶ້ນຫຼັງຈາກທ່ານເພີ່ມກະແຈແລ້ວ ກໍມີກະແຈຢູ່ນຳ. ລຶບ
ສຳເນົາເກົ່າທີ່ທ່ານບໍ່ຕ້ອງການ.

## ການປ່ຽນ ຫຼື ລຶບກະແຈ

- ແລ່ນ **Add or change keys**. ວາງກະແຈໃໝ່ເພື່ອແທນທີ່ມັນ, ຫຼື ພິມ `-` ເພື່ອລຶບມັນອອກ.
- ຫຼື ແກ້ໄຂບລັອກ `env` ດ້ວຍມື ແລ້ວເລີ່ມແອັບຄືນໃໝ່.
- ການຖອນ Fontes ອອກ ຈະລຶບລາຍການທັງໝົດຂອງມັນ, ລວມທັງກະແຈ. ມັນບໍ່ລຶບສຳເນົາສຳຮອງ.
- ຖ້າກະແຈຮົ່ວໄຫຼ, ໃຫ້ແທນທີ່ມັນຢູ່ທີ່ແຫຼ່ງນຳ: ໃນ PISTE, ສ້າງຂໍ້ມູນປະຈຳຕົວໃໝ່ສຳລັບແອັບຂອງທ່ານ;
  ສຳລັບ api.data.gov, ສະໝັກເອົາກະແຈໃໝ່.

## ຂໍ້ຄວາມທີ່ທ່ານອາດເຫັນ

| ຂໍ້ຄວາມ | ຄວາມໝາຍ |
|---|---|
| `France needs a free PISTE key: set WLM_FR_PISTE_CLIENT_ID and WLM_FR_PISTE_CLIENT_SECRET.` | ບໍ່ມີກະແຈຂອງຝຣັ່ງ. ເພີ່ມມັນ. |
| `Inactive: needs a free PISTE account. ...` (ໃນ `list_jurisdictions`) | ຄືກັນ. |
| `PISTE refused the client credentials ...` | ID ຫຼື secret ຜິດ ຫຼື ໃຊ້ບໍ່ໄດ້ອີກແລ້ວ. ສຳເນົາທັງສອງອີກຄັ້ງຈາກແຖບ Authentification. |
| `PISTE denied access to the ... API: subscribe the application to ... and accept its CGU on piste.gouv.fr.` | ແອັບຂອງທ່ານບໍ່ໄດ້ສະໝັກໃຊ້ API ນັ້ນ, ຫຼື ທ່ານຍັງບໍ່ໄດ້ຍອມຮັບເງື່ອນໄຂຂອງມັນ. ເບິ່ງຂັ້ນຕອນທີ 2 ແລະ 3. |
| `Using govinfo DEMO_KEY (about 10 searches/day per IP) ...` | ບໍ່ມີກະແຈຂອງສະຫະລັດ. ການຄົ້ນຫາເຮັດວຽກໄດ້ສອງສາມຄັ້ງຕໍ່ມື້. |
| `govinfo rate limit reached (Retry-After ...). DEMO_KEY allows only about 10 searches a day per IP ...` | ກະແຈສາທິດຖືກໃຊ້ໝົດແລ້ວ. ເພີ່ມກະແຈຂອງທ່ານເອງ. |
| `govinfo refused the API key (WLM_US_GOVINFO_KEY).` | ກະແຈຜິດ, ຫຼື ຍັງບໍ່ໄດ້ຢືນຢັນຈາກອີເມວ. |

ຄ່າທີ່ຫວ່າງເປົ່າຖືວ່າບໍ່ມີກະແຈ.

## ການອະນຸຍາດ (WLM_PERMITTED)

ນີ້ບໍ່ແມ່ນກະແຈ API, ແລະ ໂປຣແກຣມຕິດຕັ້ງບໍ່ໄດ້ຕັ້ງມັນ. **ຕັ້ງມັນ ກໍຕໍ່ເມື່ອທ່ານເອງມີ
ການອະນຸຍາດນັ້ນເທົ່ານັ້ນ.**

ບາງແຫຼ່ງຖືກປິດເປັນຄ່າເລີ່ມຕົ້ນ ເພາະເງື່ອນໄຂ ຫຼື robots.txt ຂອງພວກມັນຫ້າມການໃຊ້ແບບອັດຕະໂນມັດ ໂດຍບໍ່ມີ
ການອະນຸຍາດ. ຖ້າທ່ານໄດ້ຮັບອະນຸຍາດຈາກຜູ້ເຜີຍແຜ່, ເປີດແຫຼ່ງໂດຍການເພີ່ມລະຫັດຂອງມັນໃສ່
`WLM_PERMITTED`, ຂັ້ນດ້ວຍຈຸດ, ໃນບລັອກ `env`: `"WLM_PERMITTED": "in,de"`.

| ລະຫັດ | ແຫຼ່ງ |
|---|---|
| `az` | ອາເຊີໄບຈານ: e-qanun.az (ກະຊວງຍຸຕິທຳ) |
| `bh` | ບາເຣນ: Legislation and Legal Opinion Commission (lloc.gov.bh) |
| `co` | ໂຄລົມເບຍ: Función Pública, Gestor Normativo (ນິຕິກຳສະບັບລວມ) |
| `de` | ເຢຍລະມັນ: NeuRIS (ປະຕູຂໍ້ມູນກົດໝາຍລັດຖະບານກາງ, ບໍລິການທົດລອງ) |
| `difc` | Dubai International Financial Centre Courts (difccourts.ae) |
| `gr` | ກຣີກ: National Printing Office, ການຄົ້ນຫາ Government Gazette (search.et.gr) |
| `in` | ອິນເດຍ: India Code (indiacode.gov.in) |
| `mu` | ມໍຣິຊຽດ: ສານສູງສຸດ (supremecourt.govmu.org) |
| `sg` | ສິງກະໂປ: ຄຳພິພາກສາຂອງສານ (elitigation.sg) |

ຖ້າບໍ່ມີການອະນຸຍາດ, Fontes ຈະບອກວ່າ: `Off by default (<code>): the terms or robots.txt of ... forbid
automated use without the operator's permission.`

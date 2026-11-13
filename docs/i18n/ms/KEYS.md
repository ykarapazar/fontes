> Ini ialah terjemahan dengan bantuan mesin. Versi bahasa Inggeris adalah versi yang sahih.

# Kunci API

Hampir setiap sumber dalam Fontes berfungsi tanpa kunci. Dua memerlukan kunci percuma:

| Kunci | Membuka | Tanpanya |
|---|---|---|
| `WLM_FR_PISTE_CLIENT_ID` + `WLM_FR_PISTE_CLIENT_SECRET` | Perancis: Judilibre (keputusan mahkamah) dan Légifrance (perundangan) | Perancis dimatikan. `list_jurisdictions` menunjukkannya sebagai tidak aktif. |
| `WLM_US_GOVINFO_KEY` | Amerika Syarikat: carian govinfo (pendapat mahkamah persekutuan, Statutes at Large, public laws) | Fontes menggunakan `DEMO_KEY` yang dikongsi: kira-kira 10 carian sehari bagi setiap alamat IP. Membuka keputusan yang diketahui dan US Code tidak memerlukan kunci. |

Kunci adalah pilihan. Anda boleh menambahnya kemudian.

## Menambah kunci

**Dengan pemasang.** Semasa memasang, pemasang bertanya sama ada anda mahu menambah kunci. Pilih
**Bukan sekarang** (atau tekan Enter) untuk melangkau. Untuk menambah atau menukar kunci kemudian,
jalankan **Add or change keys**:

- Mac: buka semula aplikasi Fontes Installer dan pilih **Tambah atau tukar kunci**, atau klik dua kali
  `Add or change keys.command` dalam folder pemasang.
- Windows: klik dua kali `Add or change keys.cmd` dalam folder pemasang. Program persediaan Windows,
  sebaik sahaja tersedia, juga meletakkannya dalam menu Start > Fontes.

Taipan disembunyikan. Bagi setiap kunci: tampalkannya, tekan Enter untuk mengekalkan apa yang sedia ada,
atau taip `-` untuk membuangnya. Kunci dimasukkan ke dalam setiap aplikasi yang sudah mempunyai Fontes.

**Dengan sambungan Claude Desktop (.mcpb).** Buka Claude > Settings > Extensions > Fontes dan isi
medan-medannya. Semuanya adalah pilihan.

**Secara manual.** Tambah pemboleh ubah ke blok `env` entri `fontes` dalam konfigurasi MCP aplikasi anda:

```json
"fontes": {
  "command": "...",
  "args": ["..."],
  "env": { "WLM_US_GOVINFO_KEY": "your-key" }
}
```

Mulakan semula aplikasi selepas sebarang perubahan.

## Perancis: PISTE (percuma)

1. Cipta akaun di [piste.gouv.fr](https://piste.gouv.fr). Ini bermakna menerima syarat PISTE (CGU).
2. Pergi ke API > **Consentement CGU API**. Terima syarat untuk **JUDILIBRE** dan **Légifrance** (production).
3. Cipta **aplikasi production**. `APP_SANDBOX` yang dibuat untuk anda tidak dapat mencapai production.
   Di bawah "Modifier l'application", tandakan **JUDILIBRE (production)** dan **Légifrance (production)**,
   kemudian guna pakai.
4. Buka tab **Authentification** aplikasi itu. Salin `client_id` dan `client_secret`.
5. Jalankan **Add or change keys** dan tampalkannya.

Syarat, secara ringkas:

- Data: Licence Ouverte / Etalab 2.0. Penggunaan semula, termasuk penggunaan semula komersial, dibenarkan
  dengan atribusi.
- Jangan terbitkan atau kongsi kelayakan anda. Maklumkan PISTE jika ia bocor.
- API Légifrance ialah perkhidmatan beta. Ia boleh digantung, dan ia mempunyai kuota (sesaat, seminit dan
  sehari).
- Teks Légifrance bukan versi yang sahih. Hanya PDF Journal officiel yang ditandatangani yang sahih.
- Judilibre: jangan gunakan nama hakim atau kerani untuk menilai, membandingkan atau meramalkan kerja
  mereka (Code de l'organisation judiciaire art. L111-13; satu kesalahan jenayah).
- Judilibre: patuhi GDPR. Jangan cuba mengenal pasti semula pihak-pihak.

Kuota anda terdapat di PISTE di bawah API Sélectionnées > Actions > Consulter les quotas.

## Amerika Syarikat: api.data.gov (percuma)

1. Pergi ke [govinfo.gov/api-signup](https://www.govinfo.gov/api-signup) (kunci dipaparkan pada skrin)
   atau [api.data.gov/signup](https://api.data.gov/signup/) (kunci dihantar kepada anda melalui e-mel).
2. Masukkan nama dan e-mel anda. Medan "how will you use it" adalah pilihan.
3. Salin kunci 40 aksara itu.
4. Jalankan **Add or change keys** dan tampalkannya sebagai kunci AS.

Syarat, secara ringkas:

- Dengan kunci anda sendiri, govinfo membenarkan sehingga 36,000 permintaan sejam.
- Kami tidak menemui syarat perkhidmatan khusus API (api.data.gov/terms/ tidak wujud). Belum disahkan.
  Lihat [dasar govinfo](https://www.govinfo.gov/about/policies) dan
  [dasar privasi data.gov](https://data.gov/privacy-policy/).
- Simpan kunci itu untuk diri anda sendiri.

## Di mana kunci disimpan

- **Pemasang atau secara manual:** sebagai teks biasa dalam fail konfigurasi MCP setiap aplikasi, dalam
  blok `env` entri `fontes`. Sesiapa yang boleh membaca fail pengguna anda boleh membaca kunci itu.
  - Claude Desktop: `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac),
    `%APPDATA%\Claude\claude_desktop_config.json` (Windows)
  - Claude Code: `~/.claude.json`
  - Codex: `~/.codex/config.toml`
  - Cursor: `~/.cursor/mcp.json`
  - VS Code (Copilot): `~/.copilot/mcp-config.json`
  - Windsurf: `~/.config/devin/mcp_config.json` atau `~/.codeium/windsurf/mcp_config.json`
    (Windows: `%APPDATA%\devin\mcp_config.json`)
  - Gemini CLI: `~/.gemini/settings.json`
  - Zed: `~/.config/zed/settings.json` (Windows: `%APPDATA%\Zed\settings.json`)
  - LM Studio: `~/.lmstudio/mcp.json`
  - Cline: `~/.cline/data/settings/cline_mcp_settings.json`
- **Sambungan Claude Desktop (.mcpb):** Claude menyimpan medan-medan ini dalam tetapannya dan
  melindunginya dengan storan selamat sistem anda (Keychain pada Mac, Credential Manager pada Windows).

Sebelum setiap perubahan, pemasang menyimpan salinan fail konfigurasi di sebelahnya
(`<file>.fontes-backup-<time>`). Salinan yang dibuat selepas anda menambah kunci turut mengandungi kunci
tersebut. Padamkan salinan lama yang tidak anda perlukan.

## Menukar atau membuang kunci

- Jalankan **Add or change keys**. Tampal kunci baharu untuk menggantikannya, atau taip `-` untuk
  membuangnya.
- Atau sunting blok `env` secara manual dan mulakan semula aplikasi.
- Menyahpasang Fontes membuang keseluruhan entrinya, termasuk kunci. Ia tidak memadamkan salinan sandaran.
- Jika kunci bocor, gantikan juga di sumbernya: di PISTE, buat kelayakan baharu untuk aplikasi anda;
  untuk api.data.gov, daftar untuk kunci baharu.

## Mesej yang mungkin anda lihat

| Mesej | Maksud |
|---|---|
| `France needs a free PISTE key: set WLM_FR_PISTE_CLIENT_ID and WLM_FR_PISTE_CLIENT_SECRET.` | Tiada kunci Perancis. Tambah satu. |
| `Inactive: needs a free PISTE account. ...` (dalam `list_jurisdictions`) | Sama. |
| `PISTE refused the client credentials ...` | ID atau rahsia itu salah atau tidak lagi sah. Salin kedua-duanya semula daripada tab Authentification. |
| `PISTE denied access to the ... API: subscribe the application to ... and accept its CGU on piste.gouv.fr.` | Aplikasi anda tidak melanggan API itu, atau anda belum menerima syaratnya. Lihat langkah 2 dan 3. |
| `Using govinfo DEMO_KEY (about 10 searches/day per IP) ...` | Tiada kunci AS. Carian berfungsi untuk beberapa panggilan sehari. |
| `govinfo rate limit reached (Retry-After ...). DEMO_KEY allows only about 10 searches a day per IP ...` | Kunci demo telah habis digunakan. Tambah kunci anda sendiri. |
| `govinfo refused the API key (WLM_US_GOVINFO_KEY).` | Kunci itu salah, atau belum disahkan daripada e-mel. |

Nilai kosong dikira sebagai tiada kunci.

## Kebenaran (WLM_PERMITTED)

Ini bukan kunci API, dan pemasang tidak menetapkannya. **Tetapkannya hanya jika anda sendiri memegang
kebenaran itu.**

Sesetengah sumber dimatikan secara lalai kerana syarat penggunaan atau robots.txt mereka melarang
penggunaan automatik tanpa kebenaran. Jika anda mempunyai kebenaran daripada penerbit, hidupkan sumber
dengan menambah kodnya ke `WLM_PERMITTED`, dipisahkan dengan koma, dalam blok `env`:
`"WLM_PERMITTED": "in,de"`.

| Kod | Sumber |
|---|---|
| `az` | Azerbaijan: e-qanun.az (Kementerian Kehakiman) |
| `bh` | Bahrain: Legislation and Legal Opinion Commission (lloc.gov.bh) |
| `co` | Colombia: Función Pública, Gestor Normativo (perundangan yang disatukan) |
| `de` | Jerman: NeuRIS (portal maklumat undang-undang persekutuan, perkhidmatan percubaan) |
| `difc` | Dubai International Financial Centre Courts (difccourts.ae) |
| `gr` | Greece: National Printing Office, carian Government Gazette (search.et.gr) |
| `in` | India: India Code (indiacode.gov.in) |
| `mu` | Mauritius: Supreme Court (supremecourt.govmu.org) |
| `sg` | Singapura: penghakiman mahkamah (elitigation.sg) |

Tanpa kebenaran, Fontes menyatakan: `Off by default (<code>): the terms or robots.txt of ... forbid
automated use without the operator's permission.`

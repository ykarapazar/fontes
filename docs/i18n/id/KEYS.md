> Ini adalah terjemahan berbantuan mesin. Versi bahasa Inggris adalah yang berlaku.

# Kunci API

Hampir semua sumber di Fontes berfungsi tanpa kunci. Dua sumber memerlukan kunci gratis:

| Kunci | Membuka | Tanpa kunci |
|---|---|---|
| `WLM_FR_PISTE_CLIENT_ID` + `WLM_FR_PISTE_CLIENT_SECRET` | Prancis: Judilibre (putusan pengadilan) dan Légifrance (peraturan perundang-undangan) | Prancis nonaktif. `list_jurisdictions` menampilkannya sebagai tidak aktif. |
| `WLM_US_GOVINFO_KEY` | Amerika Serikat: pencarian govinfo (pendapat pengadilan federal, Statutes at Large, public laws) | Fontes menggunakan `DEMO_KEY` bersama: sekitar 10 pencarian per hari per alamat IP. Membuka putusan yang sudah diketahui dan US Code tidak memerlukan kunci. |

Kunci bersifat opsional. Anda dapat menambahkannya nanti.

## Menambahkan kunci

**Dengan penginstal.** Setelah Fontes disiapkan, penginstal menawarkan untuk menambahkan kunci. Di Mac,
klik **Tambah kunci**, atau **Selesai** untuk melewati; di Windows, jawab pertanyaannya (tekan Enter
untuk melewati). Untuk menambahkan atau mengubah kunci nanti, jalankan **Add or change keys**:

- Mac: buka kembali aplikasi Fontes Installer dan pilih **Tambah atau ubah kunci**.
- Windows: buka menu Start, lalu **Fontes** → **Tambah atau ubah kunci**.

Ketikan disembunyikan. Untuk setiap kunci: tempelkan kunci, tekan Enter untuk mempertahankan yang sudah ada,
atau ketik `-` untuk menghapusnya. Kunci dimasukkan ke setiap aplikasi yang sudah memiliki Fontes.

**Dengan ekstensi Claude Desktop (.mcpb).** Buka Claude > Settings > Extensions > Fontes dan isi kolomnya.
Semua kolom bersifat opsional.

**Secara manual.** Tambahkan variabel ke blok `env` pada entri `fontes` di konfigurasi MCP aplikasi Anda:

```json
"fontes": {
  "command": "...",
  "args": ["..."],
  "env": { "WLM_US_GOVINFO_KEY": "your-key" }
}
```

Mulai ulang aplikasi setelah setiap perubahan.

## Prancis: PISTE (gratis)

1. Buat akun di [piste.gouv.fr](https://piste.gouv.fr). Ini berarti menerima ketentuan PISTE (CGU).
2. Buka API > **Consentement CGU API**. Terima ketentuan untuk **JUDILIBRE** dan **Légifrance** (produksi).
3. Buat **aplikasi produksi**. `APP_SANDBOX` yang dibuat untuk Anda tidak dapat menjangkau produksi.
   Di bawah "Modifier l'application", centang **JUDILIBRE (production)** dan **Légifrance (production)**,
   lalu terapkan.
4. Buka tab **Authentification** aplikasi tersebut. Salin `client_id` dan `client_secret`.
5. Jalankan **Add or change keys** dan tempelkan keduanya.

Ketentuan, secara singkat:

- Data: Licence Ouverte / Etalab 2.0. Penggunaan ulang, termasuk penggunaan ulang komersial, diizinkan
  dengan atribusi.
- Jangan menerbitkan atau membagikan kredensial Anda. Beri tahu PISTE jika kredensial tersebut bocor.
- API Légifrance adalah layanan beta. Layanan ini dapat dihentikan sementara, dan memiliki kuota (per
  detik, menit, dan hari).
- Teks Légifrance bukan versi autentik. Hanya PDF Journal officiel yang ditandatangani yang autentik.
- Judilibre: jangan menggunakan nama hakim atau panitera untuk mengevaluasi, membandingkan, atau memprediksi
  pekerjaan mereka (Code de l'organisation judiciaire art. L111-13; merupakan tindak pidana).
- Judilibre: patuhi GDPR. Jangan mencoba mengidentifikasi ulang para pihak.

Kuota Anda ada di PISTE pada API Sélectionnées > Actions > Consulter les quotas.

## Amerika Serikat: api.data.gov (gratis)

1. Buka [govinfo.gov/api-signup](https://www.govinfo.gov/api-signup) (kunci ditampilkan di layar)
   atau [api.data.gov/signup](https://api.data.gov/signup/) (kunci dikirim kepada Anda melalui email).
2. Masukkan nama dan email Anda. Kolom "how will you use it" bersifat opsional.
3. Salin kunci yang terdiri dari 40 karakter.
4. Jalankan **Add or change keys** dan tempelkan sebagai kunci AS.

Ketentuan, secara singkat:

- Dengan kunci Anda sendiri, govinfo mengizinkan hingga 36.000 permintaan per jam.
- Kami tidak menemukan ketentuan layanan khusus API (api.data.gov/terms/ tidak ada). Belum terverifikasi.
  Lihat [kebijakan govinfo](https://www.govinfo.gov/about/policies) dan
  [kebijakan privasi data.gov](https://data.gov/privacy-policy/).
- Simpan kunci itu untuk Anda sendiri.

## Tempat kunci disimpan

- **Penginstal atau secara manual:** sebagai teks biasa di berkas konfigurasi MCP setiap aplikasi, di blok
  `env` pada entri `fontes`. Siapa pun yang dapat membaca berkas pengguna Anda dapat membaca kunci tersebut.
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
- **Ekstensi Claude Desktop (.mcpb):** Claude menyimpan kolom-kolom ini di pengaturannya dan melindunginya
  dengan penyimpanan aman sistem Anda (Keychain di Mac, Credential Manager di Windows).

Sebelum setiap perubahan, penginstal menyimpan salinan berkas konfigurasi di sebelahnya
(`<file>.fontes-backup-<time>`). Salinan yang dibuat setelah Anda menambahkan kunci juga berisi kunci
tersebut. Hapus salinan lama yang tidak Anda perlukan.

## Mengubah atau menghapus kunci

- Jalankan **Add or change keys**. Tempelkan kunci baru untuk menggantinya, atau ketik `-` untuk menghapusnya.
- Atau sunting blok `env` secara manual dan mulai ulang aplikasi.
- Menghapus instalasi Fontes menghapus seluruh entrinya, termasuk kunci. Salinan cadangan tidak dihapus.
- Jika suatu kunci bocor, gantilah juga di sumbernya: di PISTE, buat kredensial baru untuk aplikasi Anda;
  untuk api.data.gov, daftar untuk mendapatkan kunci baru.

## Pesan yang mungkin Anda lihat

| Pesan | Arti |
|---|---|
| `France needs a free PISTE key: set WLM_FR_PISTE_CLIENT_ID and WLM_FR_PISTE_CLIENT_SECRET.` | Tidak ada kunci Prancis. Tambahkan kunci. |
| `Inactive: needs a free PISTE account. ...` (di `list_jurisdictions`) | Sama. |
| `PISTE refused the client credentials ...` | ID atau secret salah atau tidak lagi berlaku. Salin keduanya lagi dari tab Authentification. |
| `PISTE denied access to the ... API: subscribe the application to ... and accept its CGU on piste.gouv.fr.` | Aplikasi Anda tidak berlangganan API tersebut, atau Anda belum menerima ketentuannya. Lihat langkah 2 dan 3. |
| `Using govinfo DEMO_KEY (about 10 searches/day per IP) ...` | Tidak ada kunci AS. Pencarian berfungsi untuk beberapa panggilan per hari. |
| `govinfo rate limit reached (Retry-After ...). DEMO_KEY allows only about 10 searches a day per IP ...` | Kunci demo sudah habis. Tambahkan kunci Anda sendiri. |
| `govinfo refused the API key (WLM_US_GOVINFO_KEY).` | Kuncinya salah, atau belum dikonfirmasi dari email. |

Nilai kosong dianggap sebagai tidak ada kunci.

## Izin (WLM_PERMITTED)

Ini bukan kunci API, dan penginstal tidak menetapkannya. **Tetapkan hanya jika Anda sendiri memegang izin
tersebut.**

Beberapa sumber nonaktif secara bawaan karena ketentuan atau robots.txt-nya melarang penggunaan otomatis
tanpa izin. Jika Anda memiliki izin dari penerbit, aktifkan suatu sumber dengan menambahkan kodenya ke
`WLM_PERMITTED`, dipisahkan koma, di blok `env`: `"WLM_PERMITTED": "in,de"`.

| Kode | Sumber |
|---|---|
| `az` | Azerbaijan: e-qanun.az (Kementerian Kehakiman) |
| `bh` | Bahrain: Legislation and Legal Opinion Commission (lloc.gov.bh) |
| `co` | Kolombia: Función Pública, Gestor Normativo (peraturan perundang-undangan terkonsolidasi) |
| `de` | Jerman: NeuRIS (portal informasi hukum federal, layanan uji coba) |
| `difc` | Dubai International Financial Centre Courts (difccourts.ae) |
| `gr` | Yunani: Percetakan Nasional, pencarian Lembaran Negara (search.et.gr) |
| `in` | India: India Code (indiacode.gov.in) |
| `mu` | Mauritius: Mahkamah Agung (supremecourt.govmu.org) |
| `sg` | Singapura: putusan pengadilan (elitigation.sg) |

Tanpa izin, Fontes menyatakan: `Off by default (<code>): the terms or robots.txt of ... forbid
automated use without the operator's permission.`

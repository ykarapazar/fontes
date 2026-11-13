> Ini adalah terjemahan berbantuan mesin. Versi bahasa Inggris adalah yang berlaku.

# Menginstal Fontes

Fontes memungkinkan aplikasi AI Anda mencari putusan pengadilan dan peraturan perundang-undangan secara
langsung di situs web pengadilan dan pemerintah di lebih dari 120 yurisdiksi. Setiap hasil menautkan ke
dokumen aslinya. Fontes adalah server MCP standar, sehingga berfungsi di aplikasi apa pun yang dapat
menjalankan server MCP lokal: Claude Desktop, Codex, Claude Code, Cursor, VS Code (GitHub Copilot),
Gemini CLI, Windsurf, Zed, LM Studio, Cline, dan lainnya.

Pilih aplikasi Anda, ikuti langkah-langkahnya, lalu [periksa apakah Fontes berfungsi](#memeriksa-apakah-fontes-berfungsi).

## Claude Desktop

1. Unduh berkas `.mcpb` Fontes dari
   [rilis terbaru](https://github.com/ykarapazar/fontes/releases/latest).
2. Klik dua kali berkas itu. Claude Desktop akan membukanya.
3. Klik **Install**.

## Codex

Di terminal:

```bash
codex mcp add fontes -- uvx fontes-mcp
```

Codex CLI dan ekstensi IDE Codex menggunakan pengaturan yang sama ini (`~/.codex/config.toml`).
Anda memerlukan [uv](#anda-memerlukan-uv).

## Claude Code

Di terminal:

```bash
claude mcp add fontes -- uvx fontes-mcp
```

Anda memerlukan [uv](#anda-memerlukan-uv).

## Aplikasi lain

Setiap aplikasi berikut memerlukan [uv](#anda-memerlukan-uv). Tambahkan entri, simpan, lalu tutup dan
buka kembali aplikasinya.

**Cursor:** di `~/.cursor/mcp.json` (semua proyek) atau `.cursor/mcp.json` (satu proyek):

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**VS Code (GitHub Copilot):** jalankan **MCP: Add Server** dari Command Palette, pilih
**Command (stdio)**, masukkan `uvx fontes-mcp`, dan beri nama server itu `fontes`. Atau tambahkan ini ke
`~/.copilot/mcp-config.json`:

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

Penyiapan VS Code versi lama menggunakan `.vscode/mcp.json`, dengan kunci tingkat atas `servers`, bukan
`mcpServers`.

**Gemini CLI:** di terminal, `gemini mcp add -s user fontes uvx fontes-mcp`. Atau tambahkan ini ke
`~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Zed:** buka berkas pengaturan Anda (**zed: open settings file**) dan tambahkan:

```json
{
  "context_servers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**LM Studio:** di bilah samping kanan, buka tab **Program**, klik **Install → Edit
mcp.json**, dan tambahkan:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Cline:** klik ikon **MCP Servers**, buka tab **Configure**, klik **Configure MCP
Servers**, dan tambahkan entri `mcpServers` yang sama seperti untuk LM Studio.

**Claude Desktop, secara manual** (sebagai ganti berkas `.mcpb`): tambahkan entri `mcpServers` yang sama ke
`claude_desktop_config.json` (macOS: `~/Library/Application Support/Claude/`, Windows:
`%APPDATA%\Claude\`).

**Aplikasi MCP lainnya** (Windsurf dan lainnya): dokumentasi aplikasi itu sendiri menjelaskan di mana
aplikasi tersebut menyimpan server MCP-nya. Sebagian besar menerima entri yang sama: perintah `uvx`,
argumen `fontes`.

Jika aplikasi tidak dapat menemukan `uvx`, gunakan path lengkapnya (di macOS dan Linux, `which uvx`
menampilkannya).

## Anda memerlukan uv

Codex, Claude Code, dan aplikasi lainnya menjalankan Fontes dengan `uvx`, yang disertakan dengan **uv**,
alat kecil gratis dari Astral. Untuk menginstalnya, lihat
[panduan Astral](https://docs.astral.sh/uv/getting-started/installation/), atau jalankan:

- macOS atau Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Windows (PowerShell): `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

## Kunci

Beberapa sumber memerlukan kunci gratis: lihat [KEYS.md](KEYS.md).

## Memeriksa apakah Fontes berfungsi

Dalam obrolan baru, tanyakan: *"Yurisdiksi mana saja yang dapat dicari oleh Fontes?"* Aplikasi seharusnya
menjawab dengan daftar negara. Jika tidak, tutup lalu buka kembali aplikasi sekali lagi.

## Penginstal sekali klik (sedang disiapkan)

Penginstal untuk Mac dan Windows yang menyiapkan Fontes di semua aplikasi Anda sekaligus sedang disiapkan.
Penginstal ini menyiapkan Claude Desktop, Codex, Claude Code, Cursor, VS Code (GitHub Copilot), Windsurf,
Gemini CLI, Zed, LM Studio, dan Cline. Setelah dirilis:

**Sebelum Anda mulai:** tutup setiap aplikasi ini sepenuhnya. Hal ini paling penting untuk Claude Code:
selama berjalan, Claude Code menulis ulang `~/.claude.json` dan dapat membatalkan perubahan yang dibuat
penginstal. Jika Anda tidak dapat menutup Claude Code, tambahkan Fontes ke dalamnya dengan `claude mcp add`
(lihat [Claude Code](#claude-code)).

**Mac**

1. Buka folder **Fontes Installer** yang telah diunduh.
2. Klik dua kali **Install Fontes.command**.
   - Jika Mac Anda menyatakan berkas itu "cannot be opened because it is from an unidentified developer":
     klik kanan (atau Control-klik) berkas tersebut, pilih **Open**, lalu **Open** lagi. Anda hanya
     perlu melakukan ini sekali.
3. Sebuah jendela terbuka dan menanyakan apakah akan mengirim jumlah penggunaan anonim; tekan Enter
   untuk tidak.
4. Penginstal menanyakan apakah akan menambahkan kunci sekarang. Tekan Enter untuk melewati; lihat
   [Langkah kunci](#langkah-kunci).
5. Ketika muncul **Selesai**, buka kembali aplikasi AI Anda.

**Windows**

1. Ekstrak **Fontes Installer** yang telah diunduh (klik kanan → Extract All).
2. Klik dua kali **Install Fontes.cmd**.
   - Jika Windows menampilkan "Windows protected your PC": klik **More info**, lalu **Run anyway**.
3. Ketika ditanya apakah akan mengirim jumlah penggunaan anonim, tekan Enter untuk tidak.
4. Penginstal menanyakan apakah akan menambahkan kunci sekarang. Tekan Enter untuk melewati; lihat
   [Langkah kunci](#langkah-kunci).
5. Ketika muncul **Selesai**, buka kembali aplikasi AI Anda. Jika salah satunya masih berjalan, tutup
   sepenuhnya (juga dari baki sistem, di dekat jam) lalu buka kembali.

Di akhir, penginstal mencantumkan aplikasi yang telah disiapkannya.

### Aplikasi yang disiapkan

Penginstal hanya menyiapkan suatu aplikasi jika folder pengaturan aplikasi tersebut sudah ada di komputer
Anda. Claude Code hanya disiapkan jika `~/.claude.json` ada. Claude Desktop selalu disiapkan. Setiap
aplikasi mendapat satu entri, `fontes`, di berkas berikut:

| Aplikasi | Berkas (Mac dan Linux) | Berkas (Windows) |
|---|---|---|
| Claude Desktop | `~/Library/Application Support/Claude/claude_desktop_config.json` (Linux: `~/.config/Claude/`) | `%APPDATA%\Claude\claude_desktop_config.json`, dan salinan tersendiri milik versi Microsoft Store |
| Codex | `~/.codex/config.toml` | `%USERPROFILE%\.codex\config.toml` |
| Claude Code | `~/.claude.json` | `%USERPROFILE%\.claude.json` |
| Cursor | `~/.cursor/mcp.json` | `%USERPROFILE%\.cursor\mcp.json` |
| VS Code (Copilot) | `~/.copilot/mcp-config.json` | `%USERPROFILE%\.copilot\mcp-config.json` |
| Windsurf | `~/.config/devin/mcp_config.json`, atau `~/.codeium/windsurf/mcp_config.json` pada versi lama | `%APPDATA%\devin\mcp_config.json`, atau `%USERPROFILE%\.codeium\windsurf\mcp_config.json` |
| Gemini CLI | `~/.gemini/settings.json` | `%USERPROFILE%\.gemini\settings.json` |
| Zed | `~/.config/zed/settings.json` | `%APPDATA%\Zed\settings.json` |
| LM Studio | `~/.lmstudio/mcp.json` | `%USERPROFILE%\.lmstudio\mcp.json` |
| Cline | `~/.cline/data/settings/cline_mcp_settings.json` | `%USERPROFILE%\.cline\data\settings\cline_mcp_settings.json` |

VS Code disiapkan jika `~/.copilot` atau folder pengaturan milik VS Code sendiri ada.

Dua aplikasi memerlukan satu langkah tambahan:

- **Windsurf:** setelah membukanya kembali, tekan tombol muat ulang (refresh) di Cascade.
- **Cline di dalam ekstensi VS Code versi lama:** tambahkan Fontes secara manual (lihat [Cline](#aplikasi-lain)).

### Langkah kunci

Tepat setelah instalasi, penginstal menawarkan untuk menambahkan kunci gratis untuk Prancis dan AS. Untuk
menambahkan atau mengubahnya nanti:

- **Mac:** klik dua kali **Add or change keys.command** di folder penginstal, atau buka kembali aplikasi
  Fontes Installer dan pilih **Tambah atau ubah kunci**.
- **Windows:** klik dua kali **Add or change keys.cmd** di folder penginstal.

Ketikan disembunyikan. Kunci dimasukkan ke setiap aplikasi yang sudah memiliki Fontes. Setelah itu, tutup
lalu buka kembali aplikasi-aplikasi tersebut. Tempat memperoleh kunci dan apa yang dibukanya: [KEYS.md](KEYS.md).

### Cadangan, menjalankan ulang, dan menghapus

Penginstal hanya mengubah entri `fontes`. Semua pengaturan dan komentar lainnya tetap seperti semula.
Sebelum mengubah suatu berkas, penginstal menyimpan salinannya di sebelahnya, dengan nama
`<file>.fontes-backup-<date>`. Salinan yang dibuat setelah Anda menambahkan kunci berisi kunci tersebut:
hapus salinan yang tidak Anda perlukan lagi. Penginstal juga menginstal uv. Menjalankannya lagi aman:
penginstal memperbaiki penyiapan dan tidak mengubah hal lain.

Untuk menghapus Fontes, klik dua kali **Uninstall Fontes.command** (Mac) atau **Uninstall Fontes.cmd**
(Windows). Ini menghapus entri `fontes`, termasuk kuncinya, dari setiap aplikasi. Pengaturan Anda yang lain
dan salinan cadangan tetap ada.

## Pembaruan

- **Penginstal dan berkas `.mcpb`:** Anda tidak perlu melakukan apa pun. Sekali sehari, saat aplikasi
  dimulai, Fontes memeriksa versi yang lebih baru di latar belakang dan menyiapkannya; saat aplikasi
  dimulai berikutnya, versi itu yang digunakan. Jika pembaruan tidak dapat diunduh atau tidak berfungsi,
  Fontes tetap menggunakan versi yang berfungsi.
- **`uvx`:** Fontes memberi tahu Anda ketika versi yang lebih baru tersedia, di bagian atas daftar
  yurisdiksinya. Untuk selalu menjalankan versi terbaru, gunakan `fontes-mcp@latest` sebagai ganti `fontes-mcp`.

Tidak ada informasi tentang Anda atau pencarian Anda yang dikirim ke mana pun untuk keperluan ini.

## Privasi

Secara bawaan, Fontes tidak mengirim apa pun tentang Anda atau pencarian Anda. Jumlah penggunaan bersifat
opt-in, dan laporan bug hanya dikirim setelah Anda melihat dan mengonfirmasinya. Rincian: [PRIVACY.md](PRIVACY.md).

## Menghapusnya

Hapus entri `fontes` dari pengaturan MCP aplikasi Anda (di Claude Code:
`claude mcp remove fontes`), lalu tutup dan buka kembali aplikasinya.

## Perlu diketahui

Fontes membaca sumber publik, sebagian besar situs web pengadilan dan pemerintah. Fontes menandai sumber yang
tidak resmi dalam jawabannya. Selalu buka tautan sumber sebelum mengandalkan suatu putusan atau ketentuan.

Jika terjadi masalah, kirim email berisi apa yang Anda lakukan dan pesan galat yang Anda lihat ke
fontesmcp@proton.me.

## Sebelum Anda mengandalkannya

- Fontes adalah alat riset, bukan nasihat hukum. Menggunakannya tidak menjadikan siapa pun advokat Anda.
- Fontes disediakan "sebagaimana adanya", tanpa jaminan, dan para pembuatnya tidak bertanggung jawab atas
  cara penggunaannya, sejauh diizinkan oleh hukum. Ketentuan lengkapnya ada di [lisensi](../../../LICENSE)
  (Apache 2.0).

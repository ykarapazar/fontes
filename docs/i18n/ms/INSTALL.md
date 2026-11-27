> Ini ialah terjemahan dengan bantuan mesin. Versi bahasa Inggeris adalah versi yang sahih.

# Memasang Fontes

Fontes membolehkan aplikasi AI anda mencari keputusan mahkamah dan perundangan secara langsung di laman web
mahkamah dan kerajaan di 125 bidang kuasa. Setiap hasil memaut kepada dokumen asal. Ia ialah
pelayan MCP standard, jadi ia berfungsi dalam mana-mana aplikasi yang boleh menjalankan pelayan MCP
setempat: Claude Desktop, Codex, Claude Code, Cursor, VS Code (GitHub Copilot), Gemini CLI, Windsurf, Zed,
LM Studio, Cline dan lain-lain.

Pilih aplikasi anda, ikut langkah-langkahnya, kemudian [semak bahawa ia berfungsi](#menyemak-bahawa-ia-berfungsi).

## Claude Desktop

1. Muat turun fail `.mcpb` Fontes daripada
   [keluaran terkini](https://github.com/ykarapazar/fontes/releases/latest).
2. Klik dua kali padanya. Claude Desktop akan membukanya.
3. Klik **Install**.

## Codex

Dalam terminal:

```bash
codex mcp add fontes -- uvx fontes-mcp
```

Codex CLI dan sambungan IDE Codex berkongsi tetapan ini (`~/.codex/config.toml`).
Anda memerlukan [uv](#anda-memerlukan-uv).

## Claude Code

Dalam terminal:

```bash
claude mcp add fontes -- uvx fontes-mcp
```

Anda memerlukan [uv](#anda-memerlukan-uv).

## Aplikasi lain

Setiap aplikasi ini memerlukan [uv](#anda-memerlukan-uv). Tambah entri, simpan, kemudian tutup dan buka
semula aplikasi.

**Cursor:** dalam `~/.cursor/mcp.json` (semua projek) atau `.cursor/mcp.json` (satu projek):

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**VS Code (GitHub Copilot):** jalankan **MCP: Add Server** daripada Command Palette, pilih
**Command (stdio)**, masukkan `uvx fontes-mcp` dan namakan pelayan itu `fontes`. Atau tambah ini ke
`~/.copilot/mcp-config.json`:

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

Persediaan VS Code yang lebih lama menggunakan `.vscode/mcp.json`, dengan kunci peringkat atas `servers`
dan bukannya `mcpServers`.

**Gemini CLI:** dalam terminal, `gemini mcp add -s user fontes uvx fontes-mcp`. Atau tambah ini ke
`~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Zed:** buka fail tetapan anda (**zed: open settings file**) dan tambah:

```json
{
  "context_servers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**LM Studio:** dalam bar sisi sebelah kanan, buka tab **Program**, klik **Install → Edit
mcp.json**, dan tambah:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Cline:** klik ikon **MCP Servers**, buka tab **Configure**, klik **Configure MCP
Servers**, dan tambah entri `mcpServers` yang sama seperti untuk LM Studio.

**Claude Desktop, secara manual** (sebagai ganti fail `.mcpb`): tambah entri `mcpServers` yang sama ke
`claude_desktop_config.json` (macOS: `~/Library/Application Support/Claude/`, Windows:
`%APPDATA%\Claude\`).

**Mana-mana aplikasi MCP lain** (Windsurf dan lain-lain): dokumentasinya sendiri menyatakan di mana ia
menyimpan pelayan MCP-nya. Kebanyakannya menerima entri yang sama: arahan `uvx`, argumen `fontes-mcp`.

Jika aplikasi tidak dapat mencari `uvx`, gunakan laluan penuhnya (pada macOS dan Linux, `which uvx`
memaparkannya).

## Anda memerlukan uv

Codex, Claude Code dan aplikasi lain memulakan Fontes dengan `uvx`, yang disertakan dengan **uv**, alat
kecil percuma daripada Astral. Untuk memasangnya, lihat
[panduan Astral](https://docs.astral.sh/uv/getting-started/installation/), atau jalankan:

- macOS atau Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Windows (PowerShell): `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

## Kunci

Sesetengah sumber memerlukan kunci percuma: lihat [KEYS.md](KEYS.md).

## Menyemak bahawa ia berfungsi

Dalam sembang baharu, tanya: *"Bidang kuasa manakah yang boleh dicari oleh Fontes?"* Aplikasi sepatutnya
menjawab dengan senarai negara. Jika tidak, tutup dan buka semula aplikasi sekali lagi.

## Pemasang satu klik (Mac dan Windows)

Pemasang menyediakan Fontes dalam semua aplikasi anda sekali gus: Claude Desktop, Codex, Claude Code,
Cursor, VS Code (GitHub Copilot), Windsurf, Gemini CLI, Zed, LM Studio dan Cline.

**Sebelum anda bermula:** tutup setiap aplikasi ini sepenuhnya. Ini paling penting untuk Claude Code:
semasa ia berjalan, ia menulis semula `~/.claude.json` dan boleh membatalkan perubahan yang dibuat oleh
pemasang. Jika anda tidak dapat menutup Claude Code, tambah Fontes kepadanya dengan `claude mcp add`
(lihat [Claude Code](#claude-code)).

**Mac**

1. Muat turun pemasang Mac (`Fontes-Installer-…-mac.zip`) daripada
   [keluaran terkini](https://github.com/ykarapazar/fontes/releases/latest) dan klik dua kali padanya
   untuk menyahzipnya.
2. Klik dua kali **Fontes Installer**. Jika Mac anda bertanya sama ada hendak membuka aplikasi yang
   dimuat turun dari internet, klik **Open**.
3. Pilih **Pasang** dan klik **OK**. Penyediaan mengambil masa kira-kira seminit.
4. Satu mesej menyenaraikan aplikasi yang telah disediakannya. Klik **Selesai**, kemudian buka semula
   aplikasi-aplikasi itu. Untuk menambah kunci percuma pilihan dahulu, klik **Tambah kunci**
   sebaliknya; lihat [Langkah kunci](#langkah-kunci).

**Windows**

1. Muat turun pemasang Windows (`Fontes-Setup-….exe`) daripada
   [keluaran terkini](https://github.com/ykarapazar/fontes/releases/latest) dan klik dua kali padanya.
   - Jika Windows memaparkan "Windows protected your PC": klik **More info**, kemudian **Run anyway**.
2. Klik **Pasang**. Tetingkap dibuka dan menyediakan Fontes.
3. Apabila ditanya sama ada hendak menghantar kiraan penggunaan tanpa nama, tekan Enter untuk tidak.
4. Ia bertanya sama ada hendak menambah kunci sekarang. Tekan Enter untuk melangkau; lihat
   [Langkah kunci](#langkah-kunci).
5. Apabila ia memaparkan **Selesai**, buka semula aplikasi AI anda. Jika salah satu masih berjalan, tutup
   sepenuhnya (juga daripada dulang sistem, berhampiran jam) dan buka semula.

Pada akhirnya, pemasang menyenaraikan aplikasi yang telah disediakannya.

### Aplikasi yang disediakannya

Ia menyediakan sesuatu aplikasi hanya jika folder tetapan aplikasi itu sudah ada pada komputer anda.
Claude Code disediakan hanya jika `~/.claude.json` wujud. Claude Desktop sentiasa disediakan. Setiap
aplikasi mendapat satu entri, `fontes`, dalam fail ini:

| Aplikasi | Fail (Mac dan Linux) | Fail (Windows) |
|---|---|---|
| Claude Desktop | `~/Library/Application Support/Claude/claude_desktop_config.json` (Linux: `~/.config/Claude/`) | `%APPDATA%\Claude\claude_desktop_config.json`, dan salinan tersendiri versi Microsoft Store |
| Codex | `~/.codex/config.toml` | `%USERPROFILE%\.codex\config.toml` |
| Claude Code | `~/.claude.json` | `%USERPROFILE%\.claude.json` |
| Cursor | `~/.cursor/mcp.json` | `%USERPROFILE%\.cursor\mcp.json` |
| VS Code (Copilot) | `~/.copilot/mcp-config.json` | `%USERPROFILE%\.copilot\mcp-config.json` |
| Windsurf | `~/.config/devin/mcp_config.json`, atau `~/.codeium/windsurf/mcp_config.json` pada versi lama | `%APPDATA%\devin\mcp_config.json`, atau `%USERPROFILE%\.codeium\windsurf\mcp_config.json` |
| Gemini CLI | `~/.gemini/settings.json` | `%USERPROFILE%\.gemini\settings.json` |
| Zed | `~/.config/zed/settings.json` | `%APPDATA%\Zed\settings.json` |
| LM Studio | `~/.lmstudio/mcp.json` | `%USERPROFILE%\.lmstudio\mcp.json` |
| Cline | `~/.cline/data/settings/cline_mcp_settings.json` | `%USERPROFILE%\.cline\data\settings\cline_mcp_settings.json` |

VS Code disediakan jika `~/.copilot` atau folder tetapan VS Code sendiri wujud.

Dua aplikasi memerlukan satu langkah lagi:

- **Windsurf:** selepas membukanya semula, tekan muat semula (refresh) dalam Cascade.
- **Cline di dalam sambungan VS Code yang lebih lama:** tambah Fontes secara manual (lihat [Cline](#aplikasi-lain)).

### Langkah kunci

Sejurus selepas pemasangan, pemasang menawarkan untuk menambah kunci percuma Perancis dan AS. Untuk
menambah atau menukarnya kemudian:

- **Mac:** buka semula **Fontes Installer** dan pilih **Tambah atau tukar kunci**.
- **Windows:** dalam menu Start, klik **Fontes** → **Tambah atau tukar kunci**.

Taipan disembunyikan. Kunci dimasukkan ke dalam setiap aplikasi yang sudah mempunyai Fontes. Tutup dan
buka semula aplikasi selepas itu. Di mana untuk mendapatkan kunci dan apa yang dibukanya: [KEYS.md](KEYS.md).

### Salinan sandaran, menjalankan semula dan membuang

Pemasang hanya mengubah entri `fontes`. Setiap tetapan dan ulasan lain kekal seperti sedia ada. Sebelum
ia mengubah sesuatu fail, ia menyimpan salinan di sebelahnya, bernama `<file>.fontes-backup-<date>`.
Salinan yang dibuat selepas anda menambah kunci mengandungi kunci tersebut: padamkan salinan yang tidak
lagi anda perlukan. Ia juga memasang uv. Menjalankannya semula adalah selamat: ia membaiki persediaan dan
tidak mengubah apa-apa yang lain.

Untuk membuang Fontes, buka **Fontes Installer** dan pilih **Buang** (Mac), atau nyahpasang **Fontes** dalam
Settings → Apps (Windows). Ia membuang entri `fontes`, termasuk kunci, daripada setiap aplikasi.
Tetapan anda yang lain dan salinan sandaran kekal.

## Kemas kini

- **Pemasang dan fail `.mcpb`:** anda tidak perlu melakukan apa-apa. Sekali sehari, apabila aplikasi
  bermula, Fontes menyemak versi yang lebih baharu di latar belakang dan menyediakannya; kali seterusnya
  aplikasi bermula, ia menggunakannya. Jika kemas kini tidak dapat dimuat turun atau tidak berfungsi,
  Fontes terus menggunakan versi yang berfungsi.
- **`uvx`:** Fontes memberitahu anda apabila versi yang lebih baharu tersedia, di bahagian atas senarai
  bidang kuasanya. Untuk sentiasa menjalankan versi terbaharu, gunakan `fontes-mcp@latest` sebagai ganti
  `fontes`.

Tiada maklumat tentang anda atau carian anda dihantar ke mana-mana untuk tujuan ini.

## Privasi

Fontes tidak menghantar apa-apa tentang anda atau carian anda secara lalai. Kiraan penggunaan adalah
opt-in, dan laporan pepijat dihantar hanya selepas anda melihat dan mengesahkannya. Butiran:
[PRIVACY.md](PRIVACY.md).

## Membuangnya

Buang entri `fontes` daripada tetapan MCP aplikasi anda (dalam Claude Code:
`claude mcp remove fontes`), kemudian tutup dan buka semula aplikasi.

## Perlu diketahui

Fontes membaca sumber awam, kebanyakannya laman web mahkamah dan kerajaan. Ia menandakan sumber yang tidak
rasmi dalam jawapannya. Sentiasa buka pautan sumber sebelum bergantung pada sesuatu keputusan atau
peruntukan.

Jika berlaku masalah, e-mel apa yang anda lakukan dan ralat yang anda lihat kepada fontesmcp@proton.me.

## Sebelum anda bergantung padanya

- Fontes ialah alat penyelidikan, bukan nasihat undang-undang. Menggunakannya tidak menjadikan sesiapa
  peguam anda.
- Ia disediakan "sebagaimana adanya", tanpa waranti, dan pengarangnya tidak bertanggungan terhadap cara ia
  digunakan, setakat yang dibenarkan oleh undang-undang. Syarat penuh terdapat dalam [lesen](../../../LICENSE)
  (Apache 2.0).

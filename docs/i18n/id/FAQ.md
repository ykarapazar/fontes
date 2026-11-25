> Ini adalah terjemahan berbantuan mesin. Versi bahasa Inggris adalah yang berlaku.

# Fontes: tanya jawab

## Apa itu Fontes?

Server MCP gratis dan bersumber terbuka (Apache 2.0). Fontes memungkinkan aplikasi apa pun yang menggunakan
Model Context Protocol (Claude, Codex, Cursor, VS Code, Gemini CLI, dan lainnya) mencari putusan pengadilan
dan peraturan perundang-undangan secara langsung di situs web pengadilan dan pemerintah di 120+ yurisdiksi
dan pengadilan internasional (124 adapter). Setiap hasil menyebutkan sumbernya dan menautkan ke dokumen aslinya.

## Apakah teksnya resmi?

Sebagian besar, tetapi tidak selalu.

- Sebagian besar sumber dikelola oleh pengadilan, kementerian, atau lembaran negara resmi.
- Beberapa teks konsolidasi diterbitkan oleh pemerintah tetapi secara tegas tidak resmi: hanya
  lembaran negara resmi yang autentik.
- Beberapa sumber sama sekali bukan situs pemerintah (misalnya LexiVox, LawPhil, Maqam,
  Wikisource).

Fontes menambahkan pemberitahuan "Sumber tidak resmi" pada setiap jawaban yang berasal dari salah satu
sumber tersebut. Sebelum Anda mengutip apa pun, periksa publikasi resminya. Tabel cakupan di
[README](README.md#cakupan) dan `list_jurisdictions` menyebutkan sumber untuk setiap yurisdiksi.

## Yurisdiksi mana yang dicakup, dan seberapa baik?

124 adapter: 108 negara anggota PBB, Hong Kong, Kosovo, Palestina, Taiwan, DIFC Courts, serta
11 pengadilan dan badan internasional (seperti Pengadilan Hak Asasi Manusia Eropa, Uni Eropa,
ICJ, dan WTO).

Cakupannya sangat berbeda-beda. Menurut aturan yang ketat (preseden pengadilan umum tertinggi, atau
konstitusi dan undang-undang, yang dijangkau sepenuhnya), 72 dari 124 dihitung tercakup.
[COVERAGE.md](COVERAGE.md) mencantumkan, untuk setiap yurisdiksi, apa yang dijangkau Fontes, apa yang tidak,
dan alasannya.

## Apakah saya memerlukan kunci API?

Untuk hampir semua yurisdiksi, tidak. Beberapa sumber memerlukan kunci gratis: lihat [KEYS.md](KEYS.md).

- **Prancis:** ya. Prancis nonaktif sampai Anda menetapkan `WLM_FR_PISTE_CLIENT_ID` dan
  `WLM_FR_PISTE_CLIENT_SECRET`. Keduanya berasal dari akun PISTE gratis (piste.gouv.fr) dengan aplikasi
  yang berlangganan Judilibre dan Légifrance.
- **Amerika Serikat:** opsional. Pencarian putusan pengadilan berfungsi tanpa kunci, tetapi kunci demo
  bersama hanya mengizinkan sekitar 10 pencarian per hari per alamat IP. Kunci api.data.gov gratis di
  `WLM_US_GOVINFO_KEY` menaikkan batas tersebut.

Tetapkan ini sebagai variabel lingkungan untuk server Fontes di pengaturan MCP aplikasi Anda. Penginstal
menanyakannya setelah instalasi, dan peluncur **Add or change keys** miliknya dapat mengubahnya
nanti.

Secara terpisah, beberapa sumber menyatakan dalam ketentuannya bahwa akses otomatis memerlukan izin
penerbit. Sumber tersebut ditandai OFF dan tetap nonaktif. Kunci tidak mengubah hal itu; hanya izin
penerbit yang dapat mengubahnya (lalu tetapkan `WLM_PERMITTED=<codes>`).

## Apa yang keluar dari komputer saya?

Pencarian Anda hanya dikirim ke sumber yang sedang dicari. Fontes tidak menyimpan basis data dan tidak
memerlukan akun.

Selain ke sumber-sumber tersebut, Fontes menanyakan kepada PyPI sekali sehari apakah ada versi yang lebih
baru (nonaktifkan dengan `FONTES_NO_UPDATE_CHECK=1`). Jumlah penggunaan nonaktif kecuali Anda
mengaktifkannya, dan laporan bug hanya dikirim setelah Anda melihat dan mengonfirmasinya. Aplikasi AI Anda
melihat percakapan Anda berdasarkan ketentuannya sendiri.

Rincian lengkap: [PRIVACY.md](PRIVACY.md).

## Apakah ini nasihat hukum?

Bukan. Fontes adalah alat riset. Fontes menemukan teks; Fontes tidak memberi tahu Anda apa artinya bagi
perkara Anda, dan menggunakannya tidak menciptakan hubungan advokat–klien dengan siapa pun. Aplikasi AI
dapat salah membaca teks, jadi baca putusan atau ketentuan secara lengkap sebelum Anda mengandalkannya.
Untuk nasihat, tanyakan kepada advokat yang berkualifikasi di tempat pertanyaan Anda timbul.

## Siapa yang memeliharanya? Apakah akan terus berfungsi?

Satu orang: Yüce Karapazar. Tidak ada perusahaan di balik Fontes, tidak ada kontrak dukungan, dan tidak ada
janji tingkat layanan. Tidak ada jasa hukum yang ditawarkan.

Sumber-sumber diperiksa sekali sehari dan hasilnya diterbitkan di
[halaman status](https://ykarapazar.github.io/fontes/status/?lang=id). Situs web pengadilan dan pemerintah
berubah tanpa pemberitahuan, sehingga suatu sumber dapat rusak kapan saja. Tidak ada jaminan bahwa sumber
mana pun, atau Fontes itu sendiri, akan terus berfungsi. Fontes disediakan "sebagaimana adanya", tanpa
jaminan (bagian 7 dan 8 [LICENSE](../../../LICENSE)).

## Teks keliru, kedaluwarsa, atau sumber rusak. Bagaimana cara melaporkannya?

- Buka issue dengan formulir "Broken or wrong source":
  <https://github.com/ykarapazar/fontes/issues/new/choose>. Sebutkan yurisdiksinya, apa yang Anda
  tanyakan, apa yang Anda dapatkan, dan halaman resmi yang menunjukkan teks yang benar.
- Atau minta aplikasi AI Anda untuk "melaporkan bug Fontes" (atau jalankan `fontes report-bug`). Anda
  melihat laporannya sebelum apa pun dikirim.
- Atau kirim email ke fontesmcp@proton.me.

Jangan menyertakan rincian klien atau fakta rahasia dalam laporan.

**Jika Anda mengelola salah satu sumber** dan ada yang keliru (ketentuan Anda, robots.txt Anda, batas
permintaan Anda), kirim email ke fontesmcp@proton.me. Sumber tersebut akan diperbaiki atau dinonaktifkan.

## Apa bedanya Fontes dengan alat riset hukum yang di-host?

- **Fontes berjalan di komputer Anda.** Tidak ada server Fontes dan tidak ada akun. Itu juga berarti Fontes
  hanya berfungsi di aplikasi yang dapat menjalankan server MCP lokal (Claude Desktop, Codex, Cursor,
  VS Code, dan sejenisnya), bukan di aplikasi khusus web yang hanya menerima konektor yang di-host.
- **Fontes tidak memiliki basis data.** Setiap pencarian dilakukan secara langsung ke situs web atau API
  milik penerbit itu sendiri, sehingga hasilnya semutakhir sumbernya, dan kualitas pencariannya adalah
  kualitas sumber itu sendiri. Tidak ada pencarian semantik atas indeks yang dikurasi.
- **Fontes tidak menetapkan batas penggunaan.** Fontes tidak memiliki batas panggilan bulanan. Fontes
  memberi jeda pada permintaannya ke setiap situs web, dan beberapa sumber membatasi seberapa cepat atau
  seberapa sering sumber tersebut dapat ditanyai.
- **Fontes bersumber terbuka.** Anda dapat membaca setiap adapter dan melihat dengan tepat dari mana setiap
  teks berasal.
- **Tidak ada vendor di baliknya.** Tidak ada kontrak, layanan dukungan, atau janji uptime (lihat "Siapa
  yang memeliharanya?").

## Aplikasi dan sistem apa saja yang didukung?

Aplikasi MCP apa pun yang dapat menjalankan server lokal (stdio), misalnya Claude Desktop, Claude Code,
Codex, Cursor, VS Code (GitHub Copilot), Gemini CLI, Windsurf, Zed, LM Studio, dan Cline. Fontes berjalan
di macOS, Windows, dan Linux, di mana pun uv berjalan (Python 3.13+). Di Mac atau PC Windows, penginstal sekali klik
menyiapkan Claude Desktop, Codex, Claude Code, Cursor, VS Code, Windsurf,
Gemini CLI, Zed, LM Studio, dan Cline sekaligus. Langkah untuk setiap aplikasi: [INSTALL.md](INSTALL.md).

## Bisakah saya menyumbangkan kode?

Tidak untuk saat ini. Issue, laporan sumber, dan permintaan yurisdiksi dipersilakan. Lihat
[CONTRIBUTING.md](../../../CONTRIBUTING.md).

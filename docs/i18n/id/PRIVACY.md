> Ini adalah terjemahan berbantuan mesin. Versi bahasa Inggris adalah yang berlaku.

# Pemberitahuan privasi Fontes

Fontes berjalan di komputer Anda. Pencarian Anda dan dokumen yang Anda buka tetap berada di antara
komputer Anda, sumber yang Anda cari (yang resmi, ditambah CourtListener dan Lexifina di tempat Anda menggunakannya, lihat di bawah), dan aplikasi AI yang Anda gunakan (berdasarkan ketentuan
aplikasi itu sendiri). Fontes sendiri **tidak mengirim apa pun secara bawaan** kepada pengembang Fontes.

## Apa yang dapat keluar dari komputer Anda, dan kapan

**1. Pemeriksaan pembaruan (aktif secara bawaan).** Sekali sehari Fontes menanyakan kepada PyPI, indeks
paket Python publik, versi mana yang terbaru. Permintaan tersebut tidak memuat apa pun tentang Anda atau
pekerjaan Anda; PyPI melihat alamat IP Anda, seperti pada unduhan apa pun. Untuk menonaktifkannya, tetapkan
`FONTES_NO_UPDATE_CHECK=1` (pemberitahuan di dalam aplikasi) dan `FONTES_NO_AUTO_UPDATE=1` (pembaruan
otomatis dari penginstal).

**2. Jumlah penggunaan (nonaktif kecuali Anda mengaktifkannya).** Jika Anda memilih ikut serta (opt-in),
sekali sehari Fontes mengirim:

- versi Fontes dan keluarga sistem operasi Anda (macOS, Windows, Linux);
- per hari, berapa kali setiap alat digunakan untuk setiap kode yurisdiksi, misalnya
  "2026-11-10, nl, search_caselaw, 12".

Itulah seluruh isi pesannya. Pesan itu tidak pernah memuat pencarian Anda, id dokumen atau perkara, teks
dokumen, nama Anda, akun, atau id apa pun untuk Anda atau komputer Anda. Jumlah tersebut menunggu di komputer
Anda (di folder cache Fontes, `stats.json`) sampai dikirim; jika pengiriman gagal, jumlah tersebut menunggu
sampai hari berikutnya.

- **Ikut serta (opt-in)**: jawab "y" ketika penginstal bertanya, atau tetapkan `FONTES_STATS=1` untuk server Fontes.
- **Berhenti (opt-out)**: jalankan penginstal lagi dan tekan Enter pada pertanyaan itu, atau hapus
  `FONTES_STATS`. Menghapus `stats.json` membuang apa pun yang belum dikirim.

**3. Laporan bug (hanya ketika Anda mengirimnya).** Ketika Anda memintanya (`fontes report-bug`, atau
meminta aplikasi AI Anda melaporkan bug Fontes), Fontes terlebih dahulu menampilkan laporan lengkapnya
kepada Anda dan hanya mengirimnya jika Anda mengonfirmasi. Laporan memuat versi Fontes, keluarga sistem
operasi Anda, kode yurisdiksi, nama alat, dan pesan galat dari panggilan alat terakhir yang gagal (dengan
kata pencarian dan id Anda dihapus), serta catatan jika Anda menulisnya. Jangan memasukkan rincian klien
ke dalam catatan. Untuk mendukung hal ini, Fontes menyimpan galat terakhir di komputer Anda
(`last-error.json` di folder cache-nya, diganti setiap kali); galat ini tidak pernah dikirim dengan
sendirinya.

**4. Lexifina (aktif secara bawaan).** `get_law_on_date`, `get_law_history`, 91 negara, dan undang-undang India yang dibaca melalui catatan hukum Lexifina dikirim ke Lexifina, baik selain maupun sebagai pengganti situs resmi. Kata pencarian, kutipan dan tanggal Anda dikirim ke server gratis Lexifina, `global-law.lexifina.com`, yang dijalankan oleh Lexifina, bukan oleh pengembang Fontes. Lexifina mendokumentasikan bahwa server-nya mencatat alat mana yang dipanggil dan berapa lama waktu yang diperlukan, tidak pernah apa yang ditanyakan; Fontes tidak dapat memeriksanya, dan ketentuan Lexifina sendiri berlaku. Lexifina melihat alamat IP Anda, seperti halnya server web mana pun. Untuk mematikan Lexifina sepenuhnya, tetapkan `WLM_LEXIFINA=0`; kedua alat dan negara tersebut kemudian berhenti bekerja dan tidak ada yang dikirim ke sana.

## Ke mana data dikirim dan berapa lama disimpan

Jumlah penggunaan dan laporan bug dikirim ke server kecil yang dijalankan oleh pengembang Fontes
(`relay.kinetra.fit`). Server ini tidak menyimpan alamat IP: alamat IP hanya digunakan di memori, sebentar,
untuk mencegah banjir permintaan, dan server web tidak menyimpan log akses untuk layanan ini. Jumlah
penggunaan dijumlahkan menjadi total harian; kiriman satu per satu tidak disimpan. Total disimpan paling
lama 2 tahun, laporan bug paling lama 1 tahun, lalu dihapus. Tidak ada yang dijual atau dibagikan.

Jika server itu tidak dapat dijangkau, tidak ada yang dikirim: jumlah penggunaan tetap berada di komputer
Anda dan laporan bug mengarahkan Anda ke issue tracker sebagai gantinya.

## Siapa yang bertanggung jawab, dan atas dasar apa

Pengendali data untuk jumlah penggunaan dan laporan bug adalah Yüce Karapazar, pengembang Fontes.
Kontak: fontesmcp@proton.me.

Dasar hukumnya adalah persetujuan Anda (Pasal 6(1)(a) UK GDPR dan EU GDPR). Jumlah penggunaan hanya dikirim
jika Anda memilih ikut serta, dan laporan bug hanya setelah Anda mengonfirmasinya. Anda dapat menarik
persetujuan kapan saja dengan berhenti ikut serta seperti dijelaskan di atas; hal ini tidak memengaruhi apa
yang telah dikirim sebelumnya.

## Kontak

Pertanyaan atau permintaan: kirim email ke fontesmcp@proton.me, atau buka issue di
<https://github.com/ykarapazar/fontes/issues>.

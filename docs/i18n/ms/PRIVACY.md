> Ini ialah terjemahan dengan bantuan mesin. Versi bahasa Inggeris adalah versi yang sahih.

# Notis privasi Fontes

Fontes berjalan pada komputer anda. Carian anda dan dokumen yang anda buka kekal antara komputer anda,
sumber rasmi yang anda cari, dan aplikasi AI yang anda gunakan (di bawah syarat aplikasi itu sendiri).
Fontes sendiri menghantar **tiada apa-apa secara lalai** kepada pembangun Fontes.

## Apa yang boleh keluar dari komputer anda, dan bila

**1. Semakan kemas kini (hidup secara lalai).** Sekali sehari Fontes bertanya kepada PyPI, indeks pakej
Python awam, versi manakah yang terbaharu. Permintaan itu tidak membawa apa-apa tentang anda atau kerja
anda; PyPI melihat alamat IP anda, seperti mana-mana muat turun. Untuk mematikannya, tetapkan
`FONTES_NO_UPDATE_CHECK=1` (notis dalam aplikasi) dan `FONTES_NO_AUTO_UPDATE=1` (kemas kini automatik
pemasang).

**2. Kiraan penggunaan (dimatikan melainkan anda menghidupkannya).** Jika anda memilih untuk menyertai
(opt-in), sekali sehari Fontes menghantar:

- versi Fontes dan keluarga sistem pengendalian anda (macOS, Windows, Linux);
- bagi setiap hari, berapa kali setiap alat digunakan bagi setiap kod bidang kuasa, contohnya
  "2026-11-10, nl, search_caselaw, 12".

Itulah keseluruhan mesej. Ia tidak sekali-kali mengandungi carian anda, id dokumen atau kes, teks dokumen,
nama anda, akaun, atau sebarang id bagi anda atau komputer anda. Kiraan menunggu pada komputer anda (dalam
folder cache Fontes, `stats.json`) sehingga ia dihantar; jika penghantaran gagal, kiraan menunggu hari
berikutnya.

- **Sertai (opt-in)**: jawab "y" apabila pemasang bertanya, atau tetapkan `FONTES_STATS=1` untuk pelayan Fontes.
- **Tarik diri (opt-out)**: jalankan pemasang sekali lagi dan tekan Enter pada soalan itu, atau buang
  `FONTES_STATS`. Memadamkan `stats.json` membuang apa-apa yang belum dihantar.

**3. Laporan pepijat (hanya apabila anda menghantarnya).** Apabila anda memintanya (`fontes report-bug`,
atau meminta aplikasi AI anda melaporkan pepijat Fontes), Fontes menunjukkan laporan penuh kepada anda
terlebih dahulu dan menghantarnya hanya jika anda mengesahkannya. Ia mengandungi versi Fontes, keluarga
sistem pengendalian anda, kod bidang kuasa, nama alat dan mesej ralat bagi panggilan alat terakhir yang
gagal (dengan kata carian dan id anda dibuang), dan nota jika anda menulisnya. Jangan masukkan butiran
anak guam dalam nota. Untuk menyokong ini, Fontes menyimpan ralat terakhir pada komputer anda
(`last-error.json` dalam folder cachenya, diganti setiap kali); ia tidak sekali-kali dihantar dengan
sendirinya.

## Ke mana ia pergi dan berapa lama ia disimpan

Kiraan penggunaan dan laporan pepijat pergi ke pelayan kecil yang dikendalikan oleh pembangun Fontes
(`relay.kinetra.fit`). Ia tidak menyimpan alamat IP: alamat IP digunakan hanya dalam memori, sebentar,
untuk menghentikan banjir permintaan, dan pelayan web tidak menyimpan log akses untuknya. Kiraan dicampur
ke dalam jumlah harian; penghantaran individu tidak disimpan. Jumlah disimpan sehingga 2 tahun, laporan
pepijat sehingga 1 tahun, kemudian dipadamkan. Tiada apa-apa dijual atau dikongsi.

Jika pelayan itu tidak dapat dihubungi, tiada apa-apa dihantar: kiraan kekal pada komputer anda dan laporan
pepijat menunjukkan anda ke penjejak isu (issue tracker) sebagai gantinya.

## Siapa yang bertanggungjawab, dan atas asas apa

Pengawal data bagi kiraan penggunaan dan laporan pepijat ialah Yüce Karapazar, pembangun Fontes.
Hubungi: fontesmcp@proton.me.

Asas sah ialah persetujuan anda (Perkara 6(1)(a) UK GDPR dan EU GDPR). Kiraan penggunaan dihantar hanya
jika anda memilih untuk menyertai, dan laporan pepijat hanya selepas anda mengesahkannya. Anda boleh
menarik balik persetujuan pada bila-bila masa dengan menarik diri seperti yang diterangkan di atas; ini
tidak menjejaskan apa yang telah dihantar sebelum itu.

## Hubungi

Soalan atau permintaan: e-mel fontesmcp@proton.me, atau buka isu di
<https://github.com/ykarapazar/fontes/issues>.

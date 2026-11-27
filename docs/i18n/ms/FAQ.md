> Ini ialah terjemahan dengan bantuan mesin. Versi bahasa Inggeris adalah versi yang sahih.

# Fontes: soalan dan jawapan

## Apakah Fontes?

Pelayan MCP percuma dan sumber terbuka (Apache 2.0). Ia membolehkan mana-mana aplikasi yang menggunakan
Model Context Protocol (Claude, Codex, Cursor, VS Code, Gemini CLI dan lain-lain) mencari keputusan mahkamah
dan perundangan secara langsung di laman web mahkamah dan kerajaan di 125 bidang kuasa dan mahkamah
antarabangsa, serta 91 lagi negara melalui rekod Lexifina (lihat di bawah). Setiap hasil menamakan sumbernya
dan memaut kepada dokumen asal.

## Adakah teks-teks itu rasmi?

Kebanyakannya, tetapi tidak selalu.

- Kebanyakan sumber dikendalikan oleh mahkamah, kementerian atau warta rasmi.
- Sesetengah teks yang disatukan diterbitkan oleh kerajaan tetapi dinyatakan dengan jelas sebagai tidak
  rasmi: hanya warta rasmi yang sahih.
- Beberapa sumber langsung bukan laman kerajaan (contohnya LexiVox, LawPhil, Maqam, Wikisource).

Fontes menambah notis "Sumber tidak rasmi" pada setiap jawapan yang datang daripada salah satu sumber ini.
Sebelum anda memetik apa-apa, semak penerbitan rasmi. Jadual liputan dalam [README](README.md#liputan) dan
`list_jurisdictions` menamakan sumber bagi setiap bidang kuasa.

## Bidang kuasa manakah yang diliputinya, dan sejauh mana?

125 penyesuai: 108 negara anggota PBB, Hong Kong, Kosovo, Palestin, Taiwan, Mahkamah DIFC, mahkamah negeri AS dan 11 mahkamah dan badan antarabangsa (seperti Mahkamah Hak Asasi Manusia Eropah, EU, ICJ dan WTO).

Liputan sangat berbeza. Di bawah peraturan yang ketat (duluan mahkamah umum tertinggi, atau perlembagaan
dan akta utama, dicapai sepenuhnya), 72 daripada 125 dikira sebagai diliputi. [COVERAGE.md](COVERAGE.md)
menyenaraikan, bagi setiap bidang kuasa, apa yang dicapai oleh Fontes, apa yang tidak, dan mengapa.

## Adakah saya memerlukan kunci API?

Bagi hampir setiap bidang kuasa, tidak. Sesetengah sumber memerlukan kunci percuma: lihat [KEYS.md](KEYS.md).

- **Perancis:** ya. Perancis dimatikan sehingga anda menetapkan `WLM_FR_PISTE_CLIENT_ID` dan
  `WLM_FR_PISTE_CLIENT_SECRET`. Ini datang daripada akaun PISTE percuma (piste.gouv.fr) dengan aplikasi
  yang melanggan Judilibre dan Légifrance.
- **Amerika Syarikat:** pilihan. Carian undang-undang kes berfungsi tanpa kunci, tetapi kunci demo yang
  dikongsi hanya membenarkan kira-kira 10 carian sehari bagi setiap alamat IP. Kunci api.data.gov percuma
  dalam `WLM_US_GOVINFO_KEY` meningkatkannya.
- **Mahkamah negeri AS:** ya. Undang-undang kes negeri (`us-states`) dimatikan sehingga anda menetapkan `WLM_US_COURTLISTENER_KEY` kepada token API CourtListener percuma anda sendiri. CourtListener dikendalikan oleh Free Law Project, sebuah organisasi bukan untung; ia bukan sumber rasmi, dan setiap jawapan menyatakannya.

Tetapkan ini sebagai pemboleh ubah persekitaran untuk pelayan Fontes dalam tetapan MCP aplikasi anda.
Pemasang memintanya selepas pemasangan, dan pelancar **Add or change
keys** menukarnya kemudian.

Secara berasingan, beberapa sumber menyatakan dalam syarat penggunaannya bahawa akses automatik memerlukan
kebenaran penerbit. Sumber ini ditandakan OFF dan kekal dimatikan. Kunci tidak mengubahnya; hanya kebenaran
penerbit yang mengubahnya (kemudian tetapkan `WLM_PERMITTED=<codes>`).

## Dari manakah versi lama dan negara tambahan itu datang?

Daripada [Lexifina](https://github.com/lexifina/global-law), yang menyimpan undang-undang kira-kira 200 negara
sebagai sejarah git: setiap perubahan ialah commit yang bertarikh pada hari ia berkuat kuasa. Fontes membacanya
melalui pelayan MCP hos percuma Lexifina. Dua alat menggunakannya: `get_law_on_date` (peruntukan seperti yang
berkuat kuasa pada tarikh, juga pada masa lampau, beserta undang-undang yang terakhir mengubahnya) dan
`get_law_history` (setiap undang-undang yang mengubah sesuatu peruntukan, atau perubahan perkata antara dua tarikh).
Fontes juga membaca 91 lagi negara dan wilayah dengan cara ini, untuk perundangan sahaja (contohnya Afrika Selatan,
Kenya, Mexico, New Zealand, Rusia, Korea Selatan, Belgium, Lithuania, Ukraine, Malaysia, Thailand dan Arab Saudi).
Ia berasingan daripada 125 penyesuai dengan liputan rasmi yang hidup, dan liputan bagi setiap negara sangat
berbeza (rekod nasional Kenya memuatkan 9 akta). Akta India juga datang daripada rekod Lexifina, kerana syarat
India Code melarang akses automatik; keputusan Mahkamah Agung India adalah hidup.

Lexifina bukan penerbit rasmi, dan rekodnya tidak hidup: Lexifina menyemak setiap negara dari semasa ke semasa,
dan laporannya sendiri pada 2026-11-26 mengira 338 daripada 383 badan undang-undang nasional sebagai tidak disemak
dalam 7 hari terakhir. Setiap jawapan menamakan Lexifina sebagai sumber, memaut halaman penerbit rasmi dan
menyatakan sejauh mana rekod itu merangkumi.

Lexifina berpendapat bahawa teks undang-undang rasmi tidak dilindungi hak cipta, maka di sesetengah negara ia
menyalin laman yang syarat atau robots.txt-nya Fontes sendiri patuhi. Fontes tetap mematuhi robots.txt dan syarat
bagi apa yang diambilnya sendiri; apa yang datang melalui Lexifina mengikut pertimbangan Lexifina sendiri,
direkodkan bagi setiap negara dalam repositorinya. Beberapa sumber mengehadkan penggunaan (penerbit Kenya:
CC BY-NC). Kata carian, petikan dan tarikh anda dihantar ke pelayan Lexifina untuk ini. Tetapkan
`WLM_LEXIFINA=0` untuk mematikannya. Pelayan percuma membenarkan 60 panggilan seminit dan 10,000 sehari bagi
setiap alamat internet; tiada kunci atau akaun. Fontes tidak berkaitan dengan Lexifina.

## Apa yang keluar dari komputer saya?

Carian anda hanya pergi ke sumber yang sedang dicari (bagi alat dan negara Lexifina, itu pelayan Lexifina).
Fontes tidak menyimpan pangkalan data dan tidak memerlukan akaun.

Selain sumber-sumber itu, Fontes bertanya kepada PyPI sekali sehari sama ada versi yang lebih baharu wujud
(matikannya dengan `FONTES_NO_UPDATE_CHECK=1`). Kiraan penggunaan dimatikan melainkan anda menghidupkannya,
dan laporan pepijat dihantar hanya selepas anda melihat dan mengesahkannya. Aplikasi AI anda melihat
perbualan anda di bawah syaratnya sendiri.

Butiran penuh: [PRIVACY.md](PRIVACY.md).

## Adakah ini nasihat undang-undang?

Tidak. Fontes ialah alat penyelidikan. Ia mencari teks; ia tidak memberitahu anda apa maksud teks itu bagi
kes anda, dan menggunakannya tidak mewujudkan hubungan peguam–anak guam dengan sesiapa pun. Aplikasi AI
boleh tersilap baca teks, jadi baca keputusan atau peruntukan itu sepenuhnya sebelum anda bergantung
padanya. Untuk nasihat, tanya peguam yang berkelayakan di tempat soalan anda timbul.

## Siapa yang menyelenggarakannya? Adakah ia akan terus berfungsi?

Seorang sahaja: Yüce Karapazar. Tiada syarikat di sebalik Fontes, tiada kontrak sokongan dan tiada janji
tahap perkhidmatan. Tiada perkhidmatan guaman ditawarkan.

Sumber-sumber disemak sekali sehari dan hasilnya diterbitkan pada
[halaman status](https://ykarapazar.github.io/fontes/status/?lang=ms). Laman web mahkamah dan kerajaan
berubah tanpa notis, jadi sesuatu sumber boleh rosak pada bila-bila masa. Tiada jaminan bahawa mana-mana
sumber, atau Fontes sendiri, akan terus berfungsi. Fontes disediakan "sebagaimana adanya", tanpa waranti
(seksyen 7 dan 8 [LICENSE](../../../LICENSE)).

## Sesuatu teks salah, lapuk atau sesuatu sumber rosak. Bagaimana saya melaporkannya?

- Buka isu dengan borang "Broken or wrong source":
  <https://github.com/ykarapazar/fontes/issues/new/choose>. Nyatakan bidang kuasa yang mana, apa yang
  anda tanya, apa yang anda dapat, dan halaman rasmi yang menunjukkan teks yang betul.
- Atau minta aplikasi AI anda untuk "laporkan pepijat Fontes" (atau jalankan `fontes report-bug`). Anda
  melihat laporan itu sebelum apa-apa dihantar.
- Atau e-mel fontesmcp@proton.me.

Jangan masukkan butiran anak guam atau fakta sulit dalam laporan.

**Jika anda mengendalikan salah satu sumber** dan ada sesuatu yang salah (syarat penggunaan anda,
robots.txt anda, had kadar anda), e-mel fontesmcp@proton.me. Sumber itu akan dibetulkan atau dimatikan.

## Apakah perbezaan Fontes dengan alat penyelidikan undang-undang yang dihoskan?

- **Ia berjalan pada komputer anda.** Tiada pelayan Fontes dan tiada akaun. Ini juga bermakna ia hanya
  berfungsi dalam aplikasi yang boleh memulakan pelayan MCP setempat (Claude Desktop, Codex, Cursor,
  VS Code dan seumpamanya), bukan dalam aplikasi web sahaja yang hanya menerima penyambung yang dihoskan.
- **Ia tiada pangkalan data.** Setiap carian pergi secara langsung ke laman web atau API penerbit itu
  sendiri, jadi hasilnya sama terkini seperti sumbernya, dan kualiti carian ialah kualiti sumber itu
  sendiri. Tiada carian semantik atas indeks yang dikurasi.
- **Ia tidak menetapkan had penggunaan.** Fontes tiada had panggilan bulanan. Ia menjarakkan
  permintaannya kepada setiap laman web, dan sesetengah sumber mengehadkan seberapa pantas atau seberapa
  kerap ia boleh ditanya.
- **Ia sumber terbuka.** Anda boleh membaca setiap penyesuai dan melihat dengan tepat dari mana setiap
  teks datang.
- **Tiada vendor di sebaliknya.** Tiada kontrak, meja sokongan atau janji masa operasi (lihat "Siapa yang
  menyelenggarakannya?").

## Aplikasi dan sistem manakah yang disokong?

Mana-mana aplikasi MCP yang boleh menjalankan pelayan setempat (stdio), contohnya Claude Desktop,
Claude Code, Codex, Cursor, VS Code (GitHub Copilot), Gemini CLI, Windsurf, Zed, LM Studio dan Cline.
Fontes berjalan pada macOS, Windows dan Linux, di mana-mana sahaja uv berjalan (Python 3.13+). Pada Mac atau PC Windows, pemasang satu klik
menyediakan Claude Desktop, Codex, Claude Code, Cursor, VS Code, Windsurf, Gemini CLI, Zed, LM Studio
dan Cline sekali gus. Langkah untuk setiap aplikasi: [INSTALL.md](INSTALL.md).

## Bolehkah saya menyumbang kod?

Tidak buat masa ini. Isu, laporan sumber dan permintaan bidang kuasa dialu-alukan. Lihat
[CONTRIBUTING.md](../../../CONTRIBUTING.md).

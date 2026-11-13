> Bu terjime maşynyň kömegi bilen taýýarlandy. Iňlis dilindäki görnüşi esasy hasaplanýar.

# Fontes gizlinlik barada bildiriş

Fontes siziň kompýuteriňizde işleýär. Gözlegleriňiz we açýan resminamalaryňyz
kompýuteriňiz, gözleýän resmi çeşmeleriňiz we ulanýan AI programmaňyz (şol programmanyň öz
şertlerine laýyklykda) arasynda galýar. Fontes programmasynyň özi adaty ýagdaýda Fontes işläp
düzüjilerine **hiç zat ibermeýär**.

## Kompýuteriňizden näme we haçan çykyp biler

**1. Täzelenmäni barlamak (adaty ýagdaýda açyk).** Günde bir gezek Fontes açyk Python bukjalar
indeksi bolan PyPI saýtyndan iň täze wersiýanyň haýsydygyny soraýar. Haýyşda siz ýa-da işiňiz
barada hiç zat ýok; islendik ýüklemedäki ýaly, PyPI IP salgyňyzy görýär. Ony öçürmek üçin
`FONTES_NO_UPDATE_CHECK=1` (programmanyň içindäki duýduryş) we `FONTES_NO_AUTO_UPDATE=1`
(gurnaýjy programmanyň awtomatik täzelenmeleri) goýuň.

**2. Ulanyş sanlary (siz açmasaňyz öçük).** Eger razylyk berseňiz, Fontes günde bir gezek
şulary iberýär:

- Fontes wersiýasy we operasion ulgamyňyzyň maşgalasy (macOS, Windows, Linux);
- her gün üçin her guralyň her ýurisdiksiýa kody boýunça näçe gezek ulanylandygy, meselem,
  “2026-11-10, nl, search_caselaw, 12”.

Habar şundan ybarat. Onda hiç haçan gözlegleriňiz, resminama ýa-da iş identifikatorlary,
resminamanyň teksti, adyňyz, hasap ýazgysy ýa-da siziň ýa-da kompýuteriňiziň hiç hili
identifikatory bolmaýar. Sanlar iberilýänçä kompýuteriňizde (Fontes keş bukjasyndaky
`stats.json` faýlynda) garaşýar; iberip bolmasa, indiki güne garaşýar.

- **Razylyk bermek**: gurnaýjy programma soranda “y” diýip jogap beriň ýa-da Fontes serweri
  üçin `FONTES_STATS=1` goýuň.
- **Ret etmek**: gurnaýjy programmany täzeden işe giriziň we şol soragda Enter düwmesine basyň
  ýa-da `FONTES_STATS` aýyryň. `stats.json` pozmak entek iberilmedik ähli zady ýatyrýar.

**3. Ýalňyşlyk hasabatlary (diňe siz iberseňiz).** Siz ony soranyňyzda (`fontes report-bug`
ýa-da AI programmaňyzdan Fontes ýalňyşlygy barada habar bermegi haýyş etseňiz), Fontes ilki
size doly hasabaty görkezýär we ony diňe siz tassyklasaňyz iberýär. Onda Fontes wersiýasy,
operasion ulgamyňyzyň maşgalasy, soňky şowsuz gural çagyryşynyň ýurisdiksiýa kody, guralyň ady
we ýalňyşlyk habary (gözleg sözleriňiz we identifikatorlar aýrylan görnüşde), hem-de ýazan
bolsaňyz, bellik bolýar. Bellige müşderileriňiz barada maglumat ýazmaň. Muny üpjün etmek
üçin Fontes soňky ýalňyşlygy kompýuteriňizde saklaýar (keş bukjasyndaky `last-error.json`, her
gezek çalşylýar); ol hiç haçan özbaşdak iberilmeýär.

## Maglumatlar nirä gidýär we näçe wagt saklanýar

Ulanyş sanlary we ýalňyşlyk hasabatlary Fontes işläp düzüjisiniň dolandyrýan kiçi serwerine
(`relay.kinetra.fit`) gidýär. Ol IP salgylaryny saklamaýar: olar diňe ýatda, gysga wagtlap,
haýyş akymlaryny saklamak üçin ulanylýar we web serwer munuň üçin giriş ýazgylaryny saklamaýar.
Sanlar gündelik jemlere goşulýar; aýry-aýry iberilen maglumatlar saklanmaýar. Jemler 2 ýyla
çenli, ýalňyşlyk hasabatlary 1 ýyla çenli saklanýar, soňra pozulýar. Hiç zat satylmaýar we hiç
kime berilmeýär.

Eger bu serwere baryp bolmasa, hiç zat iberilmeýär: sanlar kompýuteriňizde galýar, ýalňyşlyk
hasabatlary bolsa sizi onuň ýerine meseleleri yzarlaýjy ulgama (issue tracker) gönükdirýär.

## Kim jogapkär we haýsy esasda

Ulanyş sanlary we ýalňyşlyk hasabatlary boýunça maglumatlara gözegçilik edýän tarap Fontes
programmasynyň işläp düzüjisi Yüce Karapazar. Habarlaşmak üçin: fontesmcp@proton.me.

Kanuny esas siziň razylygyňyzdyr (UK GDPR-iň we EU GDPR-iň 6(1)(a) maddasy). Ulanyş sanlary
diňe siz razylyk berseňiz, ýalňyşlyk hasabaty bolsa diňe siz ony tassyklanyňyzdan soň iberilýär.
Ýokarda beýan edilişi ýaly ret edip, razylygyňyzy islendik wagt yzyna alyp bilersiňiz; bu öň
iberilen zatlara täsir etmeýär.

## Habarlaşmak

Soraglar ýa-da haýyşlar: fontesmcp@proton.me salgysyna ýazyň ýa-da
<https://github.com/ykarapazar/fontes/issues> salgysynda issue açyň.

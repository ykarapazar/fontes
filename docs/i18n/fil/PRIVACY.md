> Ito ay salin na ginawa sa tulong ng makina. Ang bersyong Ingles ang may bisa.

# Abiso sa privacy ng Fontes

Tumatakbo ang Fontes sa iyong computer. Ang iyong mga paghahanap at ang mga dokumentong binubuksan mo ay
nananatili sa pagitan ng iyong computer, ng mga sanggunian na hinahanapan mo (mga opisyal, pati ang CourtListener at Lexifina kung saan mo ginagamit ang mga ito, tingnan sa ibaba), at ng AI app na
ginagamit mo (sa ilalim ng sariling mga tuntunin ng app na iyon). Ang Fontes mismo ay **walang ipinapadala
bilang default** sa mga developer ng Fontes.

## Ano ang maaaring lumabas sa iyong computer, at kailan

**1. Pagtingin sa update (naka-on bilang default).** Minsan sa isang araw, tinatanong ng Fontes ang PyPI, ang
pampublikong index ng mga Python package, kung aling bersyon ang pinakabago. Walang dalang anumang
impormasyon tungkol sa iyo o sa iyong trabaho ang request; nakikita ng PyPI ang iyong IP address, tulad ng sa
anumang download. Para i-off ito, itakda ang `FONTES_NO_UPDATE_CHECK=1` (ang abiso sa app) at
`FONTES_NO_AUTO_UPDATE=1` (ang awtomatikong update ng installer).

**2. Bilang ng paggamit (naka-off maliban kung i-on mo).** Kung mag-opt in ka, minsan sa isang araw
nagpapadala ang Fontes ng:

- ang bersyon ng Fontes at ang pamilya ng iyong operating system (macOS, Windows, Linux);
- para sa bawat araw, kung ilang beses ginamit ang bawat tool para sa bawat code ng hurisdiksyon, halimbawa
  "2026-11-10, nl, search_caselaw, 12".

Iyan na ang buong mensahe. Hindi ito kailanman naglalaman ng iyong mga paghahanap, ng mga id ng dokumento o
kaso, ng teksto ng dokumento, ng iyong pangalan, account, o anumang id para sa iyo o sa iyong computer.
Naghihintay ang mga bilang sa iyong computer (sa cache folder ng Fontes, `stats.json`) hanggang maipadala ang
mga ito; kung pumalya ang pagpapadala, naghihintay ang mga ito sa susunod na araw.

- **Opt in**: sumagot ng "y" kapag nagtanong ang installer, o itakda ang `FONTES_STATS=1` para sa Fontes server.
- **Opt out**: patakbuhin muli ang installer at pindutin ang Enter sa tanong, o alisin ang `FONTES_STATS`.
  Ang pagbura sa `stats.json` ay nagtatapon ng anumang hindi pa naipapadala.

**3. Mga bug report (kapag ipinadala mo lamang).** Kapag hiniling mo ito (`fontes report-bug`, o hilingin sa
iyong AI app na mag-ulat ng bug sa Fontes), ipinapakita muna sa iyo ng Fontes ang buong report at ipinapadala
lamang ito kung kumpirmahin mo. Naglalaman ito ng bersyon ng Fontes, ng pamilya ng iyong operating system,
ng code ng hurisdiksyon, ng pangalan ng tool at ng error message ng huling pumalyang tawag sa tool (na inalis
ang iyong mga salitang hinanap at mga id), at ng isang note kung sumulat ka nito. Huwag maglagay ng mga
detalye ng kliyente sa note. Para suportahan ito, iniimbak ng Fontes ang huling error sa iyong computer
(`last-error.json` sa cache folder nito, pinapalitan sa bawat pagkakataon); hindi ito kailanman ipinapadala
nang kusa.

**4. Lexifina (naka-on bilang default).** Ang `get_law_on_date`, `get_law_history`, ang 91 bansa at ang mga act ng India ay binabasa sa pamamagitan ng record ng batas ng Lexifina, kaya napupunta sila sa Lexifina bukod pa sa, o sa halip ng, opisyal na site. Ang iyong mga salitang hinanap, citation at petsa ay napupunta sa libreng server ng Lexifina, `global-law.lexifina.com`, na pinapatakbo ng Lexifina, hindi ng mga developer ng Fontes. Ayon sa dokumentasyon ng Lexifina, itinatala ng server nito kung aling tool ang tinawag at gaano ito katagal, hindi kailanman kung ano ang hiningi; hindi ito kayang suriin ng Fontes, at nalalapat ang sariling mga tuntunin ng Lexifina. Nakikita ng Lexifina ang iyong IP address, gaya ng anumang web server. Para ganap na i-off ang Lexifina, itakda ang `WLM_LEXIFINA=0`; hihinto sa paggana ang dalawang tool at mga bansang iyon, at walang ipinapadalang anuman doon.

## Saan ito napupunta at gaano katagal ito iniingatan

Napupunta ang bilang ng paggamit at ang mga bug report sa isang maliit na server na pinapatakbo ng developer
ng Fontes (`relay.kinetra.fit`). Hindi ito nag-iimbak ng mga IP address: ginagamit lamang ang mga ito sa
memory, sandali, para pigilan ang pagbaha ng mga request, at hindi nag-iingat ang web server ng mga access
log para dito. Pinagsasama ang mga bilang sa mga kabuuan bawat araw; hindi iniingatan ang bawat
indibidwal na padala. Iniingatan ang mga kabuuan nang hanggang 2 taon, ang mga bug report nang hanggang
1 taon, at saka binubura. Walang ibinebenta o ibinabahagi.

Kung hindi maabot ang server na iyon, walang ipinapadala: nananatili sa iyong computer ang mga bilang at
itinuturo ka ng bug report sa issue tracker sa halip.

## Sino ang responsable, at sa anong batayan

Ang data controller para sa bilang ng paggamit at mga bug report ay si Yüce Karapazar, ang developer ng
Fontes. Contact: fontesmcp@proton.me.

Ang legal na batayan ay ang iyong pahintulot (consent) (Artikulo 6(1)(a) ng UK GDPR at ng EU GDPR).
Ipinapadala lamang ang bilang ng paggamit kung nag-opt in ka, at ang mga bug report pagkatapos mo lamang itong
kumpirmahin. Maaari mong bawiin ang pahintulot anumang oras sa pamamagitan ng pag-opt out tulad ng
inilarawan sa itaas; hindi nito naaapektuhan ang naipadala na bago noon.

## Contact

Mga tanong o kahilingan: mag-email sa fontesmcp@proton.me, o magbukas ng issue sa
<https://github.com/ykarapazar/fontes/issues>.

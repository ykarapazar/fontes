> Aceasta este o traducere asistată automat. Versiunea în limba engleză este cea care prevalează.

# Notă de confidențialitate Fontes

Fontes rulează pe computerul dumneavoastră. Căutările dumneavoastră și documentele pe care le deschideți
rămân între computerul dumneavoastră, sursele pe care le căutați (cele oficiale, plus CourtListener și Lexifina acolo unde le folosiți, vedeți mai jos) și aplicația de IA pe care o folosiți
(conform condițiilor proprii ale acelei aplicații). Fontes însuși nu trimite dezvoltatorilor Fontes
**nimic în mod implicit**.

## Ce poate părăsi computerul dumneavoastră și când

**1. Verificarea actualizărilor (activată implicit).** O dată pe zi, Fontes întreabă PyPI, indexul public
de pachete Python, care este cea mai nouă versiune. Cererea nu conține nimic despre dumneavoastră sau despre
munca dumneavoastră; PyPI vede adresa dumneavoastră IP, ca la orice descărcare. Pentru a o dezactiva, setați
`FONTES_NO_UPDATE_CHECK=1` (notificarea din aplicație) și `FONTES_NO_AUTO_UPDATE=1` (actualizările automate
ale programului de instalare).

**2. Contorizări de utilizare (dezactivate, cu excepția cazului în care le activați).** Dacă vă dați acordul
(opt-in), o dată pe zi Fontes trimite:

- versiunea Fontes și familia sistemului dumneavoastră de operare (macOS, Windows, Linux);
- pentru fiecare zi, de câte ori a fost folosit fiecare instrument pentru fiecare cod de jurisdicție, de
  exemplu „2026-11-10, nl, search_caselaw, 12”.

Acesta este întregul mesaj. Nu include niciodată căutările dumneavoastră, identificatori de documente sau
de cauze, textul documentelor, numele dumneavoastră, un cont sau vreun identificator al dumneavoastră ori
al computerului dumneavoastră. Contorizările așteaptă pe computerul dumneavoastră (în folderul cache al
Fontes, `stats.json`) până când sunt trimise; dacă trimiterea eșuează, așteaptă până a doua zi.

- **Activare (opt-in)**: răspundeți „d” când programul de instalare întreabă sau setați `FONTES_STATS=1`
  pentru serverul Fontes.
- **Dezactivare (opt-out)**: rulați din nou programul de instalare și apăsați Enter la acea întrebare sau
  eliminați `FONTES_STATS`. Ștergerea `stats.json` elimină tot ce nu a fost încă trimis.

**3. Rapoarte de eroare (doar când trimiteți unul).** Când solicitați unul (`fontes report-bug` sau cereți
aplicației dumneavoastră de IA să raporteze o eroare Fontes), Fontes vă arată mai întâi raportul complet și
îl trimite doar dacă îl confirmați. Acesta conține versiunea Fontes, familia sistemului dumneavoastră de
operare, codul de jurisdicție, numele instrumentului și mesajul de eroare al ultimului apel eșuat (cu
termenii căutați și identificatorii eliminați) și o notă, dacă scrieți una. Nu includeți în notă date despre
clienți. În acest scop, Fontes păstrează ultima eroare pe computerul dumneavoastră (`last-error.json` în
folderul său cache, înlocuit de fiecare dată); aceasta nu este niciodată trimisă separat.

**4. Lexifina (activat implicit).** `get_law_on_date`, `get_law_history`, cele 91 de țări și legile Indiei sunt citite prin registrul legii al Lexifina, deci ajung la Lexifina, pe lângă site-ul oficial sau în locul acestuia. Cuvintele dumneavoastră de căutare, citările și datele ajung la serverul gratuit al Lexifina, `global-law.lexifina.com`, care este administrat de Lexifina, nu de dezvoltatorii Fontes. Lexifina documentează că serverul său înregistrează ce instrument a fost apelat și cât a durat, niciodată ce s-a cerut; Fontes nu poate verifica acest lucru, iar condițiile proprii ale Lexifina se aplică. Lexifina vede adresa dumneavoastră IP, ca orice server web. Pentru a dezactiva complet Lexifina, setați `WLM_LEXIFINA=0`; cele două instrumente și țările respective încetează atunci să funcționeze, iar nimic nu este trimis acolo.

## Unde ajung datele și cât timp sunt păstrate

Contorizările de utilizare și rapoartele de eroare ajung la un mic server administrat de dezvoltatorul
Fontes (`relay.kinetra.fit`). Acesta nu stochează adrese IP: ele sunt folosite doar în memorie, pentru scurt
timp, pentru a opri avalanșele de cereri, iar serverul web nu păstrează niciun jurnal de acces pentru el.
Contorizările sunt adunate în totaluri zilnice; trimiterile individuale nu sunt păstrate. Totalurile sunt
păstrate până la 2 ani, rapoartele de eroare până la 1 an, apoi sunt șterse. Nimic nu este vândut sau
partajat.

Dacă acel server nu poate fi accesat, nu se trimite nimic: contorizările rămân pe computerul dumneavoastră,
iar rapoartele de eroare vă îndrumă în schimb către sistemul de urmărire a problemelor (issue tracker).

## Cine este responsabil și pe ce temei

Operatorul de date pentru contorizările de utilizare și rapoartele de eroare este Yüce Karapazar,
dezvoltatorul Fontes. Contact: fontesmcp@proton.me.

Temeiul legal este consimțământul dumneavoastră (articolul 6 alineatul (1) litera (a) din UK GDPR și din
GDPR-ul UE). Contorizările de utilizare sunt trimise doar dacă vă dați acordul (opt-in), iar un raport de
eroare doar după ce l-ați confirmat. Vă puteți retrage consimțământul în orice moment, renunțând așa cum
este descris mai sus; aceasta nu afectează ce a fost trimis anterior.

## Contact

Întrebări sau solicitări: trimiteți un e-mail la fontesmcp@proton.me sau deschideți un issue la
<https://github.com/ykarapazar/fontes/issues>.

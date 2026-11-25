> Aceasta este o traducere asistată automat. Versiunea în limba engleză este cea care prevalează.

# Fontes: întrebări și răspunsuri

## Ce este Fontes?

Un server MCP gratuit, cu sursă deschisă (Apache 2.0). Permite oricărei aplicații care folosește Model
Context Protocol (Claude, Codex, Cursor, VS Code, Gemini CLI și altele) să caute hotărâri judecătorești și
legislație în timp real pe site-urile instanțelor și ale autorităților publice, în peste 120 de jurisdicții
și la instanțe internaționale (124 de adaptoare). Fiecare rezultat își numește sursa și are un link către
original.

## Sunt textele oficiale?

În mare parte, dar nu întotdeauna.

- Majoritatea surselor sunt administrate de o instanță, un minister sau un monitor oficial.
- Unele texte consolidate sunt publicate de un guvern, dar sunt declarate expres neoficiale: doar monitorul
  oficial este autentic.
- Câteva surse nu sunt deloc site-uri guvernamentale (de exemplu LexiVox, LawPhil, Maqam, Wikisource).

Fontes adaugă mențiunea „Sursă neoficială” la fiecare răspuns care provine de la una dintre acestea. Înainte
de a cita ceva, verificați publicația oficială. Tabelul de acoperire din [README](README.md#acoperire) și
`list_jurisdictions` indică sursa pentru fiecare jurisdicție.

## Ce jurisdicții acoperă și cât de bine?

124 de adaptoare: 108 state membre ONU, Hong Kong, Kosovo, Palestina, Taiwan, instanțele DIFC și 11 instanțe
și organisme internaționale (precum Curtea Europeană a Drepturilor Omului, UE, CIJ și OMC).

Acoperirea diferă mult. Conform unei reguli stricte (precedentele instanței generale supreme sau constituția
și actele normative primare, accesate integral), 72 din cele 124 sunt considerate acoperite.
[COVERAGE.md](../../COVERAGE.md) (în limba engleză) arată, pentru fiecare jurisdicție, ce accesează Fontes,
ce nu accesează și de ce.

## Am nevoie de o cheie API?

Pentru aproape toate jurisdicțiile, nu. Unele surse necesită o cheie gratuită: vedeți [KEYS.md](KEYS.md).

- **Franța:** da. Franța este dezactivată până când setați `WLM_FR_PISTE_CLIENT_ID` și
  `WLM_FR_PISTE_CLIENT_SECRET`. Acestea provin dintr-un cont PISTE gratuit (piste.gouv.fr), cu o aplicație
  abonată la Judilibre și Légifrance.
- **Statele Unite:** opțional. Căutarea în jurisprudență funcționează fără cheie, dar cheia demo comună
  permite doar aproximativ 10 căutări pe zi pentru fiecare adresă IP. O cheie api.data.gov gratuită în
  `WLM_US_GOVINFO_KEY` crește această limită.

Setați-le ca variabile de mediu pentru serverul Fontes în setările MCP ale aplicației. Programele
de instalare vi le cer după instalare, iar lansatorul lor **Adăugați sau modificați
cheile** le modifică ulterior.

Separat, câteva surse precizează în condițiile lor că accesul automatizat necesită permisiunea editorului.
Acestea sunt marcate OFF și rămân dezactivate. O cheie nu schimbă acest lucru; doar permisiunea editorului o
face (setați apoi `WLM_PERMITTED=<codes>`).

## Ce părăsește computerul meu?

Căutările dumneavoastră ajung doar la sursa în care se caută. Fontes nu păstrează nicio bază de date și nu
necesită niciun cont.

În afară de surse, Fontes întreabă PyPI o dată pe zi dacă există o versiune mai nouă (o puteți dezactiva cu
`FONTES_NO_UPDATE_CHECK=1`). Contorizările de utilizare sunt dezactivate, cu excepția cazului în care le
activați, iar un raport de eroare este trimis doar după ce l-ați văzut și l-ați confirmat. Aplicația
dumneavoastră de IA vede conversația conform propriilor sale condiții.

Detalii complete: [PRIVACY.md](PRIVACY.md).

## Este aceasta consultanță juridică?

Nu. Fontes este un instrument de cercetare. Găsește texte; nu vă spune ce înseamnă ele pentru cauza
dumneavoastră, iar folosirea lui nu creează o relație avocat–client cu nimeni. Aplicația de IA poate
interpreta greșit un text, așa că citiți hotărârea sau dispoziția integrală înainte de a vă baza pe ea.
Pentru consultanță, adresați-vă unui avocat calificat în locul unde se pune întrebarea dumneavoastră.

## Cine îl întreține? Va funcționa în continuare?

O singură persoană: Yüce Karapazar. În spatele Fontes nu există nicio companie, niciun contract de asistență
și nicio promisiune privind nivelul serviciului. Nu se oferă servicii juridice.

Sursele sunt verificate o dată pe zi, iar rezultatele sunt publicate pe
[pagina de stare](https://ykarapazar.github.io/fontes/status/?lang=ro). Site-urile instanțelor și ale
autorităților publice se schimbă fără preaviz, astfel încât o sursă se poate defecta oricând. Nu există nicio
garanție că vreo sursă sau Fontes însuși va funcționa în continuare. Fontes este furnizat „ca atare”, fără
garanție (secțiunile 7 și 8 din [LICENȚĂ](../../../LICENSE)).

## Un text este greșit sau învechit ori o sursă nu funcționează. Cum raportez?

- Deschideți un issue cu formularul „Broken or wrong source”:
  <https://github.com/ykarapazar/fontes/issues/new/choose>. Precizați jurisdicția, ce ați întrebat, ce ați
  primit și pagina oficială care arată textul corect.
- Sau cereți aplicației dumneavoastră de IA să „raporteze o eroare Fontes” (sau rulați `fontes report-bug`).
  Vedeți raportul înainte de a se trimite ceva.
- Sau trimiteți un e-mail la fontesmcp@proton.me.

Nu includeți în raport detalii despre clienți sau fapte confidențiale.

**Dacă administrați una dintre surse** și ceva nu este în regulă (condițiile dumneavoastră, robots.txt,
limitele de trafic), trimiteți un e-mail la fontesmcp@proton.me. Sursa va fi reparată sau dezactivată.

## Prin ce se deosebește Fontes de instrumentele de cercetare juridică găzduite?

- **Rulează pe computerul dumneavoastră.** Nu există niciun server Fontes și niciun cont. Asta înseamnă și că
  funcționează doar în aplicațiile care pot porni un server MCP local (Claude Desktop, Codex, Cursor, VS Code
  și altele similare), nu în aplicațiile exclusiv web care acceptă doar conectori găzduiți.
- **Nu are bază de date.** Fiecare căutare merge în timp real la site-ul sau API-ul propriu al editorului,
  astfel încât rezultatele sunt la fel de actuale ca sursa, iar calitatea căutării este cea a sursei. Nu
  există căutare semantică într-un index selectat.
- **Nu impune nicio limită de utilizare.** Fontes nu are o limită lunară de apeluri. Își eșalonează cererile
  către fiecare site, iar unele surse limitează cât de repede sau cât de des pot fi interogate.
- **Are sursă deschisă.** Puteți citi fiecare adaptor și vedea exact de unde provine fiecare text.
- **Nu există un furnizor în spatele lui.** Niciun contract, birou de asistență sau promisiune de
  disponibilitate (vedeți „Cine îl întreține?”).

## Cu ce aplicații și sisteme funcționează?

Cu orice aplicație MCP care poate rula un server local (stdio), de exemplu Claude Desktop, Claude Code,
Codex, Cursor, VS Code (GitHub Copilot), Gemini CLI, Windsurf, Zed, LM Studio și Cline. Fontes rulează pe
macOS, Windows și Linux, oriunde rulează uv (Python 3.13+). Pe Mac sau PC Windows, un program de instalare cu un clic
configurează deodată Claude Desktop, Codex, Claude Code, Cursor, VS Code, Windsurf, Gemini CLI, Zed,
LM Studio și Cline. Pașii pentru fiecare aplicație: [INSTALL.md](INSTALL.md).

## Pot contribui cu cod?

Nu în acest moment. Issue-urile, rapoartele despre surse și solicitările de jurisdicții sunt binevenite.
Vedeți [CONTRIBUTING.md](../../../CONTRIBUTING.md).

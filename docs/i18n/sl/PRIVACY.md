> To je strojno podprt prevod. Merodajna je angleška različica.

# Obvestilo o zasebnosti orodja Fontes

Fontes deluje v vašem računalniku. Vaša iskanja in dokumenti, ki jih odprete, ostanejo med vašim
računalnikom, viri, ki jih preiskujete (uradni viri ter CourtListener in Lexifina, kjer ju
uporabljate; glejte spodaj), in aplikacijo AI, ki jo uporabljate (po lastnih pogojih te aplikacije). Sam Fontes razvijalcem orodja Fontes **privzeto ne pošilja ničesar**.

## Kaj lahko zapusti vaš računalnik in kdaj

**1. Preverjanje posodobitev (privzeto vklopljeno).** Fontes enkrat na dan vpraša PyPI, javni
indeks paketov Python, katera različica je najnovejša. Zahteva ne vsebuje ničesar o vas ali
vašem delu; PyPI vidi vaš naslov IP, kot pri vsakem prenosu. Če ga želite izklopiti, nastavite
`FONTES_NO_UPDATE_CHECK=1` (obvestilo v aplikaciji) in `FONTES_NO_AUTO_UPDATE=1` (samodejne
posodobitve namestitvenega programa).

**2. Števci uporabe (izklopljeni, razen če jih vklopite).** Če privolite (opt-in), Fontes enkrat
na dan pošlje:

- različico orodja Fontes in družino vašega operacijskega sistema (macOS, Windows, Linux);
- za vsak dan, kolikokrat je bilo posamezno orodje uporabljeno za posamezno kodo jurisdikcije,
  na primer »2026-11-10, nl, search_caselaw, 12«.

To je celotno sporočilo. Nikoli ne vsebuje vaših iskanj, identifikatorjev dokumentov ali
zadev, besedila dokumentov, vašega imena, računa ali kakršnega koli identifikatorja vas ali
vašega računalnika. Števci čakajo v vašem računalniku (v mapi predpomnilnika orodja Fontes,
`stats.json`), dokler niso poslani; če pošiljanje ne uspe, počakajo do naslednjega dne.

- **Privolitev (opt-in)**: odgovorite »y«, ko vas namestitveni program vpraša, ali nastavite
  `FONTES_STATS=1` za strežnik Fontes.
- **Odjava (opt-out)**: znova zaženite namestitveni program in pri tem vprašanju pritisnite
  Enter ali odstranite `FONTES_STATS`. Z izbrisom datoteke `stats.json` zavržete vse, kar še ni
  bilo poslano.

**3. Prijave napak (samo ko jo pošljete sami).** Ko jo zahtevate (`fontes report-bug` ali
aplikacijo AI prosite, naj prijavi napako v orodju Fontes), vam Fontes najprej pokaže celotno
prijavo in jo pošlje samo, če potrdite. Vsebuje različico orodja Fontes, družino vašega
operacijskega sistema, kodo jurisdikcije, ime orodja in sporočilo o napaki zadnjega neuspelega
klica orodja (brez vaših iskalnih besed in identifikatorjev) ter opombo, če jo napišete. V
opombo ne vpisujte podatkov o strankah. Za to Fontes hrani zadnjo napako v vašem računalniku
(`last-error.json` v svoji mapi predpomnilnika, vsakič se zamenja); ta se nikoli ne pošlje
sama od sebe.

**4. Lexifina (privzeto vklopljeno).** `get_law_on_date`, `get_law_history` 91 držav in indijski zakoni se berejo iz zapisa Lexifine, zato gredo k Lexifini poleg uradne strani ali namesto nje. Vaši iskalni izrazi, citati in datumi gredo na brezplačen strežnik Lexifine, `global-law.lexifina.com`, ki ga upravlja Lexifina, ne razvijalci orodja Fontes. Lexifina dokumentira, da njen strežnik beleži, katero orodje je bilo klicano in kako dolgo je trajalo, nikoli pa, kaj je bilo vprašano; Fontes tega ne more preveriti, veljajo pa pogoji Lexifine. Lexifina vidi vaš naslov IP, kot vsak spletni strežnik. Za popoln izklop Lexifine nastavite `WLM_LEXIFINA=0`; ta dva orodja in države potem prenehajo delovati, nič pa se tja ne pošlje.

## Kam gredo podatki in kako dolgo se hranijo

Števci uporabe in prijave napak gredo na majhen strežnik, ki ga upravlja razvijalec orodja
Fontes (`relay.kinetra.fit`). Ta ne shranjuje naslovov IP: uporabljajo se samo v pomnilniku,
kratek čas, za preprečevanje preobremenitev, spletni strežnik pa zanj ne vodi dnevnika
dostopov. Števci se seštevajo v dnevne vsote; posamezne pošiljke se ne hranijo. Vsote se hranijo
do 2 let, prijave napak do 1 leta, nato se izbrišejo. Nič se ne prodaja ali deli.

Če tega strežnika ni mogoče doseči, se nič ne pošlje: števci ostanejo v vašem računalniku,
prijave napak pa vas namesto tega usmerijo na sledilnik težav (issue tracker).

## Kdo je odgovoren in na kakšni podlagi

Upravljavec podatkov za števce uporabe in prijave napak je Yüce Karapazar, razvijalec orodja
Fontes. Stik: fontesmcp@proton.me.

Pravna podlaga je vaša privolitev (točka (a) prvega odstavka 6. člena UK GDPR in GDPR EU).
Števci uporabe se pošiljajo samo, če privolite (opt-in), prijava napake pa šele, ko jo potrdite.
Privolitev lahko kadar koli prekličete z odjavo, kot je opisano zgoraj; to ne vpliva na to, kar
je bilo poslano prej.

## Stik

Vprašanja ali zahteve: pišite na fontesmcp@proton.me ali odprite prijavo težave (issue) na
<https://github.com/ykarapazar/fontes/issues>.

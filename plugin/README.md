# Fontes plugin

Fontes fetches court decisions and legislation live from official sources at the moment you ask, and every result links to the original. It is a research tool, not legal advice.

This plugin adds the Fontes MCP server to Claude. It runs on your computer with
`uvx fontes-mcp==0.1.1` (needs [uv](https://docs.astral.sh/uv/)): no account and no hosted
service. Source code, licence (Apache 2.0) and full documentation: https://github.com/ykarapazar/fontes

Install in Claude Code:

    /plugin install fontes --marketplace ykarapazar/fontes

## Tools

- `list_jurisdictions`: List the jurisdictions covered, their sources, tools and filters.
- `search_caselaw`: Full-text search of court decisions in one jurisdiction.
- `get_decision`: Fetch one court decision as markdown with its source URL.
- `search_legislation`: Find laws, acts and statutory instruments in one jurisdiction.
- `get_legislation_toc`: Table of contents of a law with provision labels.
- `get_legislation_provision`: Current text of one article or section.
- `get_legislation_text`: Full consolidated text of a law, pageable.
- `report_bug`: Prepare a Fontes bug report; sent only if the user confirms it.

All tools only read. Nothing is written outside Fontes's own cache folder (the daily update
check and, if you opt in, usage counts).

## Settings

All optional, all stored as secrets: a PISTE client ID and secret turn France on; an
api.data.gov key lifts the United States search limit. How to get them:
https://github.com/ykarapazar/fontes/blob/main/docs/KEYS.md. They are sent only to the French and US government APIs.

## What it sends, and where

When you ask a question, Fontes sends your search terms or document id to the court or
government website of the jurisdiction you asked about, and nowhere else. It identifies itself
with a `Fontes/<version>` User-Agent that names the repository and a contact address. Besides those sources it contacts only:

- `pypi.org`: the daily version check (off: `FONTES_NO_UPDATE_CHECK=1`)
- `relay.kinetra.fit`: bug reports you confirm, and usage counts only if you set `FONTES_STATS=1`
- `github.com`: links to the Fontes repository in messages; nothing is sent

Privacy notice: https://github.com/ykarapazar/fontes/blob/main/docs/PRIVACY.md

### Every source host in the code (317)

Generated from the adapters' source by `scripts/plugin_bundle.py`: every host an adapter
fetches from or links to. A host is contacted only when you ask about its jurisdiction.

- `a9.com`
- `adala.justice.gov.ma`
- `agm.gov.bz`
- `ajudata.african-court.org`
- `aladel.gov.ly`
- `amategeko.gov.rw`
- `anle.toaan.gov.vn`
- `api-gateway.slov-lex.sk`
- `api.e-qanun.az`
- `api.eftacourt.int`
- `api.govinfo.gov`
- `api.normattiva.it`
- `api.piste.gouv.fr`
- `api.prod.legislation.gov.au`
- `api.sejm.gov.pl`
- `api.webgjk-ks.org`
- `apis.amategeko.gov.rw`
- `arbol.tribunalagroambiental.bo`
- `attorneygeneral.govmu.org`
- `au.int`
- `base.mmk.tj`
- `bdlaws.minlaw.gov.bd`
- `be.gjykataelarte.gov.al`
- `bedesten.adalet.gov.tr`
- `bjn.poderjudicial.gub.uy`
- `buscador.corteconstitucional.gob.ec`
- `busquedas.elperuano.pe`
- `caselaw.nationalarchives.gov.uk`
- `ccj.org`
- `cconstitucional.org.mz`
- `cdc.gov.kh`
- `conseilconstitutionnel.sn`
- `constcourt.tj`
- `constsot.kg`
- `consultoria.gov.do`
- `controlpanel.president.tj`
- `cour-constitutionnelle.dz`
- `courconstitutionnelle.bj`
- `courdecassation.ci`
- `coursupreme.cm`
- `court.gov.tm`
- `courtecowas.org`
- `courtofappeal.gov.jm`
- `courts.bs`
- `creativecommons.org`
- `cspj.ht`
- `data.bka.gv.at`
- `data.finlex.fi`
- `data.gov.cz`
- `data.gov.hk`
- `data.legilux.public.lu`
- `data.overheid.nl`
- `data.public.lu`
- `data.rechtspraak.nl`
- `data.riksdagen.se`
- `dati.normattiva.it`
- `decisions.scc-csc.ca`
- `diputados.gob.bo`
- `docs.oasis-open.org`
- `docs.rechtsinformationen.bund.de`
- `docs.wto.org`
- `e-qanun.az`
- `e-sbirka.gov.cz`
- `eakta.birosag.hu`
- `ecd.court.ge`
- `eftacourt.int`
- `elieta.lv`
- `esacc.corteconstitucional.gob.ec`
- `eservices.courdecassation.ci`
- `eur-lex.europa.eu`
- `faolex.fao.org`
- `fbihvlada.gov.ba`
- `fedlex.data.admin.ch`
- `files.amategeko.gov.rw`
- `flk.npc.gov.cn`
- `foundation.wikimedia.org`
- `fs.knesset.gov.il`
- `gateway.elieta.lv`
- `gazette.gov.mv`
- `gib.gov.tr`
- `gjk-ks.org`
- `gjykata-media.s3.eu-central-1.amazonaws.com`
- `gjykataelarte.gov.al`
- `gzk.rks-gov.net`
- `he.wikisource.org`
- `hj.tribunalconstitucional.es`
- `hudoc.echr.coe.int`
- `ia37rg02wpsa01.blob.core.windows.net`
- `icsid.worldbank.org`
- `icsidfiles.worldbank.org`
- `indiacode.gov.in`
- `indian-supreme-court-judgments.s3.ap-south-1.amazonaws.com`
- `instante.justice.md`
- `isap.sejm.gov.pl`
- `island.is`
- `jdih.setneg.go.id`
- `judgment.judicial.gov.tw`
- `juricaf.org`
- `jurisprudencia.cc.gob.gt`
- `jurisprudencia.cv`
- `jurisprudencia.stf.jus.br`
- `jurisprudenta.csj.md`
- `justice.gc.ca`
- `justice.sec.gouv.sn`
- `kararlar.uyusmazlik.gov.tr`
- `kararlarbilgibankasi.anayasa.gov.tr`
- `knesset.gov.il`
- `law.moj.gov.tw`
- `lawphil.net`
- `laws-lois.justice.gc.ca`
- `laws.bahamas.gov.bs`
- `laws.e-gov.go.jp`
- `laws.gov.tt`
- `laws.moj.gov.af`
- `lawsofnigeria.placng.org`
- `legilux.public.lu`
- `legimonaco.mc`
- `legis.senado.leg.br`
- `legislation.gov.bt`
- `legislation.krd`
- `legislation.mt`
- `legispan.asamblea.gob.pa`
- `lex.uz`
- `likumi.lv`
- `lovdata.no`
- `main.knesset.gov.il`
- `maqam.najah.edu`
- `matsne.gov.ge`
- `mauritiusassembly.govmu.org`
- `mededeling.rechtspraak.nl`
- `mejlis.gov.tm`
- `mevzuat.adalet.gov.tr`
- `mis.ihc.gov.pk`
- `moj.gov.af`
- `mola.gov.gy`
- `mvlaw.gov.mv`
- `narodne-novine.nn.hr`
- `nass.gov.ng`
- `nipc.gov.ng`
- `nkp.gov.np`
- `normas.leg.br`
- `nuevo.leychile.cl`
- `oauth.piste.gouv.fr`
- `ogd.ris.bka.gv.at`
- `op.europa.eu`
- `opendata.finlex.fi`
- `orzeczenia.ms.gov.pl`
- `pakistancode.gov.pk`
- `pisrs.si`
- `piste.gouv.fr`
- `portal.stf.jus.br`
- `portaljuridicandorra.ad`
- `presedinte.md`
- `president.tj`
- `primature.sn`
- `psi.rechtspraak.nl`
- `publications.europa.eu`
- `purl.org`
- `qbz.gov.al`
- `rattspraxis.etjanst.domstol.se`
- `raw.githubusercontent.com`
- `rcms.usc.gov.mm`
- `rechtspraak.sr`
- `registry.opendata.aws`
- `repository.officiele-overheidspublicaties.nl`
- `resource.data.one.gov.hk`
- `revisedacts.lawreform.ie`
- `rozhodnuti.justice.cz`
- `sandbox-api.piste.gouv.fr`
- `sandbox-oauth.piste.gouv.fr`
- `sbirka.nsoud.cz`
- `scc-csc.ca`
- `schemas.openxmlformats.org`
- `search.bger.ch`
- `search.et.gr`
- `searchetv99.azurewebsites.net`
- `servicios.infoleg.gob.ar`
- `sgg.gouv.bj`
- `shuukh.mn`
- `sigcc.courdecassation.ci`
- `sinalevi.go.cr`
- `sodnapraksa.si`
- `sso.agc.gov.sg`
- `standaarden.overheid.nl`
- `static.slov-lex.sk`
- `supreme-cms.supremecourt.gov.ng`
- `supremecourt.gov.bd`
- `supremecourt.gov.jm`
- `supremecourt.gov.ng`
- `supremecourt.govmu.org`
- `testphase.rechtsinformationen.bund.de`
- `treaties.un.org`
- `ts.gov.mz`
- `tse.do`
- `uitspraken.rechtspraak.nl`
- `uscode.house.gov`
- `vanban.chinhphu.vn`
- `vbpl.vn`
- `visorpdf.tse.do`
- `vyhledavac.nssoud.cz`
- `wetten.overheid.nl`
- `www.african-court.org`
- `www.alolya.gov.ly`
- `www.anayasa.gov.tr`
- `www.archives.gov`
- `www.areiospagos.gr`
- `www.argentina.gob.ar`
- `www.arlis.am`
- `www.assnat.ci`
- `www.barbadoslawcourts.gov.bb`
- `www.bcn.cl`
- `www.belizejudiciary.org`
- `www.boe.es`
- `www.bundesfinanzhof.de`
- `www.cc.gob.gt`
- `www.cc.gov.lb`
- `www.cco.gov.jo`
- `www.cdep.ro`
- `www.cnlegis.gov.mg`
- `www.congreso.gob.pe`
- `www.consellgeneral.ad`
- `www.constcourt.bg`
- `www.corteconstitucional.gov.co`
- `www.cour-constitutionnelle.ma`
- `www.courdecassation.fr`
- `www.courdecassation.ht`
- `www.court.gov.cn`
- `www.courtofappeal.org.bs`
- `www.courts.go.jp`
- `www.csj.md`
- `www.daisy.org`
- `www.datos.gov.co`
- `www.dgsi.pt`
- `www.difccourts.ae`
- `www.dna.sr`
- `www.domstol.no`
- `www.domstol.se`
- `www.e-gov.go.jp`
- `www.echr.coe.int`
- `www.ecowas.int`
- `www.elegislation.gov.hk`
- `www.elitigation.sg`
- `www.enag.gob.hn`
- `www.fao.org`
- `www.fedlex.admin.ch`
- `www.finlex.fi`
- `www.funcionpublica.gov.co`
- `www.gacetaoficial.gob.cu`
- `www.gazette.gov.mv`
- `www.gazette.sc`
- `www.gesetze-im-internet.de`
- `www.gesetze.li`
- `www.govinfo.gov`
- `www.hcc.gov.mg`
- `www.hopr.gov.et`
- `www.icj-cij.org`
- `www.impo.com.uy`
- `www.infoleg.gob.ar`
- `www.irishstatutebook.ie`
- `www.itlos.org`
- `www.joradp.dz`
- `www.judicial.gov.tw`
- `www.judiciary.gov.sg`
- `www.judiciary.sc`
- `www.laoofficialgazette.gov.la`
- `www.legifrance.gouv.fr`
- `www.legislation.gov.au`
- `www.legislation.gov.bt`
- `www.legislation.gov.uk`
- `www.lexivox.org`
- `www.leychile.cl`
- `www.lloc.gov.bh`
- `www.loc.gov`
- `www.mevzuat.gov.tr`
- `www.minjus.gob.cu`
- `www.mpr.go.id`
- `www.normattiva.it`
- `www.nsud.sk`
- `www.ogh.li`
- `www.parlament.ba`
- `www.parliament.bg`
- `www.pgdlisboa.pt`
- `www.prc.cm`
- `www.rechtspraak.nl`
- `www.rekabet.gov.tr`
- `www.retsinformation.dk`
- `www.riigiteataja.ee`
- `www.riksdagen.se`
- `www.sayistay.gov.tr`
- `www.sccourt.gov.eg`
- `www.scj.ro`
- `www.scl.lu`
- `www.slov-lex.sk`
- `www.sodnapraksa.si`
- `www.stj.cv`
- `www.supremecourt.gov`
- `www.supremecourt.gov.bd`
- `www.tc.gob.pe`
- `www.tribunalconstitucional.ad`
- `www.tribunalconstitucional.cv`
- `www.tribunalconstitucional.es`
- `www.tribunalconstitucional.pt`
- `www.ts.gov.mz`
- `www.tsc.gob.hn`
- `www.un.org`
- `www.unionsupremecourt.gov.mm`
- `www.ustavni.sud.rs`
- `www.ustavnisud.ba`
- `www.ustavnisud.me`
- `www.uyusmazlik.gov.tr`
- `www.vrh.sud.rs`
- `www.w3.org`
- `www.worldbank.org`
- `www.wto.org`
- `www12.senado.leg.br`
- `www3.congreso.gob.pe`
- `zoekservice.overheid.nl`

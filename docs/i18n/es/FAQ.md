> Esta es una traducción asistida por máquina. La versión en inglés es la que prevalece.

# Fontes: preguntas y respuestas

## ¿Qué es Fontes?

Un servidor MCP gratuito y de código abierto (Apache 2.0). Permite que cualquier aplicación que hable
el Model Context Protocol (Claude, Codex, Cursor, VS Code, Gemini CLI y otras) busque resoluciones
judiciales y legislación en directo en sitios web judiciales y gubernamentales de más de 120
jurisdicciones y tribunales internacionales (124 adaptadores). Cada resultado indica su fuente y
enlaza al original.

## ¿Son oficiales los textos?

En su mayoría, pero no siempre.

- La mayoría de las fuentes las gestiona un tribunal, un ministerio o un diario oficial.
- Algunos textos consolidados los publica un gobierno, pero son expresamente no oficiales: solo el
  diario oficial es auténtico.
- Unas pocas fuentes no son sitios gubernamentales en absoluto (por ejemplo LexiVox, LawPhil, Maqam,
  Wikisource).

Fontes añade un aviso "Unofficial source" (fuente no oficial) a cada respuesta que procede de una de ellas. Antes de
citar nada, compruebe la publicación oficial. La tabla de cobertura del [README](README.md#cobertura)
y `list_jurisdictions` indican la fuente de cada jurisdicción.

## ¿Qué jurisdicciones cubre, y en qué medida?

124 adaptadores: 108 Estados miembros de la ONU, Hong Kong, Kosovo, Palestina, Taiwán, los DIFC
Courts y 11 tribunales y organismos internacionales (como el Tribunal Europeo de Derechos Humanos, la
UE, la CIJ y la OMC).

La cobertura varía mucho. Con un criterio estricto (los precedentes del tribunal general supremo, o la
constitución y las leyes de rango primario, alcanzados por completo), 72 de las 124 cuentan como
cubiertas. [COVERAGE.md](../../COVERAGE.md) indica, para cada jurisdicción, qué alcanza Fontes, qué
no y por qué.

## ¿Necesito una clave de API?

Para casi todas las jurisdicciones, no. Algunas fuentes necesitan una clave gratuita: consulte
[KEYS.md](KEYS.md).

- **Francia:** sí. Francia está desactivada hasta que defina `WLM_FR_PISTE_CLIENT_ID` y
  `WLM_FR_PISTE_CLIENT_SECRET`. Se obtienen con una cuenta gratuita de PISTE (piste.gouv.fr) con una
  aplicación suscrita a Judilibre y Légifrance.
- **Estados Unidos:** opcional. La búsqueda de jurisprudencia funciona sin clave, pero la clave de
  demostración compartida solo permite unas 10 búsquedas al día por dirección IP. Una clave gratuita
  de api.data.gov en `WLM_US_GOVINFO_KEY` amplía ese límite.

Defínalas como variables de entorno para el servidor Fontes en la configuración MCP de su aplicación.
Cuando salga el instalador, se las pedirá después de instalar, y su lanzador **Add or change keys**
permite cambiarlas más tarde.

Aparte de esto, unas pocas fuentes indican en sus condiciones que el acceso automatizado requiere el
permiso del editor. Están marcadas OFF y siguen desactivadas. Una clave no cambia eso; solo lo cambia
el permiso del editor (entonces defina `WLM_PERMITTED=<codes>`).

## ¿Qué sale de mi ordenador?

Sus búsquedas solo van a la fuente en la que se busca. Fontes no mantiene ninguna base de datos ni
necesita cuenta.

Además de las fuentes, Fontes pregunta a PyPI una vez al día si existe una versión más reciente (se
desactiva con `FONTES_NO_UPDATE_CHECK=1`). Los recuentos de uso están desactivados salvo que usted los
active, y un informe de error solo se envía después de que usted lo haya visto y confirmado. Su
aplicación de IA ve su conversación conforme a sus propias condiciones.

Todos los detalles: [PRIVACY.md](PRIVACY.md).

## ¿Es esto asesoramiento jurídico?

No. Fontes es una herramienta de investigación. Encuentra textos; no le dice qué significan para su
caso, y su uso no crea una relación abogado-cliente con nadie. La aplicación de IA puede interpretar
mal un texto, así que lea la resolución o la disposición completa antes de confiar en ella. Para
obtener asesoramiento, consulte a un abogado habilitado en el lugar donde surge su consulta.

## ¿Quién lo mantiene? ¿Seguirá funcionando?

Una persona: Yüce Karapazar. No hay ninguna empresa detrás de Fontes, ni contrato de soporte ni
compromiso de nivel de servicio. No se ofrecen servicios jurídicos.

Las fuentes se comprueban una vez al día y los resultados se publican en la
[página de estado](https://ykarapazar.github.io/fontes/status/?lang=es). Los sitios web judiciales y
gubernamentales cambian sin previo aviso, por lo que una fuente puede dejar de funcionar en cualquier
momento. No hay garantía de que ninguna fuente, ni el propio Fontes, siga funcionando. Fontes se
proporciona «tal cual», sin garantía (secciones 7 y 8 de la [LICENSE](../../../LICENSE)).

## Un texto es incorrecto, está desactualizado o una fuente no funciona. ¿Cómo lo comunico?

- Abra una incidencia (issue) con el formulario "Broken or wrong source":
  <https://github.com/ykarapazar/fontes/issues/new/choose>. Indique qué jurisdicción, qué preguntó,
  qué obtuvo y la página oficial que muestra el texto correcto.
- O pida a su aplicación de IA que «informe de un error de Fontes» (o ejecute `fontes report-bug`).
  Usted ve el informe antes de que se envíe nada.
- O escriba a fontesmcp@proton.me.

No incluya datos de clientes ni hechos confidenciales en un informe.

**Si gestiona una de las fuentes** y algo es incorrecto (sus condiciones, su robots.txt, sus límites
de solicitudes), escriba a fontesmcp@proton.me. La fuente se corregirá o se desactivará.

## ¿En qué se diferencia Fontes de las herramientas de investigación jurídica alojadas?

- **Se ejecuta en su ordenador.** No hay servidor de Fontes ni cuenta. Eso también significa que solo
  funciona en aplicaciones que pueden iniciar un servidor MCP local (Claude Desktop, Codex, Cursor,
  VS Code y similares), no en aplicaciones solo web que únicamente aceptan conectores alojados.
- **No tiene base de datos.** Cada búsqueda va en directo al propio sitio web o API del editor, por lo
  que los resultados están tan actualizados como la fuente, y la calidad de la búsqueda es la de la
  propia fuente. No hay búsqueda semántica sobre un índice seleccionado.
- **No fija ningún límite de uso.** Fontes no tiene un tope mensual de llamadas. Espacia sus
  solicitudes a cada sitio web, y algunas fuentes limitan la rapidez o la frecuencia con que se pueden
  consultar.
- **Es de código abierto.** Puede leer cada adaptador y ver exactamente de dónde procede cada texto.
- **No hay ningún proveedor detrás.** Ni contrato, ni servicio de soporte, ni compromiso de
  disponibilidad (consulte «¿Quién lo mantiene?»).

## ¿Con qué aplicaciones y sistemas funciona?

Con cualquier aplicación MCP que pueda ejecutar un servidor local (stdio), por ejemplo Claude Desktop,
Claude Code, Codex, Cursor, VS Code (GitHub Copilot), Gemini CLI, Windsurf, Zed, LM Studio y Cline.
Fontes funciona en macOS, Windows y Linux, en cualquier lugar donde funcione uv (Python 3.13+). Aún no
está en PyPI; cuando lo esté, la mayoría de las aplicaciones necesitarán un comando o una entrada de
configuración, y Claude Desktop acepta un archivo `.mcpb` con un doble clic. Está en camino un
instalador en un clic para Mac y Windows. Configura Claude Desktop, Codex, Claude Code, Cursor,
VS Code, Windsurf, Gemini CLI, Zed, LM Studio y Cline de una sola vez. Pasos para cada aplicación:
[INSTALL.md](INSTALL.md).

## ¿Puedo contribuir con código?

Por ahora no. Las incidencias, los avisos sobre fuentes y las solicitudes de jurisdicciones son
bienvenidos. Consulte [CONTRIBUTING.md](../../../CONTRIBUTING.md).

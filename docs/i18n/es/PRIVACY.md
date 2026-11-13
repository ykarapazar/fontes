> Esta es una traducción asistida por máquina. La versión en inglés es la que prevalece.

# Aviso de privacidad de Fontes

Fontes se ejecuta en su ordenador. Sus búsquedas y los documentos que abre quedan entre su ordenador,
las fuentes oficiales en las que busca y la aplicación de IA que utiliza (sujeta a las condiciones
propias de esa aplicación). Fontes en sí no envía a los desarrolladores de Fontes **nada por
defecto**.

## Qué puede salir de su ordenador, y cuándo

**1. Comprobación de actualizaciones (activada por defecto).** Una vez al día, Fontes pregunta a
PyPI, el índice público de paquetes de Python, cuál es la versión más reciente. La solicitud no
contiene nada sobre usted ni sobre su trabajo; PyPI ve su dirección IP, como en cualquier descarga.
Para desactivarla, defina `FONTES_NO_UPDATE_CHECK=1` (el aviso dentro de la aplicación) y
`FONTES_NO_AUTO_UPDATE=1` (las actualizaciones automáticas del instalador).

**2. Recuentos de uso (desactivados salvo que usted los active).** Si usted lo acepta, una vez al día
Fontes envía:

- la versión de Fontes y la familia de su sistema operativo (macOS, Windows, Linux);
- por día, cuántas veces se usó cada herramienta para cada código de jurisdicción, por ejemplo
  "2026-11-10, nl, search_caselaw, 12".

Ese es el mensaje completo. Nunca incluye sus búsquedas, identificadores de documentos o de asuntos,
el texto de los documentos, su nombre, una cuenta ni ningún identificador suyo o de su ordenador. Los
recuentos esperan en su ordenador (en la carpeta de caché de Fontes, `stats.json`) hasta que se
envían; si el envío falla, esperan al día siguiente.

- **Activarlos**: responda "y" cuando el instalador lo pregunte, o defina `FONTES_STATS=1` para el
  servidor Fontes.
- **Desactivarlos**: vuelva a ejecutar el instalador y pulse Intro en esa pregunta, o elimine
  `FONTES_STATS`. Borrar `stats.json` descarta todo lo que aún no se haya enviado.

**3. Informes de error (solo cuando usted envía uno).** Cuando usted lo solicita (`fontes report-bug`,
o pidiendo a su aplicación de IA que informe de un error de Fontes), Fontes le muestra primero el
informe completo y solo lo envía si usted lo confirma. Contiene la versión de Fontes, la familia de su
sistema operativo, el código de jurisdicción, el nombre de la herramienta y el mensaje de error de la
última llamada fallida (con sus palabras de búsqueda y sus identificadores eliminados), y una nota si
usted la escribe. No incluya datos de clientes en la nota. Para ello, Fontes guarda el último error en
su ordenador (`last-error.json` en su carpeta de caché, sustituido cada vez); nunca se envía por sí
solo.

## Adónde va y cuánto tiempo se conserva

Los recuentos de uso y los informes de error van a un pequeño servidor gestionado por el desarrollador
de Fontes (`relay.kinetra.fit`). No almacena direcciones IP: solo se usan en memoria, brevemente,
para frenar avalanchas de solicitudes, y el servidor web no guarda ningún registro de acceso para él.
Los recuentos se suman en totales diarios; los envíos individuales no se conservan. Los totales se
conservan hasta 2 años y los informes de error hasta 1 año; después se eliminan. Nada se vende ni se
comparte.

Si no se puede contactar con ese servidor, no se envía nada: los recuentos permanecen en su ordenador
y los informes de error le remiten en su lugar al gestor de incidencias (issue tracker).

## Quién es responsable y sobre qué base

El responsable del tratamiento de los recuentos de uso y los informes de error es Yüce Karapazar, el
desarrollador de Fontes. Contacto: fontesmcp@proton.me.

La base jurídica es su consentimiento (artículo 6, apartado 1, letra a), del RGPD del Reino Unido y
del RGPD de la UE). Los recuentos de uso solo se envían si usted los activa, y un informe de error
solo después de que usted lo confirme. Puede retirar su consentimiento en cualquier momento
desactivándolos como se ha descrito; esto no afecta a lo que se envió antes.

## Contacto

Preguntas o solicitudes: escriba a fontesmcp@proton.me, o abra una incidencia (issue) en
<https://github.com/ykarapazar/fontes/issues>.

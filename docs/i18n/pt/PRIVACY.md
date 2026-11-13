> Esta é uma tradução feita com auxílio de máquina. A versão em inglês prevalece.

# Aviso de privacidade do Fontes

O Fontes é executado no seu computador. Suas pesquisas e os documentos que você abre ficam entre o
seu computador, as fontes oficiais que você pesquisa e o app de IA que você usa (nos termos do
próprio app). O próprio Fontes não envia **nada, por padrão**, aos desenvolvedores do Fontes.

## O que pode sair do seu computador, e quando

**1. Verificação de atualizações (ativada por padrão).** Uma vez por dia, o Fontes pergunta ao PyPI,
o índice público de pacotes Python, qual é a versão mais recente. A requisição não contém nada sobre
você ou o seu trabalho; o PyPI vê o seu endereço IP, como em qualquer download. Para desativá-la,
defina `FONTES_NO_UPDATE_CHECK=1` (o aviso dentro do app) e `FONTES_NO_AUTO_UPDATE=1` (as
atualizações automáticas do instalador).

**2. Contagens de uso (desativadas, a menos que você as ative).** Se você aderir (opt-in), uma vez
por dia o Fontes envia:

- a versão do Fontes e a família do seu sistema operacional (macOS, Windows, Linux);
- por dia, quantas vezes cada ferramenta foi usada para cada código de jurisdição, por exemplo
  "2026-11-10, nl, search_caselaw, 12".

Essa é a mensagem inteira. Ela nunca inclui suas pesquisas, identificadores de documentos ou de
processos, o texto de documentos, o seu nome, uma conta ou qualquer identificador seu ou do seu
computador. As contagens aguardam no seu computador (na pasta de cache do Fontes, `stats.json`) até
serem enviadas; se o envio falhar, elas aguardam até o dia seguinte.

- **Aderir**: responda "y" quando o instalador perguntar, ou defina `FONTES_STATS=1` para o servidor
  Fontes.
- **Desistir**: execute o instalador de novo e pressione Enter nessa pergunta, ou remova
  `FONTES_STATS`. Apagar `stats.json` descarta tudo o que ainda não foi enviado.

**3. Relatórios de erro (somente quando você envia um).** Quando você pede um (`fontes report-bug`, ou
pedindo ao seu app de IA que relate um erro do Fontes), o Fontes mostra primeiro o relatório completo
e só o envia se você confirmar. Ele contém a versão do Fontes, a família do seu sistema operacional, o
código de jurisdição, o nome da ferramenta e a mensagem de erro da última chamada com falha (com suas
palavras de pesquisa e identificadores removidos), e uma nota, se você escrever uma. Não coloque
dados de clientes na nota. Para isso, o Fontes guarda o último erro no seu computador
(`last-error.json` na pasta de cache, substituído a cada vez); ele nunca é enviado por si só.

## Para onde vai e por quanto tempo é mantido

As contagens de uso e os relatórios de erro vão para um pequeno servidor mantido pelo desenvolvedor
do Fontes (`relay.kinetra.fit`). Ele não armazena endereços IP: eles são usados apenas na memória,
brevemente, para conter excessos de requisições, e o servidor web não mantém nenhum log de acesso
para ele. As contagens são somadas em totais diários; envios individuais não são mantidos. Os totais
são mantidos por até 2 anos e os relatórios de erro por até 1 ano; depois, são apagados. Nada é
vendido nem compartilhado.

Se esse servidor não puder ser acessado, nada é enviado: as contagens ficam no seu computador e os
relatórios de erro indicam o rastreador de issues (issue tracker) em vez disso.

## Quem é o responsável, e com qual base

O controlador dos dados das contagens de uso e dos relatórios de erro é Yüce Karapazar, o
desenvolvedor do Fontes. Contato: fontesmcp@proton.me.

A base legal é o seu consentimento (artigo 6(1)(a) do UK GDPR e do GDPR da UE). As contagens de uso
só são enviadas se você aderir, e um relatório de erro só depois que você o confirmar. Você pode
retirar o consentimento a qualquer momento desistindo conforme descrito acima; isso não afeta o que
foi enviado antes.

## Contato

Perguntas ou solicitações: escreva para fontesmcp@proton.me ou abra uma issue em
<https://github.com/ykarapazar/fontes/issues>.

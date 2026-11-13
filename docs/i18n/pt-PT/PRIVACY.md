> Esta é uma tradução assistida por máquina. Faz fé a versão inglesa.

# Aviso de privacidade do Fontes

O Fontes é executado no seu computador. As suas pesquisas e os documentos que abre ficam entre o seu
computador, as fontes oficiais que pesquisa e a aplicação de IA que utiliza (nos termos da própria
aplicação). O próprio Fontes não envia **nada, por predefinição**, aos programadores do Fontes.

## O que pode sair do seu computador, e quando

**1. Verificação de atualizações (ativada por predefinição).** Uma vez por dia, o Fontes pergunta ao
PyPI, o índice público de pacotes Python, qual é a versão mais recente. O pedido não contém nada
sobre si ou sobre o seu trabalho; o PyPI vê o seu endereço IP, como em qualquer transferência. Para a
desativar, defina `FONTES_NO_UPDATE_CHECK=1` (o aviso dentro da aplicação) e
`FONTES_NO_AUTO_UPDATE=1` (as atualizações automáticas do instalador).

**2. Contagens de utilização (desativadas, salvo se as ativar).** Se der o seu consentimento
(opt-in), uma vez por dia o Fontes envia:

- a versão do Fontes e a família do seu sistema operativo (macOS, Windows, Linux);
- por dia, quantas vezes cada ferramenta foi utilizada para cada código de jurisdição, por exemplo
  "2026-11-10, nl, search_caselaw, 12".

Essa é a mensagem completa. Nunca inclui as suas pesquisas, identificadores de documentos ou de
processos, o texto de documentos, o seu nome, uma conta ou qualquer identificador seu ou do seu
computador. As contagens aguardam no seu computador (na pasta de cache do Fontes, `stats.json`) até
serem enviadas; se o envio falhar, aguardam até ao dia seguinte.

- **Ativar**: responda "y" quando o instalador perguntar, ou defina `FONTES_STATS=1` para o servidor
  Fontes.
- **Desativar**: volte a executar o instalador e prima Enter nessa pergunta, ou remova
  `FONTES_STATS`. Apagar `stats.json` descarta tudo o que ainda não foi enviado.

**3. Relatórios de erro (apenas quando envia um).** Quando pede um (`fontes report-bug`, ou pedindo à
sua aplicação de IA que comunique um erro do Fontes), o Fontes mostra primeiro o relatório completo e
só o envia se o confirmar. Contém a versão do Fontes, a família do seu sistema operativo, o código de
jurisdição, o nome da ferramenta e a mensagem de erro da última chamada falhada (com as suas palavras
de pesquisa e identificadores removidos), e uma nota, se escrever uma. Não coloque dados de clientes
na nota. Para o efeito, o Fontes guarda o último erro no seu computador (`last-error.json` na pasta
de cache, substituído de cada vez); nunca é enviado por si só.

## Para onde vai e durante quanto tempo é conservado

As contagens de utilização e os relatórios de erro vão para um pequeno servidor gerido pelo
programador do Fontes (`relay.kinetra.fit`). Este não armazena endereços IP: são utilizados apenas
em memória, brevemente, para travar abusos de pedidos, e o servidor Web não mantém qualquer registo
de acesso para ele. As contagens são somadas em totais diários; os envios individuais não são
conservados. Os totais são conservados até 2 anos e os relatórios de erro até 1 ano; depois, são
apagados. Nada é vendido nem partilhado.

Se não for possível contactar esse servidor, nada é enviado: as contagens ficam no seu computador e
os relatórios de erro remetem antes para o sistema de registo de problemas (issue tracker).

## Quem é o responsável, e com que fundamento

O responsável pelo tratamento dos dados das contagens de utilização e dos relatórios de erro é Yüce
Karapazar, o programador do Fontes. Contacto: fontesmcp@proton.me.

O fundamento jurídico é o seu consentimento (artigo 6.º, n.º 1, alínea a), do UK GDPR e do RGPD da
UE). As contagens de utilização só são enviadas se der o seu consentimento, e um relatório de erro só
depois de o confirmar. Pode retirar o consentimento a qualquer momento desativando-o como descrito
acima; isso não afeta o que foi enviado antes.

## Contacto

Perguntas ou pedidos: escreva para fontesmcp@proton.me ou abra uma issue em
<https://github.com/ykarapazar/fontes/issues>.

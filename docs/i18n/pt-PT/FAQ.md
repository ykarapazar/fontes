> Esta é uma tradução assistida por máquina. Faz fé a versão inglesa.

# Fontes: perguntas e respostas

## O que é o Fontes?

Um servidor MCP gratuito e de código aberto (Apache 2.0). Permite que qualquer aplicação que utilize
o Model Context Protocol (Claude, Codex, Cursor, VS Code, Gemini CLI e outras) pesquise decisões
judiciais e legislação em direto nos sítios Web de tribunais e governos de 125 jurisdições e tribunais
internacionais, e de mais 91 países através do registo da Lexifina (ver abaixo). Cada resultado indica a
sua fonte e inclui a ligação para o original.

## Os textos são oficiais?

Na maioria dos casos, mas nem sempre.

- A maioria das fontes é gerida por um tribunal, um ministério ou um jornal oficial.
- Alguns textos consolidados são publicados por um governo, mas são expressamente não oficiais: só o
  jornal oficial é autêntico.
- Algumas fontes nem sequer são sítios governamentais (por exemplo LexiVox, LawPhil, Maqam,
  Wikisource).

O Fontes acrescenta um aviso "Unofficial source" (fonte não oficial) a todas as respostas que provêm
de uma delas. Antes de citar o que quer que seja, verifique a publicação oficial. A tabela de
cobertura no [README](README.md#cobertura) e `list_jurisdictions` indicam a fonte de cada
jurisdição.

## Que jurisdições abrange, e em que medida?

125 adaptadores: 108 Estados-membros da ONU, Hong Kong, Kosovo, Palestina, Taiwan, os DIFC Courts, os tribunais estaduais dos EUA e 11 tribunais e organismos internacionais (como o Tribunal Europeu dos Direitos Humanos, a UE, o TIJ e
a OMC).

A cobertura varia muito. Segundo um critério estrito (a jurisprudência do tribunal supremo da ordem
judicial comum, ou a constituição e as leis, alcançadas integralmente), 72 das 125 contam como
abrangidas. [COVERAGE.md](../../COVERAGE.md) indica, para cada jurisdição, o que o Fontes alcança, o
que não alcança e porquê.

## Preciso de uma chave de API?

Para quase todas as jurisdições, não. Algumas fontes precisam de uma chave gratuita: consulte
[KEYS.md](KEYS.md).

- **França:** sim. A França fica desativada até definir `WLM_FR_PISTE_CLIENT_ID` e
  `WLM_FR_PISTE_CLIENT_SECRET`. Obtêm-se a partir de uma conta PISTE gratuita (piste.gouv.fr) com uma
  aplicação subscrita ao Judilibre e ao Légifrance.
- **Estados Unidos:** opcional. A pesquisa de jurisprudência funciona sem chave, mas a chave de
  demonstração partilhada permite apenas cerca de 10 pesquisas por dia por endereço IP. Uma chave
  gratuita do api.data.gov em `WLM_US_GOVINFO_KEY` aumenta esse limite.
- **Tribunais estaduais dos EUA:** sim. A jurisprudência estadual (`us-states`) fica desativada até definir `WLM_US_COURTLISTENER_KEY` com o seu próprio token de API gratuito do CourtListener. O CourtListener é gerido pela organização sem fins lucrativos Free Law Project; não é uma fonte oficial, e todas as respostas indicam-no.

Defina-as como variáveis de ambiente para o servidor Fontes nas definições MCP da sua aplicação.
Os instaladores pedem-nas após a instalação, e o respetivo atalho **Add or change keys**
permite alterá-las mais tarde.

À parte isso, algumas fontes indicam nos seus termos que o acesso automatizado exige a autorização
do editor. Estão assinaladas como OFF e permanecem desativadas. Uma chave não altera isso; só a
autorização do editor o altera (defina então `WLM_PERMITTED=<codes>`).

## De onde vêm as versões passadas e os países adicionais?

Do [registo da Lexifina](https://github.com/lexifina/global-law), que mantém a legislação de cerca de 200
países como histórico git: cada alteração é um commit datado do dia em que entrou em vigor. O Fontes lê-o
através do servidor gratuito e alojado da Lexifina. Duas ferramentas usam-no: `get_law_on_date` (uma
disposição tal como estava em vigor numa data, também no passado, com a lei que a alterou pela última vez)
e `get_law_history` (cada lei que alterou uma disposição, ou a alteração palavra a palavra entre duas
datas). O Fontes lê ainda, desta forma, 91 países e territórios adicionais, apenas para legislação (por
exemplo, África do Sul, Quénia, México, Nova Zelândia, Rússia, Coreia do Sul, Bélgica, Lituânia, Ucrânia,
Malásia, Tailândia e Arábia Saudita). São separados das 125 jurisdições com cobertura oficial em direto, e
a cobertura por país varia muito (o registo nacional do Quénia tem 9 atos). Os atos da Índia também vêm do
registo da Lexifina, porque os termos do India Code proíbem o acesso automatizado; os seus acórdãos do
Supremo Tribunal são em direto.

A Lexifina não é o editor oficial, e o seu registo não é em direto: a Lexifina verifica cada país de tempos
a tempos, e o seu próprio relatório de 2026-11-26 contou 338 de 383 órgãos de legislação nacionais como não
verificados nos últimos 7 dias. Cada resposta indica a Lexifina como fonte, liga à página do editor oficial
e diz até onde vai o registo.

A Lexifina considera que os textos jurídicos oficiais não estão protegidos por direitos de autor, pelo que, em
alguns países, copia sítios cujos termos ou robots.txt o Fontes respeita. O Fontes continua a respeitar ambos
em tudo o que obtém diretamente; o que chega através da Lexifina segue o juízo jurídico próprio da Lexifina,
registado por país nos seus repositórios. Alguns restringem a utilização (o editor do Quénia: CC BY-NC). As
suas palavras de pesquisa, citações e datas vão para o servidor da Lexifina, nestes casos. Defina
`WLM_LEXIFINA=0` para o desligar. O servidor gratuito permite 60 chamadas por minuto e 10 000 por dia por
endereço de Internet; sem chave nem conta. O Fontes não é afiliado da Lexifina.

## O que sai do meu computador?

As suas pesquisas vão apenas para a fonte pesquisada (no caso das ferramentas e países da Lexifina, para o
servidor da Lexifina). O Fontes não mantém qualquer base de dados e não exige conta.

Além das fontes, o Fontes pergunta ao PyPI uma vez por dia se existe uma versão mais recente
(desative com `FONTES_NO_UPDATE_CHECK=1`). As contagens de utilização estão desativadas, salvo se as
ativar, e um relatório de erro só é enviado depois de o ter visto e confirmado. A sua aplicação de IA
vê a sua conversa nos termos dela.

Todos os pormenores: [PRIVACY.md](PRIVACY.md).

## Isto é aconselhamento jurídico?

Não. O Fontes é uma ferramenta de pesquisa. Encontra textos; não lhe diz o que significam para o seu
caso, e a sua utilização não cria uma relação advogado-cliente com ninguém. A aplicação de IA pode
interpretar mal um texto, por isso leia a decisão ou a disposição completa antes de confiar nela.
Para obter aconselhamento, consulte um advogado habilitado no local onde surge a sua questão.

## Quem o mantém? Vai continuar a funcionar?

Uma pessoa: Yüce Karapazar. Não há nenhuma empresa por trás do Fontes, nem contrato de assistência,
nem compromisso de nível de serviço. Não são prestados serviços jurídicos.

As fontes são verificadas uma vez por dia e os resultados são publicados na
[página de estado](https://ykarapazar.github.io/fontes/status/?lang=pt-PT). Os sítios Web de
tribunais e governos mudam sem aviso, pelo que uma fonte pode deixar de funcionar a qualquer momento.
Não há garantia de que qualquer fonte, ou o próprio Fontes, continue a funcionar. O Fontes é
fornecido "tal como está", sem garantia (secções 7 e 8 da [LICENSE](../../../LICENSE)).

## Um texto está errado, desatualizado ou uma fonte não funciona. Como o comunico?

- Abra uma issue com o formulário "Broken or wrong source":
  <https://github.com/ykarapazar/fontes/issues/new/choose>. Indique a jurisdição, o que perguntou, o
  que obteve e a página oficial que mostra o texto correto.
- Ou peça à sua aplicação de IA que "comunique um erro do Fontes" (ou execute `fontes report-bug`).
  Vê o relatório antes de qualquer envio.
- Ou escreva para fontesmcp@proton.me.

Não inclua dados de clientes nem factos confidenciais num relatório.

**Se gere uma das fontes** e algo está errado (os seus termos, o seu robots.txt, os seus limites de
pedidos), escreva para fontesmcp@proton.me. A fonte será corrigida ou desativada.

## Em que difere o Fontes das ferramentas de pesquisa jurídica alojadas?

- **É executado no seu computador.** Não há servidor do Fontes nem conta. Isso também significa que
  só funciona em aplicações capazes de iniciar um servidor MCP local (Claude Desktop, Codex, Cursor,
  VS Code e semelhantes), e não em aplicações apenas Web que só aceitam conectores alojados.
- **Não tem base de dados.** Cada pesquisa vai em direto ao próprio sítio ou API do editor, pelo que
  os resultados são tão atuais como a fonte, e a qualidade da pesquisa é a da própria fonte. Não há
  pesquisa semântica sobre um índice selecionado.
- **Não impõe limite de utilização.** O Fontes não tem um teto mensal de chamadas. Espaça os pedidos
  a cada sítio, e algumas fontes limitam a rapidez ou a frequência com que podem ser consultadas.
- **É de código aberto.** Pode ler cada adaptador e ver exatamente de onde provém cada texto.
- **Não há nenhum fornecedor por trás.** Nenhum contrato, serviço de assistência ou compromisso de
  disponibilidade (consulte "Quem o mantém?").

## Com que aplicações e sistemas funciona?

Com qualquer aplicação MCP capaz de executar um servidor local (stdio), por exemplo Claude Desktop,
Claude Code, Codex, Cursor, VS Code (GitHub Copilot), Gemini CLI, Windsurf, Zed, LM Studio e Cline. O
Fontes funciona em macOS, Windows e Linux, em qualquer sítio onde o uv funcione (Python 3.13+). Num
Mac ou PC com Windows, um instalador de um clique configura o Claude Desktop, Codex, Claude Code, Cursor, VS Code,
Windsurf, Gemini CLI, Zed, LM Studio e Cline de uma só vez. Passos para cada aplicação: [INSTALL.md](INSTALL.md).

## Posso contribuir com código?

De momento, não. Issues, comunicações sobre fontes e pedidos de jurisdições são bem-vindos. Consulte
[CONTRIBUTING.md](../../../CONTRIBUTING.md).

> Esta é uma tradução assistida por máquina. Faz fé a versão inglesa.

# Fontes: perguntas e respostas

## O que é o Fontes?

Um servidor MCP gratuito e de código aberto (Apache 2.0). Permite que qualquer aplicação que utilize
o Model Context Protocol (Claude, Codex, Cursor, VS Code, Gemini CLI e outras) pesquise decisões
judiciais e legislação em direto nos sítios Web de tribunais e governos de mais de 120 jurisdições e
tribunais internacionais (124 adaptadores). Cada resultado indica a sua fonte e inclui a ligação para
o original.

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

124 adaptadores: 108 Estados-membros da ONU, Hong Kong, Kosovo, Palestina, Taiwan, os DIFC Courts e
11 tribunais e organismos internacionais (como o Tribunal Europeu dos Direitos Humanos, a UE, o TIJ e
a OMC).

A cobertura varia muito. Segundo um critério estrito (a jurisprudência do tribunal supremo da ordem
judicial comum, ou a constituição e as leis, alcançadas integralmente), 72 das 124 contam como
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

Defina-as como variáveis de ambiente para o servidor Fontes nas definições MCP da sua aplicação.
Quando o instalador sair, pedi-las-á após a instalação, e o respetivo atalho **Add or change keys**
permite alterá-las mais tarde.

À parte isso, algumas fontes indicam nos seus termos que o acesso automatizado exige a autorização
do editor. Estão assinaladas como OFF e permanecem desativadas. Uma chave não altera isso; só a
autorização do editor o altera (defina então `WLM_PERMITTED=<codes>`).

## O que sai do meu computador?

As suas pesquisas vão apenas para a fonte pesquisada. O Fontes não mantém qualquer base de dados e
não exige conta.

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
Fontes funciona em macOS, Windows e Linux, em qualquer sítio onde o uv funcione (Python 3.13+). Está a
caminho um instalador de um clique para Mac e Windows. Configura o Claude Desktop, Codex, Claude
Code, Cursor, VS Code, Windsurf, Gemini CLI, Zed, LM Studio e Cline de uma só vez. Passos para cada
aplicação: [INSTALL.md](INSTALL.md).

## Posso contribuir com código?

De momento, não. Issues, comunicações sobre fontes e pedidos de jurisdições são bem-vindos. Consulte
[CONTRIBUTING.md](../../../CONTRIBUTING.md).

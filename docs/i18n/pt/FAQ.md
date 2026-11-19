> Esta é uma tradução feita com auxílio de máquina. A versão em inglês prevalece.

# Fontes: perguntas e respostas

## O que é o Fontes?

Um servidor MCP gratuito e de código aberto (Apache 2.0). Ele permite que qualquer app que use o
Model Context Protocol (Claude, Codex, Cursor, VS Code, Gemini CLI e outros) pesquise decisões
judiciais e legislação ao vivo nos sites de tribunais e governos de mais de 120 jurisdições e
tribunais internacionais (124 adaptadores). Cada resultado indica sua fonte e traz o link para o
original.

## Os textos são oficiais?

Na maioria das vezes, mas nem sempre.

- A maioria das fontes é mantida por um tribunal, um ministério ou um diário oficial.
- Alguns textos compilados são publicados por um governo, mas são expressamente não oficiais: só o
  diário oficial é autêntico.
- Algumas fontes nem sequer são sites governamentais (por exemplo LexiVox, LawPhil, Maqam,
  Wikisource).

O Fontes acrescenta um aviso "Unofficial source" (fonte não oficial) a toda resposta que vem de uma
delas. Antes de citar qualquer coisa, verifique a publicação oficial. A tabela de cobertura no
[README](README.md#cobertura) e `list_jurisdictions` indicam a fonte de cada jurisdição.

## Quais jurisdições ele cobre, e em que medida?

124 adaptadores: 108 Estados-membros da ONU, Hong Kong, Kosovo, Palestina, Taiwan, os DIFC Courts e
11 tribunais e órgãos internacionais (como a Corte Europeia de Direitos Humanos, a UE, a CIJ e a
OMC).

A cobertura varia muito. Por um critério estrito (os precedentes do tribunal de cúpula da justiça
comum, ou a constituição e as leis, alcançados por completo), 72 das 124 contam como cobertas.
[COVERAGE.md](../../COVERAGE.md) lista, para cada jurisdição, o que o Fontes alcança, o que não
alcança e por quê.

## Preciso de uma chave de API?

Para quase todas as jurisdições, não. Algumas fontes precisam de uma chave gratuita: veja
[KEYS.md](KEYS.md).

- **França:** sim. A França fica desativada até você definir `WLM_FR_PISTE_CLIENT_ID` e
  `WLM_FR_PISTE_CLIENT_SECRET`. Eles vêm de uma conta PISTE gratuita (piste.gouv.fr) com um app
  assinado no Judilibre e no Légifrance.
- **Estados Unidos:** opcional. A pesquisa de jurisprudência funciona sem chave, mas a chave de
  demonstração compartilhada permite apenas cerca de 10 pesquisas por dia por endereço IP. Uma chave
  gratuita do api.data.gov em `WLM_US_GOVINFO_KEY` aumenta esse limite.

Defina-as como variáveis de ambiente para o servidor Fontes nas configurações MCP do seu app. Quando
o instalador for lançado, ele as pedirá após a instalação, e o seu atalho **Add or change keys**
permite alterá-las depois.

À parte isso, algumas fontes dizem em seus termos que o acesso automatizado exige a permissão do
publicador. Elas estão marcadas como OFF e continuam desativadas. Uma chave não muda isso; só a
permissão do publicador muda (então defina `WLM_PERMITTED=<codes>`).

## O que sai do meu computador?

Suas pesquisas vão apenas para a fonte pesquisada. O Fontes não mantém banco de dados e não exige
conta.

Além das fontes, o Fontes pergunta ao PyPI uma vez por dia se existe uma versão mais nova (desative
com `FONTES_NO_UPDATE_CHECK=1`). As contagens de uso ficam desativadas, a menos que você as ative, e
um relatório de erro só é enviado depois que você o viu e confirmou. O seu app de IA vê a sua
conversa nos termos dele.

Todos os detalhes: [PRIVACY.md](PRIVACY.md).

## Isto é consultoria jurídica?

Não. O Fontes é uma ferramenta de pesquisa. Ele encontra textos; não diz o que eles significam para o
seu caso, e usá-lo não cria uma relação advogado-cliente com ninguém. O app de IA pode interpretar um
texto de forma errada, então leia a decisão ou o dispositivo na íntegra antes de confiar nele. Para
obter orientação, consulte um advogado habilitado no lugar onde surge a sua questão.

## Quem o mantém? Ele vai continuar funcionando?

Uma pessoa: Yüce Karapazar. Não há empresa por trás do Fontes, nem contrato de suporte, nem promessa
de nível de serviço. Não são oferecidos serviços jurídicos.

As fontes são verificadas uma vez por dia e os resultados são publicados na
[página de status](https://ykarapazar.github.io/fontes/status/?lang=pt). Sites de tribunais e
governos mudam sem aviso, então uma fonte pode parar de funcionar a qualquer momento. Não há garantia
de que qualquer fonte, ou o próprio Fontes, continue funcionando. O Fontes é fornecido "no estado em
que se encontra", sem garantia (seções 7 e 8 da [LICENSE](../../../LICENSE)).

## Um texto está errado, desatualizado ou uma fonte não funciona. Como informo?

- Abra uma issue com o formulário "Broken or wrong source":
  <https://github.com/ykarapazar/fontes/issues/new/choose>. Diga qual jurisdição, o que você
  perguntou, o que recebeu e a página oficial que mostra o texto correto.
- Ou peça ao seu app de IA que "relate um erro do Fontes" (ou execute `fontes report-bug`). Você vê o
  relatório antes de qualquer envio.
- Ou escreva para fontesmcp@proton.me.

Não inclua dados de clientes nem fatos confidenciais em um relatório.

**Se você administra uma das fontes** e algo está errado (seus termos, seu robots.txt, seus limites
de requisições), escreva para fontesmcp@proton.me. A fonte será corrigida ou desativada.

## Em que o Fontes difere das ferramentas de pesquisa jurídica hospedadas?

- **Ele é executado no seu computador.** Não há servidor do Fontes nem conta. Isso também significa
  que ele só funciona em apps capazes de iniciar um servidor MCP local (Claude Desktop, Codex,
  Cursor, VS Code e similares), não em apps só para web que aceitam apenas conectores hospedados.
- **Ele não tem banco de dados.** Cada pesquisa vai ao vivo ao próprio site ou API do publicador,
  então os resultados são tão atuais quanto a fonte, e a qualidade da pesquisa é a da própria fonte.
  Não há pesquisa semântica sobre um índice curado.
- **Ele não impõe limite de uso.** O Fontes não tem um teto mensal de chamadas. Ele espaça as
  requisições a cada site, e algumas fontes limitam a rapidez ou a frequência com que podem ser
  consultadas.
- **Ele é de código aberto.** Você pode ler cada adaptador e ver exatamente de onde vem cada texto.
- **Não há fornecedor por trás.** Nenhum contrato, central de suporte ou promessa de disponibilidade
  (veja "Quem o mantém?").

## Com quais apps e sistemas ele funciona?

Com qualquer app MCP capaz de executar um servidor local (stdio), por exemplo Claude Desktop, Claude
Code, Codex, Cursor, VS Code (GitHub Copilot), Gemini CLI, Windsurf, Zed, LM Studio e Cline. O Fontes
roda no macOS, Windows e Linux, em qualquer lugar onde o uv rode (Python 3.13+). No Mac ou PC com Windows, um instalador
de um clique configura o Claude Desktop, Codex, Claude Code,
Cursor, VS Code, Windsurf, Gemini CLI, Zed, LM Studio e Cline de uma só vez. Etapas para cada app:
[INSTALL.md](INSTALL.md).

## Posso contribuir com código?

No momento, não. Issues, relatos sobre fontes e pedidos de jurisdições são bem-vindos. Veja
[CONTRIBUTING.md](../../../CONTRIBUTING.md).

> Esta é uma tradução feita com auxílio de máquina. A versão em inglês prevalece.

# Chaves de API

Quase todas as fontes do Fontes funcionam sem chave. Duas precisam de uma chave gratuita:

| Chave | Libera | Sem ela |
|---|---|---|
| `WLM_FR_PISTE_CLIENT_ID` + `WLM_FR_PISTE_CLIENT_SECRET` | França: Judilibre (decisões judiciais) e Légifrance (legislação) | A França fica desativada. `list_jurisdictions` a mostra como inativa. |
| `WLM_US_GOVINFO_KEY` | Estados Unidos: pesquisa no govinfo (decisões de tribunais federais, Statutes at Large, public laws) | O Fontes usa a `DEMO_KEY` compartilhada: cerca de 10 pesquisas por dia por endereço IP. Abrir uma decisão conhecida e o US Code não exigem chave. |

As chaves são opcionais. Você pode adicioná-las depois.

## Adicionar uma chave

**Com o instalador.** Depois que o Fontes é configurado, o instalador oferece adicionar chaves. No Mac,
clique em **Adicionar chaves**, ou em **Concluído** para pular; no Windows, responda à pergunta (pressione
Enter para pular). Para adicionar ou alterar chaves depois, execute **Add or change keys**:

- Mac: abra de novo o app Fontes Installer e escolha **Adicionar ou alterar chaves**.
- Windows: abra o menu Iniciar e escolha **Fontes** → **Adicionar ou alterar chaves**.

O que você digita fica oculto. Para cada chave: cole-a, pressione Enter para manter a atual ou digite
`-` para removê-la. As chaves vão para todos os apps que já têm o Fontes.

**Com a extensão do Claude Desktop (.mcpb).** Abra Claude > Settings > Extensions > Fontes e preencha
os campos. Todos são opcionais.

**Manualmente.** Adicione as variáveis ao bloco `env` da entrada `fontes` na configuração MCP do seu
app:

```json
"fontes": {
  "command": "...",
  "args": ["..."],
  "env": { "WLM_US_GOVINFO_KEY": "your-key" }
}
```

Reinicie o app depois de qualquer alteração.

## França: PISTE (gratuito)

1. Crie uma conta em [piste.gouv.fr](https://piste.gouv.fr). Isso implica aceitar os termos do PISTE
   (CGU).
2. Vá em API > **Consentement CGU API**. Aceite os termos de **JUDILIBRE** e **Légifrance**
   (produção).
3. Crie um **app de produção**. O `APP_SANDBOX` criado para você não acessa a produção. Em "Modifier
   l'application", marque **JUDILIBRE (production)** e **Légifrance (production)** e aplique.
4. Abra a aba **Authentification** do app. Copie o `client_id` e o `client_secret`.
5. Execute **Add or change keys** e cole-os.

Termos, em resumo:

- Dados: Licence Ouverte / Etalab 2.0. A reutilização, inclusive comercial, é permitida com
  atribuição.
- Não publique nem compartilhe as suas credenciais. Avise o PISTE se elas vazarem.
- A API do Légifrance é um serviço beta. Pode ser suspensa e tem cotas (por segundo, minuto e dia).
- Os textos do Légifrance não são a versão autêntica. Só o PDF assinado do Journal officiel é.
- Judilibre: não use nomes de juízes ou de escrivães para avaliar, comparar ou prever o trabalho
  deles (Code de l'organisation judiciaire, art. L111-13; é crime).
- Judilibre: siga o GDPR. Não tente reidentificar as partes.

As suas cotas estão no PISTE, em API Sélectionnées > Actions > Consulter les quotas.

## Estados Unidos: api.data.gov (gratuito)

1. Acesse [govinfo.gov/api-signup](https://www.govinfo.gov/api-signup) (a chave aparece na tela) ou
   [api.data.gov/signup](https://api.data.gov/signup/) (a chave é enviada por e-mail).
2. Informe o seu nome e e-mail. O campo "how will you use it" é opcional.
3. Copie a chave de 40 caracteres.
4. Execute **Add or change keys** e cole-a como chave dos EUA.

Termos, em resumo:

- Com a sua própria chave, o govinfo permite até 36.000 requisições por hora.
- Não encontramos termos de serviço específicos da API (api.data.gov/terms/ não existe). Não
  verificado. Veja as [políticas do govinfo](https://www.govinfo.gov/about/policies) e a
  [política de privacidade do data.gov](https://data.gov/privacy-policy/).
- Não compartilhe a chave.

## Onde as chaves ficam guardadas

- **Instalador ou manualmente:** em texto simples no arquivo de configuração MCP de cada app, no bloco
  `env` da entrada `fontes`. Qualquer pessoa que consiga ler os seus arquivos de usuário consegue ler
  as chaves.
  - Claude Desktop: `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac),
    `%APPDATA%\Claude\claude_desktop_config.json` (Windows)
  - Claude Code: `~/.claude.json`
  - Codex: `~/.codex/config.toml`
  - Cursor: `~/.cursor/mcp.json`
  - VS Code (Copilot): `~/.copilot/mcp-config.json`
  - Windsurf: `~/.config/devin/mcp_config.json` ou `~/.codeium/windsurf/mcp_config.json`
    (Windows: `%APPDATA%\devin\mcp_config.json`)
  - Gemini CLI: `~/.gemini/settings.json`
  - Zed: `~/.config/zed/settings.json` (Windows: `%APPDATA%\Zed\settings.json`)
  - LM Studio: `~/.lmstudio/mcp.json`
  - Cline: `~/.cline/data/settings/cline_mcp_settings.json`
- **Extensão do Claude Desktop (.mcpb):** o Claude guarda esses campos nas configurações dele e os
  protege com o armazenamento seguro do seu sistema (Keychain no Mac, Credential Manager no Windows).

Antes de cada alteração, o instalador salva uma cópia do arquivo de configuração ao lado dele
(`<file>.fontes-backup-<time>`). Cópias feitas depois que você adicionou chaves também contêm as
chaves. Apague as cópias antigas de que não precisar.

## Alterar ou remover uma chave

- Execute **Add or change keys**. Cole uma nova chave para substituí-la ou digite `-` para removê-la.
- Ou edite o bloco `env` manualmente e reinicie o app.
- Desinstalar o Fontes remove toda a entrada dele, inclusive as chaves. As cópias de backup não são
  apagadas.
- Se uma chave vazou, substitua-a também na origem: no PISTE, gere novas credenciais para o seu app;
  no api.data.gov, cadastre-se para obter uma nova chave.

## Mensagens que você pode ver

| Mensagem | Significado |
|---|---|
| `France needs a free PISTE key: set WLM_FR_PISTE_CLIENT_ID and WLM_FR_PISTE_CLIENT_SECRET.` | Não há chave da França. Adicione uma. |
| `Inactive: needs a free PISTE account. ...` (em `list_jurisdictions`) | O mesmo. |
| `PISTE refused the client credentials ...` | O ID ou o secret está errado ou não é mais válido. Copie os dois de novo na aba Authentification. |
| `PISTE denied access to the ... API: subscribe the application to ... and accept its CGU on piste.gouv.fr.` | O seu app não está assinado nessa API, ou você não aceitou os termos dela. Veja as etapas 2 e 3. |
| `Using govinfo DEMO_KEY (about 10 searches/day per IP) ...` | Não há chave dos EUA. A pesquisa funciona para algumas chamadas por dia. |
| `govinfo rate limit reached (Retry-After ...). DEMO_KEY allows only about 10 searches a day per IP ...` | A chave de demonstração se esgotou. Adicione a sua própria chave. |
| `govinfo refused the API key (WLM_US_GOVINFO_KEY).` | A chave está errada ou ainda não foi confirmada pelo e-mail. |

Um valor vazio conta como ausência de chave.

## Permissões (WLM_PERMITTED)

Isto não é uma chave de API, e o instalador não o define. **Defina-o somente se você mesmo tiver essa
permissão.**

Algumas fontes ficam desativadas por padrão porque os termos ou o robots.txt delas proíbem o uso
automatizado sem permissão. Se você tiver a permissão do publicador, ative uma fonte adicionando o
código dela a `WLM_PERMITTED`, separado por vírgulas, no bloco `env`: `"WLM_PERMITTED": "in,de"`.

| Código | Fonte |
|---|---|
| `az` | Azerbaijão: e-qanun.az (Ministério da Justiça) |
| `bh` | Bahrein: Legislation and Legal Opinion Commission (lloc.gov.bh) |
| `co` | Colômbia: Función Pública, Gestor Normativo (legislação compilada) |
| `de` | Alemanha: NeuRIS (portal federal de informação jurídica, serviço de teste) |
| `difc` | Dubai International Financial Centre Courts (difccourts.ae) |
| `gr` | Grécia: Imprensa Nacional, pesquisa no Diário Oficial do Governo (search.et.gr) |
| `in` | Índia: India Code (indiacode.gov.in) |
| `mu` | Maurício: Supreme Court (supremecourt.govmu.org) |
| `sg` | Singapura: decisões judiciais (elitigation.sg) |

Sem permissão, o Fontes diz: `Off by default (<code>): the terms or robots.txt of ... forbid
automated use without the operator's permission.`

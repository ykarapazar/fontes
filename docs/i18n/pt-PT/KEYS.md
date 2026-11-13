> Esta é uma tradução assistida por máquina. Faz fé a versão inglesa.

# Chaves de API

Quase todas as fontes do Fontes funcionam sem chave. Duas precisam de uma chave gratuita:

| Chave | Desbloqueia | Sem ela |
|---|---|---|
| `WLM_FR_PISTE_CLIENT_ID` + `WLM_FR_PISTE_CLIENT_SECRET` | França: Judilibre (decisões judiciais) e Légifrance (legislação) | A França fica desativada. `list_jurisdictions` mostra-a como inativa. |
| `WLM_US_GOVINFO_KEY` | Estados Unidos: pesquisa no govinfo (decisões de tribunais federais, Statutes at Large, public laws) | O Fontes utiliza a `DEMO_KEY` partilhada: cerca de 10 pesquisas por dia por endereço IP. Abrir uma decisão conhecida e o US Code não exigem chave. |

As chaves são opcionais. Pode adicioná-las mais tarde.

## Adicionar uma chave

**Com o instalador.** Durante a instalação, o instalador pergunta se pretende adicionar chaves.
Escolha **Agora não** (ou prima Enter) para saltar este passo. Para adicionar ou alterar chaves mais
tarde, execute **Add or change keys**:

- Mac: volte a abrir a aplicação Fontes Installer e escolha **Adicionar ou alterar chaves**, ou faça
  duplo clique em `Add or change keys.command` na pasta do instalador.
- Windows: faça duplo clique em `Add or change keys.cmd` na pasta do instalador. O programa de
  configuração para Windows, quando estiver disponível, coloca-o também em Start menu > Fontes.

O que escreve fica oculto. Para cada chave: cole-a, prima Enter para manter a atual ou escreva `-`
para a remover. As chaves vão para todas as aplicações que já têm o Fontes.

**Com a extensão do Claude Desktop (.mcpb).** Abra Claude > Settings > Extensions > Fontes e preencha
os campos. Todos são opcionais.

**Manualmente.** Adicione as variáveis ao bloco `env` da entrada `fontes` na configuração MCP da sua
aplicação:

```json
"fontes": {
  "command": "...",
  "args": ["..."],
  "env": { "WLM_US_GOVINFO_KEY": "your-key" }
}
```

Reinicie a aplicação depois de qualquer alteração.

## França: PISTE (gratuito)

1. Crie uma conta em [piste.gouv.fr](https://piste.gouv.fr). Isso implica aceitar os termos do PISTE
   (CGU).
2. Aceda a API > **Consentement CGU API**. Aceite os termos de **JUDILIBRE** e **Légifrance**
   (produção).
3. Crie uma **aplicação de produção**. A `APP_SANDBOX` criada para si não acede à produção. Em
   "Modifier l'application", assinale **JUDILIBRE (production)** e **Légifrance (production)** e
   aplique.
4. Abra o separador **Authentification** da aplicação. Copie o `client_id` e o `client_secret`.
5. Execute **Add or change keys** e cole-os.

Termos, em resumo:

- Dados: Licence Ouverte / Etalab 2.0. A reutilização, incluindo comercial, é permitida com
  atribuição.
- Não publique nem partilhe as suas credenciais. Informe o PISTE se forem divulgadas.
- A API do Légifrance é um serviço beta. Pode ser suspensa e tem quotas (por segundo, minuto e dia).
- Os textos do Légifrance não são a versão autêntica. Só o PDF assinado do Journal officiel o é.
- Judilibre: não utilize nomes de juízes ou de oficiais de justiça para avaliar, comparar ou prever o
  seu trabalho (Code de l'organisation judiciaire, art. L111-13; é crime).
- Judilibre: cumpra o RGPD. Não tente reidentificar as partes.

As suas quotas estão no PISTE, em API Sélectionnées > Actions > Consulter les quotas.

## Estados Unidos: api.data.gov (gratuito)

1. Aceda a [govinfo.gov/api-signup](https://www.govinfo.gov/api-signup) (a chave aparece no ecrã)
   ou a [api.data.gov/signup](https://api.data.gov/signup/) (a chave é enviada por e-mail).
2. Indique o seu nome e e-mail. O campo "how will you use it" é opcional.
3. Copie a chave de 40 caracteres.
4. Execute **Add or change keys** e cole-a como chave dos EUA.

Termos, em resumo:

- Com a sua própria chave, o govinfo permite até 36 000 pedidos por hora.
- Não encontrámos termos de serviço específicos da API (api.data.gov/terms/ não existe). Não
  verificado. Consulte as [políticas do govinfo](https://www.govinfo.gov/about/policies) e a
  [política de privacidade do data.gov](https://data.gov/privacy-policy/).
- Não partilhe a chave.

## Onde ficam guardadas as chaves

- **Instalador ou manualmente:** em texto simples no ficheiro de configuração MCP de cada aplicação,
  no bloco `env` da entrada `fontes`. Qualquer pessoa que consiga ler os seus ficheiros de utilizador
  consegue ler as chaves.
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
- **Extensão do Claude Desktop (.mcpb):** o Claude guarda estes campos nas suas definições e
  protege-os com o armazenamento seguro do seu sistema (Keychain no Mac, Credential Manager no
  Windows).

Antes de cada alteração, o instalador guarda uma cópia do ficheiro de configuração ao lado dele
(`<file>.fontes-backup-<time>`). As cópias feitas depois de ter adicionado chaves também contêm as
chaves. Apague as cópias antigas de que não precisa.

## Alterar ou remover uma chave

- Execute **Add or change keys**. Cole uma nova chave para a substituir ou escreva `-` para a
  remover.
- Ou edite o bloco `env` manualmente e reinicie a aplicação.
- Desinstalar o Fontes remove toda a sua entrada, incluindo as chaves. As cópias de segurança não são
  apagadas.
- Se uma chave tiver sido divulgada, substitua-a também na origem: no PISTE, gere novas credenciais
  para a sua aplicação; no api.data.gov, registe-se para obter uma nova chave.

## Mensagens que pode ver

| Mensagem | Significado |
|---|---|
| `France needs a free PISTE key: set WLM_FR_PISTE_CLIENT_ID and WLM_FR_PISTE_CLIENT_SECRET.` | Não há chave de França. Adicione uma. |
| `Inactive: needs a free PISTE account. ...` (em `list_jurisdictions`) | O mesmo. |
| `PISTE refused the client credentials ...` | O ID ou o secret está errado ou já não é válido. Copie ambos novamente a partir do separador Authentification. |
| `PISTE denied access to the ... API: subscribe the application to ... and accept its CGU on piste.gouv.fr.` | A sua aplicação não está subscrita a essa API, ou não aceitou os respetivos termos. Consulte os passos 2 e 3. |
| `Using govinfo DEMO_KEY (about 10 searches/day per IP) ...` | Não há chave dos EUA. A pesquisa funciona para algumas chamadas por dia. |
| `govinfo rate limit reached (Retry-After ...). DEMO_KEY allows only about 10 searches a day per IP ...` | A chave de demonstração esgotou-se. Adicione a sua própria chave. |
| `govinfo refused the API key (WLM_US_GOVINFO_KEY).` | A chave está errada ou ainda não foi confirmada por e-mail. |

Um valor vazio conta como ausência de chave.

## Autorizações (WLM_PERMITTED)

Isto não é uma chave de API, e o instalador não o define. **Defina-o apenas se tiver, o próprio,
essa autorização.**

Algumas fontes estão desativadas por predefinição porque os seus termos ou o seu robots.txt proíbem
a utilização automatizada sem autorização. Se tiver a autorização do editor, ative uma fonte
adicionando o respetivo código a `WLM_PERMITTED`, separado por vírgulas, no bloco `env`:
`"WLM_PERMITTED": "in,de"`.

| Código | Fonte |
|---|---|
| `az` | Azerbaijão: e-qanun.az (Ministério da Justiça) |
| `bh` | Barém: Legislation and Legal Opinion Commission (lloc.gov.bh) |
| `co` | Colômbia: Función Pública, Gestor Normativo (legislação consolidada) |
| `de` | Alemanha: NeuRIS (portal federal de informação jurídica, serviço de teste) |
| `difc` | Dubai International Financial Centre Courts (difccourts.ae) |
| `gr` | Grécia: Imprensa Nacional, pesquisa no Jornal Oficial do Governo (search.et.gr) |
| `in` | Índia: India Code (indiacode.gov.in) |
| `mu` | Maurícia: Supreme Court (supremecourt.govmu.org) |
| `sg` | Singapura: decisões judiciais (elitigation.sg) |

Sem autorização, o Fontes indica: `Off by default (<code>): the terms or robots.txt of ... forbid
automated use without the operator's permission.`

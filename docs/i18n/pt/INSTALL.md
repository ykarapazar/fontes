> Esta é uma tradução feita com auxílio de máquina. A versão em inglês prevalece.

# Como instalar o Fontes

O Fontes permite que o seu app de IA consulte decisões judiciais e legislação ao vivo nos sites de
tribunais e governos de mais de 120 jurisdições. Cada resultado traz o link para o original. É um
servidor MCP padrão, então funciona em qualquer app capaz de executar um servidor MCP local: Claude
Desktop, Codex, Claude Code, Cursor, VS Code (GitHub Copilot), Gemini CLI, Windsurf, Zed, LM Studio,
Cline e outros.

Escolha o seu app, siga as etapas dele e depois [verifique se funciona](#verificar-se-funciona).

## Claude Desktop

1. Baixe o arquivo `.mcpb` do Fontes na
   [versão mais recente](https://github.com/ykarapazar/fontes/releases/latest).
2. Clique duas vezes nele. O Claude Desktop o abre.
3. Clique em **Install**.

## Codex

Em um terminal:

```bash
codex mcp add fontes -- uvx fontes-mcp
```

A CLI do Codex e a extensão do Codex para IDE compartilham esta configuração
(`~/.codex/config.toml`). Você precisa do [uv](#você-precisa-do-uv).

## Claude Code

Em um terminal:

```bash
claude mcp add fontes -- uvx fontes-mcp
```

Você precisa do [uv](#você-precisa-do-uv).

## Outros apps

Cada um destes precisa do [uv](#você-precisa-do-uv). Adicione a entrada, salve e depois feche e abra
o app de novo.

**Cursor:** em `~/.cursor/mcp.json` (todos os projetos) ou `.cursor/mcp.json` (um projeto):

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**VS Code (GitHub Copilot):** execute **MCP: Add Server** na Paleta de Comandos (Command Palette),
escolha **Command (stdio)**, digite `uvx fontes-mcp` e dê ao servidor o nome `fontes`. Ou adicione isto a
`~/.copilot/mcp-config.json`:

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

Configurações mais antigas do VS Code usam `.vscode/mcp.json`, em que a chave de nível superior é
`servers` em vez de `mcpServers`.

**Gemini CLI:** em um terminal, `gemini mcp add -s user fontes uvx fontes-mcp`. Ou adicione isto a
`~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Zed:** abra o seu arquivo de configurações (**zed: open settings file**) e adicione:

```json
{
  "context_servers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**LM Studio:** na barra lateral direita, abra a aba **Program**, clique em **Install → Edit
mcp.json** e adicione:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Cline:** clique no ícone **MCP Servers**, abra a aba **Configure**, clique em **Configure MCP
Servers** e adicione a mesma entrada `mcpServers` usada no LM Studio.

**Claude Desktop, manualmente** (em vez do arquivo `.mcpb`): adicione a mesma entrada `mcpServers` a
`claude_desktop_config.json` (macOS: `~/Library/Application Support/Claude/`, Windows:
`%APPDATA%\Claude\`).

**Qualquer outro app MCP** (Windsurf e outros): a documentação do próprio app informa onde ele guarda
os seus servidores MCP. A maioria aceita a mesma entrada: comando `uvx`, argumento `fontes`.

Se o app não encontrar o `uvx`, use o caminho completo dele (no macOS e no Linux, `which uvx` o
mostra).

## Você precisa do uv

O Codex, o Claude Code e os outros apps iniciam o Fontes com o `uvx`, que vem com o **uv**, uma
pequena ferramenta gratuita da Astral. Para instalá-lo, veja o
[guia da Astral](https://docs.astral.sh/uv/getting-started/installation/) ou execute:

- macOS ou Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Windows (PowerShell): `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

## Chaves

Algumas fontes precisam de uma chave gratuita: veja [KEYS.md](KEYS.md).

## Verificar se funciona

Em um novo chat, pergunte: *"Em quais jurisdições o Fontes pode pesquisar?"* O app deve responder com
uma lista de países. Se não responder, feche e abra o app mais uma vez.

## Instalador de um clique (Mac)

O instalador para Mac configura o Fontes em todos os seus apps de uma vez: Claude Desktop, Codex,
Claude Code, Cursor, VS Code (GitHub Copilot), Windsurf, Gemini CLI, Zed, LM Studio e Cline. Um
instalador para Windows está a caminho; até lá, use as etapas do seu app acima.

**Antes de começar:** feche completamente cada um desses apps. Isso é mais importante para o Claude
Code: enquanto está em execução, ele reescreve `~/.claude.json` e pode desfazer a alteração do
instalador. Se você não puder fechar o Claude Code, adicione o Fontes a ele com `claude mcp add`
(veja [Claude Code](#claude-code)).

**Mac**

1. Baixe o instalador para Mac (`Fontes-Installer-…-mac.zip`) da
   [versão mais recente](https://github.com/ykarapazar/fontes/releases/latest) e clique duas vezes nele para descompactá-lo.
2. Clique duas vezes em **Fontes Installer**. Se o Mac perguntar se você quer abrir um app baixado da
   internet, clique em **Open**.
3. Escolha **Instalar** e clique em **OK**. A configuração leva cerca de um minuto.
4. Uma mensagem lista os apps que ele configurou. Clique em **Concluído** e depois abra esses apps de
   novo. Para adicionar antes as chaves gratuitas opcionais, clique em **Adicionar chaves**; veja
   [A etapa das chaves](#a-etapa-das-chaves).

**Windows** (quando o instalador para Windows for lançado)

1. Descompacte o **Fontes Installer** baixado (botão direito → Extract All).
2. Clique duas vezes em **Install Fontes.cmd**.
   - Se o Windows mostrar "Windows protected your PC": clique em **More info** e depois em
     **Run anyway**.
3. Quando perguntado se deve enviar contagens de uso anônimas, pressione Enter para não.
4. Ele pergunta se você quer adicionar chaves agora. Pressione Enter para pular; veja
   [A etapa das chaves](#a-etapa-das-chaves).
5. Quando aparecer **Pronto**, abra os seus apps de IA de novo. Se algum ainda estava em execução,
   feche-o completamente (também na bandeja do sistema, perto do relógio) e abra-o de novo.

No final, o instalador lista os apps que configurou.

### Quais apps ele configura

Ele configura um app somente se a pasta de configurações desse app já existir no seu computador. O
Claude Code só é configurado se `~/.claude.json` existir. O Claude Desktop é sempre configurado. Cada
app recebe uma entrada, `fontes`, neste arquivo:

| App | Arquivo (Mac e Linux) | Arquivo (Windows) |
|---|---|---|
| Claude Desktop | `~/Library/Application Support/Claude/claude_desktop_config.json` (Linux: `~/.config/Claude/`) | `%APPDATA%\Claude\claude_desktop_config.json`, e a cópia própria da versão da Microsoft Store |
| Codex | `~/.codex/config.toml` | `%USERPROFILE%\.codex\config.toml` |
| Claude Code | `~/.claude.json` | `%USERPROFILE%\.claude.json` |
| Cursor | `~/.cursor/mcp.json` | `%USERPROFILE%\.cursor\mcp.json` |
| VS Code (Copilot) | `~/.copilot/mcp-config.json` | `%USERPROFILE%\.copilot\mcp-config.json` |
| Windsurf | `~/.config/devin/mcp_config.json`, ou `~/.codeium/windsurf/mcp_config.json` em versões mais antigas | `%APPDATA%\devin\mcp_config.json`, ou `%USERPROFILE%\.codeium\windsurf\mcp_config.json` |
| Gemini CLI | `~/.gemini/settings.json` | `%USERPROFILE%\.gemini\settings.json` |
| Zed | `~/.config/zed/settings.json` | `%APPDATA%\Zed\settings.json` |
| LM Studio | `~/.lmstudio/mcp.json` | `%USERPROFILE%\.lmstudio\mcp.json` |
| Cline | `~/.cline/data/settings/cline_mcp_settings.json` | `%USERPROFILE%\.cline\data\settings\cline_mcp_settings.json` |

O VS Code é configurado se `~/.copilot` ou a pasta de configurações do próprio VS Code existir.

Dois apps precisam de mais uma etapa:

- **Windsurf:** depois de reabri-lo, clique em atualizar (refresh) no Cascade.
- **Cline dentro da extensão antiga do VS Code:** adicione o Fontes manualmente (veja
  [Cline](#outros-apps)).

### A etapa das chaves

Logo após a instalação, o instalador oferece adicionar as chaves gratuitas da França e dos EUA. Para
adicioná-las ou alterá-las depois:

- **Mac:** abra de novo o **Fontes Installer** e escolha **Adicionar ou alterar chaves**.
- **Windows:** clique duas vezes em **Add or change keys.cmd** na pasta do instalador.

O que você digita fica oculto. As chaves vão para todos os apps que já têm o Fontes. Depois, feche e
abra os apps de novo. Onde obter as chaves e o que elas liberam: [KEYS.md](KEYS.md).

### Backups, novas execuções e remoção

O instalador só altera a entrada `fontes`. Todas as outras configurações e comentários continuam
como estavam. Antes de alterar um arquivo, ele salva uma cópia ao lado, chamada
`<file>.fontes-backup-<date>`. Cópias feitas depois que você adicionou chaves contêm essas chaves:
apague as que não precisar mais. Ele também instala o uv. Executá-lo de novo é seguro: ele repara a
configuração e não altera mais nada.

Para remover o Fontes, abra o **Fontes Installer** e escolha **Remover** (Mac), ou clique duas vezes em
**Uninstall Fontes.cmd** (Windows). Ele remove a entrada `fontes`, inclusive as chaves, de todos os
apps. As suas outras configurações e as cópias de backup permanecem.

## Atualizações

- **Instalador e arquivo `.mcpb`:** você não precisa fazer nada. Uma vez por dia, quando o app
  inicia, o Fontes verifica em segundo plano se há uma versão mais nova e a deixa pronta; na próxima
  vez que o app iniciar, ele a usa. Se uma atualização não puder ser baixada ou não funcionar, o
  Fontes continua usando a versão que funcionava.
- **`uvx`:** o Fontes avisa quando há uma versão mais nova, no topo da sua lista de jurisdições. Para
  sempre executar a versão mais nova, use `fontes-mcp@latest` no lugar de `fontes-mcp`.

Nenhuma informação sobre você ou suas pesquisas é enviada a lugar nenhum para isso.

## Privacidade

Por padrão, o Fontes não envia nada sobre você ou suas pesquisas. As contagens de uso dependem da sua
autorização (opt-in), e um relatório de erro só é enviado depois que você o vê e confirma. Detalhes:
[PRIVACY.md](PRIVACY.md).

## Como remover

Remova a entrada `fontes` das configurações MCP do seu app (no Claude Code:
`claude mcp remove fontes`) e depois feche e abra o app de novo.

## Bom saber

O Fontes lê fontes públicas, principalmente sites de tribunais e governos. Ele marca as não oficiais
nas respostas. Sempre abra o link da fonte antes de confiar em uma decisão ou em um dispositivo.

Se algo der errado, envie para fontesmcp@proton.me o que você fez e o erro que apareceu.

## Antes de confiar nele

- O Fontes é uma ferramenta de pesquisa, não consultoria jurídica. Usá-lo não torna ninguém seu
  advogado.
- Ele é fornecido "no estado em que se encontra", sem garantia, e seus autores não são responsáveis
  pela forma como ele é usado, na medida permitida por lei. Os termos completos estão na
  [licença](../../../LICENSE) (Apache 2.0).

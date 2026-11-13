> Esta é uma tradução assistida por máquina. Faz fé a versão inglesa.

# Como instalar o Fontes

O Fontes permite que a sua aplicação de IA consulte decisões judiciais e legislação em direto nos
sítios Web de tribunais e governos de mais de 120 jurisdições. Cada resultado inclui a ligação para o
original. É um servidor MCP normal, pelo que funciona em qualquer aplicação capaz de executar um
servidor MCP local: Claude Desktop, Codex, Claude Code, Cursor, VS Code (GitHub Copilot), Gemini CLI,
Windsurf, Zed, LM Studio, Cline e outras.

Escolha a sua aplicação, siga os respetivos passos e depois
[verifique se funciona](#verificar-se-funciona).

## Claude Desktop

1. Transfira o ficheiro `.mcpb` do Fontes a partir da
   [versão mais recente](https://github.com/ykarapazar/fontes/releases/latest).
2. Faça duplo clique nele. O Claude Desktop abre-o.
3. Clique em **Install**.

## Codex

Num terminal:

```bash
codex mcp add fontes -- uvx fontes-mcp
```

A CLI do Codex e a extensão do Codex para IDE partilham esta configuração (`~/.codex/config.toml`).
Precisa do [uv](#precisa-do-uv).

## Claude Code

Num terminal:

```bash
claude mcp add fontes -- uvx fontes-mcp
```

Precisa do [uv](#precisa-do-uv).

## Outras aplicações

Cada uma destas precisa do [uv](#precisa-do-uv). Adicione a entrada, guarde e depois feche e volte a
abrir a aplicação.

**Cursor:** em `~/.cursor/mcp.json` (todos os projetos) ou `.cursor/mcp.json` (um projeto):

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**VS Code (GitHub Copilot):** execute **MCP: Add Server** a partir da Paleta de Comandos (Command
Palette), escolha **Command (stdio)**, introduza `uvx fontes-mcp` e dê ao servidor o nome `fontes`. Ou
adicione isto a `~/.copilot/mcp-config.json`:

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

Configurações mais antigas do VS Code utilizam `.vscode/mcp.json`, em que a chave de nível superior é
`servers` em vez de `mcpServers`.

**Gemini CLI:** num terminal, `gemini mcp add -s user fontes uvx fontes-mcp`. Ou adicione isto a
`~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Zed:** abra o seu ficheiro de definições (**zed: open settings file**) e adicione:

```json
{
  "context_servers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**LM Studio:** na barra lateral direita, abra o separador **Program**, clique em **Install → Edit
mcp.json** e adicione:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Cline:** clique no ícone **MCP Servers**, abra o separador **Configure**, clique em **Configure MCP
Servers** e adicione a mesma entrada `mcpServers` que no LM Studio.

**Claude Desktop, manualmente** (em vez do ficheiro `.mcpb`): adicione a mesma entrada `mcpServers` a
`claude_desktop_config.json` (macOS: `~/Library/Application Support/Claude/`, Windows:
`%APPDATA%\Claude\`).

**Qualquer outra aplicação MCP** (Windsurf e outras): a documentação da própria aplicação indica onde
guarda os seus servidores MCP. A maioria aceita a mesma entrada: comando `uvx`, argumento `fontes`.

Se a aplicação não encontrar o `uvx`, utilize o caminho completo (em macOS e Linux, `which uvx`
mostra-o).

## Precisa do uv

O Codex, o Claude Code e as outras aplicações iniciam o Fontes com o `uvx`, que vem com o **uv**, uma
pequena ferramenta gratuita da Astral. Para o instalar, consulte o
[guia da Astral](https://docs.astral.sh/uv/getting-started/installation/) ou execute:

- macOS ou Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Windows (PowerShell): `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

## Chaves

Algumas fontes precisam de uma chave gratuita: consulte [KEYS.md](KEYS.md).

## Verificar se funciona

Numa nova conversa, pergunte: *"Em que jurisdições pode o Fontes pesquisar?"* A aplicação deverá
responder com uma lista de países. Se não o fizer, feche e volte a abrir a aplicação mais uma vez.

## Instalador de um clique (a caminho)

Está a caminho um instalador para Mac e Windows que configura o Fontes em todas as suas aplicações de
uma só vez. Configura o Claude Desktop, Codex, Claude Code, Cursor, VS Code (GitHub Copilot),
Windsurf, Gemini CLI, Zed, LM Studio e Cline. Quando sair:

**Antes de começar:** feche completamente cada uma destas aplicações. Isto é mais importante para o
Claude Code: enquanto está em execução, reescreve `~/.claude.json` e pode anular a alteração do
instalador. Se não puder fechar o Claude Code, adicione-lhe o Fontes com `claude mcp add` (consulte
[Claude Code](#claude-code)).

**Mac**

1. Abra a pasta **Fontes Installer** transferida.
2. Faça duplo clique em **Install Fontes.command**.
   - Se o Mac indicar que "cannot be opened because it is from an unidentified developer" (não pode
     ser aberto porque é de um programador não identificado): clique com o botão direito (ou
     Control-clique) no ficheiro, escolha **Open** e depois **Open** novamente. Só tem de o fazer uma
     vez.
3. Abre-se uma janela que pergunta se deve enviar contagens de utilização anónimas; prima Enter para
   não.
4. Pergunta se pretende adicionar chaves agora. Prima Enter para saltar este passo; consulte
   [O passo das chaves](#o-passo-das-chaves).
5. Quando aparecer **Concluído**, volte a abrir as suas aplicações de IA.

**Windows**

1. Descomprima o **Fontes Installer** transferido (botão direito → Extract All).
2. Faça duplo clique em **Install Fontes.cmd**.
   - Se o Windows mostrar "Windows protected your PC": clique em **More info** e depois em
     **Run anyway**.
3. Quando lhe for perguntado se deve enviar contagens de utilização anónimas, prima Enter para não.
4. Pergunta se pretende adicionar chaves agora. Prima Enter para saltar este passo; consulte
   [O passo das chaves](#o-passo-das-chaves).
5. Quando aparecer **Concluído**, volte a abrir as suas aplicações de IA. Se alguma ainda estava em
   execução, feche-a completamente (também na área de notificação, junto ao relógio) e volte a
   abri-la.

No fim, o instalador lista as aplicações que configurou.

### Que aplicações configura

Configura uma aplicação apenas se a pasta de definições dessa aplicação já existir no seu computador.
O Claude Code só é configurado se `~/.claude.json` existir. O Claude Desktop é sempre configurado.
Cada aplicação recebe uma entrada, `fontes`, neste ficheiro:

| Aplicação | Ficheiro (Mac e Linux) | Ficheiro (Windows) |
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

O VS Code é configurado se existir `~/.copilot` ou a pasta de definições do próprio VS Code.

Duas aplicações precisam de mais um passo:

- **Windsurf:** depois de o voltar a abrir, clique em atualizar (refresh) no Cascade.
- **Cline dentro da antiga extensão do VS Code:** adicione o Fontes manualmente (consulte
  [Cline](#outras-aplicações)).

### O passo das chaves

Logo após a instalação, o instalador propõe-lhe adicionar as chaves gratuitas de França e dos EUA.
Para as adicionar ou alterar mais tarde:

- **Mac:** faça duplo clique em **Add or change keys.command** na pasta do instalador, ou volte a
  abrir a aplicação Fontes Installer e escolha **Adicionar ou alterar chaves**.
- **Windows:** faça duplo clique em **Add or change keys.cmd** na pasta do instalador.

O que escreve fica oculto. As chaves vão para todas as aplicações que já têm o Fontes. Depois, feche
e volte a abrir as aplicações. Onde obter as chaves e o que desbloqueiam: [KEYS.md](KEYS.md).

### Cópias de segurança, novas execuções e remoção

O instalador só altera a entrada `fontes`. Todas as outras definições e comentários ficam como
estavam. Antes de alterar um ficheiro, guarda uma cópia ao lado dele, chamada
`<file>.fontes-backup-<date>`. As cópias feitas depois de ter adicionado chaves contêm essas chaves:
apague as de que já não precisa. Também instala o uv. Voltar a executá-lo é seguro: repara a
configuração e não altera mais nada.

Para remover o Fontes, faça duplo clique em **Uninstall Fontes.command** (Mac) ou
**Uninstall Fontes.cmd** (Windows). Remove a entrada `fontes`, incluindo as chaves, de todas as
aplicações. As suas outras definições e as cópias de segurança mantêm-se.

## Atualizações

- **Instalador e ficheiro `.mcpb`:** não precisa de fazer nada. Uma vez por dia, quando a aplicação
  arranca, o Fontes verifica em segundo plano se existe uma versão mais recente e prepara-a; da
  próxima vez que a aplicação arrancar, utiliza-a. Se não for possível transferir uma atualização ou
  se esta não funcionar, o Fontes continua a utilizar a versão que funcionava.
- **`uvx`:** o Fontes avisa quando existe uma versão mais recente, no topo da sua lista de
  jurisdições. Para executar sempre a versão mais recente, utilize `fontes-mcp@latest` em vez de
  `fontes`.

Para isso, não é enviada para lado nenhum qualquer informação sobre si ou sobre as suas pesquisas.

## Privacidade

Por predefinição, o Fontes não envia nada sobre si ou sobre as suas pesquisas. As contagens de
utilização dependem do seu consentimento (opt-in), e um relatório de erro só é enviado depois de o
ver e confirmar. Pormenores: [PRIVACY.md](PRIVACY.md).

## Como remover

Remova a entrada `fontes` das definições MCP da sua aplicação (no Claude Code:
`claude mcp remove fontes`) e depois feche e volte a abrir a aplicação.

## Bom saber

O Fontes lê fontes públicas, sobretudo sítios Web de tribunais e governos. Assinala as não oficiais
nas respostas. Abra sempre a ligação para a fonte antes de confiar numa decisão ou numa disposição.

Se algo correr mal, envie para fontesmcp@proton.me o que fez e o erro que obteve.

## Antes de confiar nele

- O Fontes é uma ferramenta de pesquisa, não aconselhamento jurídico. A sua utilização não faz de
  ninguém o seu advogado.
- É fornecido "tal como está", sem garantia, e os seus autores não são responsáveis pela forma como é
  utilizado, na medida permitida por lei. Os termos completos constam da
  [licença](../../../LICENSE) (Apache 2.0).

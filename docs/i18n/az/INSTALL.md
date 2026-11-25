> Bu, maşın dəstəyi ilə hazırlanmış tərcümədir. Əsas olan ingiliscə versiyadır.

# Fontes-in quraşdırılması

Fontes süni intellekt proqramınıza 120-dən çox yurisdiksiyada məhkəmə qərarlarını və
qanunvericiliyi məhkəmə və dövlət saytlarında canlı olaraq axtarmağa imkan verir. Hər nəticə
orijinala keçid verir. Bu, standart MCP serveridir, buna görə yerli MCP serverini işə sala bilən
istənilən proqramda işləyir: Claude Desktop, Codex, Claude Code, Cursor, VS Code (GitHub Copilot),
Gemini CLI, Windsurf, Zed, LM Studio, Cline və digərləri.

Proqramınızı seçin, onun addımlarını izləyin, sonra
[işlədiyini yoxlayın](#fontes-in-işlədiyini-yoxlamaq).

## Claude Desktop

1. Fontes `.mcpb` faylını
   [son buraxılışdan](https://github.com/ykarapazar/fontes/releases/latest) yükləyin.
2. Üzərinə iki dəfə klikləyin. Claude Desktop onu açır.
3. **Install** düyməsini klikləyin.

## Codex

Terminalda:

```bash
codex mcp add fontes -- uvx fontes-mcp
```

Codex CLI və Codex IDE genişləndirməsi bu parametri paylaşır (`~/.codex/config.toml`).
[uv lazımdır](#uv-lazımdır).

## Claude Code

Terminalda:

```bash
claude mcp add fontes -- uvx fontes-mcp
```

[uv lazımdır](#uv-lazımdır).

## Digər proqramlar

Bunların hər biri üçün [uv lazımdır](#uv-lazımdır). Qeydi əlavə edin, yadda saxlayın, sonra
proqramı bağlayıb yenidən açın.

**Cursor:** `~/.cursor/mcp.json` (bütün layihələr) və ya `.cursor/mcp.json` (bir layihə) faylında:

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**VS Code (GitHub Copilot):** Command Palette-dən **MCP: Add Server** əmrini işə salın,
**Command (stdio)** seçin, `uvx fontes-mcp` daxil edin və serveri `fontes` adlandırın. Və ya bunu
`~/.copilot/mcp-config.json` faylına əlavə edin:

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

Köhnə VS Code quraşdırmaları `.vscode/mcp.json` faylından istifadə edir; orada yuxarı səviyyəli
açar `mcpServers` əvəzinə `servers`-dir.

**Gemini CLI:** terminalda `gemini mcp add -s user fontes uvx fontes-mcp`. Və ya bunu
`~/.gemini/settings.json` faylına əlavə edin:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Zed:** parametrlər faylınızı açın (**zed: open settings file**) və bunu əlavə edin:

```json
{
  "context_servers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**LM Studio:** sağ yan paneldə **Program** tabını açın, **Install → Edit mcp.json** düyməsini
klikləyin və bunu əlavə edin:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Cline:** **MCP Servers** ikonunu klikləyin, **Configure** tabını açın, **Configure MCP
Servers** düyməsini klikləyin və LM Studio-dakı ilə eyni `mcpServers` qeydini əlavə edin.

**Claude Desktop, əl ilə** (`.mcpb` faylı əvəzinə): eyni `mcpServers` qeydini
`claude_desktop_config.json` faylına əlavə edin (macOS: `~/Library/Application Support/Claude/`,
Windows: `%APPDATA%\Claude\`).

**İstənilən digər MCP proqramı** (Windsurf və digərləri): onun MCP serverlərini harada saxladığını
öz sənədləri göstərir. Əksəriyyəti eyni qeydi qəbul edir: əmr `uvx`, arqument `fontes-mcp`.

Proqram `uvx`-i tapa bilmirsə, onun tam yolundan istifadə edin (macOS və Linux-da `which uvx` onu
göstərir).

## uv lazımdır

Codex, Claude Code və digər proqramlar Fontes-i `uvx` ilə işə salır; `uvx` Astral-ın kiçik, pulsuz
aləti olan **uv** ilə birlikdə gəlir. Onu quraşdırmaq üçün
[Astral-ın bələdçisinə](https://docs.astral.sh/uv/getting-started/installation/) baxın və ya bunu
işə salın:

- macOS və ya Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Windows (PowerShell): `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

## Açarlar

Bəzi mənbələr pulsuz açar tələb edir: bax [KEYS.md](KEYS.md).

## Fontes-in işlədiyini yoxlamaq

Yeni söhbətdə soruşun: *"Fontes hansı yurisdiksiyalarda axtarış apara bilər?"* Proqram ölkələrin
siyahısı ilə cavab verməlidir. Vermirsə, proqramı bir daha bağlayıb yenidən açın.

## Bir kliklə quraşdırıcı (Mac və Windows)

Quraşdırıcı Fontes-i bütün proqramlarınızda bir dəfəyə quraşdırır: Claude Desktop, Codex,
Claude Code, Cursor, VS Code (GitHub Copilot), Windsurf, Gemini CLI, Zed, LM Studio və Cline.

**Başlamazdan əvvəl:** bu proqramların hər birini tamamilə bağlayın. Bu, ən çox Claude Code üçün
vacibdir: o işləyərkən `~/.claude.json` faylını yenidən yazır və quraşdırıcının dəyişikliyini geri
qaytara bilər. Claude Code-u bağlaya bilmirsinizsə, Fontes-i ona bunun əvəzinə `claude mcp add`
ilə əlavə edin (bax [Claude Code](#claude-code)).

**Mac**

1. Mac quraşdırıcısını (`Fontes-Installer-…-mac.zip`) [son
   buraxılışdan](https://github.com/ykarapazar/fontes/releases/latest) yükləyin və arxivi açmaq üçün
   ona iki dəfə klikləyin.
2. **Fontes Installer** proqramına iki dəfə klikləyin. Mac-iniz internetdən yüklənmiş proqramı açmaq
   istəyib-istəmədiyinizi soruşsa, **Open** klikləyin.
3. **Quraşdır** seçin və **OK** klikləyin. Quraşdırma təxminən bir dəqiqə çəkir.
4. Mesaj quraşdırılmış proqramları sadalayır. **Hazır** klikləyin, sonra həmin proqramları yenidən
   açın. Əvvəlcə istəyə bağlı pulsuz açarları əlavə etmək üçün bunun əvəzinə **Açarları əlavə et**
   klikləyin; bax [Açarlar addımı](#açarlar-addımı).

**Windows**

1. Windows quraşdırıcısını (`Fontes-Setup-….exe`) [son buraxılışdan](https://github.com/ykarapazar/fontes/releases/latest) yükləyin və ona iki dəfə klikləyin.
   - Windows "Windows protected your PC" göstərsə: **More info**, sonra **Run anyway** klikləyin.
2. **Quraşdır** klikləyin. Pəncərə açılır və Fontes-i quraşdırır.
3. Anonim istifadə saylarının göndərilib-göndərilməməsi soruşulduqda "xeyr" üçün Enter basın.
4. Açarların indi əlavə edilib-edilməməsini soruşur. Ötürmək üçün Enter basın; bax
   [Açarlar addımı](#açarlar-addımı).
5. **Hazırdır** dedikdə süni intellekt proqramlarınızı yenidən açın. Onlardan biri hələ də
   işləyirdisə, onu tamamilə bağlayın (saatın yanındakı sistem nimçəsindən də) və yenidən açın.

Sonda quraşdırıcı quraşdırdığı proqramları sadalayır.

### Hansı proqramları quraşdırır

Proqramı yalnız onun parametrlər qovluğu kompüterinizdə artıq mövcuddursa quraşdırır. Claude Code
yalnız `~/.claude.json` mövcuddursa quraşdırılır. Claude Desktop həmişə quraşdırılır. Hər proqram bu
faylda bir `fontes` qeydi alır:

| Proqram | Fayl (Mac və Linux) | Fayl (Windows) |
|---|---|---|
| Claude Desktop | `~/Library/Application Support/Claude/claude_desktop_config.json` (Linux: `~/.config/Claude/`) | `%APPDATA%\Claude\claude_desktop_config.json` və Microsoft Store versiyasının öz nüsxəsi |
| Codex | `~/.codex/config.toml` | `%USERPROFILE%\.codex\config.toml` |
| Claude Code | `~/.claude.json` | `%USERPROFILE%\.claude.json` |
| Cursor | `~/.cursor/mcp.json` | `%USERPROFILE%\.cursor\mcp.json` |
| VS Code (Copilot) | `~/.copilot/mcp-config.json` | `%USERPROFILE%\.copilot\mcp-config.json` |
| Windsurf | `~/.config/devin/mcp_config.json` və ya köhnə versiyalarda `~/.codeium/windsurf/mcp_config.json` | `%APPDATA%\devin\mcp_config.json` və ya `%USERPROFILE%\.codeium\windsurf\mcp_config.json` |
| Gemini CLI | `~/.gemini/settings.json` | `%USERPROFILE%\.gemini\settings.json` |
| Zed | `~/.config/zed/settings.json` | `%APPDATA%\Zed\settings.json` |
| LM Studio | `~/.lmstudio/mcp.json` | `%USERPROFILE%\.lmstudio\mcp.json` |
| Cline | `~/.cline/data/settings/cline_mcp_settings.json` | `%USERPROFILE%\.cline\data\settings\cline_mcp_settings.json` |

VS Code, `~/.copilot` və ya VS Code-un öz parametrlər qovluğu mövcuddursa quraşdırılır.

İki proqram üçün bir addım da lazımdır:

- **Windsurf:** onu yenidən açdıqdan sonra Cascade-də yenilə düyməsini basın.
- **Köhnə VS Code genişləndirməsinin içindəki Cline:** Fontes-i əl ilə əlavə edin
  (bax [Cline](#digər-proqramlar)).

### Açarlar addımı

Quraşdırmadan dərhal sonra quraşdırıcı pulsuz Fransa və ABŞ açarlarını əlavə etməyi təklif edir.
Onları sonra əlavə etmək və ya dəyişmək üçün:

- **Mac:** **Fontes Installer** proqramını yenidən açıb **Açarları əlavə et və ya dəyiş** seçin.
- **Windows:** Start menyusunu açın, sonra **Fontes** → **Açarları əlavə et və ya dəyiş** seçin.

Yazdığınız görünmür. Açarlar Fontes-in artıq olduğu hər proqrama əlavə olunur. Sonra proqramları
bağlayıb yenidən açın. Açarları haradan almaq və onların nəyi açdığı: [KEYS.md](KEYS.md).

### Ehtiyat nüsxələr, təkrar işə salma və silmə

Quraşdırıcı yalnız `fontes` qeydini dəyişir. Bütün digər parametrlər və şərhlər olduğu kimi qalır.
Faylı dəyişməzdən əvvəl onun yanında `<file>.fontes-backup-<date>` adlı nüsxəsini saxlayır. Açarları
əlavə etdikdən sonra yaradılan nüsxələr həmin açarları ehtiva edir: artıq lazım olmayanları silin.
O, həmçinin uv-ni quraşdırır. Onu yenidən işə salmaq təhlükəsizdir: quraşdırmanı bərpa edir və başqa
heç nəyi dəyişmir.

Fontes-i silmək üçün **Fontes Installer** proqramını açıb **Sil** seçin (Mac) və ya Settings → Apps (Windows) bölməsində **Fontes** proqramını silin. O, `fontes` qeydini, açarlar daxil olmaqla, hər
proqramdan silir.
Digər parametrləriniz və ehtiyat nüsxələr qalır.

## Yeniləmələr

- **Quraşdırıcı və `.mcpb` faylı:** heç nə etməyinizə ehtiyac yoxdur. Gündə bir dəfə, proqram işə
  düşəndə Fontes arxa planda daha yeni versiyanı yoxlayır və onu hazırlayır; proqram növbəti dəfə
  işə düşəndə ondan istifadə edir. Yeniləmə yüklənə bilməzsə və ya işləməzsə, Fontes işləmiş
  versiyadan istifadəyə davam edir.
- **`uvx`:** daha yeni versiya mövcud olduqda Fontes bunu yurisdiksiyalar siyahısının ən yuxarısında
  sizə bildirir. Həmişə ən yeni versiyanı işə salmaq üçün `fontes-mcp` əvəzinə `fontes-mcp@latest` istifadə
  edin.

Bunun üçün siz və ya axtarışlarınız barədə heç bir məlumat heç yerə göndərilmir.

## Məxfilik

Fontes defolt olaraq siz və ya axtarışlarınız barədə heç nə göndərmir. İstifadə sayları yalnız
sizin razılığınızla (opt-in) göndərilir, xəta hesabatı isə yalnız siz onu görüb təsdiq etdikdən
sonra göndərilir. Təfərrüatlar: [PRIVACY.md](PRIVACY.md).

## Silmək

`fontes` qeydini proqramınızın MCP parametrlərindən silin (Claude Code-da:
`claude mcp remove fontes`), sonra proqramı bağlayıb yenidən açın.

## Bilmək faydalıdır

Fontes açıq mənbələri, əsasən məhkəmə və dövlət saytlarını oxuyur. Qeyri-rəsmi mənbələri
cavablarında işarələyir. Qərara və ya müddəaya etibar etməzdən əvvəl həmişə mənbə keçidini açın.

Nəsə səhv getsə, nə etdiyinizi və gördüyünüz xətanı fontesmcp@proton.me ünvanına e-poçtla göndərin.

## Etibar etməzdən əvvəl

- Fontes tədqiqat alətidir, hüquqi məsləhət deyil. Ondan istifadə heç kimi sizin vəkiliniz etmir.
- O, heç bir zəmanət olmadan "olduğu kimi" təqdim olunur və onun müəllifləri, qanunun icazə verdiyi
  həddə, ondan necə istifadə edildiyinə görə məsuliyyət daşımırlar. Şərtlərin tam mətni
  [lisenziyadadır](../../../LICENSE) (Apache 2.0).

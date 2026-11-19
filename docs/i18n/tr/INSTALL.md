> Bu çeviri makine desteğiyle hazırlanmıştır. Esas olan İngilizce sürümdür.

# Fontes'i kurmak

Fontes, yapay zekâ uygulamanızın 120'den fazla yargı alanında mahkeme kararlarını ve mevzuatı mahkeme
ve devlet internet sitelerinde canlı olarak aramasını sağlar. Her sonuç asıl metne bağlantı verir.
Standart bir MCP sunucusu olduğundan, yerel bir MCP sunucusu çalıştırabilen her uygulamada çalışır:
Claude Desktop, Codex, Claude Code, Cursor, VS Code (GitHub Copilot), Gemini CLI, Windsurf, Zed,
LM Studio, Cline ve diğerleri.

Uygulamanızı seçin, adımlarını izleyin, ardından [çalıştığını kontrol edin](#çalıştığını-kontrol-etmek).

## Claude Desktop

1. Fontes `.mcpb` dosyasını
   [en son sürümden](https://github.com/ykarapazar/fontes/releases/latest) indirin.
2. Üzerine çift tıklayın. Claude Desktop dosyayı açar.
3. **Install**'a tıklayın.

## Codex

Bir terminalde:

```bash
codex mcp add fontes -- uvx fontes-mcp
```

Codex CLI ve Codex IDE eklentisi bu ayarı paylaşır (`~/.codex/config.toml`).
[uv gerekir](#uv-gerekir).

## Claude Code

Bir terminalde:

```bash
claude mcp add fontes -- uvx fontes-mcp
```

[uv gerekir](#uv-gerekir).

## Diğer uygulamalar

Bunların her biri [uv gerektirir](#uv-gerekir). Girdiyi ekleyin, kaydedin, ardından uygulamayı
kapatıp yeniden açın.

**Cursor:** `~/.cursor/mcp.json` (tüm projeler) veya `.cursor/mcp.json` (tek proje) içinde:

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**VS Code (GitHub Copilot):** Command Palette'ten **MCP: Add Server** komutunu çalıştırın,
**Command (stdio)** seçeneğini seçin, `uvx fontes-mcp` girin ve sunucuya `fontes` adını verin. Ya da
bunu `~/.copilot/mcp-config.json` dosyasına ekleyin:

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

Eski VS Code kurulumları `.vscode/mcp.json` dosyasını kullanır; orada üst düzey anahtar
`mcpServers` yerine `servers`'dır.

**Gemini CLI:** bir terminalde `gemini mcp add -s user fontes uvx fontes-mcp`. Ya da bunu
`~/.gemini/settings.json` dosyasına ekleyin:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Zed:** ayar dosyanızı açın (**zed: open settings file**) ve şunu ekleyin:

```json
{
  "context_servers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**LM Studio:** sağ kenar çubuğunda **Program** sekmesini açın, **Install → Edit mcp.json**'a
tıklayın ve şunu ekleyin:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Cline:** **MCP Servers** simgesine tıklayın, **Configure** sekmesini açın, **Configure MCP
Servers**'a tıklayın ve LM Studio'dakiyle aynı `mcpServers` girdisini ekleyin.

**Claude Desktop, elle** (`.mcpb` dosyası yerine): aynı `mcpServers` girdisini
`claude_desktop_config.json` dosyasına ekleyin (macOS: `~/Library/Application Support/Claude/`,
Windows: `%APPDATA%\Claude\`).

**Diğer herhangi bir MCP uygulaması** (Windsurf ve diğerleri): MCP sunucularını nerede tuttuğunu
kendi belgeleri söyler. Çoğu aynı girdiyi kabul eder: komut `uvx`, argüman `fontes`.

Uygulama `uvx`'i bulamazsa tam yolunu kullanın (macOS ve Linux'ta `which uvx` bu yolu yazdırır).

## uv gerekir

Codex, Claude Code ve diğer uygulamalar Fontes'i `uvx` ile başlatır; `uvx`, Astral'ın küçük ve
ücretsiz bir aracı olan **uv** ile birlikte gelir. Kurmak için
[Astral'ın kılavuzuna](https://docs.astral.sh/uv/getting-started/installation/) bakın ya da şunu
çalıştırın:

- macOS veya Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Windows (PowerShell): `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

## Anahtarlar

Bazı kaynaklar ücretsiz bir anahtar gerektirir: bkz. [KEYS.md](KEYS.md).

## Çalıştığını kontrol etmek

Yeni bir sohbette sorun: *"Fontes hangi yargı alanlarında arama yapabilir?"* Uygulamanın bir ülke
listesiyle yanıt vermesi gerekir. Vermezse uygulamayı bir kez daha kapatıp yeniden açın.

## Tek tıkla kurulum programı (Mac ve Windows)

Kurulum programı Fontes'i tüm uygulamalarınızda tek seferde kurar: Claude Desktop, Codex, Claude Code,
Cursor, VS Code (GitHub Copilot), Windsurf, Gemini CLI, Zed, LM Studio ve Cline.

**Başlamadan önce:** bu uygulamaların her birini tamamen kapatın. Bu en çok Claude Code için
önemlidir: Claude Code çalışırken `~/.claude.json` dosyasını yeniden yazar ve kurulum programının
yaptığı değişikliği geri alabilir. Claude Code'u kapatamıyorsanız, Fontes'i ona bunun yerine
`claude mcp add` ile ekleyin (bkz. [Claude Code](#claude-code)).

**Mac**

1. Mac kurulum programını (`Fontes-Installer-…-mac.zip`) [son sürümden](https://github.com/ykarapazar/fontes/releases/latest)
   indirin ve zipten çıkarmak için üzerine çift tıklayın.
2. **Fontes Installer**'a çift tıklayın. Mac'iniz internetten indirilen bir uygulamayı açmak isteyip
   istemediğinizi sorarsa **Aç**'a tıklayın.
3. **Kur**'u seçin ve **Tamam**'a tıklayın. Kurulum yaklaşık bir dakika sürer.
4. Bir mesaj, kurduğu uygulamaları listeler. **Bitti**'ye tıklayın, ardından bu uygulamaları yeniden açın.
   Önce isteğe bağlı ücretsiz anahtarları eklemek için bunun yerine **Anahtar ekle**'ye tıklayın; bkz.
   [Anahtar adımı](#anahtar-adımı).

**Windows**

1. Windows kurulum programını (`Fontes-Setup-….exe`) [son sürümden](https://github.com/ykarapazar/fontes/releases/latest) indirin ve çift tıklayın.
   - Windows "Windows protected your PC" uyarısını gösterirse: **More info**'ya, ardından
     **Run anyway**'e tıklayın.
2. **Kur**'a tıklayın. Bir pencere açılır ve Fontes'i kurar.
3. Anonim kullanım sayılarının gönderilip gönderilmeyeceği sorulduğunda, hayır için Enter'a basın.
4. Anahtarların şimdi eklenip eklenmeyeceğini sorar. Atlamak için Enter'a basın; bkz.
   [Anahtar adımı](#anahtar-adımı).
5. **Tamamlandı** dediğinde yapay zekâ uygulamalarınızı yeniden açın. Biri hâlâ çalışıyorsa, onu
   tamamen kapatın (saatin yanındaki sistem tepsisinden de) ve yeniden açın.

Sonunda kurulum programı kurduğu uygulamaları listeler.

### Hangi uygulamaları kurar

Bir uygulamayı yalnızca o uygulamanın ayar klasörü bilgisayarınızda zaten varsa kurar. Claude Code
yalnızca `~/.claude.json` varsa kurulur. Claude Desktop her zaman kurulur. Her uygulama, şu dosyada
tek bir `fontes` girdisi alır:

| Uygulama | Dosya (Mac ve Linux) | Dosya (Windows) |
|---|---|---|
| Claude Desktop | `~/Library/Application Support/Claude/claude_desktop_config.json` (Linux: `~/.config/Claude/`) | `%APPDATA%\Claude\claude_desktop_config.json` ve Microsoft Store sürümünün kendi kopyası |
| Codex | `~/.codex/config.toml` | `%USERPROFILE%\.codex\config.toml` |
| Claude Code | `~/.claude.json` | `%USERPROFILE%\.claude.json` |
| Cursor | `~/.cursor/mcp.json` | `%USERPROFILE%\.cursor\mcp.json` |
| VS Code (Copilot) | `~/.copilot/mcp-config.json` | `%USERPROFILE%\.copilot\mcp-config.json` |
| Windsurf | `~/.config/devin/mcp_config.json` veya eski sürümlerde `~/.codeium/windsurf/mcp_config.json` | `%APPDATA%\devin\mcp_config.json` veya `%USERPROFILE%\.codeium\windsurf\mcp_config.json` |
| Gemini CLI | `~/.gemini/settings.json` | `%USERPROFILE%\.gemini\settings.json` |
| Zed | `~/.config/zed/settings.json` | `%APPDATA%\Zed\settings.json` |
| LM Studio | `~/.lmstudio/mcp.json` | `%USERPROFILE%\.lmstudio\mcp.json` |
| Cline | `~/.cline/data/settings/cline_mcp_settings.json` | `%USERPROFILE%\.cline\data\settings\cline_mcp_settings.json` |

VS Code, `~/.copilot` veya VS Code'un kendi ayar klasörü varsa kurulur.

İki uygulama bir adım daha gerektirir:

- **Windsurf:** yeniden açtıktan sonra Cascade'de yenile'ye basın.
- **Eski VS Code eklentisinin içindeki Cline:** Fontes'i elle ekleyin (bkz. [Cline](#diğer-uygulamalar)).

### Anahtar adımı

Kurulumdan hemen sonra kurulum programı, ücretsiz Fransa ve ABD anahtarlarını eklemeyi önerir.
Bunları daha sonra eklemek veya değiştirmek için:

- **Mac:** **Fontes Installer**'ı yeniden açın ve **Anahtar ekle veya değiştir**'i seçin.
- **Windows:** Başlat menüsünü açın, ardından **Fontes** → **Anahtar ekle veya değiştir**'i seçin.

Yazdıklarınız gizlenir. Anahtarlar, Fontes'in zaten kurulu olduğu her uygulamaya eklenir. Ardından
uygulamaları kapatıp yeniden açın. Anahtarları nereden alacağınız ve neyi açtıkları:
[KEYS.md](KEYS.md).

### Yedekler, yeniden çalıştırma ve kaldırma

Kurulum programı yalnızca `fontes` girdisini değiştirir. Diğer tüm ayarlar ve yorumlar olduğu gibi
kalır. Bir dosyayı değiştirmeden önce yanına `<file>.fontes-backup-<date>` adlı bir kopyasını
kaydeder. Anahtarları ekledikten sonra alınan kopyalar bu anahtarları içerir: artık ihtiyacınız
olmayanları silin. Ayrıca uv'yi de kurar. Yeniden çalıştırmak güvenlidir: kurulumu onarır ve başka
hiçbir şeyi değiştirmez.

Fontes'i kaldırmak için **Fontes Installer**'ı açıp **Kaldır**'ı seçin (Mac) veya **Fontes**'i Ayarlar → Uygulamalar üzerinden kaldırın (Windows). `fontes` girdisini, anahtarlar dahil, her uygulamadan kaldırır. Diğer
ayarlarınız ve yedek kopyalar kalır.

## Güncellemeler

- **Kurulum programı ve `.mcpb` dosyası:** hiçbir şey yapmanız gerekmez. Günde bir kez, uygulama
  başladığında Fontes arka planda daha yeni bir sürüm olup olmadığını kontrol eder ve onu hazırlar;
  uygulama bir sonraki başlayışında onu kullanır. Bir güncelleme indirilemezse veya çalışmazsa,
  Fontes çalışan sürümü kullanmaya devam eder.
- **`uvx`:** daha yeni bir sürüm çıktığında Fontes bunu yargı alanları listesinin en üstünde size
  bildirir. Her zaman en yeni sürümü çalıştırmak için `fontes-mcp` yerine `fontes-mcp@latest` kullanın.

Bunun için sizinle veya aramalarınızla ilgili hiçbir bilgi hiçbir yere gönderilmez.

## Gizlilik

Fontes varsayılan olarak sizinle veya aramalarınızla ilgili hiçbir şey göndermez. Kullanım sayıları
isteğe bağlıdır (opt-in) ve bir hata bildirimi yalnızca siz onu görüp onayladıktan sonra
gönderilir. Ayrıntılar: [PRIVACY.md](PRIVACY.md).

## Kaldırmak

`fontes` girdisini uygulamanızın MCP ayarlarından kaldırın (Claude Code'da:
`claude mcp remove fontes`), ardından uygulamayı kapatıp yeniden açın.

## Bilinmesi gerekenler

Fontes kamuya açık kaynakları, çoğunlukla mahkeme ve devlet internet sitelerini okur. Resmî olmayan
kaynakları yanıtlarında işaretler. Bir karara veya hükme güvenmeden önce her zaman kaynak
bağlantısını açın.

Bir şeyler ters giderse, ne yaptığınızı ve gördüğünüz hatayı fontesmcp@proton.me adresine e-postayla
gönderin.

## Güvenmeden önce

- Fontes bir araştırma aracıdır, hukuki danışmanlık değildir. Kullanılması kimseyi avukatınız yapmaz.
- Hiçbir garanti olmaksızın "olduğu gibi" sunulur ve yazarları, hukukun izin verdiği ölçüde, nasıl
  kullanıldığından sorumlu değildir. Koşulların tamamı [lisanstadır](../../../LICENSE) (Apache 2.0).

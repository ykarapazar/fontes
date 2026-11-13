# Fontes installer core for Windows: make sure uv is present, then run fontes_setup.py.
# Usage: install.ps1 [install|keys|uninstall]
param([ValidateSet('install', 'keys', 'uninstall')][string]$Action = 'install')
$ErrorActionPreference = 'Stop'
$UvVersion = '0.11.4'   # uv release fetched from astral.sh when uv is missing; bump deliberately

$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$setup = Join-Path $here 'fontes_setup.py'
if (-not (Test-Path $setup)) { $setup = Join-Path (Split-Path -Parent $here) 'fontes_setup.py' }

# Text from locales\<lang>.json (same order as fontes_i18n.py: FONTES_LANG, Windows UI language, English;
# pt-BR -> pt, pt-AO -> pt-PT -> pt, zh-TW -> zh-Hant). fontes_setup.py picks the language again by itself.
$locales = Join-Path (Split-Path -Parent $setup) 'locales'
function Read-Locale($code) {
    $f = Join-Path $locales "$code.json"
    if (Test-Path $f) { return Get-Content -Raw -Encoding UTF8 $f | ConvertFrom-Json }
}
$en = Read-Locale 'en'
$text = $null
foreach ($tag in @($env:FONTES_LANG, (Get-UICulture).Name)) {
    while ($tag -and -not $text) {
        $alias = @{ 'zh' = 'zh-Hans'; 'zh-CN' = 'zh-Hans'; 'zh-SG' = 'zh-Hans'; 'zh-TW' = 'zh-Hant'; 'zh-HK' = 'zh-Hant'; 'zh-MO' = 'zh-Hant' }[$tag]
        if ($tag -match '^pt-[A-Za-z]{2}$' -and $tag -ne 'pt-BR') { $alias = 'pt-PT' }   # Portuguese outside Brazil
        $text = Read-Locale $tag
        if (-not $text -and $alias) { $text = Read-Locale $alias }
        $tag = if ($tag.Contains('-')) { $tag.Substring(0, $tag.LastIndexOf('-')) } else { $null }
    }
    if ($text) { break }
}
function T($key) { if ($text -and $text.$key) { $text.$key } else { $en.$key } }

$uv = (Get-Command uv -ErrorAction SilentlyContinue).Source
foreach ($c in "$env:USERPROFILE\.local\bin\uv.exe", "$env:USERPROFILE\.cargo\bin\uv.exe") {
    if (-not $uv -and (Test-Path $c)) { $uv = $c }
}
if (-not $uv) {
    if ($Action -ne 'install') { Write-Host (T 'sh_no_uv'); exit 0 }
    Write-Host (T 'sh_installing_uv')
    $env:UV_NO_MODIFY_PATH = '1'
    powershell -NoProfile -ExecutionPolicy Bypass -Command "irm https://astral.sh/uv/$UvVersion/install.ps1 | iex"
    $uv = "$env:USERPROFILE\.local\bin\uv.exe"
}
$uvArgs = @('run', '--managed-python', '--python', '3.13', '--no-project', '--quiet', $setup, $Action)
& $uv @uvArgs
exit $LASTEXITCODE

; Inno Setup script: a signable Setup.exe wrapping install.ps1 (for SmartScreen / SignPath).
; Built in CI by .github/workflows/windows.yml. By hand: Windows + Inno Setup 6, from installer\windows:
;   iscc /DAppVersion=0.1.0 fontes.iss
; after writing privacy-languages.txt next to it (see the Build step in windows.yml).
; Signing slot: add  SignTool=signpath  (configured in the Inno IDE) or sign Output\*.exe
; afterwards in the SignPath CI step.
#ifndef AppVersion
  #define AppVersion "0.0.0"
#endif

[Setup]
AppName=Fontes
AppVersion={#AppVersion}
AppPublisher=Fontes (github.com/ykarapazar/fontes)
DefaultDirName={localappdata}\Fontes\Installer
PrivilegesRequired=lowest
DisableProgramGroupPage=yes
DisableDirPage=yes
OutputBaseFilename=Fontes-Setup-{#AppVersion}
Compression=lzma2
SolidCompression=yes

[Files]
Source: "install.ps1"; DestDir: "{app}"
Source: "..\fontes_setup.py"; DestDir: "{app}"
Source: "..\fontes_i18n.py"; DestDir: "{app}"
Source: "privacy-languages.txt"; DestDir: "{app}"
Source: "..\locales\*.json"; DestDir: "{app}\locales"
Source: "..\fontes_launcher.py"; DestDir: "{app}"
Source: "Add or change keys.cmd"; DestDir: "{app}"

[Icons]
Name: "{userprograms}\Fontes\Add or change keys"; Filename: "{app}\Add or change keys.cmd"

[Run]
Filename: "powershell.exe"; Parameters: "-NoProfile -ExecutionPolicy Bypass -File ""{app}\install.ps1"" install -Pause"; StatusMsg: "Setting up Fontes for your AI apps..."; Flags: waituntilterminated

[UninstallRun]
Filename: "powershell.exe"; Parameters: "-NoProfile -ExecutionPolicy Bypass -File ""{app}\install.ps1"" uninstall"; RunOnceId: "FontesUninstall"; Flags: waituntilterminated

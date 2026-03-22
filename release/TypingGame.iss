#define MyAppName "TypingGame"
#ifndef MyAppVersion
  #define MyAppVersion "0.0.0"
#endif
#ifndef SourceDir
  #define SourceDir "dist\\portable\\TypingGame"
#endif
#ifndef OutputDir
  #define OutputDir "dist\\installer"
#endif

[Setup]
AppId={{FA6D3834-0045-4558-9C73-43B201A271D1}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher=TypingGame Team
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
LicenseFile=
OutputDir={#OutputDir}
OutputBaseFilename=TypingGame-Setup-{#MyAppVersion}
Compression=lzma
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "chinesesimp"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "创建桌面快捷方式"; GroupDescription: "附加任务:"; Flags: unchecked

[Files]
Source: "{#SourceDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\TypingGame.exe"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\TypingGame.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\TypingGame.exe"; Description: "启动 {#MyAppName}"; Flags: nowait postinstall skipifsilent

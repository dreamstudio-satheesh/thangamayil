; Inno Setup Script for Thangamayil Billing Software
; Download Inno Setup from: https://jrsoftware.org/isdl.php

[Setup]
AppName=தங்கமயில் சில்க்ஸ் - Billing Software
AppVersion=1.0
AppPublisher=Thangamayil Silks
AppPublisherURL=https://github.com/your-repo
AppSupportURL=https://github.com/your-repo/issues
AppUpdatesURL=https://github.com/your-repo/releases
DefaultDirName={autopf}\ThangamayilBilling
DefaultGroupName=Thangamayil Billing
AllowNoIcons=yes
LicenseFile=LICENSE.txt
OutputDir=installer_output
OutputBaseFilename=ThangamayilBilling_Setup
SetupIconFile=icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesAllowed=x64

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 0,6.1

[Files]
Source: "dist\ThangamayilBilling.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\db.sql"; DestDir: "{app}"; Flags: ignoreversion
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{group}\தங்கமயில் சில்க்ஸ் Billing"; Filename: "{app}\ThangamayilBilling.exe"
Name: "{group}\{cm:UninstallProgram,தங்கமயில் சில்க்ஸ்}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\தங்கமயில் சில்க்ஸ் Billing"; Filename: "{app}\ThangamayilBilling.exe"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\தங்கமயில் சில்க்ஸ் Billing"; Filename: "{app}\ThangamayilBilling.exe"; Tasks: quicklaunchicon

[Run]
Filename: "{app}\ThangamayilBilling.exe"; Description: "{cm:LaunchProgram,தங்கமயில் சில்க்ஸ் Billing}"; Flags: nowait postinstall skipifsilent

[Registry]
Root: HKCU; Subkey: "Software\ThangamayilBilling"; ValueType: string; ValueName: "InstallPath"; ValueData: "{app}"

[Code]
procedure InitializeWizard;
begin
  WizardForm.WelcomeLabel1.Caption := 'Welcome to தங்கமயில் சில்க்ஸ் Billing Software Setup';
  WizardForm.WelcomeLabel2.Caption := 'This will install the complete billing solution for silk shops with barcode scanning, GST calculations, and thermal printer support.' + #13#13 + 'Click Next to continue or Cancel to exit Setup.';
end;
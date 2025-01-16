[Setup]
AppName=EBSoftware
AppVersion=1.0
DefaultDirName={pf}\EBSoftware
DefaultGroupName=EBSoftware
OutputBaseFilename=EBSoftware_Setup
SetupIconFile=assets\HS2.ico
LicenseFile=C:\Users\pc\Documents\GitHub\SoftwareEBS\LICENSE.txt
Compression=lzma
SolidCompression=yes

[Files]
Source: "dist\EBSoftware\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "C:\Users\pc\Documents\GitHub\SoftwareEBS\CP210x_Windows_Drivers\*"; DestDir: "{app}\CP210x_Windows_Drivers"; Flags: ignoreversion recursesubdirs createallsubdirs


[Icons]
Name: "{group}\EBSoftware"; Filename: "{app}\EBSoftware.exe"
Name: "{group}\Desinstalar EBSoftware"; Filename: "{uninstallexe}"
Name: "{commondesktop}\EBSoftware"; Filename: "{app}\EBSoftware.exe"

[Run]
Filename: "{app}\EBSoftware.exe"; Description: "{cm:LaunchProgram,EBSoftware}"; Flags: nowait postinstall skipifsilent

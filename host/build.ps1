# Builds VegasDirector.dll (Application Extension = auto-start host) and installs it plus the Script Menu fallback.
# Run: powershell -ExecutionPolicy Bypass -File host\build.ps1   (close VEGAS first if updating an installed DLL)
$ErrorActionPreference = 'Stop'
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$vegasDir = 'C:\Program Files\VEGAS\VEGAS Pro 22.0'
$csc = 'C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe'
$out = Join-Path $here 'bin\VegasDirector.dll'
New-Item -ItemType Directory -Force (Join-Path $here 'bin') | Out-Null
& $csc /nologo /target:library /optimize+ /out:$out `
  /r:"$vegasDir\ScriptPortal.Vegas.dll" /r:System.Windows.Forms.dll /r:System.Drawing.dll /r:System.Core.dll /r:System.Xml.dll /r:System.Data.dll `
  (Join-Path $here 'VegasDirectorHost.cs') (Join-Path $here 'VegasDirectorExtension.cs')
if ($LASTEXITCODE -ne 0) { throw "csc failed ($LASTEXITCODE)" }
$ext = Join-Path $env:USERPROFILE 'Documents\Vegas Application Extensions'
New-Item -ItemType Directory -Force $ext | Out-Null
Copy-Item $out (Join-Path $ext 'VegasDirector.dll') -Force
# Script Menu copy stays as a manual fallback (it detects the running extension and exits politely)
Copy-Item (Join-Path $here 'VegasDirectorHost.cs') (Join-Path $env:USERPROFILE 'Documents\Vegas Script Menu\VegasDirectorHost.cs') -Force
"built $out and installed to $ext"

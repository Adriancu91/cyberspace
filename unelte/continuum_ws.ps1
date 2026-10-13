# Porneste bucla CONTINUUM de pe workstation (config/continuum_ws.toml), fara fereastra, cu tot ce scrie pus in
# lucru/continuum_ws/bucla.log. Ciclurile lui stau in lucru/continuum_ws/cicluri.jsonl.
# Il porneste Task Scheduler (unelte/programeaza_continuum_ws.ps1): acum si dupa fiecare logare in Windows.
# Nu porneste nimic daca: exista butonul STOP (lucru/STOP) sau bucla ruleaza deja.
# Oprire: python -m kronos opreste --config config/proba.toml (acelasi STOP ca Kronos); apoi, ca sa poata porni din nou:
# python -m kronos porneste --config config/proba.toml
#
#   powershell -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File unelte\continuum_ws.ps1
param(
    [string]$Config = "config/continuum_ws.toml",
    [string]$Stare = "lucru/continuum_ws"
)

$ErrorActionPreference = "Stop"
$radacina = Split-Path -Parent $PSScriptRoot
Set-Location $radacina
$python = Join-Path $radacina ".venv\Scripts\python.exe"
New-Item -ItemType Directory -Force (Join-Path $radacina $Stare) | Out-Null
$jurnal = Join-Path $radacina "$Stare\bucla.log"
[Console]::OutputEncoding = [Text.Encoding]::UTF8   # ce scrie Python e UTF-8

function Scrie([string]$text) {
    Add-Content -Path $jurnal -Value ("[{0}] {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $text) -Encoding utf8
}

function In-Jurnal {
    process { Add-Content -Path $jurnal -Value ("$_") -Encoding utf8 }
}

$gasite = Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
    Where-Object { $_.CommandLine -and ($_.CommandLine -like "*module.continuum.bucla*") -and
                   (($_.CommandLine -replace "\\", "/") -like ("*" + $Config + "*")) -and
                   ($_.CommandLine -notlike "*--simuleaza*") -and ($_.CommandLine -notlike "*--jurnal*") }
if (@($gasite).Count -gt 0) { Scrie "Nu pornesc: bucla CONTINUUM ruleaza deja."; exit 0 }
if (Test-Path (Join-Path $radacina "lucru\STOP")) { Scrie "Nu pornesc: exista butonul STOP (lucru/STOP)."; exit 0 }

$argumente = @("-X", "utf8", "-m", "module.continuum.bucla", "--config", $Config, "--stare", $Stare)
Scrie ("Pornesc: python " + ($argumente -join " "))
$env:PYTHONUNBUFFERED = "1"
$env:PYTHONIOENCODING = "utf-8"
$ErrorActionPreference = "Continue"
& $python @argumente 2>&1 | In-Jurnal
$cod = $LASTEXITCODE
Scrie "Bucla CONTINUUM s-a incheiat (cod $cod)."
exit $cod

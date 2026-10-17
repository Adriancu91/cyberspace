# Paznicul de procese de pe workstation (17 octombrie 2026). Il porneste Task Scheduler la fiecare 15 minute
# (unelte/programeaza_paznic_procese_ws.ps1). Verifica trei lucruri si porneste la loc ce lipseste:
#   1. Claude Code cu Remote Control "-Nume" (prin unelte/dupa_logare_ws.ps1 -Claude: continua conversatia folderului,
#      sau, daca nu are niciuna, porneste o sesiune noua);
#   2. interfata (portul -Port; prin unelte/interfata_ws.ps1);
#   3. bucla CONTINUUM (prin sarcina "Kronos continuum ws"; nu, daca exista butonul STOP, lucru/STOP).
# Fiecare repornire se scrie in lucru/paznic_procese.log (sau in -Jurnal). Cand totul ruleaza, nu scrie nimic.
# In primele -MinuteDeLaPornire minute dupa pornirea calculatorului nu face nimic: atunci pornesc sarcinile de dupa
# logare (Claude Code la 30 de secunde), iar paznicul n-ar trebui sa porneasca al doilea.
# De ce: azi, la 07:59, Claude Code s-a inchis singur, iar odata cu el si interfata; nimic nu le-a pornit la loc.
# -Proba: nu porneste nimic; scrie in jurnal ce ar porni (si pentru ce ruleaza deja).
#
#   powershell -ExecutionPolicy Bypass -File unelte\paznic_procese_ws.ps1 -Proba
param(
    [switch]$Proba,
    [string]$Jurnal = "",
    [string]$Folder = "C:\Kronos\cyberspace",
    [string]$Nume = "Kronos",
    [string]$Exe = "",
    [string]$Conversatii = "",
    [int]$Port = 8787,
    [double]$MinuteDeLaPornire = 5
)

$radacina = Split-Path -Parent $PSScriptRoot
$fisierJurnal = if ($Jurnal) { $Jurnal } else { Join-Path $radacina "lucru\paznic_procese.log" }
New-Item -ItemType Directory -Force (Split-Path -Parent $fisierJurnal) | Out-Null

function Scrie([string]$text) {
    Add-Content -Path $fisierJurnal -Value ("[{0}] {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $text) -Encoding utf8
}

$minute = ((Get-Date) - (Get-CimInstance Win32_OperatingSystem).LastBootUpTime).TotalMinutes
if ($minute -lt $MinuteDeLaPornire -and -not $Proba) { exit 0 }

# 1. Claude Code cu Remote Control
$claude = @(Get-CimInstance Win32_Process -Filter "Name='claude.exe'" |
    Where-Object { $_.CommandLine -and $_.CommandLine -like "*--remote-control*$Nume*" }).Count -gt 0
if (-not $claude -or $Proba) {
    if (-not $claude) { Scrie "Lipseste Claude Code cu Remote Control '$Nume'." }
    $argumente = @{ Claude = $true; Folder = $Folder; Nume = $Nume; Jurnal = $fisierJurnal }
    if ($Exe) { $argumente.Exe = $Exe }
    if ($Conversatii) { $argumente.Conversatii = $Conversatii }
    if ($Proba) { $argumente.Proba = $true }
    & (Join-Path $PSScriptRoot "dupa_logare_ws.ps1") @argumente
}

# 2. Interfata
$interfata = $null -ne (Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue)
if (-not $interfata) {
    if ($Proba) { Scrie "Proba (nu pornesc nimic): interfata nu asculta pe portul $Port; as porni unelte\interfata_ws.ps1 -Port $Port." }
    else {
        Scrie "Lipseste interfata (portul $Port nu asculta): o pornesc."
        $iesire = & powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot "interfata_ws.ps1") -Port $Port
        Scrie ($iesire -join " ")
    }
} elseif ($Proba) { Scrie "Proba: interfata asculta pe portul $Port; n-as porni nimic." }

# 3. CONTINUUM
$continuum = @(Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
    Where-Object { $_.CommandLine -and ($_.CommandLine -like "*module.continuum.bucla*") -and
                   (($_.CommandLine -replace "\\", "/") -like "*config/continuum_ws.toml*") -and
                   ($_.CommandLine -notlike "*--simuleaza*") -and ($_.CommandLine -notlike "*--jurnal*") }).Count -gt 0
$stop = Test-Path (Join-Path $radacina "lucru\STOP")
if ($continuum) {
    if ($Proba) { Scrie "Proba: CONTINUUM ruleaza; n-as porni nimic." }
} elseif ($stop) {
    Scrie "CONTINUUM nu ruleaza, dar exista butonul STOP (lucru/STOP): nu-l pornesc."
} elseif ($Proba) {
    Scrie "Proba (nu pornesc nimic): CONTINUUM nu ruleaza; as porni sarcina 'Kronos continuum ws'."
} else {
    Scrie "Lipseste CONTINUUM: pornesc sarcina 'Kronos continuum ws'."
    Start-ScheduledTask -TaskName "Kronos continuum ws"
}

# Porneste (sau reia) o antrenare lunga pe workstation, fara fereastra, cu tot ce scrie pus intr-un jurnal de rulare.
# Il porneste Task Scheduler (unelte/programeaza_noapte_ws.ps1), la ora noptii si dupa o repornire de Windows.
# Antrenarea isi citeste orele facute din jurnalul Kronos, deci aceeasi comanda continua de unde a ramas.
# Nu porneste nimic daca: exista butonul STOP (lucru/STOP), antrenarea ruleaza deja, sau toate orele sunt facute.
#
#   powershell -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File unelte\noapte_ws.ps1 -Config config/ws_w1.toml -Ore 10 -AlaturiDe fapte_zero
#   ... -Opreste     # cere oprirea (python -m kronos opreste), doar daca antrenarea acestei configurari ruleaza
param(
    [Parameter(Mandatory = $true)][string]$Config,
    [int]$Ore = 10,
    [string]$AlaturiDe = "",
    [string]$Inceput = "Once upon a time, there was a fearful little dog named Coco",
    [string]$PanaLa = "",        # ex. "07:30": dupa ora asta nu mai porneste nimic (o repornire de Windows dimineata)
    [switch]$Opreste
)

$ErrorActionPreference = "Stop"
$radacina = Split-Path -Parent $PSScriptRoot
Set-Location $radacina
$python = Join-Path $radacina ".venv\Scripts\python.exe"
$nume = [IO.Path]::GetFileNameWithoutExtension($Config)
$jurnal = Join-Path $radacina "lucru\noapte_$nume.log"
New-Item -ItemType Directory -Force (Join-Path $radacina "lucru") | Out-Null
[Console]::OutputEncoding = [Text.Encoding]::UTF8   # ce scrie Python e UTF-8

function Scrie([string]$text) {
    Add-Content -Path $jurnal -Value ("[{0}] {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $text) -Encoding utf8
}

function In-Jurnal {
    # tot ce scrie programul (si erorile) ajunge in jurnal, rand cu rand, in UTF-8
    process { Add-Content -Path $jurnal -Value ("$_") -Encoding utf8 }
}

function Ruleaza-Deja {
    $tinta = "*antrenare_lunga.py*" + ($Config -replace "\\", "/") + "*"
    $gasite = Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
        Where-Object { $_.CommandLine -and (($_.CommandLine -replace "\\", "/") -like $tinta) }
    return @($gasite).Count -gt 0
}

if ($Opreste) {
    if (Ruleaza-Deja) {
        Scrie "Cer oprirea: ora in curs se incheie si e ultima."
        & $python -X utf8 -m kronos opreste --config $Config 2>&1 | In-Jurnal
    } else {
        Scrie "Oprirea n-a fost necesara: antrenarea nu mai rula."
    }
    exit 0
}

if (Test-Path (Join-Path $radacina "lucru\STOP")) { Scrie "Nu pornesc: exista butonul STOP (lucru/STOP)."; exit 0 }
if (Ruleaza-Deja) { Scrie "Nu pornesc: antrenarea ruleaza deja."; exit 0 }
if ($PanaLa -and ((Get-Date) -ge [datetime]::ParseExact($PanaLa, "HH:mm", $null)) -and ((Get-Date).Hour -lt 18)) {
    Scrie "Nu pornesc: a trecut de $PanaLa (noaptea s-a incheiat)."
    exit 0
}

$argumente = @("-X", "utf8", "unelte/antrenare_lunga.py", "--config", $Config, "--ore", "$Ore", "--inceput", $Inceput)
if ($AlaturiDe) { $argumente += @("--alaturi-de", $AlaturiDe) }
Scrie ("Pornesc: python " + ($argumente -join " "))
$env:PYTHONUNBUFFERED = "1"
$env:PYTHONIOENCODING = "utf-8"
$ErrorActionPreference = "Continue"
& $python @argumente 2>&1 | In-Jurnal
$cod = $LASTEXITCODE
Scrie "Antrenarea s-a incheiat (cod $cod)."
exit $cod

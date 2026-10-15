# Noaptea 15-16 octombrie 2026 (aleasa de Adrian, nu de CONTINUUM): linia W2-conv, examenele ei, apoi scoala de cod.
# O porneste Task Scheduler la 19:00 (sarcina "Kronos noapte conversatie"), fara fereastra. Tot ce scrie e in
# lucru/noapte_conversatie.log. Urmarirea placii porneste aici, odata cu noaptea, si se opreste la sfarsitul ei
# (lucru/placa_noapte_2026-10-15.csv); antrenarea lunga mai tine si ea una, doar pe orele ei.
#   1. W2-conv: python unelte/antrenare_lunga.py --config config/conv_w2.toml --ore 3 --porneste-din 353
#   2. examenul de conversatie si cel de romana si cod, pe ultimul model pastrat al liniei w2_conv
#   3. scoala de cod (ramura kronos-cod, C:\Kronos\cyberspace-cod): config/scoala_cod_v04_noapte.toml --pilot, oprire 06:45
# Nu porneste nimic daca exista butonul STOP (lucru/STOP) sau daca noaptea ruleaza deja.
param([string]$Cod = "C:\Kronos\cyberspace-cod")

$ErrorActionPreference = "Stop"
$radacina = Split-Path -Parent $PSScriptRoot
Set-Location $radacina
$python = Join-Path $radacina ".venv\Scripts\python.exe"
$jurnal = Join-Path $radacina "lucru\noapte_conversatie.log"
[Console]::OutputEncoding = [Text.Encoding]::UTF8

function Scrie([string]$text) {
    Add-Content -Path $jurnal -Value ("[{0}] {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $text) -Encoding utf8
}
function In-Jurnal { process { Add-Content -Path $jurnal -Value ("$_") -Encoding utf8 } }
function Ruleaza([string]$director, [string[]]$argumente) {
    Scrie ("Pornesc: python " + ($argumente -join " ") + "  (in $director)")
    Push-Location $director
    $ErrorActionPreference = "Continue"
    & $python @argumente 2>&1 | Where-Object { "$_" -notmatch "Loading weights|triton|flop_counter" } | In-Jurnal
    $cod = $LASTEXITCODE
    $ErrorActionPreference = "Stop"
    Pop-Location
    Scrie "S-a incheiat (cod $cod)."
    return $cod
}

if (Test-Path (Join-Path $radacina "lucru\STOP")) { Scrie "Nu pornesc: exista butonul STOP (lucru/STOP)."; exit 0 }
$deja = Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
    Where-Object { $_.CommandLine -and ($_.CommandLine -like "*conv_w2.toml*" -or $_.CommandLine -like "*scoala_cod_v04_noapte*") }
if (@($deja).Count -gt 0) { Scrie "Nu pornesc: noaptea ruleaza deja."; exit 0 }

$env:PYTHONUNBUFFERED = "1"
$env:PYTHONIOENCODING = "utf-8"
$urmarire = Start-Process -FilePath $python -PassThru -WindowStyle Hidden -WorkingDirectory $radacina -ArgumentList @(
    "-X", "utf8", "unelte/urmareste_placa.py", "--minute", "780", "--la-secunde", "10", "--iesire", "lucru/placa_noapte_2026-10-15.csv")
Scrie "Noaptea incepe (aleasa de Adrian). Urmarirea placii: lucru/placa_noapte_2026-10-15.csv (proces $($urmarire.Id))."
try {
    $cod = Ruleaza $radacina @("-X", "utf8", "unelte/antrenare_lunga.py", "--config", "config/conv_w2.toml", "--ore", "3",
                               "--porneste-din", "353", "--inceput", "Întrebare: Ce este ploaia?`nRăspuns:", "--lungime", "300")
    $ultimul = & $python -X utf8 -c "import json; f=[json.loads(l) for l in open('lucru/jurnal/experimente.jsonl', encoding='utf-8')]; p=[x for x in f if x.get('linie')=='w2_conv' and x.get('model_salvat')]; print(p[-1]['id'] if p else '')"
    if ($ultimul) {
        Scrie "Ultimul model pastrat al liniei w2_conv: #$ultimul."
        Ruleaza $radacina @("-X", "utf8", "unelte/examen_conversatie.py", "--experiment", "$ultimul", "--doar-local") | Out-Null
        Ruleaza $radacina @("-X", "utf8", "unelte/examen_validari_ws.py", "--experiment", "$ultimul") | Out-Null
    } else {
        Scrie "Linia w2_conv n-are niciun model pastrat: sar peste examenele ei."
    }
    if (Test-Path (Join-Path $radacina "lucru\STOP")) { Scrie "Butonul STOP e apasat: nu mai pornesc scoala de cod." }
    else { Ruleaza $Cod @("-X", "utf8", "unelte/scoala_cod.py", "--config", "config/scoala_cod_v04_noapte.toml", "--pilot") | Out-Null
           Ruleaza $Cod @("-X", "utf8", "unelte/raport_cod.py", "--dosar", "cod_v04_noapte") | Out-Null }
}
finally {
    if ($urmarire -and -not $urmarire.HasExited) { Stop-Process -Id $urmarire.Id -Force -ErrorAction SilentlyContinue }
    Scrie "Noaptea s-a incheiat; urmarirea placii e oprita."
}
exit 0

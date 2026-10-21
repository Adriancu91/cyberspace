# Porneste interfata (chat in browser, docs/INTERFATA_v0.md) pe workstation, fara fereastra, pe procesor, cu tot ce
# scrie pus in lucru/interfata/server.log (erorile in server_erori.log). O porneste paznicul de procese
# (unelte/paznic_procese_ws.ps1) cand portul nu asculta.
# Nu porneste nimic daca portul asculta deja (interfata ruleaza).
# 17 octombrie 2026: pana acum interfata se pornea de mana sau din Claude Code si cadea odata cu el.
# 20 octombrie 2026 (S5): si fila "Intreaba din text", cu modelul -ExperimentText (#401); -ExperimentText 0 = fara fila.
# 21 octombrie 2026 (S13, aprobat de Adrian): fila "Intreaba din text" trece de la #401 la #407 (noaptea 11).
#
#   powershell -NoProfile -ExecutionPolicy Bypass -File unelte\interfata_ws.ps1
param(
    [string]$Config = "config/ws_w1.toml",
    [int]$Experiment = 312,
    [int]$ExperimentText = 407,
    [int]$Port = 8787
)

$radacina = Split-Path -Parent $PSScriptRoot
Set-Location $radacina
$python = Join-Path $radacina ".venv\Scripts\python.exe"
$dosar = Join-Path $radacina "lucru\interfata"
New-Item -ItemType Directory -Force $dosar | Out-Null

if (Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue) {
    Write-Output "Interfata asculta deja pe portul $Port`: nu pornesc alta."
    exit 0
}

$env:PYTHONUNBUFFERED = "1"
$env:PYTHONIOENCODING = "utf-8"
$env:CUDA_VISIBLE_DEVICES = "-1"   # placa video ramane a antrenarii
$argumente = @("-X", "utf8", "-m", "module.interfata", "--config", $Config, "--experiment", "$Experiment",
               "--port", "$Port", "--dispozitiv", "cpu")
if ($ExperimentText -gt 0) { $argumente += @("--experiment-text", "$ExperimentText") }
$p = Start-Process -FilePath $python -ArgumentList $argumente -WorkingDirectory $radacina -WindowStyle Hidden -PassThru `
    -RedirectStandardOutput (Join-Path $dosar "server.log") -RedirectStandardError (Join-Path $dosar "server_erori.log")
Write-Output "Am pornit interfata (proces $($p.Id)): python $($argumente -join ' ')"

# Raportul de dimineata (19 octombrie 2026, cerut de Adrian): Task Scheduler porneste la 07:40, in fiecare zi, Claude Code
# fara fereastra (claude -p), din C:\Kronos\cyberspace, cu instructiunea din unelte/raport_dimineata.txt: raportul scris
# dupa regula din CLAUDE.md (docs/rapoarte/...), cu commit si push. Asa raportul nu mai depinde de sesiunea deschisa.
# Tot ce scrie e in lucru/raport_dimineata.log.
#   -Uscat: proba pe uscat; Claude Code doar citeste si spune ce ar scrie (fara fisiere, fara commit, fara push).
param([switch]$Uscat)

$ErrorActionPreference = "Stop"
$radacina = Split-Path -Parent $PSScriptRoot
Set-Location $radacina
$jurnal = Join-Path $radacina "lucru\raport_dimineata.log"
$claude = Join-Path $env:USERPROFILE ".local\bin\claude.exe"
[Console]::OutputEncoding = [Text.Encoding]::UTF8
$OutputEncoding = New-Object System.Text.UTF8Encoding $false

function Scrie([string]$text) {
    Add-Content -Path $jurnal -Value ("[{0}] {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $text) -Encoding utf8
}

# S14 (21 octombrie 2026): instructiunea se citeste dupa git pull, ca sa fie cea de pe GitHub. Daca pull-ul pica
# (fara retea, conflict), scriem in jurnal si continuam cu fisierul local: raportul nu se opreste din cauza asta.
$ErrorActionPreference = "Continue"
try {
    $iesire = & git pull --ff-only 2>&1 | Out-String
    if ($LASTEXITCODE -eq 0) { Scrie ("git pull --ff-only: " + $iesire.Trim()) }
    else { Scrie ("git pull --ff-only a picat (cod $LASTEXITCODE), continui cu fisierul local: " + $iesire.Trim()) }
} catch {
    Scrie ("git pull --ff-only a picat, continui cu fisierul local: " + $_)
}
$ErrorActionPreference = "Stop"

$instructiunea = Get-Content (Join-Path $PSScriptRoot "raport_dimineata.txt") -Encoding utf8 -Raw
$citire = @("Read", "Glob", "Grep", "Bash(git status*)", "Bash(git log*)", "Bash(git diff*)", "Bash(git show*)",
            "Bash(ls *)", "Bash(cat *)", "Bash(tail *)", "Bash(head *)", "Bash(grep *)", "Bash(date*)", "Bash(nvidia-smi*)")
if ($Uscat) {
    $instructiunea = "PROBA PE USCAT: nu scrie niciun fisier, nu rula preinregistrare.py --inchide, nu face commit sau push. " +
                     "Fa doar pasii de citire si scrie aici, in raspuns, raportul pe care l-ai pune in docs/rapoarte/ " +
                     "si comenzile pe care le-ai rula.`n`n" + $instructiunea
    $unelte = $citire + @("Bash(.venv/Scripts/python -X utf8 -c *)", "Bash(CUDA_VISIBLE_DEVICES=-1 .venv/Scripts/python -m pytest*)")
    $mod = "default"
} else {
    $unelte = $citire + @("Write", "Edit", "Bash(.venv/Scripts/python *)", "Bash(CUDA_VISIBLE_DEVICES=-1 .venv/Scripts/python *)",
                          "Bash(git add docs/*)", "Bash(git commit *)", "Bash(git push*)")
    $mod = "acceptEdits"
}

Scrie ("Pornesc Claude Code" + $(if ($Uscat) { " (pe uscat)" } else { "" }) + ".")
$ErrorActionPreference = "Continue"
$instructiunea | & $claude -p --permission-mode $mod --allowedTools @unelte 2>&1 |
    ForEach-Object { Add-Content -Path $jurnal -Value ("$_") -Encoding utf8 }
$cod = $LASTEXITCODE
Scrie "Claude Code s-a incheiat (cod $cod)."
exit $cod

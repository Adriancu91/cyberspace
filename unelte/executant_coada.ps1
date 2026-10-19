# Executantul din cascada (19 octombrie 2026, cerut de Adrian; regulile: plan/REGULI_CASCADA.md): Task Scheduler
# porneste la fiecare 30 de minute Claude Code fara fereastra (claude -p), din C:\Kronos\cyberspace, cu instructiunea
# din unelte/executant_coada.txt: ia prima sarcina aprobat din plan/coada.md, o porneste, iar la final scrie raportul.
# O singura rulare odata (lucru/executant_coada.lock). Tot ce scrie e in lucru/executant_coada.log.
#   -Proba: coada de proba plan/coada_proba.md (Adrian: separata de plan/coada.md, pe care proba n-are voie s-o
#           atinga), sarcinile in lucru/cascada_proba, rapoartele in docs/rapoarte/ (cu "proba" in nume), cu commit si
#           push. Sarcinile de proba sunt pe procesor, deci pot rula si cand placa e ocupata.
param([switch]$Proba)

$ErrorActionPreference = "Stop"
$radacina = Split-Path -Parent $PSScriptRoot
Set-Location $radacina
$jurnal = Join-Path $radacina "lucru\executant_coada.log"
$blocare = Join-Path $radacina "lucru\executant_coada.lock"
$claude = Join-Path $env:USERPROFILE ".local\bin\claude.exe"
[Console]::OutputEncoding = [Text.Encoding]::UTF8
$OutputEncoding = New-Object System.Text.UTF8Encoding $false

function Scrie([string]$text) {
    Add-Content -Path $jurnal -Value ("[{0}] {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $text) -Encoding utf8
}

# O singura rulare odata: daca blocarea e a unui proces care inca merge, ies.
if (Test-Path $blocare) {
    $vechi = (Get-Content $blocare -Raw).Trim()
    if ($vechi -match '^\d+$' -and (Get-Process -Id ([int]$vechi) -ErrorAction SilentlyContinue)) {
        Scrie "Ruleaza deja executantul (procesul $vechi); ies."
        exit 0
    }
    Scrie "Blocarea veche ($vechi) nu mai e a nimanui; o iau eu."
}
Set-Content -Path $blocare -Value $PID -Encoding ascii

try {
    $instructiunea = Get-Content (Join-Path $PSScriptRoot "executant_coada.txt") -Encoding utf8 -Raw
    if ($Proba) {
        $instructiunea = $instructiunea.Replace("{COADA}", "plan/coada_proba.md").Replace("{RAPOARTE}", "docs/rapoarte")
        $instructiunea = "PROBA (ceruta de Adrian): coada e plan/coada_proba.md. plan/coada.md NU o atingi deloc (S1 ruleaza acum, " +
                         "S2 e pentru maine ziua). La unelte/cascada.py adauga mereu `--dosar lucru/cascada_proba` (dupa numele " +
                         "sarcinii). Sarcinile de proba sunt pe procesor: ia-le chiar daca placa e ocupata de noaptea 10 (doar in " +
                         "proba asta). Rapoartele au `proba` in nume.`n`n" + $instructiunea
    } else {
        $instructiunea = $instructiunea.Replace("{COADA}", "plan/coada.md").Replace("{RAPOARTE}", "docs/rapoarte")
    }
    $unelte = @("Read", "Glob", "Grep", "Write", "Edit",
                "Bash(git status*)", "Bash(git log*)", "Bash(git diff*)", "Bash(git show*)",
                "Bash(ls *)", "Bash(cat *)", "Bash(tail *)", "Bash(head *)", "Bash(grep *)", "Bash(date*)", "Bash(nvidia-smi*)",
                "Bash(.venv/Scripts/python *)", "Bash(CUDA_VISIBLE_DEVICES=-1 .venv/Scripts/python *)")
    $unelte += @("Bash(git pull*)", "Bash(git rebase --abort*)", "Bash(git add *)", "Bash(git commit *)", "Bash(git push*)")
    $interzise = @("Edit(kronos/**)", "Edit(module/examen_bpb.py)", "Edit(config/continuum_ws.toml)",
                   "Edit(lucru/jurnal/**)", "Bash(*pip *)", "Bash(*curl *)", "Bash(*wget *)",
                   "Bash(*schtasks*)", "Bash(*ScheduledTask*)", "Bash(rm *)", "Bash(git push --force*)", "Bash(git reset*)")
    if ($Proba) { $interzise += @("Edit(plan/coada.md)") }
    $inainte = (git rev-parse HEAD).Trim()

    Scrie ("Pornesc Claude Code" + $(if ($Proba) { " (proba)" } else { "" }) + ".")
    $ErrorActionPreference = "Continue"
    $instructiunea | & $claude -p --permission-mode acceptEdits --allowedTools @unelte --disallowedTools @interzise 2>&1 |
        ForEach-Object { Add-Content -Path $jurnal -Value ("$_") -Encoding utf8 }
    $cod = $LASTEXITCODE
    Scrie "Claude Code s-a incheiat (cod $cod)."

    # Paza de dupa: nimic in kronos/ sau in examen, nici in commit-uri noi, nici nesalvat.
    $schimbate = @(git diff --name-only $inainte HEAD) + @(git status --porcelain | ForEach-Object { $_.Substring(3) })
    $atinse = $schimbate | Where-Object { $_ -like "kronos/*" -or $_ -eq "module/examen_bpb.py" }
    if ($atinse) { Scrie ("ATENTIE: executantul a atins ce nu are voie: " + ($atinse -join ", ")) }
    exit $cod
} finally {
    Remove-Item $blocare -ErrorAction SilentlyContinue
}

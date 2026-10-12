# Ruleaza la fiecare logare in Windows (Task Scheduler, vezi unelte/programeaza_dupa_logare_ws.ps1).
# -Blocheaza: blocheaza ecranul, dar doar daca logarea e la mai putin de -MinuteDeLaPornire minute dupa pornirea
#   calculatorului, adica logarea automata de dupa o repornire. La o logare facuta de om mai tarziu nu blocheaza.
#   Sarcinile pornite ruleaza mai departe si cu ecranul blocat.
# -Claude: porneste Claude Code cu Remote Control, continuand ultima conversatie din C:\Kronos, intr-o fereastra de
#   terminal. Nu porneste a doua oara daca ruleaza deja.
# Tot ce face se noteaza in C:\Kronos\cyberspace\lucru\dupa_logare.log.
param(
    [switch]$Blocheaza,
    [switch]$Claude,
    [double]$MinuteDeLaPornire = 5,
    [string]$Folder = "C:\Kronos",
    [string]$Nume = "Kronos"
)

$radacina = Split-Path -Parent $PSScriptRoot
$jurnal = Join-Path $radacina "lucru\dupa_logare.log"
New-Item -ItemType Directory -Force (Join-Path $radacina "lucru") | Out-Null

function Scrie([string]$text) {
    Add-Content -Path $jurnal -Value ("[{0}] {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $text) -Encoding utf8
}

$pornit = (Get-CimInstance Win32_OperatingSystem).LastBootUpTime
$minute = [math]::Round(((Get-Date) - $pornit).TotalMinutes, 1)

if ($Blocheaza) {
    if ($minute -le $MinuteDeLaPornire) {
        Scrie "Logare la $minute minute dupa pornirea calculatorului: blochez ecranul."
        & rundll32.exe user32.dll,LockWorkStation
    } else {
        Scrie "Logare la $minute minute dupa pornire (facuta de om): nu blochez ecranul."
    }
}

if ($Claude) {
    $ruleaza = @(Get-CimInstance Win32_Process -Filter "Name='claude.exe'" |
        Where-Object { $_.CommandLine -and $_.CommandLine -like "*--remote-control*" }).Count -gt 0
    if ($ruleaza) {
        Scrie "Claude Code cu Remote Control ruleaza deja: nu pornesc altul."
    } else {
        $claude = Join-Path $env:USERPROFILE ".local\bin\claude.exe"
        if (-not (Test-Path $claude)) {
            Scrie "Nu gasesc $claude : Claude Code nu a pornit."
        } else {
            Scrie "Pornesc Claude Code cu Remote Control ('$Nume'), continuand ultima conversatie din $Folder."
            $comanda = "Set-Location '$Folder'; & '$claude' --continue --remote-control '$Nume'"
            Start-Process -FilePath "powershell.exe" -ArgumentList @("-NoExit", "-NoProfile", "-Command", $comanda) -WorkingDirectory $Folder
        }
    }
}

# Ruleaza la fiecare logare in Windows (Task Scheduler, vezi unelte/programeaza_dupa_logare_ws.ps1).
# -Blocheaza: blocheaza ecranul, dar doar daca logarea e la mai putin de -MinuteDeLaPornire minute dupa pornirea
#   calculatorului, adica logarea automata de dupa o repornire. La o logare facuta de om mai tarziu nu blocheaza.
#   Sarcinile pornite ruleaza mai departe si cu ecranul blocat.
# -Claude: porneste Claude Code cu Remote Control, continuand ultima conversatie din C:\Kronos, intr-o fereastra de
#   terminal. Nu porneste a doua oara daca ruleaza deja.
# -Proba: nu porneste nimic; doar scrie in jurnal ce ar porni (comanda intreaga), ca sa se poata verifica.
# Tot ce face se noteaza in C:\Kronos\cyberspace\lucru\dupa_logare.log (sau in -Jurnal).
#
# 16 octombrie 2026: pana atunci, variabila cu calea lui claude.exe se numea $claude, adica la fel ca parametrul
# -Claude (PowerShell nu deosebeste literele mari de cele mici). O cale nu se poate pune intr-un parametru de tip
# switch, deci variabila ramanea "True", iar la logarea automata de la 00:33 jurnalul a scris "Nu gasesc True" si
# Claude Code n-a pornit. Acum calea e in $exe.
#
#   powershell -ExecutionPolicy Bypass -File unelte\dupa_logare_ws.ps1 -Claude -Proba    # proba, fara sa porneasca
param(
    [switch]$Blocheaza,
    [switch]$Claude,
    [double]$MinuteDeLaPornire = 5,
    [string]$Folder = "C:\Kronos",
    [string]$Nume = "Kronos",
    [switch]$Proba,
    [string]$Jurnal = "",
    [string]$Exe = ""
)

$radacina = Split-Path -Parent $PSScriptRoot
$fisierJurnal = if ($Jurnal) { $Jurnal } else { Join-Path $radacina "lucru\dupa_logare.log" }
New-Item -ItemType Directory -Force (Split-Path -Parent $fisierJurnal) | Out-Null

function Scrie([string]$text) {
    Add-Content -Path $fisierJurnal -Value ("[{0}] {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $text) -Encoding utf8
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
    $exe = if ($Exe) { $Exe } else { Join-Path $env:USERPROFILE ".local\bin\claude.exe" }
    if ($ruleaza -and -not $Proba) {
        Scrie "Claude Code cu Remote Control ruleaza deja: nu pornesc altul."
    } elseif (-not (Test-Path $exe)) {
        Scrie "Nu gasesc $exe : Claude Code nu a pornit."
    } else {
        $comanda = "Set-Location '$Folder'; & '$exe' --continue --remote-control '$Nume'"
        if ($Proba) {
            $acum = if ($ruleaza) { "; acum ruleaza deja unul, deci la o logare adevarata n-as porni altul" } else { "" }
            Scrie "Proba (nu pornesc nimic): as porni powershell.exe -NoExit -Command `"$comanda`"$acum."
        } else {
            Scrie "Pornesc Claude Code cu Remote Control ('$Nume'), continuand ultima conversatie din $Folder."
            Start-Process -FilePath "powershell.exe" -ArgumentList @("-NoExit", "-NoProfile", "-Command", $comanda) -WorkingDirectory $Folder
        }
    }
}

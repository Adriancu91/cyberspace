# Ruleaza la fiecare logare in Windows (Task Scheduler, vezi unelte/programeaza_dupa_logare_ws.ps1).
# -Blocheaza: blocheaza ecranul, dar doar daca logarea e la mai putin de -MinuteDeLaPornire minute dupa pornirea
#   calculatorului, adica logarea automata de dupa o repornire. La o logare facuta de om mai tarziu nu blocheaza.
#   Sarcinile pornite ruleaza mai departe si cu ecranul blocat.
# -Claude: porneste Claude Code cu Remote Control, intr-o fereastra de terminal, in -Folder. Daca folderul are o
#   conversatie salvata (in ~\.claude\projects), o continua (--continue); daca nu are, sau daca --continue se opreste
#   in primul minut, porneste o sesiune noua (claude --remote-control "Kronos"). Nu porneste a doua oara daca ruleaza
#   deja unul cu Remote Control "-Nume". Il foloseste si paznicul de procese (unelte/paznic_procese_ws.ps1).
# -Proba: nu porneste nimic; doar scrie in jurnal ce ar porni (comanda intreaga), ca sa se poata verifica.
# Tot ce face se noteaza in C:\Kronos\cyberspace\lucru\dupa_logare.log (sau in -Jurnal).
#
# 16 octombrie 2026: pana atunci, variabila cu calea lui claude.exe se numea $claude, adica la fel ca parametrul
# -Claude (PowerShell nu deosebeste literele mari de cele mici). O cale nu se poate pune intr-un parametru de tip
# switch, deci variabila ramanea "True", iar la logarea automata de la 00:33 jurnalul a scris "Nu gasesc True" si
# Claude Code n-a pornit. Acum calea e in $exe.
#
# 17 octombrie 2026: Claude Code s-a inchis la 07:59, iar "claude --continue" pornit de mana in C:\Kronos\cyberspace a
# raspuns "No conversation found to continue" (conversatia veche era a folderului C:\Kronos). De atunci: folderul
# implicit e C:\Kronos\cyberspace, iar fara o conversatie de continuat porneste o sesiune noua.
#
#   powershell -ExecutionPolicy Bypass -File unelte\dupa_logare_ws.ps1 -Claude -Proba    # proba, fara sa porneasca
param(
    [switch]$Blocheaza,
    [switch]$Claude,
    [double]$MinuteDeLaPornire = 5,
    [string]$Folder = "C:\Kronos\cyberspace",
    [string]$Nume = "Kronos",
    [switch]$Proba,
    [string]$Jurnal = "",
    [string]$Exe = "",
    [string]$Conversatii = ""   # unde isi tine Claude Code conversatiile (implicit ~\.claude\projects)
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
        Where-Object { $_.CommandLine -and $_.CommandLine -like "*--remote-control*$Nume*" }).Count -gt 0
    $exe = if ($Exe) { $Exe } else { Join-Path $env:USERPROFILE ".local\bin\claude.exe" }
    # Claude Code tine conversatiile unui folder in ~\.claude\projects\<calea, cu "-" in loc de ":" si "\">
    $proiecte = if ($Conversatii) { $Conversatii } else { Join-Path $env:USERPROFILE ".claude\projects" }
    $dosarConversatii = Join-Path $proiecte ($Folder -replace "[^A-Za-z0-9]", "-")
    $areConversatie = @(Get-ChildItem -Path $dosarConversatii -Filter "*.jsonl" -File -ErrorAction SilentlyContinue).Count -gt 0
    if ($ruleaza -and -not $Proba) {
        Scrie "Claude Code cu Remote Control '$Nume' ruleaza deja: nu pornesc altul."
    } elseif (-not (Test-Path $exe)) {
        Scrie "Nu gasesc $exe : Claude Code nu a pornit."
    } else {
        $noua = "& '$exe' --remote-control '$Nume'"
        if ($areConversatie) {
            # daca --continue se opreste in primul minut (de ex. "No conversation found"), porneste una noua
            $comanda = "Set-Location '$Folder'; `$t = Get-Date; & '$exe' --continue --remote-control '$Nume'; " +
                       "if (((Get-Date) - `$t).TotalSeconds -lt 60) { $noua }"
            $ce = "continuand ultima conversatie din $Folder"
        } else {
            $comanda = "Set-Location '$Folder'; $noua"
            $ce = "sesiune noua: $Folder nu are nicio conversatie de continuat (in $dosarConversatii)"
        }
        if ($Proba) {
            $acum = if ($ruleaza) { "; acum ruleaza deja unul, deci la o logare adevarata n-as porni altul" } else { "" }
            Scrie "Proba (nu pornesc nimic; $ce): as porni powershell.exe -NoExit -Command `"$comanda`"$acum."
        } else {
            Scrie "Pornesc Claude Code cu Remote Control ('$Nume'), $ce."
            Start-Process -FilePath "powershell.exe" -ArgumentList @("-NoExit", "-NoProfile", "-Command", $comanda) -WorkingDirectory $Folder
        }
    }
}

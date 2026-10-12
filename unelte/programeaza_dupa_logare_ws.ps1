# Pune in Task Scheduler ce porneste singur la fiecare logare in Windows (unelte/dupa_logare_ws.ps1):
#   "Kronos blocare ecran": blocheaza ecranul daca logarea e imediat dupa pornirea calculatorului (logarea automata);
#   "Kronos Claude Code":   porneste Claude Code cu Remote Control, la 30 de secunde dupa logare.
# Sarcinile ruleaza in contul utilizatorului de acum, doar cat e logat; nu cer parola si nici drepturi de administrator.
# Logarea automata insasi NU se pune de aici: se pune cu Autologon (Sysinternals), de catre om (docs/PORNIRE_automata.md).
#
#   powershell -ExecutionPolicy Bypass -File unelte\programeaza_dupa_logare_ws.ps1
#   powershell -ExecutionPolicy Bypass -File unelte\programeaza_dupa_logare_ws.ps1 -Sterge
param([switch]$Sterge)

$ErrorActionPreference = "Stop"
$radacina = Split-Path -Parent $PSScriptRoot
$script = Join-Path $radacina "unelte\dupa_logare_ws.ps1"
$sarcini = @("Kronos blocare ecran", "Kronos Claude Code")

foreach ($s in $sarcini) {
    if (Get-ScheduledTask -TaskName $s -ErrorAction SilentlyContinue) { Unregister-ScheduledTask -TaskName $s -Confirm:$false }
}
if ($Sterge) { Write-Output "Am sters sarcinile de dupa logare."; exit 0 }

$cine = New-ScheduledTaskPrincipal -UserId ([Security.Principal.WindowsIdentity]::GetCurrent().Name) -LogonType Interactive
$setari = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable `
    -ExecutionTimeLimit ([TimeSpan]::Zero) -MultipleInstances IgnoreNew

function Actiune([string]$ce) {
    # conhost --headless: scriptul insusi nu arata nicio fereastra (Claude Code isi deschide singur fereastra lui)
    $comanda = "--headless powershell.exe -NoProfile -ExecutionPolicy Bypass -File `"$script`" $ce"
    return New-ScheduledTaskAction -Execute "conhost.exe" -Argument $comanda -WorkingDirectory $radacina
}

$imediat = New-ScheduledTaskTrigger -AtLogOn -User $cine.UserId
Register-ScheduledTask -TaskName $sarcini[0] -Action (Actiune "-Blocheaza") -Trigger $imediat -Settings $setari -Principal $cine `
    -Description "Blocheaza ecranul daca logarea e imediat dupa pornirea calculatorului (logare automata)." | Out-Null

$dupa = New-ScheduledTaskTrigger -AtLogOn -User $cine.UserId
$dupa.Delay = "PT30S"
Register-ScheduledTask -TaskName $sarcini[1] -Action (Actiune "-Claude") -Trigger $dupa -Settings $setari -Principal $cine `
    -Description "Porneste Claude Code cu Remote Control, continuand ultima conversatie din C:\Kronos." | Out-Null

Get-ScheduledTask -TaskName "Kronos*" | Select-Object TaskName, State | Format-Table -AutoSize

# Pune in Task Scheduler paznicul de procese (unelte/paznic_procese_ws.ps1): peste un minut si apoi la fiecare 15
# minute, fara fereastra. Ruleaza in contul utilizatorului de acum, doar cat e logat; nu cere parola si nici drepturi
# de administrator.
#
#   powershell -ExecutionPolicy Bypass -File unelte\programeaza_paznic_procese_ws.ps1
#   powershell -ExecutionPolicy Bypass -File unelte\programeaza_paznic_procese_ws.ps1 -Sterge
param([switch]$Sterge)

$ErrorActionPreference = "Stop"
$radacina = Split-Path -Parent $PSScriptRoot
$nume = "Kronos paznic procese"

if (Get-ScheduledTask -TaskName $nume -ErrorAction SilentlyContinue) { Unregister-ScheduledTask -TaskName $nume -Confirm:$false }
if ($Sterge) { Write-Output "Am sters sarcina $nume."; exit 0 }

$script = Join-Path $radacina "unelte\paznic_procese_ws.ps1"
# conhost --headless: fara nicio fereastra (Claude Code isi deschide singur fereastra lui)
$actiune = New-ScheduledTaskAction -Execute "conhost.exe" -WorkingDirectory $radacina `
    -Argument "--headless powershell.exe -NoProfile -ExecutionPolicy Bypass -File `"$script`""
$setari = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable `
    -ExecutionTimeLimit ([TimeSpan]::Zero) -MultipleInstances IgnoreNew
$cine = New-ScheduledTaskPrincipal -UserId ([Security.Principal.WindowsIdentity]::GetCurrent().Name) -LogonType Interactive
$declansare = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) -RepetitionInterval (New-TimeSpan -Minutes 15)
Register-ScheduledTask -TaskName $nume -Action $actiune -Trigger $declansare -Settings $setari -Principal $cine `
    -Description "La fiecare 15 minute: porneste la loc Claude Code (Remote Control Kronos), interfata si CONTINUUM, daca lipsesc." | Out-Null
Write-Output "Programat: $nume, peste un minut si apoi la fiecare 15 minute."
Get-ScheduledTask -TaskName "Kronos*" | Get-ScheduledTaskInfo | Select-Object TaskName, NextRunTime, LastRunTime, LastTaskResult | Format-Table -AutoSize

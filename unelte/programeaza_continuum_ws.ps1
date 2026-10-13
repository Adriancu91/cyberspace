# Programeaza in Task Scheduler bucla CONTINUUM de pe workstation (unelte/continuum_ws.ps1), fara fereastra:
# porneste peste un minut si dupa fiecare logare in Windows. Ruleaza in contul utilizatorului de acum, cat timp el e
# logat (nu cere parola si nici drepturi de administrator).
#
#   powershell -ExecutionPolicy Bypass -File unelte\programeaza_continuum_ws.ps1
#   ... -Sterge       # sterge sarcina (bucla care ruleaza deja se opreste cu butonul STOP, nu de aici)
param(
    [switch]$Sterge
)

$ErrorActionPreference = "Stop"
$radacina = Split-Path -Parent $PSScriptRoot
$nume = "Kronos continuum ws"

if (Get-ScheduledTask -TaskName $nume -ErrorAction SilentlyContinue) { Unregister-ScheduledTask -TaskName $nume -Confirm:$false }
if ($Sterge) { Write-Output "Am sters sarcina $nume."; exit 0 }

$script = Join-Path $radacina "unelte\continuum_ws.ps1"
# conhost --headless: fara nicio fereastra, nici macar una care clipeste
$actiune = New-ScheduledTaskAction -Execute "conhost.exe" -WorkingDirectory $radacina `
    -Argument "--headless powershell.exe -NoProfile -ExecutionPolicy Bypass -File `"$script`""
$setari = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable `
    -ExecutionTimeLimit ([TimeSpan]::Zero) -MultipleInstances IgnoreNew
$cine = New-ScheduledTaskPrincipal -UserId ([Security.Principal.WindowsIdentity]::GetCurrent().Name) -LogonType Interactive
$declansari = @((New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1)), (New-ScheduledTaskTrigger -AtLogOn -User $cine.UserId))
Register-ScheduledTask -TaskName $nume -Action $actiune -Trigger $declansari -Settings $setari -Principal $cine `
    -Description "Bucla CONTINUUM de pe workstation (config/continuum_ws.toml), fara fereastra." | Out-Null
Write-Output "Programat: $nume porneste peste un minut si dupa fiecare logare in Windows."
Get-ScheduledTask -TaskName "Kronos*" | Get-ScheduledTaskInfo | Select-Object TaskName, NextRunTime, LastRunTime, LastTaskResult | Format-Table -AutoSize

# Programeaza in Task Scheduler pornirea unei antrenari lungi (unelte/noapte_ws.ps1), fara fereastra.
# Sarcinile ruleaza in contul utilizatorului de acum, cat timp el e logat in Windows (nu cer parola si nici drepturi
# de administrator). Dupa o repornire de Windows pornesc abia dupa logare: vezi docs/PORNIRE_automata.md.
#
#   powershell -ExecutionPolicy Bypass -File unelte\programeaza_noapte_ws.ps1 -Config config/ws_w1.toml -Ore 10 -AlaturiDe fapte_zero -La 19:00 -OprireLa 07:30
#   ... -LaLogare     # in plus: reia antrenarea la fiecare logare in Windows (dupa o repornire), pana la -OprireLa
#   ... -Sterge       # sterge sarcinile acestei configurari
param(
    [Parameter(Mandatory = $true)][string]$Config,
    [int]$Ore = 10,
    [string]$AlaturiDe = "",
    [string]$La = "19:00",
    [string]$OprireLa = "07:30",
    [switch]$LaLogare,
    [switch]$Sterge
)

$ErrorActionPreference = "Stop"
$radacina = Split-Path -Parent $PSScriptRoot
$nume = [IO.Path]::GetFileNameWithoutExtension($Config)
$sarcini = @{ porneste = "Kronos noapte $nume"; opreste = "Kronos oprire $nume"; logare = "Kronos reluare $nume" }

foreach ($s in $sarcini.Values) {
    if (Get-ScheduledTask -TaskName $s -ErrorAction SilentlyContinue) { Unregister-ScheduledTask -TaskName $s -Confirm:$false }
}
if ($Sterge) { Write-Output "Am sters sarcinile pentru $nume."; exit 0 }

function Actiune([string]$inPlus) {
    $script = Join-Path $radacina "unelte\noapte_ws.ps1"
    $comanda = "--headless powershell.exe -NoProfile -ExecutionPolicy Bypass -File `"$script`" -Config $Config -Ore $Ore $inPlus"
    if ($AlaturiDe) { $comanda += " -AlaturiDe $AlaturiDe" }
    # conhost --headless: fara nicio fereastra, nici macar una care clipeste
    return New-ScheduledTaskAction -Execute "conhost.exe" -Argument $comanda -WorkingDirectory $radacina
}

$setari = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable `
    -ExecutionTimeLimit ([TimeSpan]::Zero) -MultipleInstances IgnoreNew
$cine = New-ScheduledTaskPrincipal -UserId ([Security.Principal.WindowsIdentity]::GetCurrent().Name) -LogonType Interactive

$acum = Get-Date
$pornire = [datetime]::ParseExact($La, "HH:mm", $null)
if ($pornire -le $acum) { $pornire = $pornire.AddDays(1) }
$oprire = [datetime]::ParseExact($OprireLa, "HH:mm", $null)
while ($oprire -le $pornire) { $oprire = $oprire.AddDays(1) }

Register-ScheduledTask -TaskName $sarcini.porneste -Action (Actiune "") -Trigger (New-ScheduledTaskTrigger -Once -At $pornire) `
    -Settings $setari -Principal $cine -Description "Porneste antrenarea lunga $nume ($Ore ore), fara fereastra." | Out-Null
Register-ScheduledTask -TaskName $sarcini.opreste -Action (Actiune "-Opreste") -Trigger (New-ScheduledTaskTrigger -Once -At $oprire) `
    -Settings $setari -Principal $cine -Description "Cere oprirea antrenarii $nume, daca mai ruleaza." | Out-Null
Write-Output ("Programat: pornire {0:yyyy-MM-dd HH:mm}, oprire de siguranta {1:yyyy-MM-dd HH:mm}." -f $pornire, $oprire)
if ($LaLogare) {
    Register-ScheduledTask -TaskName $sarcini.logare -Action (Actiune "-PanaLa $OprireLa") -Trigger (New-ScheduledTaskTrigger -AtLogOn -User $cine.UserId) `
        -Settings $setari -Principal $cine -Description "Dupa o repornire de Windows si logare: reia antrenarea $nume de unde a ramas." | Out-Null
    Write-Output "Programat si: reluare la fiecare logare in Windows, pana la $OprireLa."
}
Get-ScheduledTask -TaskName "Kronos*" | Get-ScheduledTaskInfo | Select-Object TaskName, NextRunTime, LastRunTime, LastTaskResult | Format-Table -AutoSize

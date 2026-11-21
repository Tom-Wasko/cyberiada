# Instalator cyberiady: .\zainstaluj.ps1 [-Sprawdz] [-BezPamieci]
param([switch]$Sprawdz, [switch]$BezPamieci)
$argumenty = @()
if ($Sprawdz) { $argumenty += '--sprawdz' }
if ($BezPamieci) { $argumenty += '--bez-pamieci' }
python -m pip install --quiet --user pyyaml
python -X utf8 "$PSScriptRoot\narzedzia\instaluj.py" @argumenty
exit $LASTEXITCODE

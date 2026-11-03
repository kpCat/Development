[CmdletBinding()]
param([Parameter(Mandatory=$true)][string]$Path, [Parameter(Mandatory=$true)][string]$OutputDirectory)
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'Harness.Common.ps1')
if (-not (Get-Command python -ErrorAction SilentlyContinue)) { throw 'Нужен Python 3.8+ в PATH; пакеты и модели не требуются.' }
Invoke-HarnessPython -PythonArguments @((Join-Path $PSScriptRoot 'xlsx_mockup.py'), $Path, '--out', $OutputDirectory)

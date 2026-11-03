[CmdletBinding()]
param([switch]$Staged, [string]$PrivatePatternsPath, [string]$ReportPath)
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'Harness.Common.ps1')
if (-not (Get-Command python -ErrorAction SilentlyContinue)) { throw 'Нужен Python 3.8+ в PATH.' }
$arguments = @((Join-Path $PSScriptRoot 'safety_audit.py'), '--root', (Split-Path $PSScriptRoot -Parent))
if ($Staged) { $arguments += '--staged' }
if ($PrivatePatternsPath) { $arguments += @('--patterns', $PrivatePatternsPath) }
if ($ReportPath) { $arguments += @('--report', $ReportPath) }
Invoke-HarnessPython -PythonArguments $arguments

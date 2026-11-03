[CmdletBinding()]
param([ValidateSet('mkr','mkp')][string]$Name='mkr', [string]$ProjectRoot, [string]$ConfigPath,
    [string]$LibraryRoot, [string]$ReportPath)
. (Join-Path $PSScriptRoot 'Harness.Common.ps1')
$root = Resolve-HarnessProject -Name $Name -ProjectRoot $ProjectRoot -ConfigPath $ConfigPath
if (-not $LibraryRoot) { $LibraryRoot = $root }
if (-not (Get-Command python -ErrorAction SilentlyContinue)) { throw 'Нужен Python 3.8+ в PATH.' }
$arguments = @((Join-Path $PSScriptRoot 'check_library.py'), '--project', $root, '--library', $LibraryRoot)
if ($ReportPath) { $arguments += @('--report', $ReportPath) }
Invoke-HarnessPython -PythonArguments $arguments

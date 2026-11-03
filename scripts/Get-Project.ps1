[CmdletBinding()]
param([ValidateSet('mkr','mkp')][string]$Name = 'mkr', [string]$ProjectRoot, [string]$ConfigPath)
. (Join-Path $PSScriptRoot 'Harness.Common.ps1')
Resolve-HarnessProject -Name $Name -ProjectRoot $ProjectRoot -ConfigPath $ConfigPath

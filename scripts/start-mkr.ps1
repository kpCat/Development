[CmdletBinding()]
param([string]$ProjectRoot, [string]$ConfigPath, [ValidateSet('opencode','bionic')][string]$Harness='opencode',
    [switch]$DryRun, [switch]$Launch)
. (Join-Path $PSScriptRoot 'Harness.Common.ps1')
Start-HarnessProject -Name mkr -ProjectRoot $ProjectRoot -ConfigPath $ConfigPath -Harness $Harness -DryRun:$DryRun -Launch:$Launch

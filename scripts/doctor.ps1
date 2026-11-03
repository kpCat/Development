[CmdletBinding()]
param([ValidateSet('mkr','mkp')][string]$Name='mkr', [string]$ProjectRoot, [string]$ConfigPath)
. (Join-Path $PSScriptRoot 'Harness.Common.ps1')
$root = Resolve-HarnessProject -Name $Name -ProjectRoot $ProjectRoot -ConfigPath $ConfigPath
$missing = @()
foreach ($relative in @('AGENTS.md','docs/ai/INDEX.md','.agents/skills')) {
    $exists = Test-Path -LiteralPath (Join-Path $root $relative)
    if (-not $exists) { $missing += $relative }
    [pscustomobject]@{Check=$relative; Status=$(if ($exists) {'PRESENT'} else {'MISSING'})}
}
foreach ($toolName in @('python','powershell','dotnet','msbuild','opencode','bionic')) {
    [pscustomobject]@{Check=$toolName; Status=$(if (Get-Command $toolName -ErrorAction SilentlyContinue) {'FOUND_NOT_RUN'} else {'NOT_FOUND'})}
}
[pscustomobject]@{Check='context_length=65536'; Status='FUTURE_NOT_TESTED'}
[pscustomobject]@{Check='model/network/live DB'; Status='NOT_CONTACTED'}
if ($missing.Count -gt 0) { throw 'Не хватает проектной документации/skills. Проверьте путь или установите подготовленный приватный overlay.' }

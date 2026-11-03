[CmdletBinding()]
param([Parameter(Mandatory=$true)][ValidateSet('mkr','mkp')][string]$Name,
    [string]$Path, [string]$ConfigPath, [switch]$PickFolder)
. (Join-Path $PSScriptRoot 'Harness.Common.ps1')
if (-not $Path -and $PickFolder) {
    Add-Type -AssemblyName System.Windows.Forms
    $dialog = New-Object System.Windows.Forms.FolderBrowserDialog
    try {
        $dialog.Description = 'Выберите корень рабочего репозитория'
        if ($dialog.ShowDialog() -eq [Windows.Forms.DialogResult]::OK) { $Path = $dialog.SelectedPath }
    } finally { $dialog.Dispose() }
}
if (-not $Path) { throw 'Передайте -Path или используйте необязательный -PickFolder.' }
$root = Test-HarnessProject -Name $Name -Root $Path
$file = Get-HarnessConfigPath $ConfigPath
$config = Read-HarnessConfig $file
if ($null -eq $config) { $config = [pscustomobject]@{schemaVersion=1; projects=[pscustomobject]@{}} }
$entry = [pscustomobject]@{root=$root; harness='opencode'; targetContextTokens=65536; contextStatus='FUTURE_NOT_TESTED'}
$config.projects | Add-Member -MemberType NoteProperty -Name $Name -Value $entry -Force
$parent = Split-Path $file -Parent
New-Item -ItemType Directory -Path $parent -Force | Out-Null
$temporary = Join-Path $parent ([IO.Path]::GetRandomFileName())
$backup = $temporary + '.bak'
try {
    [IO.File]::WriteAllText($temporary, ($config | ConvertTo-Json -Depth 10), (New-Object Text.UTF8Encoding($true)))
    if (Test-Path -LiteralPath $file) { [IO.File]::Replace($temporary, $file, $backup) }
    else { [IO.File]::Move($temporary, $file) }
} finally {
    if (Test-Path -LiteralPath $temporary) { Remove-Item -LiteralPath $temporary }
    if (Test-Path -LiteralPath $backup) { Remove-Item -LiteralPath $backup }
}
Write-Output "Проект $Name зарегистрирован. Локальная конфигурация сохранена."

$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
$files = @(Get-ChildItem -LiteralPath (Join-Path $root 'scripts'), $PSScriptRoot -Filter '*.ps1' -File)
$failures = @()
foreach ($file in $files) {
    $tokens = $null
    $parseErrors = $null
    [void][Management.Automation.Language.Parser]::ParseFile($file.FullName, [ref]$tokens, [ref]$parseErrors)
    foreach ($parseError in $parseErrors) { $failures += ($file.Name + ': ' + $parseError.Message) }
    $bytes = [IO.File]::ReadAllBytes($file.FullName)
    if ($bytes.Length -lt 3 -or $bytes[0] -ne 239 -or $bytes[1] -ne 187 -or $bytes[2] -ne 191) {
        $failures += ($file.Name + ': требуется UTF-8 BOM для Windows PowerShell 5.1')
    }
}
if ($failures.Count -gt 0) { throw ($failures -join [Environment]::NewLine) }
Write-Output ('PASS: PowerShell ' + $PSVersionTable.PSVersion + ', scripts=' + $files.Count)

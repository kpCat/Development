$ErrorActionPreference = 'Stop'
$scripts = Join-Path (Split-Path $PSScriptRoot -Parent) 'scripts'
$fixture = Join-Path ([IO.Path]::GetTempPath()) ('harness пробел ' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $fixture | Out-Null
$config = Join-Path $fixture 'projects.json'
$original = $env:MKR_PROJECT_ROOT
function Assert-Equal($Actual, $Expected, $Message) {
    if ($Actual -cne $Expected) { throw "$Message : $Actual" }
}
try {
    foreach ($name in @('проект один', 'проект два')) {
        $root = Join-Path $fixture $name
        New-Item -ItemType Directory -Path (Join-Path $root '.git'), (Join-Path $root 'src/libs/MKR.Core') -Force | Out-Null
        [IO.File]::WriteAllText((Join-Path $root 'MKR.sln'), 'synthetic')
    }
    $first = Join-Path $fixture 'проект один'
    $second = Join-Path $fixture 'проект два'
    & (Join-Path $scripts 'Set-Project.ps1') -Name mkr -Path $first -ConfigPath $config | Out-Null
    $env:MKR_PROJECT_ROOT = ''
    Push-Location ([IO.Path]::GetTempPath())
    try {
        Assert-Equal (& (Join-Path $scripts 'Get-Project.ps1') -Name mkr -ConfigPath $config) $first 'JSON mapping'
        $env:MKR_PROJECT_ROOT = $second
        Assert-Equal (& (Join-Path $scripts 'Get-Project.ps1') -Name mkr -ConfigPath $config) $second 'env priority'
        Assert-Equal (& (Join-Path $scripts 'Get-Project.ps1') -Name mkr -ProjectRoot $first -ConfigPath $config) $first 'argument priority'
        $dry = & (Join-Path $scripts 'start-mkr.ps1') -ProjectRoot $first -DryRun -ConfigPath $config
        Assert-Equal $dry.WorkingDirectory $first 'DryRun cwd'
        Assert-Equal $dry.Mode 'DryRun' 'DryRun mode'
        Assert-Equal $dry.TargetContextTokens 65536 'future target'
        $default = & (Join-Path $scripts 'start-mkr.ps1') -ProjectRoot $first -ConfigPath $config
        Assert-Equal $default.Mode 'DryRun' 'safe default'
        $bionic = & (Join-Path $scripts 'start-mkr.ps1') -ProjectRoot $first -ConfigPath $config -Harness bionic -DryRun
        Assert-Equal $bionic.Command 'GUI_ONLY' 'Bionic GUI path'
        $failed = $false
        try { & (Join-Path $scripts 'start-mkr.ps1') -ProjectRoot $first -DryRun -Launch | Out-Null } catch { $failed = $true }
        if (-not $failed) { throw 'Противоречивые flags должны отвергаться.' }
        & (Join-Path $scripts 'Set-Project.ps1') -Name mkr -Path $second -ConfigPath $config | Out-Null
        $env:MKR_PROJECT_ROOT = ''
        Assert-Equal (& (Join-Path $scripts 'Get-Project.ps1') -Name mkr -ConfigPath $config) $second 'relocation'
        New-Item -ItemType Directory -Path (Join-Path $second 'docs/ai'), (Join-Path $second '.agents/skills') -Force | Out-Null
        [IO.File]::WriteAllText((Join-Path $second 'AGENTS.md'), 'synthetic')
        [IO.File]::WriteAllText((Join-Path $second 'docs/ai/INDEX.md'), 'synthetic')
        $doctor = @(& (Join-Path $scripts 'doctor.ps1') -Name mkr -ProjectRoot $second -ConfigPath $config)
        Assert-Equal @($doctor | Where-Object { $_.Check -eq 'python' }).Count 1 'doctor offline tool inventory'
        $failed = $false
        try { & (Join-Path $scripts 'Get-Project.ps1') -Name mkp -ConfigPath $config | Out-Null } catch { $failed = $true }
        if (-not $failed) { throw 'MKP должен требовать независимую регистрацию.' }
        $mkp = Join-Path $fixture 'отдельный mkp'
        New-Item -ItemType Directory -Path (Join-Path $mkp '.git'), (Join-Path $mkp 'src') -Force | Out-Null
        [IO.File]::WriteAllText((Join-Path $mkp 'MKP.sln'), 'synthetic')
        & (Join-Path $scripts 'Set-Project.ps1') -Name mkp -Path $mkp -ConfigPath $config | Out-Null
        $mkpDry = & (Join-Path $scripts 'start-mkp.ps1') -ConfigPath $config -DryRun
        Assert-Equal $mkpDry.WorkingDirectory $mkp 'independent MKP root'
        Assert-Equal (& (Join-Path $scripts 'Get-Project.ps1') -Name mkr -ConfigPath $config) $second 'MKR preserved after MKP registration'
        $failed = $false
        try { & (Join-Path $scripts 'Get-Project.ps1') -Name mkr -ProjectRoot $fixture -ConfigPath $config | Out-Null } catch { $failed = $true }
        if (-not $failed) { throw 'Неверные markers должны отвергаться.' }
    } finally { Pop-Location }
    Write-Output 'PASS: JSON/env/argument, relocation, Unicode/spaces, cwd, DryRun, invalid markers, MKP isolation'
} finally {
    $env:MKR_PROJECT_ROOT = $original
    # Fixture deliberately retained in TEMP for inspection; no recursive deletion.
}

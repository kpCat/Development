Set-StrictMode -Version 2.0
$ErrorActionPreference = 'Stop'
$script:HarnessRoot = Split-Path $PSScriptRoot -Parent

function Invoke-HarnessPython {
    param([string[]]$PythonArguments)
    if (-not (Get-Command python -ErrorAction SilentlyContinue)) { throw 'Нужен Python 3.8+ в PATH.' }
    $previousEncoding = [Console]::OutputEncoding
    $previousPythonEncoding = $env:PYTHONIOENCODING
    $pythonExit = 1
    try {
        [Console]::OutputEncoding = New-Object Text.UTF8Encoding($false)
        $env:PYTHONIOENCODING = 'utf-8'
        & python @PythonArguments
        $pythonExit = $LASTEXITCODE
    } finally {
        [Console]::OutputEncoding = $previousEncoding
        $env:PYTHONIOENCODING = $previousPythonEncoding
    }
    if ($pythonExit -ne 0) { throw "Офлайн-проверка Python завершилась с кодом $pythonExit. См. причины выше." }
}

function Get-HarnessConfigPath {
    param([string]$ConfigPath)
    if ($ConfigPath) { return [IO.Path]::GetFullPath($ConfigPath) }
    return Join-Path $script:HarnessRoot 'config/projects.local.json'
}

function Read-HarnessConfig {
    param([string]$ConfigPath)
    $file = Get-HarnessConfigPath $ConfigPath
    if (-not (Test-Path -LiteralPath $file -PathType Leaf)) { return $null }
    try { $config = Get-Content -LiteralPath $file -Raw -Encoding UTF8 | ConvertFrom-Json }
    catch { throw 'Не удалось прочитать локальный JSON. Проверьте config/projects.local.json.' }
    if (-not $config.PSObject.Properties['schemaVersion'] -or $config.schemaVersion -ne 1 -or
        -not $config.PSObject.Properties['projects'] -or $null -eq $config.projects) {
        throw 'Неизвестная схема конфигурации. Требуются schemaVersion=1 и projects.'
    }
    return $config
}

function Test-HarnessProject {
    param([ValidateSet('mkr','mkp')][string]$Name, [string]$Root)
    if (-not $Root -or -not [IO.Path]::IsPathRooted($Root)) {
        throw 'Укажите абсолютный путь к проекту через -ProjectRoot, переменную окружения или Set-Project.ps1.'
    }
    $resolved = [IO.Path]::GetFullPath($Root).TrimEnd([IO.Path]::DirectorySeparatorChar)
    if (-not (Test-Path -LiteralPath $resolved -PathType Container)) {
        throw 'Проект перенесён или каталог недоступен. Повторите Set-Project.ps1 -Name с новым -Path.'
    }
    if (-not (Test-Path -LiteralPath (Join-Path $resolved '.git')) -or
        -not (Test-Path -LiteralPath (Join-Path $resolved 'src') -PathType Container)) {
        throw 'Это не корень проекта: требуются .git и каталог src.'
    }
    if ($Name -eq 'mkr') {
        if (-not (Test-Path -LiteralPath (Join-Path $resolved 'MKR.sln') -PathType Leaf) -or
            -not (Test-Path -LiteralPath (Join-Path $resolved 'src/libs/MKR.Core') -PathType Container)) {
            throw 'Для mkr требуются MKR.sln и src/libs/MKR.Core. Другой репозиторий не подставляется.'
        }
    } else {
        $solutions = @(Get-ChildItem -LiteralPath $resolved -Filter '*.sln' -File)
        if ($solutions.Count -eq 0 -or (Test-Path -LiteralPath (Join-Path $resolved 'MKR.sln'))) {
            throw 'Для mkp требуется отдельное решение .sln и src; ASU-MKR нельзя регистрировать как mkp.'
        }
    }
    return $resolved
}

function Resolve-HarnessProject {
    param([ValidateSet('mkr','mkp')][string]$Name, [string]$ProjectRoot, [string]$ConfigPath)
    $candidate = $ProjectRoot
    if (-not $candidate) { $candidate = [Environment]::GetEnvironmentVariable(($Name.ToUpperInvariant() + '_PROJECT_ROOT')) }
    if (-not $candidate) {
        $config = Read-HarnessConfig $ConfigPath
        if ($null -ne $config -and $config.projects.PSObject.Properties[$Name]) {
            $entry = $config.projects.$Name
            if ($entry.PSObject.Properties['root']) { $candidate = [string]$entry.root }
        }
    }
    if (-not $candidate) { throw "Проект $Name не зарегистрирован. Один раз выполните scripts/Set-Project.ps1 -Name $Name -Path '<корень проекта>'." }
    return Test-HarnessProject -Name $Name -Root $candidate
}

function Start-HarnessProject {
    param([ValidateSet('mkr','mkp')][string]$Name, [string]$ProjectRoot, [string]$ConfigPath,
        [ValidateSet('opencode','bionic')][string]$Harness = 'opencode', [switch]$DryRun, [switch]$Launch)
    if ($DryRun -and $Launch) { throw 'Выберите один режим: -DryRun или -Launch.' }
    $root = Resolve-HarnessProject -Name $Name -ProjectRoot $ProjectRoot -ConfigPath $ConfigPath
    $command = 'opencode'
    $arguments = @($root)
    if ($Harness -eq 'bionic') { $command = 'GUI_ONLY'; $arguments = @('Project > Allow coding > Choose folder') }
    $plan = [pscustomobject]@{
        Project = $Name; WorkingDirectory = $root; Command = $command; Arguments = $arguments
        Mode = 'DryRun'; TargetContextTokens = 65536; ContextStatus = 'FUTURE_NOT_TESTED'
        IntegrationStatus = 'PREPARED_UNTESTED'
    }
    if (-not $Launch) { return $plan }
    if ($Harness -eq 'bionic') { throw 'Для Bionic используйте GUI: Project > Allow coding > Choose folder. Проверенного CLI открытия проекта нет.' }
    $tool = Get-Command opencode -ErrorAction SilentlyContinue
    if (-not $tool) { throw 'OpenCode не найден в PATH. Интеграция PREPARED_UNTESTED; установка автоматически не выполняется.' }
    Push-Location -LiteralPath $root
    try { & $tool.Source @arguments }
    finally { Pop-Location }
    if ($LASTEXITCODE -ne 0) { throw "OpenCode завершился с кодом $LASTEXITCODE." }
}

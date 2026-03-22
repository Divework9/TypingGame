param(
    [string]$Version = "",
    [switch]$SkipInstaller,
    [switch]$Clean
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ReleaseDir = $PSScriptRoot
$ProjectRoot = (Resolve-Path (Join-Path $ReleaseDir "..")).Path
$SpecFile = Join-Path $ReleaseDir "TypingGame.spec"
$PortableOutDir = Join-Path $ReleaseDir "dist\portable"
$InstallerOutDir = Join-Path $ReleaseDir "dist\installer"
$PyinstallerWorkDir = Join-Path $ReleaseDir "build\pyinstaller"
$IssFile = Join-Path $ReleaseDir "TypingGame.iss"

function Get-PythonExecutable {
    $venvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
    if (Test-Path $venvPython) {
        return $venvPython
    }

    $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
    if ($null -ne $pythonCmd) {
        return $pythonCmd.Source
    }

    throw "未找到可用 Python，请先安装 Python 或创建 .venv。"
}

function Resolve-Version {
    param([string]$InputVersion)

    if (-not [string]::IsNullOrWhiteSpace($InputVersion)) {
        return $InputVersion.Trim()
    }

    try {
        $tag = (git -C $ProjectRoot describe --tags --abbrev=0 2>$null)
        if (-not [string]::IsNullOrWhiteSpace($tag)) {
            return $tag.TrimStart("v")
        }
    }
    catch {
    }

    return (Get-Date -Format "yyyy.MM.dd")
}

function Get-IsccExecutable {
    $isccCmd = Get-Command iscc -ErrorAction SilentlyContinue
    if ($null -ne $isccCmd) {
        return $isccCmd.Source
    }

    $candidates = @(
        (Join-Path $env:LOCALAPPDATA "Programs\Inno Setup 6\ISCC.exe"),
        (Join-Path ${env:ProgramFiles(x86)} "Inno Setup 6\ISCC.exe"),
        (Join-Path $env:ProgramFiles "Inno Setup 6\ISCC.exe")
    )

    foreach ($path in $candidates) {
        if (-not [string]::IsNullOrWhiteSpace($path) -and (Test-Path $path)) {
            return $path
        }
    }

    return $null
}

$pythonExe = Get-PythonExecutable
$resolvedVersion = Resolve-Version -InputVersion $Version

Write-Host "[Release] 项目目录: $ProjectRoot"
Write-Host "[Release] Python: $pythonExe"
Write-Host "[Release] Version: $resolvedVersion"

if ($Clean.IsPresent) {
    if (Test-Path $PortableOutDir) {
        Remove-Item -Recurse -Force $PortableOutDir
    }
    if (Test-Path $InstallerOutDir) {
        Remove-Item -Recurse -Force $InstallerOutDir
    }
    if (Test-Path $PyinstallerWorkDir) {
        Remove-Item -Recurse -Force $PyinstallerWorkDir
    }
}

New-Item -ItemType Directory -Force -Path $PortableOutDir | Out-Null
New-Item -ItemType Directory -Force -Path $InstallerOutDir | Out-Null
New-Item -ItemType Directory -Force -Path $PyinstallerWorkDir | Out-Null

& $pythonExe -m pip install --upgrade pip pyinstaller

Push-Location $ProjectRoot
try {
    & $pythonExe -m PyInstaller --noconfirm --clean --distpath $PortableOutDir --workpath $PyinstallerWorkDir $SpecFile
    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller 构建失败，退出码: $LASTEXITCODE"
    }
}
finally {
    Pop-Location
}

$portableAppDir = Join-Path $PortableOutDir "TypingGame"
if (-not (Test-Path $portableAppDir)) {
    throw "PyInstaller 构建完成，但未找到目录: $portableAppDir"
}

Write-Host "[Release] 便携版已生成: $portableAppDir"

if ($SkipInstaller.IsPresent) {
    Write-Host "[Release] 已跳过安装包构建。"
    exit 0
}

$isccExe = Get-IsccExecutable
if ([string]::IsNullOrWhiteSpace($isccExe)) {
    Write-Warning "未检测到 Inno Setup 编译器 iscc，已跳过 setup.exe 生成。"
    Write-Host "可安装 Inno Setup 后重试，或运行: .\\release\\build.ps1 -SkipInstaller"
    exit 0
}

& $isccExe "/DMyAppVersion=$resolvedVersion" "/DSourceDir=$portableAppDir" "/DOutputDir=$InstallerOutDir" $IssFile

Write-Host "[Release] 安装包输出目录: $InstallerOutDir"
Write-Host "[Release] 完成。"
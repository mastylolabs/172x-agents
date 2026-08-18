[CmdletBinding()]
param(
    [string]$Version = $env:AGENTS_172X_VERSION,
    [string]$BaseUrl = $(if ($env:AGENTS_172X_RELEASE_BASE_URL) { $env:AGENTS_172X_RELEASE_BASE_URL } else { "https://github.com/mastylolabs/172x-agents/releases/download" }),
    [string]$Target = "windows-x64",
    [string]$Prefix = $(if ($env:AGENTS_172X_INSTALL_PREFIX) { $env:AGENTS_172X_INSTALL_PREFIX } else { Join-Path $env:LOCALAPPDATA "172x-agents" }),
    [switch]$DryRun,
    [switch]$Force
)

$ErrorActionPreference = "Stop"

function Fail([string]$Message) {
    throw "install.ps1: $Message"
}

if ([string]::IsNullOrWhiteSpace($Version)) {
    Fail "-Version is required; pin an immutable release"
}
if ($Version -notmatch '^v[0-9]+\.[0-9]+\.[0-9]+(?:-[0-9A-Za-z.-]+)?$') {
    Fail "version must look like vMAJOR.MINOR.PATCH"
}
if ($Version.Contains('/') -or $Version.Contains('..')) {
    Fail "version contains an unsafe path"
}
if ($Target -ne "windows-x64") {
    Fail "unsupported target: $Target"
}

$BaseUrl = $BaseUrl.TrimEnd('/')
$Archive = "agents-$Target.zip"
$ArchiveUrl = "$BaseUrl/$Version/$Archive"
$ChecksumUrl = "$ArchiveUrl.sha256"
$Destination = Join-Path $Prefix "agents.exe"

if ($DryRun) {
    Write-Output "target:       $Target"
    Write-Output "archive:      $ArchiveUrl"
    Write-Output "checksum:     $ChecksumUrl"
    Write-Output "destination:  $Destination"
    exit 0
}

$TempRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("172x-install-" + [Guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $TempRoot | Out-Null
try {
    $ArchivePath = Join-Path $TempRoot $Archive
    $ChecksumPath = "$ArchivePath.sha256"
    Invoke-WebRequest -Uri $ArchiveUrl -OutFile $ArchivePath
    Invoke-WebRequest -Uri $ChecksumUrl -OutFile $ChecksumPath

    $Expected = (Get-Content -Path $ChecksumPath -Raw).Trim() -split '\s+' | Select-Object -First 1
    if ($Expected -notmatch '^[0-9a-fA-F]{64}$') {
        Fail "checksum file is malformed"
    }
    $Actual = (Get-FileHash -Path $ArchivePath -Algorithm SHA256).Hash
    if ($Actual -ne $Expected) {
        Fail "checksum verification failed"
    }

    $ExtractRoot = Join-Path $TempRoot "extracted"
    Expand-Archive -Path $ArchivePath -DestinationPath $ExtractRoot
    $Extracted = Join-Path $ExtractRoot "agents.exe"
    $Entries = @(Get-ChildItem -LiteralPath $ExtractRoot -Recurse -File)
    if ($Entries.Count -ne 1 -or $Entries[0].FullName -ne $Extracted) {
        Fail "release archive does not contain agents.exe"
    }
    if ((Test-Path -LiteralPath $Destination) -and -not $Force) {
        Fail "$Destination already exists; use -Force to replace it"
    }
    New-Item -ItemType Directory -Force -Path $Prefix | Out-Null
    Copy-Item -LiteralPath $Extracted -Destination $Destination -Force
    Write-Output "installed $Version to $Destination"
    Write-Output "run: $Destination install codex --dry-run"
}
finally {
    Remove-Item -LiteralPath $TempRoot -Recurse -Force -ErrorAction SilentlyContinue
}

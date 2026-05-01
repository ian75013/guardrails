param(
  [Parameter(Position = 0, Mandatory = $true)]
  [string]$TargetRepo,
  [switch]$WithoutCopilotInstructions,
  [switch]$Force,
  [string]$ProjectName = ""
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$KitRoot = (Resolve-Path (Join-Path $ScriptDir "..")).Path

if (-not (Test-Path $TargetRepo -PathType Container)) {
  throw "Target path does not exist: $TargetRepo"
}

$TargetRepo = (Resolve-Path $TargetRepo).Path

if (-not (Test-Path (Join-Path $TargetRepo ".git") -PathType Container)) {
  throw "Target is not a git repository: $TargetRepo"
}

$RepoName = Split-Path -Leaf $TargetRepo
if ([string]::IsNullOrWhiteSpace($ProjectName)) {
  $ProjectName = $RepoName
}

$withCopilotInstructions = -not $WithoutCopilotInstructions.IsPresent

New-Item -ItemType Directory -Force (Join-Path $TargetRepo ".guardrails\bin") | Out-Null
New-Item -ItemType Directory -Force (Join-Path $TargetRepo ".guardrails\rules") | Out-Null
New-Item -ItemType Directory -Force (Join-Path $TargetRepo ".github\workflows") | Out-Null
New-Item -ItemType Directory -Force (Join-Path $TargetRepo ".github") | Out-Null

function Copy-FileSafely {
  param(
    [string]$Source,
    [string]$Destination
  )

  if ((Test-Path $Destination -PathType Leaf) -and -not $Force.IsPresent) {
    Write-Host "Skip existing file (use -Force to overwrite): $Destination"
    return
  }

  Copy-Item -Path $Source -Destination $Destination -Force
  Write-Host "Installed: $Destination"
}

function Render-TemplateSafely {
  param(
    [string]$Source,
    [string]$Destination
  )

  if ((Test-Path $Destination -PathType Leaf) -and -not $Force.IsPresent) {
    Write-Host "Skip existing file (use -Force to overwrite): $Destination"
    return
  }

  $content = Get-Content -Raw $Source
  $content = $content.Replace("{{PROJECT_NAME}}", $ProjectName)
  $content = $content.Replace("{{REPO_NAME}}", $RepoName)
  Set-Content -NoNewline -Path $Destination -Value $content
  Write-Host "Installed: $Destination"
}

Copy-FileSafely (Join-Path $KitRoot ".guardrails\config.env") (Join-Path $TargetRepo ".guardrails\config.env")
Copy-FileSafely (Join-Path $KitRoot ".guardrails\bin\validate_guardrails.sh") (Join-Path $TargetRepo ".guardrails\bin\validate_guardrails.sh")

$rulesPath = Join-Path $KitRoot ".guardrails\rules\*.md"
Get-ChildItem -Path $rulesPath -File | ForEach-Object {
  Copy-FileSafely $_.FullName (Join-Path $TargetRepo ".guardrails\rules\$($_.Name)")
}

Copy-FileSafely (Join-Path $KitRoot ".github\workflows\guardrails.yml") (Join-Path $TargetRepo ".github\workflows\guardrails.yml")

if ($withCopilotInstructions) {
  Render-TemplateSafely (Join-Path $KitRoot "templates\copilot-instructions.template.md") (Join-Path $TargetRepo ".github\copilot-instructions.md")
}

Write-Host "Guardrails Kit installation completed for: $TargetRepo"

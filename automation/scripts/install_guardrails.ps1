param(
  [Parameter(Position = 0)]
  [string]$TargetRepo = (Get-Location).Path,
  [switch]$WithCI,
  [string]$ProjectName = ""
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$KitRoot = Resolve-Path (Join-Path $ScriptDir "..\..")

if (-not (Test-Path $TargetRepo -PathType Container)) {
  Write-Error "[guardrails] Target repository path does not exist: $TargetRepo"
}

$TargetRepo = (Resolve-Path $TargetRepo).Path

if (-not (Test-Path (Join-Path $TargetRepo ".git") -PathType Container)) {
  Write-Error "[guardrails] Target is not a git repository: $TargetRepo"
}

$RepoName = Split-Path -Leaf $TargetRepo
if ([string]::IsNullOrWhiteSpace($ProjectName)) {
  $ProjectName = $RepoName
}

New-Item -ItemType Directory -Force (Join-Path $TargetRepo ".guardrails\bin") | Out-Null
New-Item -ItemType Directory -Force (Join-Path $TargetRepo ".github") | Out-Null
New-Item -ItemType Directory -Force (Join-Path $TargetRepo ".github\agents") | Out-Null

$ConfigPath = Join-Path $TargetRepo ".guardrails\config.env"
if (-not (Test-Path $ConfigPath -PathType Leaf)) {
  Copy-Item (Join-Path $KitRoot "templates\guardrails.config.template.env") $ConfigPath -Force
  Write-Host "[guardrails] Created .guardrails/config.env"
} else {
  Write-Host "[guardrails] Keeping existing .guardrails/config.env"
}

Copy-Item (Join-Path $KitRoot "automation\scripts\validate_guardrails.sh") (Join-Path $TargetRepo ".guardrails\bin\validate_guardrails.sh") -Force
Write-Host "[guardrails] Installed .guardrails/bin/validate_guardrails.sh"

function Render-Template {
  param(
    [string]$Source,
    [string]$Destination
  )

  $content = Get-Content -Raw $Source
  $content = $content.Replace("{{PROJECT_NAME}}", $ProjectName)
  $content = $content.Replace("{{REPO_NAME}}", $RepoName)
  Set-Content -NoNewline -Path $Destination -Value $content
}

$SkillsPath = Join-Path $TargetRepo "SKILLS.md"
if (-not (Test-Path $SkillsPath -PathType Leaf)) {
  Render-Template (Join-Path $KitRoot "templates\SKILLS.template.md") $SkillsPath
  Write-Host "[guardrails] Created SKILLS.md"
} else {
  Write-Host "[guardrails] Keeping existing SKILLS.md"
}

$RoadmapPath = Join-Path $TargetRepo "ROADMAP.md"
if (-not (Test-Path $RoadmapPath -PathType Leaf)) {
  Render-Template (Join-Path $KitRoot "templates\ROADMAP.template.md") $RoadmapPath
  Write-Host "[guardrails] Created ROADMAP.md"
} else {
  Write-Host "[guardrails] Keeping existing ROADMAP.md"
}

$InstructionsPath = Join-Path $TargetRepo ".github\copilot-instructions.md"
if (-not (Test-Path $InstructionsPath -PathType Leaf)) {
  Render-Template (Join-Path $KitRoot "templates\copilot-instructions.template.md") $InstructionsPath
  Write-Host "[guardrails] Created .github/copilot-instructions.md"
} else {
  Write-Host "[guardrails] Keeping existing .github/copilot-instructions.md"
}

$AgentPath = Join-Path $TargetRepo ".github\agents\$RepoName-agent.agent.md"
if (-not (Test-Path $AgentPath -PathType Leaf)) {
  Render-Template (Join-Path $KitRoot "templates\agents\project-agent.template.agent.md") $AgentPath
  Write-Host "[guardrails] Created .github/agents/$RepoName-agent.agent.md"
} else {
  Write-Host "[guardrails] Keeping existing .github/agents/$RepoName-agent.agent.md"
}

$PreCommitPath = Join-Path $TargetRepo ".git\hooks\pre-commit"
$HookMarker = "# guardrails-pre-commit-hook"
if ((Test-Path $PreCommitPath -PathType Leaf) -and (Select-String -Path $PreCommitPath -SimpleMatch $HookMarker -Quiet)) {
  Write-Host "[guardrails] Pre-commit hook already configured."
} else {
  Add-Content -Path $PreCommitPath -Value $HookMarker
  Add-Content -Path $PreCommitPath -Value "if [[ -x .guardrails/bin/validate_guardrails.sh ]]; then"
  Add-Content -Path $PreCommitPath -Value "  ./.guardrails/bin/validate_guardrails.sh"
  Add-Content -Path $PreCommitPath -Value "fi"
  Write-Host "[guardrails] Installed pre-commit hook."
}

if ($WithCI.IsPresent) {
  New-Item -ItemType Directory -Force (Join-Path $TargetRepo ".github\workflows") | Out-Null
  $CiPath = Join-Path $TargetRepo ".github\workflows\guardrails.yml"
  if (-not (Test-Path $CiPath -PathType Leaf)) {
    Copy-Item (Join-Path $KitRoot "templates\ci\github-actions-guardrails.yml") $CiPath -Force
    Write-Host "[guardrails] Created .github/workflows/guardrails.yml"
  } else {
    Write-Host "[guardrails] Keeping existing .github/workflows/guardrails.yml"
  }
} else {
  Write-Host "[guardrails] CI workflow skipped (default). Use -WithCI to enable."
}

Write-Host "[guardrails] Automatic guardrails are now active for $TargetRepo"
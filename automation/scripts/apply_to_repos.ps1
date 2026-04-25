param(
  [Parameter(Mandatory = $true, Position = 0, ValueFromRemainingArguments = $true)]
  [string[]]$RepoPaths,
  [switch]$WithCI,
  [string]$ProjectName = ""
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Installer = Join-Path $ScriptDir "install_guardrails.ps1"

foreach ($repo in $RepoPaths) {
  Write-Host "[guardrails] Applying to $repo"
  if ($WithCI.IsPresent) {
    if ([string]::IsNullOrWhiteSpace($ProjectName)) {
      & $Installer -TargetRepo $repo -WithCI
    } else {
      & $Installer -TargetRepo $repo -WithCI -ProjectName $ProjectName
    }
  } else {
    if ([string]::IsNullOrWhiteSpace($ProjectName)) {
      & $Installer -TargetRepo $repo
    } else {
      & $Installer -TargetRepo $repo -ProjectName $ProjectName
    }
  }
}

Write-Host "[guardrails] Completed for all repositories."
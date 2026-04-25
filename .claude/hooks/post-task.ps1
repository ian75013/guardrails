param(
    [string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\.."))
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Push-Location $RepoRoot
try {
    Write-Host "[post-task] Validation guardrails"

    if (Test-Path "automation/scripts/validate_guardrails.sh") {
        if (Get-Command bash -ErrorAction SilentlyContinue) {
            bash automation/scripts/validate_guardrails.sh
        }
        else {
            Write-Warning "[post-task] Bash absent: impossible d'exécuter validate_guardrails.sh"
        }
    }
    else {
        Write-Warning "[post-task] Script validate_guardrails.sh absent."
    }
}
finally {
    Pop-Location
}

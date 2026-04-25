param(
    [string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\.."))
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Push-Location $RepoRoot
try {
    Write-Host "[preflight] Repo: $RepoRoot"

    $required = @("SKILLS.md", "ROADMAP.md", "CLAUDE.md", ".github/copilot-instructions.md")
    foreach ($file in $required) {
        if (-not (Test-Path $file)) {
            throw "Fichier requis manquant: $file"
        }
    }

    if (Get-Command bash -ErrorAction SilentlyContinue) {
        Write-Host "[preflight] Bash détecté"
    }
    else {
        Write-Warning "[preflight] Bash non détecté."
    }

    Write-Host "[preflight] OK"
}
finally {
    Pop-Location
}

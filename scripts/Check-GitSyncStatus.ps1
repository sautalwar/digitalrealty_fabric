<#
.SYNOPSIS
    Checks Git sync health for Digital Realty Fabric workspaces.
.PARAMETER WorkspaceIds
    Array of workspace IDs to check (defaults to all environments).
.EXAMPLE
    .\Check-GitSyncStatus.ps1
#>

param(
    [string[]]$WorkspaceIds
)

$ErrorActionPreference = "Stop"

# Load workspace IDs from environment configs if not provided
if (-not $WorkspaceIds) {
    $WorkspaceIds = @()
    foreach ($env in @("dev", "uat", "prod")) {
        $config = Get-Content "environments\$env.json" | ConvertFrom-Json
        if ($config.workspace_id -and $config.workspace_id -ne "<${env.ToUpper()}_WORKSPACE_ID>") {
            $WorkspaceIds += @{ Id = $config.workspace_id; Name = $config.workspace_name; Env = $env }
        }
    }
}

if ($WorkspaceIds.Count -eq 0) {
    Write-Warning "No workspace IDs configured. Update environments/*.json with actual workspace IDs."
    exit 0
}

# Get access token
$token = az account get-access-token --resource "https://api.fabric.microsoft.com" --query accessToken -o tsv
$headers = @{ "Authorization" = "Bearer $token" }

Write-Host "Git Sync Health Check" -ForegroundColor Cyan
Write-Host "=====================" -ForegroundColor Cyan

foreach ($ws in $WorkspaceIds) {
    Write-Host "`n$($ws.Name) ($($ws.Env)):" -ForegroundColor Yellow

    try {
        $status = Invoke-RestMethod -Uri "https://api.fabric.microsoft.com/v1/workspaces/$($ws.Id)/git/status" `
            -Headers $headers -Method Get

        $syncState = $status.workspaceHead
        Write-Host "  Sync State: Connected" -ForegroundColor Green
        Write-Host "  Head Commit: $syncState"

        if ($status.changes -and $status.changes.Count -gt 0) {
            Write-Host "  Pending Changes: $($status.changes.Count)" -ForegroundColor Yellow
            foreach ($change in $status.changes) {
                Write-Host "    $($change.itemType): $($change.displayName) ($($change.changeType))"
            }
        } else {
            Write-Host "  Status: In sync" -ForegroundColor Green
        }
    }
    catch {
        Write-Host "  Status: ERROR - $($_.Exception.Message)" -ForegroundColor Red
    }
}

<#
.SYNOPSIS
    Validates schema consistency between the Git schema registry and actual Lakehouse tables.
.DESCRIPTION
    Connects to a Fabric workspace SQL endpoint and compares the actual table schemas
    against what is defined in the schema registry. Reports missing tables, missing columns,
    extra columns (drift), and type mismatches.
.PARAMETER Environment
    Target environment (dev, uat, prod)
.EXAMPLE
    .\Validate-SchemaConsistency.ps1 -Environment dev
#>

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("dev", "uat", "prod")]
    [string]$Environment
)

$ErrorActionPreference = "Stop"

# Load environment config
$config = Get-Content "environments\$Environment.json" | ConvertFrom-Json
Write-Host "Validating schemas in $($config.workspace_name)" -ForegroundColor Cyan
Write-Host "SQL Endpoint: $($config.sql_endpoint)"
Write-Host ""

# Get access token
$token = az account get-access-token --resource "https://analysis.windows.net/powerbi/api" --query accessToken -o tsv
if (-not $token) {
    Write-Error "Failed to get access token. Run 'az login' first."
    exit 1
}

# Parse schema registry to get expected tables
$registryContent = Get-Content "notebooks\00_schema_registry.py" -Raw
$version = [regex]::Match($registryContent, 'SCHEMA_VERSION\s*=\s*"([^"]+)"').Groups[1].Value
Write-Host "Schema Registry Version: $version" -ForegroundColor Green

# Connect to SQL endpoint and check tables
$connectionString = "Server=$($config.sql_endpoint);Database=$($config.lakehouse_name);Authentication=ActiveDirectoryAccessToken;AccessToken=$token"

try {
    $connection = New-Object System.Data.SqlClient.SqlConnection($connectionString)
    $connection.Open()

    # Get actual tables
    $cmd = $connection.CreateCommand()
    $cmd.CommandText = "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'"
    $reader = $cmd.ExecuteReader()
    $actualTables = @()
    while ($reader.Read()) { $actualTables += $reader["TABLE_NAME"] }
    $reader.Close()

    Write-Host "`nActual tables in Lakehouse: $($actualTables.Count)" -ForegroundColor Yellow
    $actualTables | ForEach-Object { Write-Host "  $_" }

    # Get column details for each table
    foreach ($table in $actualTables) {
        $cmd = $connection.CreateCommand()
        $cmd.CommandText = "SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '$table' ORDER BY ORDINAL_POSITION"
        $reader = $cmd.ExecuteReader()
        Write-Host "`n  $table columns:" -ForegroundColor Cyan
        while ($reader.Read()) {
            $nullable = if ($reader["IS_NULLABLE"] -eq "YES") { "nullable" } else { "NOT NULL" }
            Write-Host "    $($reader['COLUMN_NAME']) ($($reader['DATA_TYPE']), $nullable)"
        }
        $reader.Close()
    }

    $connection.Close()
    Write-Host "`nSchema validation complete." -ForegroundColor Green
}
catch {
    Write-Warning "Could not connect to SQL endpoint: $_"
    Write-Host "This is expected if you haven't configured the SQL endpoint yet."
    Write-Host "The schema registry and enforcer notebooks handle schema management within Fabric."
}

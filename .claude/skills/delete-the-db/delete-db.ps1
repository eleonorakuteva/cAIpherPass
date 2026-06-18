# Delete the vault database to reset to first-time setup
$dbPath = "C:\Users\eleon\Desktop\cAIpherPass\data\vault.db"

if (Test-Path $dbPath) {
    Remove-Item -Path $dbPath -Force
    Write-Host "✓ Database deleted successfully" -ForegroundColor Green
    Write-Host "Next app launch will show the setup screen"
} else {
    Write-Host "ℹ Database does not exist (already clean)" -ForegroundColor Yellow
}

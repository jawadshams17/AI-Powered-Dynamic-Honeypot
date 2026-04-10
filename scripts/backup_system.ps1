# Automated Backup Script for FYP Environment
$backupDir = "D:\Personal\FYP_Project\backups\$(Get-Date -Format 'yyyy-MM-dd')"
if (!(Test-Path $backupDir)) { New-Item -ItemType Directory -Path $backupDir }

Write-Host "--- Starting System Backup ---" -ForegroundColor Cyan

# 1. Backup Configs
Copy-Item "D:\Personal\FYP_Project\configs\*" -Destination $backupDir -Recurse
Write-Host "[+] Configs backed up." -ForegroundColor Green

# 2. Backup Models
Copy-Item "D:\Personal\FYP_Project\models\*" -Destination $backupDir -Recurse
Write-Host "[+] ML Models backed up." -ForegroundColor Green

# 3. Backup Scripts
Copy-Item "D:\Personal\FYP_Project\scripts\*" -Destination $backupDir -Recurse
Write-Host "[+] Project Scripts backed up." -ForegroundColor Green

Write-Host "`nBackup complete. Location: $backupDir" -ForegroundColor Yellow

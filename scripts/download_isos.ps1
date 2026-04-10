$isoDir = "D:\Personal\FYP_Project\ISOs"
if (!(Test-Path $isoDir)) { New-Item -ItemType Directory -Path $isoDir }

$isos = @(
    @{
        Name = "pfSense-CE-2.7.2-RELEASE-amd64.iso.gz"
        Url  = "https://atxfiles.netgate.com/mirror/downloads/pfSense-CE-2.7.2-RELEASE-amd64.iso.gz"
    },
    @{
        Name = "ubuntu-22.04.4-live-server-amd64.iso"
        Url  = "https://releases.ubuntu.com/22.04/ubuntu-22.04.4-live-server-amd64.iso"
    }
)

foreach ($iso in $isos) {
    $dest = Join-Path $isoDir $iso.Name
    if (!(Test-Path $dest)) {
        Write-Host "Downloading $($iso.Name)..." -ForegroundColor Cyan
        Invoke-WebRequest -Uri $iso.Url -OutFile $dest
    } else {
        Write-Host "$($iso.Name) already exists." -ForegroundColor Green
    }
}

Write-Host "`nDownload complete. Check $isoDir" -ForegroundColor Yellow
Write-Host "NOTE: You must manually install VMware Workstation Pro 17.x from https://www.vmware.com/products/workstation-pro.html" -ForegroundColor White

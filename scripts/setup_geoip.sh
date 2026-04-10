# GeoIP Database Setup
mkdir -p /usr/share/GeoIP
cd /usr/share/GeoIP

# Download logic (placeholder - requires MaxMind license key, but provided for the user)
# wget -O GeoLite2-City.tar.gz "https://download.maxmind.com/app/geoip_download?edition_id=GeoLite2-City&license_key=YOUR_LICENSE_KEY&suffix=tar.gz"
# tar -xzvf GeoLite2-City.tar.gz
# mv GeoLite2-City_*/GeoLite2-City.mmdb .

echo "GeoIP Directory Prepared. Please place GeoLite2-City.mmdb in /usr/share/GeoIP/"

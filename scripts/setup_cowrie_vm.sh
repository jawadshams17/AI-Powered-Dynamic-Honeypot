#!/bin/bash
# automated Cowrie Honeypot Setup for Ubuntu 22.04
# To be run inside the DMZ VM (10.10.20.10)

echo "=== Cowrie Automated Setup ==="

# 1. System Updates
sudo apt update && sudo apt upgrade -y
sudo apt install -y git python3-venv libssl-dev libffi-dev build-essential libpython3-dev python3-minimal authbind virtualenv

# 2. Setup Cowrie User
sudo adduser --disabled-password --gecos "" cowrie
cd /home/cowrie

# 3. Clone and Setup
sudo -u cowrie git clone https://github.com/cowrie/cowrie.git
cd cowrie
sudo -u cowrie python3 -m venv cowrie-env
source cowrie-env/bin/activate
pip install --upgrade pip
pip install --upgrade -r requirements.txt

# 4. Configure Port Forwarding (Authbind)
sudo touch /etc/authbind/byport/22
sudo chown cowrie:cowrie /etc/authbind/byport/22
sudo chmod 770 /etc/authbind/byport/22

# 5. Move SSH to 2222 (Host)
sudo sed -i 's/#Port 22/Port 2222/' /etc/ssh/sshd_config
sudo systemctl restart ssh

# 6. Apply Cowrie Config (Placeholder for local copy)
# cp /tmp/cowrie.cfg /home/cowrie/cowrie/etc/cowrie.cfg

echo "Cowrie setup complete. Start with: bin/cowrie start"

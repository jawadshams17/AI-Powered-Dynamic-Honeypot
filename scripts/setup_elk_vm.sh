#!/bin/bash
# automated ELK Stack Setup for Ubuntu 22.04
# To be run inside the LAN VM (10.10.10.20)

echo "=== ELK Stack Automated Setup ==="

# 1. Install Java and Dependencies
sudo apt update
sudo apt install -y openjdk-17-jdk wget gpg apt-transport-https

# 2. Add Elastic Repository
wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo gpg --dearmor -o /usr/share/keyrings/elasticsearch-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/elasticsearch-keyring.gpg] https://artifacts.elastic.co/packages/8.x/apt stable main" | sudo tee /etc/apt/sources.list.d/elastic-8.x.list

# 3. Install ELK
sudo apt update
sudo apt install -y elasticsearch logstash kibana

# 4. Enable Services
sudo systemctl daemon-reload
sudo systemctl enable elasticsearch logstash kibana

# 5. Network Binding
sudo sed -i 's/#network.host: 192.168.0.1/network.host: 0.0.0.0/' /etc/elasticsearch/elasticsearch.yml
sudo sed -i 's/#server.host: "localhost"/server.host: "0.0.0.0"/' /etc/kibana/kibana.yml

echo "ELK Basic setup complete. "
echo "Action: Start services and capture the auto-generated elastic password!"
echo "sudo systemctl start elasticsearch"

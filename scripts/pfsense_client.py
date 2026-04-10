"""pfSense REST API wrapper for firewall alias management."""
import json
import logging
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)

class PfSenseClient:
    def __init__(self, config):
        pf = config['pfsense']
        self.base_url = pf['url']
        self.alias_name = pf['block_alias']
        self.headers = {
            "Authorization": f"{pf['client_id']} {pf['client_token']}",
            "Content-Type": "application/json"
        }
        self.blocked_ips = set()

    def _load_existing_blocks(self):
        """Load currently blocked IPs from pfSense alias."""
        try:
            r = requests.get(
                f"{self.base_url}/firewall/alias",
                headers=self.headers, verify=False, timeout=10
            )
            if r.status_code == 200:
                for alias in r.json().get('data', []):
                    if alias.get('name') == self.alias_name:
                        for addr in alias.get('address', '').split(' '):
                            if addr.strip():
                                self.blocked_ips.add(addr.strip())
                logger.info(f"Loaded {len(self.blocked_ips)} existing blocks")
        except Exception as e:
            logger.error(f"Failed to load existing blocks: {e}")

    def block_ip(self, ip_address, reason="AI-detected threat"):
        """Add IP to the block alias and apply firewall changes."""
        if ip_address in self.blocked_ips:
            return True

        try:
            # Get current alias
            r = requests.get(
                f"{self.base_url}/firewall/alias",
                headers=self.headers, verify=False, timeout=10
            )
            current_alias = None
            for alias in r.json().get('data', []):
                if alias.get('name') == self.alias_name:
                    current_alias = alias
                    break

            # Build updated address list
            existing = current_alias.get('address', '').split(' ') if current_alias else []
            existing = [a for a in existing if a.strip()]
            existing.append(ip_address)

            details = current_alias.get('detail', '').split('||') if current_alias else []
            details = [d for d in details if d.strip()]
            details.append(reason)

            # Update alias
            data = {
                "name": self.alias_name,
                "type": "host",
                "address": ' '.join(existing),
                "detail": '||'.join(details)
            }

            r = requests.patch(
                f"{self.base_url}/firewall/alias",
                headers=self.headers, json=data, verify=False, timeout=10
            )

            if r.status_code in (200, 201):
                requests.post(
                    f"{self.base_url}/firewall/apply",
                    headers=self.headers, verify=False, timeout=15
                )
                self.blocked_ips.add(ip_address)
                logger.info(f"BLOCKED: {ip_address}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to block {ip_address}: {e}")
            return False

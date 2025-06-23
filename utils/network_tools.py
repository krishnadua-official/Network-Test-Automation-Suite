"""
Network Tools - Common network utilities
"""

import subprocess
import platform
import re
import socket
from config import PLATFORM_COMMANDS, TEST_CONFIG


class NetworkTools:
    def __init__(self):
        self.system = platform.system()  # This line MUST come first
        self.commands = PLATFORM_COMMANDS.get(self.system, PLATFORM_COMMANDS["Linux"])
        self.timeout = TEST_CONFIG["network_tools"]["command_timeout"]
    
    def run_command(self, command, timeout=None):
        """Execute system command and return output"""
        if timeout is None:
            timeout = self.timeout
            
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=timeout
            )
            return result.stdout, result.stderr, result.returncode
        except subprocess.TimeoutExpired:
            return "", "Command timed out", 1
        except Exception as e:
            return "", str(e), 1
    
    def ping(self, host, count=10):
        """Ping a host and return statistics"""
        ping_cmd = self.commands["ping"].format(count=count, host=host)
        
        stdout, stderr, code = self.run_command(ping_cmd)
        
        if code == 0:
            # Parse ping statistics
            stats = self._parse_ping_output(stdout)
            return {
                "success": True,
                "avg_ms": stats.get('avg', 0),
                "min_ms": stats.get('min', 0),
                "max_ms": stats.get('max', 0),
                "packet_loss": stats.get('loss', 0),
                "packets_sent": count,
                "packets_received": count - int(count * stats.get('loss', 0) / 100)
            }
        else:
            return {
                "success": False,
                "error": stderr or "Ping failed"
            }
    
    def _parse_ping_output(self, output):
        """Parse ping command output for statistics"""
        stats = {'avg': 0, 'min': 0, 'max': 0, 'loss': 0}
        
        if self.system == "Windows":
            # Windows ping parsing
            loss_match = re.search(r'\((\d+)% loss\)', output)
            if loss_match:
                stats['loss'] = float(loss_match.group(1))
            
            # Parse min/max/avg
            time_match = re.search(r'Minimum = (\d+)ms, Maximum = (\d+)ms, Average = (\d+)ms', output)
            if time_match:
                stats['min'] = float(time_match.group(1))
                stats['max'] = float(time_match.group(2))
                stats['avg'] = float(time_match.group(3))
        else:
            # Unix-like ping parsing
            loss_match = re.search(r'(\d+(?:\.\d+)?)% packet loss', output)
            if loss_match:
                stats['loss'] = float(loss_match.group(1))
            
            # Parse min/avg/max/mdev
            time_match = re.search(r'min/avg/max/(?:mdev|stddev) = ([\d.]+)/([\d.]+)/([\d.]+)', output)
            if time_match:
                stats['min'] = float(time_match.group(1))
                stats['avg'] = float(time_match.group(2))
                stats['max'] = float(time_match.group(3))
        
        return stats
    
    def get_ip_info(self):
        """Get current IP configuration"""
        cmd = self.commands.get("ip_config", "")
        if not cmd:
            return None
        
        stdout, stderr, code = self.run_command(cmd)
        
        if code == 0:
            # Parse IP address
            ip_pattern = r'inet\s+(\d+\.\d+\.\d+\.\d+)' if self.system != "Windows" else r'IPv4 Address.*?:\s*(\d+\.\d+\.\d+\.\d+)'
            ip_match = re.search(ip_pattern, stdout)
            
            if ip_match:
                return {
                    "ip_address": ip_match.group(1),
                    "interface": self._get_interface_name(stdout),
                    "raw_output": stdout
                }
        
        return None
    
    def _get_interface_name(self, output):
        """Extract network interface name from ip config output"""
        if self.system == "Windows":
            # Look for wireless adapter
            match = re.search(r'Wireless LAN adapter (.*?):', output)
            if match:
                return match.group(1)
        else:
            # Look for common wireless interface names
            for iface in ['wlan0', 'wlp', 'en0', 'en1']:
                if iface in output:
                    return iface
        return "unknown"
    
    def get_signal_strength(self):
        """Get Wi-Fi signal strength information"""
        cmd = self.commands.get("signal_strength") or self.commands.get("wifi_info", "")
        if not cmd:
            return {"success": False, "error": "Signal strength command not available for this platform"}
        
        stdout, stderr, code = self.run_command(cmd)
        
        if code == 0 and stdout:
            # Parse RSSI/Signal strength
            rssi_match = re.search(r'Signal level[=:]?\s*(-?\d+)\s*dBm', stdout)
            if not rssi_match:
                rssi_match = re.search(r'RSSI:\s*(-?\d+)', stdout)
            
            if rssi_match:
                rssi = int(rssi_match.group(1))
                return {
                    "success": True,
                    "rssi": rssi,
                    "raw_info": stdout.strip()
                }
            else:
                return {
                    "success": True,
                    "raw_info": stdout.strip()
                }
        
        return {
            "success": False,
            "error": "Could not retrieve signal strength"
        }
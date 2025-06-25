"""
Security Test Cases
"""

import subprocess
import re
import platform
from utils.network_tools import NetworkTools


class SecurityTests:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.network_tools = NetworkTools()
        self.router_ip = config['router_ip']
    
    def test_open_ports_router(self):
        """Test for open/exposed ports on router"""
        print("\n[TEST] Scanning router ports...")
        
        # Common ports to check
        critical_ports = {
            21: "FTP",
            22: "SSH", 
            23: "Telnet",
            80: "HTTP",
            443: "HTTPS",
            445: "SMB",
            3389: "RDP",
            8080: "HTTP-Alt",
            8443: "HTTPS-Alt"
        }
        
        open_ports = []
        
        # Check if nc (netcat) is available
        stdout, stderr, code = self.network_tools.run_command("which nc", timeout=2)
        if code != 0:
            print("ℹ netcat (nc) not found - using basic port check")
            # Fallback to basic connectivity test
            for port, service in list(critical_ports.items())[:4]:  # Test fewer ports
                cmd = f"bash -c 'echo >/dev/tcp/{self.router_ip}/{port}' 2>/dev/null"
                stdout, stderr, code = self.network_tools.run_command(cmd, timeout=2)
                if code == 0:
                    open_ports.append(f"{port}/{service}")
                    print(f"  ⚠ Port {port} ({service}) is open")
        else:
            # Use netcat for more reliable scanning
            for port, service in critical_ports.items():
                cmd = f"nc -zv -w 2 {self.router_ip} {port} 2>&1"
                stdout, stderr, code = self.network_tools.run_command(cmd, timeout=3)
                
                if "succeeded" in stdout.lower() or "connected" in stdout.lower() or code == 0:
                    open_ports.append(f"{port}/{service}")
                    print(f"  ⚠ Port {port} ({service}) is open")
        
        if not open_ports:
            print("✓ No critical ports found open")
            status = "PASS"
        elif len(open_ports) <= 2 and any("HTTP" in p for p in open_ports):
            print(f"⚠ Found {len(open_ports)} open ports (likely admin interface)")
            status = "WARNING"
        else:
            print(f"✗ Multiple open ports detected - potential security risk")
            status = "FAIL"
        
        self.logger.log_info(f"Port scan - {len(open_ports)} open ports found")
        
        return {
            "status": status,
            "open_ports": open_ports,
            "total_scanned": len(critical_ports)
        }
    
    def test_upnp_enabled(self):
        """Test if UPnP is enabled on router"""
        print("\n[TEST] Checking UPnP status...")
        
        # Try multiple methods to detect UPnP
        upnp_detected = False
        detection_method = None
        
        # Method 1: Check for UPnP port 1900 (SSDP)
        cmd = f"nc -zuv -w 2 {self.router_ip} 1900 2>&1"
        stdout, stderr, code = self.network_tools.run_command(cmd, timeout=3)
        
        if "succeeded" in stdout.lower() or "connected" in stdout.lower() or code == 0:
            upnp_detected = True
            detection_method = "SSDP port 1900 open"
            print("  ⚠ UPnP port 1900 (SSDP) is open")
        
        # Method 2: Try upnpc if available (miniupnpc package)
        if not upnp_detected:
            stdout, stderr, code = self.network_tools.run_command("which upnpc", timeout=2)
            if code == 0:
                cmd = "upnpc -l 2>&1 | head -20"
                stdout, stderr, code = self.network_tools.run_command(cmd, timeout=5)
                
                if "igd" in stdout.lower() or "found" in stdout.lower():
                    upnp_detected = True
                    detection_method = "UPnP IGD device found"
                    print("  ⚠ UPnP is enabled - IGD device detected")
        
        # Method 3: Check common UPnP ports
        if not upnp_detected:
            upnp_ports = [1900, 2869, 5000]  # SSDP, UPnP, and common router UPnP port
            for port in upnp_ports:
                cmd = f"bash -c 'echo >/dev/tcp/{self.router_ip}/{port}' 2>/dev/null"
                stdout, stderr, code = self.network_tools.run_command(cmd, timeout=2)
                if code == 0:
                    upnp_detected = True
                    detection_method = f"Port {port} open"
                    break
        
        if upnp_detected:
            print(f"⚠ UPnP appears to be enabled ({detection_method})")
            print("  Recommendation: Disable UPnP for better security")
            status = "WARNING"
        else:
            print("✓ UPnP not detected (good for security)")
            status = "PASS"
        
        self.logger.log_info(f"UPnP test - {'Detected' if upnp_detected else 'Not detected'}")
        
        return {
            "status": status,
            "upnp_detected": upnp_detected,
            "detection_method": detection_method if upnp_detected else None
        }
    
    def test_mac_address_filtering(self):
        """Test MAC address filtering (informational)"""
        print("\n[TEST] Checking MAC address filtering...")
        
        # Get current device MAC address
        mac_address = None
        
        if platform.system() == "Darwin":  # macOS
            cmd = "ifconfig en0 | grep ether | awk '{print $2}'"
        elif platform.system() == "Linux":
            cmd = "ip link show | grep ether | head -1 | awk '{print $2}'"
        else:  # Windows
            cmd = "getmac /v | findstr Wi-Fi"
        
        stdout, stderr, code = self.network_tools.run_command(cmd)
        
        if code == 0 and stdout:
            mac_address = stdout.strip()
            print(f"  Current device MAC: {mac_address}")
        
        # Note: We can't actually test MAC filtering without disconnecting
        # This is more of an informational test
        print("ℹ MAC address filtering check:")
        print("  - Cannot test without disconnecting from network")
        print("  - If enabled, only registered MACs can connect")
        print("  - Recommendation: Enable for additional security")
        
        self.logger.log_info("MAC filtering test - informational only")
        
        return {
            "status": "INFO",
            "device_mac": mac_address,
            "details": "Manual verification required"
        }
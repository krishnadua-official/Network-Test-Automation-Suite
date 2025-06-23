
import socket
import platform
from utils.network_tools import NetworkTools


class ConnectivityTests:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.network_tools = NetworkTools()
        self.router_ip = config['router_ip']
    
    def test_ping_router(self):
        """Test Case 1: Ping router's IP from client"""
        self.logger.log_info("Starting router ping test...")
        print("\n[TEST] Pinging router...")
        
        result = self.network_tools.ping(self.router_ip, count=10)
        
        if result['success']:
            print(f"✓ Router ping successful (avg: {result['avg_ms']:.2f}ms)")
            self.logger.log_info(f"Router ping successful - avg: {result['avg_ms']}ms")
            return {
                "status": "PASS",
                "average_ms": result['avg_ms']
            }
        else:
            print("✗ Router ping failed")
            self.logger.log_error(f"Router ping failed: {result['error']}")
            return {
                "status": "FAIL",
                "error": result['error']
            }
    
    def test_ping_internet(self):
        """Test Case 2: Ping external IP to verify internet access"""
        self.logger.log_info("Testing internet connection...")
        print("\n[TEST] Pinging internet (8.8.8.8)...")
        
        result = self.network_tools.ping("8.8.8.8", count=10)
        
        if result['success']:
            print("✓ Internet ping successful")
            self.logger.log_info("Internet connectivity confirmed")
            return {
                "status": "PASS",
                "average_ms": result['avg_ms']
            }
        else:
            print("✗ Internet ping failed")
            self.logger.log_error("No internet connectivity")
            return {
                "status": "FAIL",
                "error": "No internet connectivity"
            }
    
    def test_dns_resolution(self):
        """Test Case 3: DNS resolution test"""
        self.logger.log_info("Testing DNS resolution...")
        print("\n[TEST] Testing DNS resolution...")
        
        try:
            test_domains = ["google.com", "opendns.com"]
            resolved = {}
            
            for domain in test_domains:
                try:
                    ip = socket.gethostbyname(domain)
                    resolved[domain] = ip
                except socket.gaierror:
                    resolved[domain] = None
            
            successful_resolutions = [d for d, ip in resolved.items() if ip]
            
            if successful_resolutions:
                print(f"✓ DNS resolution successful for: {', '.join(successful_resolutions)}")
                self.logger.log_info(f"DNS resolution successful for: {', '.join(successful_resolutions)}")
                return {
                    "status": "PASS",
                    "resolved_domains": resolved
                }
            else:
                print("✗ DNS resolution failed for all test domains")
                self.logger.log_error("DNS resolution failed")
                return {
                    "status": "FAIL",
                    "error": "DNS resolution failed for all test domains"
                }
        except Exception as e:
            print(f"Error during DNS resolution: {e}")
            self.logger.log_error(f"DNS test error: {e}")
            return {
                "status": "ERROR",
                "error": str(e)
            }
    
    def test_dhcp_assignment(self):
        """Test Case 4: Verify DHCP IP assignment"""
        self.logger.log_info("Testing DHCP assignment...")
        print("\n[TEST] Checking DHCP IP assignment...")
        
        try:
            ip_info = self.network_tools.get_ip_info()
            
            if ip_info and ip_info.get('ip_address'):
                ip_parts = ip_info['ip_address'].split('.')
                router_parts = self.router_ip.split('.')
                
                if ip_parts[:3] == router_parts[:3]:
                    print("✓ DHCP assignment successful")
                    self.logger.log_info(f"DHCP assigned IP: {ip_info['ip_address']}")
                    return {
                        "status": "PASS",
                        "assigned_ip": ip_info['ip_address']
                    }
                else:
                    print(f"⚠ IP assigned but not in expected subnet: {ip_info['ip_address']}")
                    return {
                        "status": "WARNING",
                        "assigned_ip": ip_info['ip_address']
                    }
            else:
                print("✗ No IP address assigned")
                self.logger.log_error("No IP address found")
                return {
                    "status": "FAIL",
                    "error": "No IP address assigned"
                }
        except Exception as e:
            print(f"Error during DHCP test: {e}")
            self.logger.log_error(f"DHCP test error: {e}")
            return {
                "status": "ERROR",
                "error": str(e)
            }
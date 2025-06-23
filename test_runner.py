from datetime import datetime
from tests.connectivity_tests import ConnectivityTests
from tests.performance_tests import PerformanceTests
#from tests.stability_tests import StabilityTests


class TestRunner:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.results = {
            "test_info": {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "router_ip": config['router_ip'],
                "ssid": config['ssid']
            },
            "connectivity_tests": {},
            "performance_tests": {},
            "stability_tests": {}
        }
        
        # Initialize test classes
        self.connectivity_tests = ConnectivityTests(config, logger)
        self.performance_tests = PerformanceTests(config, logger)
        self.stability_tests = StabilityTests(config, logger)
    
    def run_all_tests(self):
        """Run all test categories"""
        # Connectivity Tests
        print("\n--- CONNECTIVITY TESTS ---")
        self.logger.log_info("Starting connectivity tests")
        self.results["connectivity_tests"] = self._run_connectivity_tests()
        
        # Performance Tests
        print("\n--- PERFORMANCE TESTS ---")
        self.logger.log_info("Starting performance tests")
        self.results["performance_tests"] = self._run_performance_tests()
        
        # Stability Tests
        print("\n--- STABILITY TESTS ---")
        self.logger.log_info("Starting stability tests")
        self.results["stability_tests"] = self._run_stability_tests()
        
        return self.results
    
    def _run_connectivity_tests(self):
        """Execute all connectivity tests"""
        results = {}
        
        # Test 1: Ping Router
        results["ping_router"] = self.connectivity_tests.test_ping_router()
        
        # Test 2: Ping Internet
        results["ping_internet"] = self.connectivity_tests.test_ping_internet()
        
        # Test 3: DNS Resolution
        results["dns_resolution"] = self.connectivity_tests.test_dns_resolution()
        
        # Test 4: DHCP Assignment
        results["dhcp_assignment"] = self.connectivity_tests.test_dhcp_assignment()
        
        return results
    
    def _run_performance_tests(self):
        """Execute all performance tests"""
        results = {}
        
        if self.config.get('iperf_server'):
            # Test 1: Upload Speed
            results["upload_speed"] = self.performance_tests.test_iperf_upload_speed()
            
            # Test 2: Download Speed
            results["download_speed"] = self.performance_tests.test_iperf_download_speed()
            
            # Test 3: Latency Under Load
            results["latency_under_load"] = self.performance_tests.test_latency_under_load()
        else:
            self.logger.log_warning("Skipping performance tests - no iperf server specified")
            results["status"] = "SKIPPED"
            results["reason"] = "No iperf3 server specified"
        
        return results
    
    def _run_stability_tests(self):
        """Execute all stability tests"""
        results = {}
        
        # Test 1: Continuous Ping
        results["continuous_ping"] = self.stability_tests.test_continuous_ping()
        
        # Test 2: Signal Strength
        results["signal_strength"] = self.stability_tests.test_signal_strength()
        
        # Test 3: Multiple Reconnections
        results["multiple_reconnections"] = self.stability_tests.test_multiple_reconnections()
        
        return results
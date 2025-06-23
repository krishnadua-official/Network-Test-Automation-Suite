import sys
import os

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Now do the other imports
import socket
from datetime import datetime
from utils.logger import Logger
from utils.report_generator import ReportGenerator

from tests.connectivity_tests import ConnectivityTests
from tests.performance_tests import PerformanceTests


def get_user_input():
    """Get connection details from user"""
    print("Wi-Fi Router Test Automation Suite")
    print("-" * 35)
    
    router_ip = input("Enter router IP address (e.g., 192.168.1.1): ").strip()
    ssid = input("Enter Wi-Fi SSID: ").strip()
    password = input("Enter Wi-Fi password: ").strip()
    
    # Validate IP
    try:
        socket.inet_aton(router_ip)
    except socket.error:
        print("Error: Invalid IP address format")
        sys.exit(1)
    
    return {
        'router_ip': router_ip,
        'ssid': ssid,
        'password': password,
        'iperf_server': None
    }


def run_connectivity_tests_only(config, logger):
    """Run only connectivity tests"""
    print("\n" + "="*50)
    print("CONNECTIVITY TESTS")
    print("="*50)
    
    connectivity = ConnectivityTests(config, logger)
    results = {}
    
    # Run each test
    results['ping_router'] = connectivity.test_ping_router()
    results['ping_internet'] = connectivity.test_ping_internet()
    results['dns_resolution'] = connectivity.test_dns_resolution()
    results['dhcp_assignment'] = connectivity.test_dhcp_assignment()
    
    return results


def run_performance_tests_only(config, logger):
    """Run only performance tests"""
    print("\n" + "="*50)
    print("PERFORMANCE TESTS")
    print("="*50)
    
    # Ask for iperf server
    iperf_server = input("\nEnter iperf3 server IP (or press Enter to skip): ").strip()
    if iperf_server:
        try:
            socket.inet_aton(iperf_server)
            config['iperf_server'] = iperf_server  # THIS LINE IS IMPORTANT
        except socket.error:
            print("Invalid IP format, skipping performance tests")
            return {"status": "SKIPPED"}
    else:
        print("Skipping performance tests - no server specified")
        return {"status": "SKIPPED"}
    
    performance = PerformanceTests(config, logger)
    results = {}
    
    # Run each test
    results['upload_speed'] = performance.test_iperf_upload_speed()
    results['download_speed'] = performance.test_iperf_download_speed()
    results['latency_under_load'] = performance.test_latency_under_load()
    
    return results

def print_simple_summary(results):
    """Print a simple summary of results"""
    print("\n" + "="*50)
    print("SUMMARY")
    print("="*50)
    
    for category, tests in results.items():
        print(f"\n{category}:")
        if isinstance(tests, dict):
            for test_name, result in tests.items():
                if isinstance(result, dict) and 'status' in result:
                    status = result['status']
                    symbol = "✓" if status == "PASS" else "✗" if status == "FAIL" else "⚠"
                    print(f"  {symbol} {test_name}: {status}")


def main():
    """Main function"""
    # Get user input
    config = get_user_input()
    
    # Create logger
    logger = Logger()
    
    # Ask what to test
    print("\nWhat would you like to test?")
    print("1. Connectivity tests only")
    print("2. Performance tests only")
    print("3. Both")
    choice = input("Enter choice (1-3): ").strip()
    
    results = {}
    
    if choice in ['1', '3']:
        results['connectivity'] = run_connectivity_tests_only(config, logger)
    
    if choice in ['2', '3']:
        results['performance'] = run_performance_tests_only(config, logger)
    
    # Print summary
    print_simple_summary(results)
    
    print(f"\nLog file: {logger.get_log_file_path()}")


if __name__ == "__main__":
    main()
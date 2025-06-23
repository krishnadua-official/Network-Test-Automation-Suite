"""
Configuration file for Wi-Fi Test Suite
"""

TEST_CONFIG = {
    # Connectivity Test Settings
    "connectivity": {
        "ping_count": 10,
        "ping_timeout": 30,
        "dns_test_domains": ["google.com", "cloudflare.com", "opendns.com"],
        "internet_test_ip": "8.8.8.8"
    },
    
    # Performance Test Settings
    "performance": {
        "iperf_duration": 10,  # seconds
        "iperf_port": 5201,
        "bandwidth_test_protocol": "TCP",
        "parallel_streams": 1
    },
    
    # Stability Test Settings
    "stability": {
        "continuous_ping_duration": 30,  # seconds
        "reconnection_attempts": 5,
        "reconnection_delay": 2,  # seconds between attempts
        "packet_loss_threshold": {
            "excellent": 0,
            "good": 2,
            "acceptable": 5,
            "poor": 10
        }
    },
    
    # Signal Strength Thresholds (dBm)
    "signal_strength": {
        "excellent": -50,
        "good": -60,
        "fair": -70,
        "poor": -80
    },
    
    # Reporting Settings
    "reporting": {
        "json_indent": 4,
        "timestamp_format": "%Y-%m-%d %H:%M:%S",
        "report_filename_format": "wifi_test_results_%Y%m%d_%H%M%S",
        "save_raw_outputs": False
    },
    
    # Logging Settings
    "logging": {
        "log_level": "INFO",
        "log_format": "%(asctime)s - %(levelname)s - %(message)s",
        "log_filename_format": "wifi_test_log_%Y%m%d_%H%M%S.log",
        "console_output": True
    },
    
    # Network Tools Settings
    "network_tools": {
        "command_timeout": 30,
        "retry_attempts": 3,
        "retry_delay": 2
    }
}

# Platform-specific commands
PLATFORM_COMMANDS = {
    "Windows": {
        "ping": "ping -n {count} {host}",
        "traceroute": "tracert {host}",
        "ip_config": "ipconfig /all",
        "wifi_info": "netsh wlan show interfaces"
    },
    "Linux": {
        "ping": "ping -c {count} {host}",
        "traceroute": "traceroute {host}",
        "ip_config": "ip addr show",
        "wifi_info": "iwconfig 2>/dev/null",
        "signal_strength": "iwconfig 2>/dev/null | grep -E 'Signal level|Quality'"
    },
    "Darwin": {  # macOS
        "ping": "ping -c {count} {host}",
        "traceroute": "traceroute {host}",
        "ip_config": "ifconfig",
        "wifi_info": "/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport -I",
        "signal_strength": "/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport -I | grep RSSI"
    }
}

# Test Categories
TEST_CATEGORIES = [
    "connectivity_tests",
    "performance_tests",
    "stability_tests"
]

# Default test suite
DEFAULT_TEST_SUITE = {
    "connectivity_tests": [
        "test_ping_router",
        "test_ping_internet",
        "test_dns_resolution",
        "test_dhcp_assignment"
    ],
    "performance_tests": [
        "test_iperf_upload_speed",
        "test_iperf_download_speed",
        "test_latency_under_load"
    ],
    "stability_tests": [
        "test_continuous_ping",
        "test_signal_strength",
        "test_multiple_reconnections"
    ]
}
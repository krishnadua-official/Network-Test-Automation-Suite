import socket
import platform
from utils.network_tools import NetworkTools
import json
import threading
import time

class PerformanceTests:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.network_tools = NetworkTools()
        self.iperf_server = config.get('iperf_server')  # This line extracts it from config
        
        
    def test_iperf_upload_speed(self):
        if not self.iperf_server:
             return {"status": "SKIPPED", "reason": "No iperf server specified"}
        
        cmd = f"iperf3 -c {self.iperf_server} -t 10 -J"
        stdout, stderr, code = self.network_tools.run_command(cmd)

        if code ==0:
             try:
                data = json.loads(stdout)
                upload_mbps = data['end']['sum_sent']['bits_per_second'] / 1000000
                print(f"✓ Upload speed: {upload_mbps:.2f} Mbps")
                self.logger.log_info(f"Upload speed: {upload_mbps:.2f} Mbps")
                
             except Exception as e:
                print("✗ Failed to parse iperf3 output")
                return {
                    "status": "ERROR",
                    "error": "Failed to parse iperf3 output"}
        else:
            print("✗ Upload test failed - check if iperf3 is installed")
            self.logger.log_error("iperf3 upload test failed")
            return {
                "status": "FAIL",
                "error": stderr or "iperf3 test failed"}            

    def test_iperf_download_speed(self):
        print("\n[TEST] Download speed...")
        
        cmd = f"iperf3 -c {self.iperf_server} -t 10 -R -J"
        stdout, stderr, code = self.network_tools.run_command(cmd)
        
        if code == 0:
            try:
                data = json.loads(stdout)
                download_mbps = data['end']['sum_received']['bits_per_second'] / 1000000
                
                print(f"✓ Download speed: {download_mbps:.2f} Mbps")
                self.logger.log_info(f"Download speed: {download_mbps:.2f} Mbps")
                
                return {
                    "status": "PASS",
                    "speed_mbps": round(download_mbps, 2)
                }
            except Exception as e:
                print("✗ Failed to parse iperf3 output")
                self.logger.log_error(f"Failed to parse iperf3 output: {e}")
                return {
                    "status": "ERROR",
                    "error": "Failed to parse iperf3 output"
                }
        else:
            print("✗ Download test failed")
            self.logger.log_error("iperf3 download test failed")
            return {
                "status": "FAIL",
                "error": stderr or "iperf3 test failed"
            }
    
    def test_latency_under_load(self):
        print("\n[TEST] Latency under load...")
        
        try:
            # Baseline latency
            baseline = self.network_tools.ping(self.config['router_ip'], count=10)
            if not baseline['success']:
                print("✗ Could not establish baseline latency")
                return {"status": "FAIL", "error": "Could not establish baseline latency"}
            
            baseline_ms = baseline['avg_ms']
            
            # Start network load
            iperf_thread = threading.Thread(
                target=lambda: self.network_tools.run_command(
                    f"iperf3 -c {self.iperf_server} -t 15"
                )
            )
            iperf_thread.daemon = True
            iperf_thread.start()
            
            time.sleep(2)  # Wait for iperf to start
            
            # Measure loaded latency
            loaded = self.network_tools.ping(self.config['router_ip'], count=10)
            if not loaded['success']:
                print("✗ Could not measure loaded latency")
                return {"status": "FAIL", "error": "Could not measure loaded latency"}
            
            loaded_ms = loaded['avg_ms']
            increase_ms = loaded_ms - baseline_ms
            
            iperf_thread.join(timeout=20)
            
            # Results
            if increase_ms < 50:
                print(f"✓ Latency increase: {increase_ms:.2f}ms (acceptable)")
                status = "PASS"
            else:
                print(f"⚠ Latency increase: {increase_ms:.2f}ms (high)")
                status = "WARNING"
            
            self.logger.log_info(f"Latency test - baseline: {baseline_ms:.2f}ms, loaded: {loaded_ms:.2f}ms, increase: {increase_ms:.2f}ms")
            
            return {
                "status": status,
                "baseline_ms": round(baseline_ms, 2),
                "loaded_ms": round(loaded_ms, 2),
                "increase_ms": round(increase_ms, 2)
            }
                
        except Exception as e:
            print(f"✗ Latency test error: {e}")
            self.logger.log_error(f"Latency test error: {e}")
            return {
                "status": "ERROR",
                "error": str(e)
            }
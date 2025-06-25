"""
Multi-Device and Traffic Isolation Test Cases
"""

import time
import threading
import json
from utils.network_tools import NetworkTools


class MultiDeviceTests:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.network_tools = NetworkTools()
        self.router_ip = config['router_ip']
        self.iperf_server = config.get('iperf_server')
    
    def test_multiple_clients_bandwidth(self):
        """Test bandwidth distribution with multiple clients"""
        print("\n[TEST] Multiple clients bandwidth test...")
        
        if not self.iperf_server:
            print("⚠ Skipping - requires iperf3 server")
            return {"status": "SKIPPED", "reason": "No iperf3 server specified"}
        
        # Note: This simulates multiple clients from same device
        # Real multi-client testing requires multiple physical devices
        
        print("  Simulating 2 concurrent bandwidth tests...")
        
        results = {
            "client1": {"status": None, "speed": 0},
            "client2": {"status": None, "speed": 0}
        }
        
        def run_iperf_test(client_name, port_offset=0):
            """Run iperf test for a client"""
            try:
                port = 5201 + port_offset
                cmd = f"iperf3 -c {self.iperf_server} -p {port} -t 5 -J"
                stdout, stderr, code = self.network_tools.run_command(cmd, timeout=10)
                
                if code == 0:
                    data = json.loads(stdout)
                    speed_mbps = data['end']['sum_sent']['bits_per_second'] / 1000000
                    results[client_name] = {
                        "status": "SUCCESS",
                        "speed": round(speed_mbps, 2)
                    }
                else:
                    results[client_name] = {
                        "status": "FAILED",
                        "speed": 0
                    }
            except Exception as e:
                results[client_name] = {
                    "status": "ERROR",
                    "speed": 0,
                    "error": str(e)
                }
        
        # Run tests concurrently (if server supports multiple ports)
        thread1 = threading.Thread(target=run_iperf_test, args=("client1", 0))
        thread2 = threading.Thread(target=run_iperf_test, args=("client2", 1))
        
        # Try concurrent first
        print("  Testing concurrent connections...")
        thread1.start()
        thread2.start()
        
        thread1.join(timeout=15)
        thread2.join(timeout=15)
        
        # If concurrent failed, try sequential
        if results["client1"]["status"] == "FAILED" or results["client2"]["status"] == "FAILED":
            print("  Concurrent test failed, trying sequential...")
            run_iperf_test("client1", 0)
            time.sleep(1)
            run_iperf_test("client2", 0)
        
        # Analyze results
        if results["client1"]["status"] == "SUCCESS" and results["client2"]["status"] == "SUCCESS":
            total_bandwidth = results["client1"]["speed"] + results["client2"]["speed"]
            print(f"✓ Multi-client test successful")
            print(f"  Client 1: {results['client1']['speed']} Mbps")
            print(f"  Client 2: {results['client2']['speed']} Mbps")
            print(f"  Total: {total_bandwidth:.2f} Mbps")
            
            # Check if bandwidth is fairly distributed
            if abs(results["client1"]["speed"] - results["client2"]["speed"]) < 20:
                fairness = "FAIR"
            else:
                fairness = "UNFAIR"
            
            status = "PASS"
        else:
            print("✗ Multi-client test failed")
            status = "FAIL"
            fairness = "N/A"
            total_bandwidth = 0
        
        self.logger.log_info(f"Multi-client test - Total bandwidth: {total_bandwidth:.2f} Mbps")
        
        return {
            "status": status,
            "client1_speed_mbps": results["client1"]["speed"],
            "client2_speed_mbps": results["client2"]["speed"],
            "total_bandwidth_mbps": round(total_bandwidth, 2),
            "bandwidth_distribution": fairness
        }
    
    def test_qos_prioritization(self):
        """Test QoS (Quality of Service) prioritization"""
        print("\n[TEST] QoS prioritization test...")
        
        if not self.iperf_server:
            print("⚠ Skipping - requires iperf3 server")
            return {"status": "SKIPPED", "reason": "No iperf3 server specified"}
        
        # This test simulates different traffic types
        # Real QoS testing requires router configuration
        
        print("  Testing latency with simulated video stream...")
        
        # Baseline latency
        baseline = self.network_tools.ping(self.router_ip, count=5)
        if not baseline['success']:
            return {"status": "FAIL", "error": "Baseline ping failed"}
        
        baseline_latency = baseline['avg_ms']
        
        # Start simulated video stream (UDP traffic)
        video_thread = threading.Thread(
            target=lambda: self.network_tools.run_command(
                f"iperf3 -c {self.iperf_server} -u -b 5M -t 10"
            )
        )
        video_thread.daemon = True
        video_thread.start()
        
        time.sleep(2)  # Let video stream stabilize
        
        # Measure latency during "video stream"
        video_latency_result = self.network_tools.ping(self.router_ip, count=5)
        
        # Start bulk transfer (TCP traffic)
        bulk_thread = threading.Thread(
            target=lambda: self.network_tools.run_command(
                f"iperf3 -c {self.iperf_server} -t 8"
            )
        )
        bulk_thread.daemon = True
        bulk_thread.start()
        
        time.sleep(2)  # Let both streams run
        
        # Measure latency with both streams
        combined_latency_result = self.network_tools.ping(self.router_ip, count=5)
        
        # Wait for threads to complete
        video_thread.join(timeout=15)
        bulk_thread.join(timeout=15)
        
        # Analyze results
        if video_latency_result['success'] and combined_latency_result['success']:
            video_latency = video_latency_result['avg_ms']
            combined_latency = combined_latency_result['avg_ms']
            
            video_increase = video_latency - baseline_latency
            combined_increase = combined_latency - baseline_latency
            
            print(f"  Baseline latency: {baseline_latency:.1f}ms")
            print(f"  With video stream: {video_latency:.1f}ms (+{video_increase:.1f}ms)")
            print(f"  With both streams: {combined_latency:.1f}ms (+{combined_increase:.1f}ms)")
            
            # Determine QoS effectiveness
            if combined_increase < 50:
                print("✓ Good QoS performance - latency well controlled")
                status = "PASS"
                qos_rating = "EFFECTIVE"
            elif combined_increase < 100:
                print("⚠ Moderate QoS performance - some latency increase")
                status = "WARNING"
                qos_rating = "MODERATE"
            else:
                print("✗ Poor QoS performance - high latency under load")
                status = "FAIL"
                qos_rating = "POOR"
        else:
            print("✗ QoS test failed - could not measure latency")
            status = "FAIL"
            qos_rating = "N/A"
            video_increase = 0
            combined_increase = 0
        
        self.logger.log_info(f"QoS test - Rating: {qos_rating}")
        
        return {
            "status": status,
            "baseline_latency_ms": round(baseline_latency, 1),
            "video_stream_latency_increase_ms": round(video_increase, 1),
            "combined_load_latency_increase_ms": round(combined_increase, 1),
            "qos_effectiveness": qos_rating
        }
    
    def test_speed_at_different_distances(self):
        """Test speed at current location (distance test requires movement)"""
        print("\n[TEST] Speed at current distance...")
        
        # Get current signal strength
        signal_info = self.network_tools.get_signal_strength()
        
        current_rssi = None
        if signal_info['success'] and 'rssi' in signal_info:
            current_rssi = signal_info['rssi']
            print(f"  Current signal strength: {current_rssi} dBm")
        
        # Run speed test at current location
        if self.iperf_server:
            cmd = f"iperf3 -c {self.iperf_server} -t 5 -J"
            stdout, stderr, code = self.network_tools.run_command(cmd, timeout=10)
            
            if code == 0:
                try:
                    data = json.loads(stdout)
                    speed_mbps = data['end']['sum_sent']['bits_per_second'] / 1000000
                    
                    print(f"✓ Speed at current location: {speed_mbps:.2f} Mbps")
                    
                    # Correlate with signal strength
                    if current_rssi:
                        if current_rssi > -50 and speed_mbps > 50:
                            correlation = "EXCELLENT"
                        elif current_rssi > -60 and speed_mbps > 25:
                            correlation = "GOOD"
                        elif current_rssi > -70 and speed_mbps > 10:
                            correlation = "FAIR"
                        else:
                            correlation = "POOR"
                    else:
                        correlation = "UNKNOWN"
                    
                    self.logger.log_info(f"Distance test - Speed: {speed_mbps:.2f} Mbps at {current_rssi} dBm")
                    
                    return {
                        "status": "PASS",
                        "current_location_speed_mbps": round(speed_mbps, 2),
                        "signal_strength_dbm": current_rssi,
                        "speed_signal_correlation": correlation,
                        "note": "Test multiple locations manually for full analysis"
                    }
                except Exception as e:
                    print(f"✗ Failed to parse speed test results")
                    return {"status": "ERROR", "error": str(e)}
            else:
                print("✗ Speed test failed")
                return {"status": "FAIL", "error": "iperf3 test failed"}
        else:
            # No iperf server, just report signal strength
            print("ℹ No iperf server - reporting signal strength only")
            return {
                "status": "INFO",
                "signal_strength_dbm": current_rssi,
                "note": "Configure iperf3 server for speed correlation"
            }
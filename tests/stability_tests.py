
import time
import platform
from utils.network_tools import NetworkTools


class StabilityTests:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.network_tools = NetworkTools()
        self.router_ip = config['router_ip']
    
    def test_continuous_ping(self, duration=30):
        """Test continuous ping for packet loss"""
        print(f"\n[TEST] Continuous ping ({duration}s)...")
        
        result = self.network_tools.ping(self.router_ip, count=duration)
        
        if result['success']:
            packet_loss = result['packet_loss']
            
            if packet_loss == 0:
                print(f"✓ Perfect stability - 0% packet loss")
                status = "PASS"
            elif packet_loss < 2:
                print(f"✓ Good stability - {packet_loss}% packet loss")
                status = "PASS"
            elif packet_loss < 5:
                print(f"⚠ Acceptable stability - {packet_loss}% packet loss")
                status = "WARNING"
            else:
                print(f"✗ Poor stability - {packet_loss}% packet loss")
                status = "FAIL"
            
            self.logger.log_info(f"Continuous ping - {packet_loss}% loss")
            
            return {
                "status": status,
                "packet_loss_percent": packet_loss,
                "duration_seconds": duration
            }
        else:
            print("✗ Continuous ping failed")
            return {"status": "FAIL", "error": result['error']}
    
    def test_signal_strength(self):
        """Check Wi-Fi signal strength"""
        print("\n[TEST] Signal strength...")
        
        signal_info = self.network_tools.get_signal_strength()
        
        if signal_info['success']:
            if 'rssi' in signal_info:
                rssi = signal_info['rssi']
                
                if rssi > -50:
                    print(f"✓ Excellent signal: {rssi} dBm")
                    status = "PASS"
                elif rssi > -60:
                    print(f"✓ Good signal: {rssi} dBm")
                    status = "PASS"
                elif rssi > -70:
                    print(f"⚠ Fair signal: {rssi} dBm")
                    status = "WARNING"
                else:
                    print(f"✗ Poor signal: {rssi} dBm")
                    status = "FAIL"
                
                self.logger.log_info(f"Signal strength: {rssi} dBm")
                
                return {
                    "status": status,
                    "rssi_dbm": rssi
                }
            else:
                print(f"ℹ Signal info retrieved")
                return {"status": "INFO", "details": "Signal data available"}
        else:
            print(f"ℹ Signal strength not available on this system")
            return {"status": "INFO", "details": signal_info['error']}
    
    def test_multiple_reconnections(self, iterations=5):
        """Test connection stability with rapid tests"""
        print(f"\n[TEST] Connection stability ({iterations} rapid tests)...")
        
        successful = 0
        failed = 0
        response_times = []
        
        for i in range(iterations):
            result = self.network_tools.ping(self.router_ip, count=3)
            
            if result['success']:
                successful += 1
                response_times.append(result['avg_ms'])
                print(f"  Test {i+1}: ✓ ({result['avg_ms']:.1f}ms)")
            else:
                failed += 1
                print(f"  Test {i+1}: ✗")
            
            time.sleep(1)  # Brief pause between tests
        
        success_rate = (successful / iterations) * 100
        
        if success_rate == 100:
            print(f"\n✓ Perfect connection stability")
            status = "PASS"
        elif success_rate >= 80:
            print(f"\n⚠ {success_rate:.0f}% success rate")
            status = "WARNING"
        else:
            print(f"\n✗ Poor stability - {success_rate:.0f}% success")
            status = "FAIL"
        
        avg_response = sum(response_times) / len(response_times) if response_times else 0
        
        self.logger.log_info(f"Connection stability - {success_rate}% success")
        
        return {
            "status": status,
            "total_attempts": iterations,
            "successful": successful,
            "failed": failed,
            "success_rate_percent": success_rate,
            "average_response_ms": round(avg_response, 1)
        }
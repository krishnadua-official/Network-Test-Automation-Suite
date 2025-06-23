
import json
import os
from datetime import datetime
from config import TEST_CONFIG


class ReportGenerator:
    def __init__(self, results, config):
        self.results = results
        self.config = config
        self.report_config = TEST_CONFIG["reporting"]
        self.report_dir = "reports"
        
        # Create reports directory if it doesn't exist
        if not os.path.exists(self.report_dir):
            os.makedirs(self.report_dir)
    
    def generate_json_report(self):
        """Generate JSON format report"""
        timestamp = datetime.now()
        filename = timestamp.strftime(self.report_config["report_filename_format"]) + ".json"
        filepath = os.path.join(self.report_dir, filename)
        
        # Add metadata to results
        report_data = {
            "metadata": {
                "test_timestamp": self.results["test_info"]["timestamp"],
                "report_generated": timestamp.strftime(self.report_config["timestamp_format"]),
                "router_ip": self.config["router_ip"],
                "ssid": self.config["ssid"]
            },
            "test_results": self.results,
            "summary": self._generate_summary()
        }
        
        # Write JSON report
        with open(filepath, 'w') as f:
            json.dump(report_data, f, indent=self.report_config["json_indent"])
        
        return filepath
    
    def _generate_summary(self):
        """Generate test summary statistics"""
        summary = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "warnings": 0,
            "skipped": 0
        }
        
        # Process each category
        for category in ["connectivity_tests", "performance_tests", "stability_tests"]:
            if category in self.results:
                for test_name, test_result in self.results[category].items():
                    if isinstance(test_result, dict) and "status" in test_result:
                        summary["total_tests"] += 1
                        
                        status = test_result["status"]
                        if status == "PASS":
                            summary["passed"] += 1
                        elif status == "FAIL":
                            summary["failed"] += 1
                        elif status == "WARNING":
                            summary["warnings"] += 1
                        elif status == "SKIPPED":
                            summary["skipped"] += 1
        
        # Calculate pass rate
        if summary["total_tests"] > 0:
            summary["pass_rate"] = round((summary["passed"] / summary["total_tests"]) * 100, 2)
        else:
            summary["pass_rate"] = 0
        
        return summary
    
    def print_summary(self):
        """Print test summary to console"""
        summary = self._generate_summary()
        
        print("\n" + "="*50)
        print("TEST SUMMARY")
        print("="*50)
        
        print(f"\nTotal Tests: {summary['total_tests']}")
        print(f"Passed: {summary['passed']} ({summary['pass_rate']}%)")
        print(f"Failed: {summary['failed']}")
        print(f"Warnings: {summary['warnings']}")
        print(f"Skipped: {summary['skipped']}")
        
        print("\n" + "="*50)
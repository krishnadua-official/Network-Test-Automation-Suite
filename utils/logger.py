"""
Logger - Logging utility for test suite
"""

import logging
import os
from datetime import datetime
from config import TEST_CONFIG


class Logger:
    def __init__(self, log_dir="logs"):
        self.log_config = TEST_CONFIG["logging"]
        self.log_dir = log_dir
        
        # Create logs directory if it doesn't exist
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Set up logger
        self.logger = logging.getLogger("WiFiTestSuite")
        self.logger.setLevel(getattr(logging, self.log_config["log_level"]))
        
        # Create formatter
        formatter = logging.Formatter(self.log_config["log_format"])
        
        # File handler
        log_filename = datetime.now().strftime(self.log_config["log_filename_format"])
        log_path = os.path.join(log_dir, log_filename)
        file_handler = logging.FileHandler(log_path)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        # Console handler (if enabled)
        if self.log_config["console_output"]:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
        
        self.log_file = log_path
        self.log_info(f"Logger initialized - Log file: {log_path}")
    
    def log_info(self, message):
        """Log info level message"""
        self.logger.info(message)
    
    def log_warning(self, message):
        """Log warning level message"""
        self.logger.warning(message)
    
    def log_error(self, message):
        """Log error level message"""
        self.logger.error(message)
    
    def log_debug(self, message):
        """Log debug level message"""
        self.logger.debug(message)
    
    def log_test_start(self, test_name):
        """Log test start"""
        self.logger.info(f"[TEST START] {test_name}")
    
    def log_test_result(self, test_name, status, details=None):
        """Log test result"""
        if details:
            self.logger.info(f"[TEST RESULT] {test_name}: {status} - {details}")
        else:
            self.logger.info(f"[TEST RESULT] {test_name}: {status}")
    
    def get_log_file_path(self):
        """Return the current log file path"""
        return self.log_file
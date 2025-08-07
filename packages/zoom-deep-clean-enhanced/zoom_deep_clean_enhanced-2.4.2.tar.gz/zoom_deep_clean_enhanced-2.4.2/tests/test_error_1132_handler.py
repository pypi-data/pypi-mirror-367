#!/usr/bin/env python3
"""
Test suite for Error 1132 Handler functionality
Tests diagnostic and fix capabilities for Zoom Error 1132
"""

import unittest
import tempfile
import os
import sys
import json
import shutil
import logging
import socket
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from zoom_deep_clean.error_1132_handler import Error1132Handler


class TestError1132HandlerInitialization(unittest.TestCase):
    """Test Error 1132 Handler initialization"""

    def setUp(self):
        self.logger = logging.getLogger("test")

    def test_handler_initialization(self):
        """Test that Error 1132 handler initializes correctly"""
        handler = Error1132Handler(self.logger)

        self.assertIsNotNone(handler)
        self.assertEqual(handler.logger, self.logger)
        self.assertFalse(handler.dry_run)
        self.assertIsInstance(handler.zoom_domains, list)
        self.assertIsInstance(handler.zoom_ports, list)
        self.assertGreater(len(handler.zoom_domains), 0)
        self.assertGreater(len(handler.zoom_ports), 0)

    def test_handler_initialization_with_dry_run(self):
        """Test that Error 1132 handler initializes with dry_run flag"""
        handler = Error1132Handler(self.logger, dry_run=True)

        self.assertTrue(handler.dry_run)


class TestError1132Diagnostics(unittest.TestCase):
    """Test Error 1132 diagnostic functions"""

    def setUp(self):
        self.logger = logging.getLogger("test")
        self.handler = Error1132Handler(self.logger)

    @patch("socket.gethostbyname")
    def test_check_zoom_connectivity_success(self, mock_gethostbyname):
        """Test successful Zoom connectivity check"""
        # Mock successful DNS resolution
        mock_gethostbyname.return_value = "1.2.3.4"

        results = self.handler._check_zoom_connectivity()

        self.assertIsInstance(results, dict)
        self.assertIn("domains_tested", results)
        self.assertIn("domains_resolved", results)
        self.assertIn("domains_failed", results)
        self.assertIn("all_passed", results)
        self.assertTrue(results["all_passed"])
        self.assertEqual(
            len(results["domains_resolved"]), len(self.handler.zoom_domains)
        )
        self.assertEqual(len(results["domains_failed"]), 0)

    @patch("socket.gethostbyname")
    def test_check_zoom_connectivity_failure(self, mock_gethostbyname):
        """Test failed Zoom connectivity check"""
        # Mock failed DNS resolution
        mock_gethostbyname.side_effect = socket.gaierror("DNS resolution failed")

        results = self.handler._check_zoom_connectivity()

        self.assertIsInstance(results, dict)
        self.assertFalse(results["all_passed"])
        self.assertEqual(len(results["domains_failed"]), len(self.handler.zoom_domains))
        self.assertEqual(len(results["domains_resolved"]), 0)

    @patch("subprocess.run")
    def test_check_firewall_rules_success(self, mock_subprocess):
        """Test successful firewall rules check"""
        # Mock all subprocess calls to simulate no Zoom rules found
        mock_subprocess.side_effect = [
            # First call - pfctl -sr
            Mock(returncode=0, stdout="No firewall rules found"),
            # Second call - defaults read firewall
            Mock(returncode=0, stdout="firewall = { state = 0; }"),
            # Third call - socketfilterfw
            Mock(returncode=0, stdout="Firewall is disabled"),
        ]

        results = self.handler._check_firewall_rules()

        self.assertIsInstance(results, dict)
        self.assertTrue(results["pfctl_available"])
        self.assertFalse(results["zoom_rules_found"])

    @patch("subprocess.run")
    def test_check_firewall_rules_with_zoom_rules(self, mock_subprocess):
        """Test firewall rules check with Zoom rules found"""
        # Mock all subprocess calls to simulate Zoom rules found
        mock_subprocess.side_effect = [
            # First call - pfctl -sr (with Zoom rules)
            Mock(
                returncode=0,
                stdout="block drop quick proto tcp from any to any port = zoom",
            ),
            # Second call - defaults read firewall
            Mock(returncode=0, stdout="firewall = { state = 0; }"),
            # Third call - socketfilterfw
            Mock(returncode=0, stdout="Firewall is disabled"),
        ]

        results = self.handler._check_firewall_rules()

        self.assertIsInstance(results, dict)
        self.assertTrue(results["pfctl_available"])
        self.assertTrue(results["zoom_rules_found"])
        self.assertIn(
            "block drop quick proto tcp from any to any port = zoom", results["rules"]
        )

    @patch("os.environ", {})
    def test_check_proxy_settings_no_proxies(self):
        """Test proxy settings check with no proxies"""
        results = self.handler._check_proxy_settings()

        self.assertIsInstance(results, dict)
        self.assertFalse(results["has_proxies"])
        self.assertEqual(len(results["found_proxies"]), 0)

    @patch("os.environ", {"http_proxy": "http://proxy.example.com:8080"})
    def test_check_proxy_settings_with_proxies(self):
        """Test proxy settings check with proxies found"""
        results = self.handler._check_proxy_settings()

        self.assertIsInstance(results, dict)
        self.assertTrue(results["has_proxies"])
        self.assertIn("http_proxy", results["found_proxies"])
        self.assertEqual(
            results["found_proxies"]["http_proxy"], "http://proxy.example.com:8080"
        )

    def test_check_zoom_logs_no_logs(self):
        """Test Zoom logs check with no log files"""
        with patch("os.path.exists", return_value=False):
            results = self.handler._check_zoom_logs()

            self.assertIsInstance(results, dict)
            self.assertFalse(results["error_1132_found"])

    @patch("os.path.exists")
    @patch("os.listdir")
    def test_check_zoom_logs_no_error_1132(self, mock_listdir, mock_exists):
        """Test Zoom logs check with logs but no error 1132"""
        # Mock that log directories exist
        mock_exists.return_value = True
        # Mock that we find log files
        mock_listdir.return_value = ["zoom.log"]

        # Mock file reading to return content without error 1132
        with patch(
            "builtins.open",
            unittest.mock.mock_open(read_data="No issues found in logs"),
        ):
            results = self.handler._check_zoom_logs()

            self.assertIsInstance(results, dict)
            self.assertFalse(results["error_1132_found"])

    @patch("os.path.exists")
    @patch("os.listdir")
    def test_check_zoom_logs_with_error_1132(self, mock_listdir, mock_exists):
        """Test Zoom logs check with error 1132 found"""
        # Mock that log directories exist
        mock_exists.return_value = True
        # Mock that we find log files
        mock_listdir.return_value = ["zoom.log"]

        # Mock file reading to return content with error 1132
        with patch(
            "builtins.open",
            unittest.mock.mock_open(read_data="Error 1132 found in connection"),
        ):
            results = self.handler._check_zoom_logs()

            self.assertIsInstance(results, dict)
            self.assertTrue(results["error_1132_found"])


class TestError1132Fixes(unittest.TestCase):
    """Test Error 1132 fix functions"""

    def setUp(self):
        self.logger = logging.getLogger("test")

    def test_clear_dns_cache_dry_run(self):
        """Test DNS cache clearing in dry run mode"""
        handler = Error1132Handler(self.logger, dry_run=True)

        result = handler._clear_dns_cache()

        self.assertTrue(result)  # Should always return True in dry run mode

    def test_reset_firewall_rules_dry_run(self):
        """Test firewall rules reset in dry run mode"""
        handler = Error1132Handler(self.logger, dry_run=True)

        result = handler._reset_firewall_rules()

        self.assertTrue(result)  # Should always return True in dry run mode

    def test_clear_problematic_proxy_settings_dry_run(self):
        """Test clearing proxy settings in dry run mode"""
        handler = Error1132Handler(self.logger, dry_run=True)

        result = handler._clear_problematic_proxy_settings()

        self.assertTrue(result)  # Should always return True

    @patch("subprocess.run")
    def test_clear_dns_cache_success(self, mock_subprocess):
        """Test successful DNS cache clearing"""
        mock_subprocess.return_value.returncode = 0
        mock_subprocess.return_value.stdout = ""
        mock_subprocess.return_value.stderr = ""

        handler = Error1132Handler(self.logger, dry_run=False)
        result = handler._clear_dns_cache()

        self.assertTrue(result)

    @patch("subprocess.run")
    def test_clear_dns_cache_failure(self, mock_subprocess):
        """Test failed DNS cache clearing"""
        mock_subprocess.side_effect = Exception("Command failed")

        handler = Error1132Handler(self.logger, dry_run=False)
        result = handler._clear_dns_cache()

        self.assertFalse(result)


class TestError1132Integration(unittest.TestCase):
    """Test integration of Error 1132 diagnostic and fix functions"""

    def setUp(self):
        self.logger = logging.getLogger("test")
        self.handler = Error1132Handler(self.logger)

    @patch.object(Error1132Handler, "_check_zoom_connectivity")
    @patch.object(Error1132Handler, "_check_firewall_rules")
    @patch.object(Error1132Handler, "_check_proxy_settings")
    @patch.object(Error1132Handler, "_check_zoom_logs")
    @patch.object(Error1132Handler, "_check_network_configuration")
    @patch.object(Error1132Handler, "_check_port_connectivity")
    @patch.object(Error1132Handler, "_check_advanced_network_diagnostics")
    def test_diagnose_error_1132(
        self,
        mock_advanced,
        mock_port,
        mock_network,
        mock_logs,
        mock_proxy,
        mock_firewall,
        mock_connectivity,
    ):
        """Test complete Error 1132 diagnostic"""
        # Mock all diagnostic functions
        mock_connectivity.return_value = {"all_passed": True}
        mock_firewall.return_value = {"zoom_rules_found": False}
        mock_proxy.return_value = {"has_proxies": False}
        mock_logs.return_value = {"error_1132_found": False}
        mock_network.return_value = {"status": "ok"}
        mock_port.return_value = {"all_passed": True}
        mock_advanced.return_value = {"ping_results": {"zoom.us": "success"}}

        results = self.handler.diagnose_error_1132()

        self.assertIsInstance(results, dict)
        self.assertIn("connectivity", results)
        self.assertIn("firewall", results)
        self.assertIn("proxy", results)
        self.assertIn("logs", results)
        self.assertIn("network_config", results)
        self.assertIn("port_connectivity", results)
        self.assertIn("advanced_network", results)

    @patch.object(Error1132Handler, "_reset_network_configurations")
    @patch.object(Error1132Handler, "_clear_dns_cache")
    @patch.object(Error1132Handler, "_reset_firewall_rules")
    @patch.object(Error1132Handler, "_clear_problematic_proxy_settings")
    @patch.object(Error1132Handler, "_reset_network_interfaces")
    @patch.object(Error1132Handler, "_apply_advanced_network_fixes")
    def test_fix_error_1132_all_success(
        self,
        mock_advanced,
        mock_interfaces,
        mock_proxy,
        mock_firewall,
        mock_dns,
        mock_network,
    ):
        """Test Error 1132 fix with all fixes successful"""
        # Mock all fix functions to return success
        mock_network.return_value = True
        mock_dns.return_value = True
        mock_firewall.return_value = True
        mock_proxy.return_value = True
        mock_interfaces.return_value = True
        mock_advanced.return_value = True

        result = self.handler.fix_error_1132()

        self.assertTrue(result)

    @patch.object(Error1132Handler, "_reset_network_configurations")
    @patch.object(Error1132Handler, "_clear_dns_cache")
    @patch.object(Error1132Handler, "_reset_firewall_rules")
    @patch.object(Error1132Handler, "_clear_problematic_proxy_settings")
    @patch.object(Error1132Handler, "_reset_network_interfaces")
    @patch.object(Error1132Handler, "_apply_advanced_network_fixes")
    def test_fix_error_1132_with_failure(
        self,
        mock_advanced,
        mock_interfaces,
        mock_proxy,
        mock_firewall,
        mock_dns,
        mock_network,
    ):
        """Test Error 1132 fix with some fixes failing"""
        # Mock some fix functions to return failure
        mock_network.return_value = True
        mock_dns.return_value = False  # This one fails
        mock_firewall.return_value = True
        mock_proxy.return_value = True
        mock_interfaces.return_value = True
        mock_advanced.return_value = True

        result = self.handler.fix_error_1132()

        self.assertFalse(result)  # Should return False if any fix fails


class TestError1132ReportGeneration(unittest.TestCase):
    """Test Error 1132 report generation"""

    def setUp(self):
        self.logger = logging.getLogger("test")
        self.handler = Error1132Handler(self.logger)

    def test_generate_error_1132_report_empty_results(self):
        """Test report generation with empty results"""
        results = {}
        report = self.handler.generate_error_1132_report(results)

        self.assertIsInstance(report, str)
        self.assertIn("ZOOM ERROR 1132 DIAGNOSTIC REPORT", report)

    def test_generate_error_1132_report_complete_results(self):
        """Test report generation with complete diagnostic results"""
        results = {
            "connectivity": {"all_passed": True},
            "firewall": {"zoom_rules_found": False},
            "proxy": {"has_proxies": False},
            "logs": {"error_1132_found": False},
            "port_connectivity": {"all_passed": True},
            "advanced_network": {"ping_results": {"zoom.us": "success"}},
        }

        report = self.handler.generate_error_1132_report(results)

        self.assertIsInstance(report, str)
        self.assertIn("ZOOM ERROR 1132 DIAGNOSTIC REPORT", report)
        self.assertIn("All Zoom domains resolved successfully", report)
        self.assertIn("All critical Zoom ports are accessible", report)
        self.assertIn("No Zoom-blocking firewall rules found", report)
        self.assertIn("No proxy settings found", report)
        self.assertIn("No error 1132 references found in logs", report)
        self.assertIn("Ping to zoom.us successful", report)


def run_tests():
    """Run all Error 1132 handler tests"""
    # Create test suite
    test_suite = unittest.TestSuite()

    # Add all test classes
    test_classes = [
        TestError1132HandlerInitialization,
        TestError1132Diagnostics,
        TestError1132Fixes,
        TestError1132Integration,
        TestError1132ReportGeneration,
    ]

    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    return result.wasSuccessful()


if __name__ == "__main__":
    # Setup logging for tests
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    print("🧪 Running Error 1132 Handler Test Suite")
    print("=" * 50)

    success = run_tests()

    if success:
        print("\n✅ All Error 1132 Handler tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some Error 1132 Handler tests failed!")
        sys.exit(1)

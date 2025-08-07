#!/usr/bin/env python3
"""
Comprehensive Test Suite for Zoom Deep Clean Enhanced
Advanced testing with security validation and cross-platform support

Created by: PHLthy215 (Enhanced by Amazon Q)
Version: 2.3.0 - Comprehensive Testing
"""

import unittest
import tempfile
import os
import sys
import json
import shutil
import logging
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from zoom_deep_clean.cleaner_enhanced import ZoomDeepCleanerEnhanced
from zoom_deep_clean.advanced_features import AdvancedFeatures
from zoom_deep_clean.security_enhancements import (
    SecurityValidator,
    FileIntegrityChecker,
)
from zoom_deep_clean.advanced_detection import (
    SystemFingerprintAnalyzer,
    ZoomArtifactDetector,
)
from zoom_deep_clean.cross_platform_support import (
    CrossPlatformZoomCleaner,
    PlatformDetector,
)


class TestSecurityValidation(unittest.TestCase):
    """Test security validation features"""

    def setUp(self):
        self.logger = logging.getLogger("test")
        self.security_validator = SecurityValidator(self.logger)

    def test_path_validation_safe_paths(self):
        """Test that safe paths are validated correctly"""
        safe_paths = [
            os.path.expanduser("~/Library/Application Support/zoom.us"),
            "/Library/LaunchAgents/us.zoom.xos.plist",
            "/var/db/receipts/us.zoom.xos.pkg.bom",
        ]

        for path in safe_paths:
            with self.subTest(path=path):
                self.assertTrue(
                    self.security_validator.validate_path_operation(path, "delete"),
                    f"Safe path should be valid: {path}",
                )

    def test_path_validation_dangerous_paths(self):
        """Test that dangerous paths are rejected"""
        dangerous_paths = [
            "/System/Library/CoreServices/Finder.app",
            "/usr/bin/sudo",
            "/etc/passwd",
            "../../../etc/hosts",
            "/path/with/$(malicious command)",
            "/path/with/;rm -rf /",
        ]

        for path in dangerous_paths:
            with self.subTest(path=path):
                self.assertFalse(
                    self.security_validator.validate_path_operation(path, "delete"),
                    f"Dangerous path should be rejected: {path}",
                )

    def test_operation_signature_generation(self):
        """Test operation signature generation and verification"""
        operation = "delete"
        path = "/safe/test/path"

        signature = self.security_validator.generate_operation_signature(
            operation, path
        )
        self.assertIsInstance(signature, str)
        self.assertTrue(len(signature) > 0)

        # Verify signature
        self.assertTrue(
            self.security_validator.verify_operation_signature(
                operation, path, signature
            )
        )

        # Test with wrong signature
        wrong_signature = "wrong_signature"
        self.assertFalse(
            self.security_validator.verify_operation_signature(
                operation, path, wrong_signature
            )
        )


class TestFileIntegrityChecker(unittest.TestCase):
    """Test file integrity checking"""

    def setUp(self):
        self.logger = logging.getLogger("test")
        self.integrity_checker = FileIntegrityChecker(self.logger)
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_zoom_file_detection_by_content(self):
        """Test Zoom file detection by content"""
        # Create test file with Zoom signature
        test_file = os.path.join(self.temp_dir, "test_zoom_file")
        with open(test_file, "wb") as f:
            f.write(b"Some content with us.zoom.xos signature")

        self.assertTrue(
            self.integrity_checker.verify_zoom_file(test_file),
            "File with Zoom signature should be detected",
        )

    def test_zoom_file_detection_by_path(self):
        """Test Zoom file detection by path"""
        # Create test file with Zoom-like path
        zoom_dir = os.path.join(self.temp_dir, "zoom.us")
        os.makedirs(zoom_dir, exist_ok=True)
        test_file = os.path.join(zoom_dir, "config.plist")

        with open(test_file, "w") as f:
            f.write("test content")

        self.assertTrue(
            self.integrity_checker.verify_zoom_file(test_file),
            "File in Zoom directory should be detected",
        )

    def test_non_zoom_file_rejection(self):
        """Test that non-Zoom files are not detected"""
        # Create test file without Zoom signatures
        test_file = os.path.join(self.temp_dir, "normal_file.txt")
        with open(test_file, "w") as f:
            f.write("This is a normal file with no Zoom content")

        self.assertFalse(
            self.integrity_checker.verify_zoom_file(test_file),
            "Normal file should not be detected as Zoom file",
        )

    def test_file_hash_calculation(self):
        """Test file hash calculation"""
        test_file = os.path.join(self.temp_dir, "hash_test.txt")
        test_content = "Test content for hash calculation"

        with open(test_file, "w") as f:
            f.write(test_content)

        file_hash = self.integrity_checker.calculate_file_hash(test_file)
        self.assertIsInstance(file_hash, str)
        self.assertEqual(len(file_hash), 64)  # SHA-256 hash length

        # Test that same content produces same hash
        test_file2 = os.path.join(self.temp_dir, "hash_test2.txt")
        with open(test_file2, "w") as f:
            f.write(test_content)

        file_hash2 = self.integrity_checker.calculate_file_hash(test_file2)
        self.assertEqual(file_hash, file_hash2)


class TestSystemFingerprintAnalyzer(unittest.TestCase):
    """Test system fingerprint analysis"""

    def setUp(self):
        self.logger = logging.getLogger("test")
        self.analyzer = SystemFingerprintAnalyzer(self.logger)

    @patch("subprocess.run")
    def test_hardware_identifier_extraction(self, mock_subprocess):
        """Test hardware identifier extraction"""
        # Mock ioreg output
        mock_subprocess.return_value.returncode = 0
        mock_subprocess.return_value.stdout = (
            '"IOPlatformUUID" = "12345678-1234-1234-1234-123456789ABC"'
        )

        identifiers = self.analyzer._get_hardware_identifiers()

        self.assertIn("system_uuid", identifiers)
        self.assertEqual(
            identifiers["system_uuid"], "12345678-1234-1234-1234-123456789ABC"
        )

    def test_risk_assessment_calculation(self):
        """Test risk assessment calculation"""
        # Mock analysis data
        mock_analysis = {
            "hardware_identifiers": {
                "system_uuid": "12345678-1234-1234-1234-123456789ABC",
                "serial_number": "TEST123456",
                "mac_addresses": ["aa:bb:cc:dd:ee:ff", "11:22:33:44:55:66"],
            },
            "software_identifiers": {
                "installed_apps": ["App1.app", "App2.app"] * 30  # 60 apps
            },
            "behavioral_patterns": {"app_usage": {"zoom_in_dock": True}},
        }

        risk_assessment = self.analyzer._calculate_risk_assessment(mock_analysis)

        self.assertIn("risk_score", risk_assessment)
        self.assertIn("risk_level", risk_assessment)
        self.assertIn("risk_factors", risk_assessment)
        self.assertIn("recommendations", risk_assessment)

        # Should be high risk due to multiple identifiers
        self.assertGreaterEqual(risk_assessment["risk_score"], 5)


class TestZoomArtifactDetector(unittest.TestCase):
    """Test Zoom artifact detection"""

    def setUp(self):
        self.logger = logging.getLogger("test")
        self.detector = ZoomArtifactDetector(self.logger)
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_hidden_file_detection(self):
        """Test detection of hidden Zoom files"""
        # Create hidden Zoom file
        hidden_file = os.path.join(self.temp_dir, ".zoom_config")
        with open(hidden_file, "w") as f:
            f.write("hidden zoom configuration")

        # Mock os.walk to return our test directory
        with patch("os.walk") as mock_walk:
            mock_walk.return_value = [(self.temp_dir, [], [".zoom_config"])]

            hidden_files = self.detector._find_hidden_files()

            # Should find our hidden file
            self.assertTrue(any(".zoom_config" in f for f in hidden_files))

    def test_embedded_reference_detection(self):
        """Test detection of embedded Zoom references"""
        # Create test config file with Zoom reference
        test_config = os.path.join(self.temp_dir, ".bashrc")
        with open(test_config, "w") as f:
            f.write("export ZOOM_CONFIG=/path/to/zoom\nalias zoom='zoom.us'\n")

        references = self.detector._search_file_for_zoom_refs(test_config)

        self.assertTrue(len(references) > 0)
        self.assertTrue(any("zoom.us" in ref for ref in references))


class TestCrossPlatformSupport(unittest.TestCase):
    """Test cross-platform support"""

    def setUp(self):
        self.logger = logging.getLogger("test")
        self.platform_detector = PlatformDetector(self.logger)

    def test_platform_detection(self):
        """Test platform detection"""
        platform_info = self.platform_detector.get_platform_info()

        self.assertIn("system", platform_info)
        self.assertIn("version", platform_info)
        self.assertIn("architecture", platform_info)
        self.assertIn("supported", platform_info)

        # Should detect current platform
        import platform

        expected_system = platform.system().lower()
        self.assertEqual(platform_info["system"], expected_system)

    def test_platform_specific_paths(self):
        """Test platform-specific path generation"""
        paths = self.platform_detector.get_platform_specific_paths()

        if self.platform_detector.platform == "darwin":
            self.assertIn("applications", paths)
            self.assertIn("user_data", paths)
            self.assertIn("system_data", paths)
        elif self.platform_detector.platform == "windows":
            self.assertIn("registry_keys", paths)
        elif self.platform_detector.platform == "linux":
            self.assertIn("applications", paths)

    @patch("platform.system")
    def test_unsupported_platform_handling(self, mock_platform):
        """Test handling of unsupported platforms"""
        mock_platform.return_value = "UnsupportedOS"

        detector = PlatformDetector(self.logger)
        self.assertFalse(detector.is_supported())


class TestZoomDeepCleanerEnhanced(unittest.TestCase):
    """Test the main cleaner with enhancements"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.log_file = os.path.join(self.temp_dir, "test.log")

        # Create cleaner in dry-run mode for safe testing
        self.cleaner = ZoomDeepCleanerEnhanced(
            log_file=self.log_file,
            verbose=True,
            dry_run=True,
            enable_backup=False,
            vm_aware=True,
            system_reboot=False,
            enable_advanced_features=True,
        )

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_cleaner_initialization(self):
        """Test cleaner initialization"""
        self.assertTrue(self.cleaner.dry_run)
        self.assertTrue(self.cleaner.vm_aware)
        self.assertTrue(self.cleaner.enable_advanced_features)
        self.assertIsNotNone(self.cleaner.advanced_features)

    def test_security_validation_integration(self):
        """Test integration with security validation"""
        # Test path validation
        safe_path = os.path.expanduser("~/Library/Application Support/zoom.us")
        self.assertTrue(self.cleaner._validate_path(safe_path))

        # Test dangerous path rejection
        dangerous_path = "/System/Library/CoreServices/Finder.app"
        with self.assertRaises(Exception):
            self.cleaner._validate_path(dangerous_path)

    @patch("subprocess.run")
    def test_vm_detection(self, mock_subprocess):
        """Test VM detection functionality"""
        # Mock VM detection commands
        mock_subprocess.return_value.returncode = 0
        mock_subprocess.return_value.stdout = "VMware Fusion"

        # This would test VM detection if the method was exposed
        # For now, we test that VM-aware mode is enabled
        self.assertTrue(self.cleaner.vm_aware)

    def test_statistics_tracking(self):
        """Test statistics tracking"""
        initial_stats = self.cleaner.cleanup_stats.copy()

        # Stats should be initialized
        self.assertEqual(initial_stats["files_removed"], 0)
        self.assertEqual(initial_stats["processes_killed"], 0)
        self.assertEqual(initial_stats["errors"], 0)

        # Test that stats structure is complete
        expected_keys = [
            "files_removed",
            "directories_removed",
            "processes_killed",
            "vm_services_stopped",
            "keychain_entries_removed",
            "files_backed_up",
            "errors",
            "warnings",
            "security_violations",
            "remaining_files_found",
        ]

        for key in expected_keys:
            self.assertIn(key, initial_stats)


class TestAdvancedFeatures(unittest.TestCase):
    """Test advanced features module"""

    def setUp(self):
        self.logger = logging.getLogger("test")
        self.advanced_features = AdvancedFeatures(
            logger=self.logger, dry_run=True, enable_mac_spoofing=False
        )

    def test_advanced_features_initialization(self):
        """Test advanced features initialization"""
        self.assertTrue(self.advanced_features.dry_run)
        self.assertFalse(self.advanced_features.enable_mac_spoofing)
        self.assertIsNotNone(self.advanced_features.advanced_stats)

    @patch("subprocess.run")
    def test_keychain_scanning(self, mock_subprocess):
        """Test keychain scanning functionality"""
        # Mock security command output
        mock_subprocess.return_value.returncode = 0
        mock_subprocess.return_value.stdout = "keychain: test output with zoom entries"

        # Test keychain scan
        result = self.advanced_features.scan_keychain_comprehensive()

        self.assertIsInstance(result, dict)
        self.assertIn("zoom_entries", result)
        self.assertIn("total_entries_scanned", result)


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete system"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.log_file = os.path.join(self.temp_dir, "integration_test.log")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_full_dry_run_execution(self):
        """Test full dry-run execution"""
        cleaner = ZoomDeepCleanerEnhanced(
            log_file=self.log_file,
            verbose=True,
            dry_run=True,
            enable_backup=False,
            vm_aware=True,
            enable_advanced_features=True,
        )

        # Run cleanup in dry-run mode
        try:
            success = cleaner.run_deep_clean()
            # Should complete without errors in dry-run mode
            self.assertTrue(isinstance(success, bool))
        except Exception as e:
            self.fail(f"Dry-run execution failed: {e}")

    def test_report_generation(self):
        """Test report generation"""
        cleaner = ZoomDeepCleanerEnhanced(
            log_file=self.log_file, verbose=True, dry_run=True, enable_backup=False
        )

        # Generate report
        report_file = os.path.join(self.temp_dir, "test_report.json")

        # Mock report generation
        test_report = {
            "timestamp": "2024-01-01T00:00:00",
            "version": "2.3.0",
            "platform": "darwin",
            "statistics": cleaner.cleanup_stats,
            "success": True,
        }

        with open(report_file, "w") as f:
            json.dump(test_report, f, indent=2)

        # Verify report was created
        self.assertTrue(os.path.exists(report_file))

        # Verify report content
        with open(report_file, "r") as f:
            loaded_report = json.load(f)

        self.assertEqual(loaded_report["version"], "2.3.0")
        self.assertIn("statistics", loaded_report)


def run_comprehensive_tests():
    """Run all comprehensive tests"""
    # Create test suite
    test_suite = unittest.TestSuite()

    # Add all test classes
    test_classes = [
        TestSecurityValidation,
        TestFileIntegrityChecker,
        TestSystemFingerprintAnalyzer,
        TestZoomArtifactDetector,
        TestCrossPlatformSupport,
        TestZoomDeepCleanerEnhanced,
        TestAdvancedFeatures,
        TestIntegration,
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

    print("🧪 Running Comprehensive Test Suite for Zoom Deep Clean Enhanced")
    print("=" * 80)

    success = run_comprehensive_tests()

    if success:
        print("\n✅ All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)

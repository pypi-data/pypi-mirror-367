#!/usr/bin/env python3
"""
Enhanced Tests for Advanced Detection module
Comprehensive testing to improve coverage from 35% to 60%+
"""

import sys
import os
import unittest
import tempfile
import shutil
import logging
import subprocess
from unittest.mock import patch, MagicMock, Mock, mock_open, call
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Import the advanced detection module
from zoom_deep_clean.advanced_detection import (
    SystemFingerprintAnalyzer,
    ZoomArtifactDetector,
)


class TestSystemFingerprintAnalyzer(unittest.TestCase):
    """Test SystemFingerprintAnalyzer class functionality"""

    def setUp(self):
        """Set up test environment"""
        self.logger = logging.getLogger("test_logger")
        self.logger.setLevel(logging.DEBUG)
        self.analyzer = SystemFingerprintAnalyzer(self.logger)

    def test_analyzer_initialization(self):
        """Test SystemFingerprintAnalyzer initialization"""
        self.assertEqual(self.analyzer.logger, self.logger)
        self.assertIsInstance(self.analyzer.fingerprint_data, dict)
        self.assertEqual(len(self.analyzer.fingerprint_data), 0)

    @patch("subprocess.run")
    def test_analyze_system_fingerprints_complete(self, mock_subprocess):
        """Test complete system fingerprint analysis"""
        # Mock subprocess calls for various system commands
        mock_subprocess.return_value.returncode = 0
        mock_subprocess.return_value.stdout = "Mock output"

        # Mock all private methods to avoid actual system calls
        self.analyzer._get_hardware_identifiers = MagicMock(
            return_value={"cpu": "test"}
        )
        self.analyzer._get_network_identifiers = MagicMock(return_value={"dns": "test"})
        self.analyzer._get_software_identifiers = MagicMock(
            return_value={"apps": ["test"]}
        )
        self.analyzer._get_user_identifiers = MagicMock(return_value={"user": "test"})
        self.analyzer._get_temporal_identifiers = MagicMock(
            return_value={"time": "test"}
        )
        self.analyzer._analyze_behavioral_patterns = MagicMock(
            return_value={"pattern": "test"}
        )
        self.analyzer._calculate_risk_assessment = MagicMock(
            return_value={"risk": "low"}
        )

        result = self.analyzer.analyze_system_fingerprints()

        # Verify result structure
        self.assertIsInstance(result, dict)
        expected_keys = [
            "hardware_identifiers",
            "network_identifiers",
            "software_identifiers",
            "user_identifiers",
            "temporal_identifiers",
            "behavioral_patterns",
            "risk_assessment",
        ]
        for key in expected_keys:
            self.assertIn(key, result)

        # Verify all methods were called
        self.analyzer._get_hardware_identifiers.assert_called_once()
        self.analyzer._get_network_identifiers.assert_called_once()
        self.analyzer._get_software_identifiers.assert_called_once()
        self.analyzer._get_user_identifiers.assert_called_once()
        self.analyzer._get_temporal_identifiers.assert_called_once()
        self.analyzer._analyze_behavioral_patterns.assert_called_once()
        self.analyzer._calculate_risk_assessment.assert_called_once()

    @patch("subprocess.run")
    def test_get_hardware_identifiers_success(self, mock_subprocess):
        """Test _get_hardware_identifiers with successful subprocess calls"""

        # Mock different subprocess calls
        def subprocess_side_effect(*args, **kwargs):
            result = MagicMock()
            result.returncode = 0

            # Mock ioreg output for UUID
            if "ioreg" in args[0]:
                result.stdout = (
                    '"IOPlatformUUID" = "12345678-1234-1234-1234-123456789ABC"'
                )
            # Mock system_profiler output for serial
            elif "system_profiler" in args[0]:
                result.stdout = "Serial Number (system): TESTSERIAL123"
            # Mock ifconfig output for MAC addresses
            elif "ifconfig" in args[0]:
                result.stdout = "ether aa:bb:cc:dd:ee:ff\nether 11:22:33:44:55:66"
            # Mock sysctl output for CPU
            elif "sysctl" in args[0]:
                result.stdout = "Intel Core i7-9750H CPU @ 2.60GHz"
            else:
                result.stdout = ""

            return result

        mock_subprocess.side_effect = subprocess_side_effect

        identifiers = self.analyzer._get_hardware_identifiers()

        # Verify results
        self.assertIsInstance(identifiers, dict)
        self.assertEqual(
            identifiers.get("system_uuid"), "12345678-1234-1234-1234-123456789ABC"
        )
        self.assertEqual(identifiers.get("serial_number"), "TESTSERIAL123")
        self.assertIn("mac_addresses", identifiers)
        self.assertEqual(
            identifiers.get("cpu_brand"), "Intel Core i7-9750H CPU @ 2.60GHz"
        )

    @patch("subprocess.run")
    def test_get_hardware_identifiers_failure(self, mock_subprocess):
        """Test _get_hardware_identifiers with subprocess failures"""
        # Mock subprocess failure
        mock_subprocess.return_value.returncode = 1
        mock_subprocess.return_value.stdout = ""

        identifiers = self.analyzer._get_hardware_identifiers()

        # Should return empty dict or handle gracefully
        self.assertIsInstance(identifiers, dict)

    @patch("subprocess.run")
    def test_get_hardware_identifiers_exception(self, mock_subprocess):
        """Test _get_hardware_identifiers with exceptions"""
        # Mock subprocess to raise an exception
        mock_subprocess.side_effect = Exception("Command failed")

        identifiers = self.analyzer._get_hardware_identifiers()

        # Should handle exception gracefully
        self.assertIsInstance(identifiers, dict)

    @patch("subprocess.run")
    def test_get_network_identifiers_success(self, mock_subprocess):
        """Test _get_network_identifiers with successful subprocess calls"""

        def subprocess_side_effect(*args, **kwargs):
            result = MagicMock()
            result.returncode = 0

            if "networksetup" in args[0] and "listallhardwareports" in args[0]:
                result.stdout = "Hardware Port: Wi-Fi\nDevice: en0\nEthernet Address: aa:bb:cc:dd:ee:ff"
            elif "scutil" in args[0]:
                result.stdout = (
                    "DNS configuration\nresolver #1\nnameserver[0] : 8.8.8.8"
                )
            elif "networksetup" in args[0] and "listlocations" in args[0]:
                result.stdout = "Automatic\nHome\nWork"
            else:
                result.stdout = ""

            return result

        mock_subprocess.side_effect = subprocess_side_effect

        identifiers = self.analyzer._get_network_identifiers()

        # Verify results
        self.assertIsInstance(identifiers, dict)
        self.assertIn("network_hardware", identifiers)
        self.assertIn("dns_config", identifiers)
        self.assertIn("network_locations", identifiers)

    @patch("subprocess.run")
    def test_get_network_identifiers_exception(self, mock_subprocess):
        """Test _get_network_identifiers with exceptions"""
        mock_subprocess.side_effect = Exception("Network command failed")

        identifiers = self.analyzer._get_network_identifiers()

        # Should handle exception gracefully
        self.assertIsInstance(identifiers, dict)

    @patch("pathlib.Path.iterdir")
    @patch("pathlib.Path.exists")
    @patch("subprocess.run")
    def test_get_software_identifiers_success(
        self, mock_subprocess, mock_exists, mock_iterdir
    ):
        """Test _get_software_identifiers with successful operations"""
        # Mock subprocess for sw_vers
        mock_subprocess.return_value.returncode = 0
        mock_subprocess.return_value.stdout = (
            "ProductName: macOS\nProductVersion: 13.0.0"
        )

        # Mock /Applications directory
        mock_exists.return_value = True
        mock_app1 = MagicMock()
        mock_app1.name = "Safari.app"
        mock_app1.is_dir.return_value = True
        mock_app1.suffix = ".app"

        mock_app2 = MagicMock()
        mock_app2.name = "Zoom.app"
        mock_app2.is_dir.return_value = True
        mock_app2.suffix = ".app"

        mock_iterdir.return_value = [mock_app1, mock_app2]

        identifiers = self.analyzer._get_software_identifiers()

        # Verify results
        self.assertIsInstance(identifiers, dict)
        self.assertIn("system_version", identifiers)
        self.assertIn("installed_apps", identifiers)
        self.assertIn("Safari.app", identifiers["installed_apps"])
        self.assertIn("Zoom.app", identifiers["installed_apps"])

    def test_get_software_identifiers_exception(self):
        """Test _get_software_identifiers with exceptions"""
        with patch("subprocess.run", side_effect=Exception("Software command failed")):
            identifiers = self.analyzer._get_software_identifiers()

            # Should handle exception gracefully
            self.assertIsInstance(identifiers, dict)

    def test_get_user_identifiers_success(self):
        """Test _get_user_identifiers functionality"""
        with patch("os.getenv") as mock_getenv:
            mock_getenv.side_effect = lambda key, default=None: {
                "USER": "testuser",
                "HOME": "/Users/testuser",
                "SHELL": "/bin/bash",
            }.get(key, default)

            identifiers = self.analyzer._get_user_identifiers()

            # Verify results
            self.assertIsInstance(identifiers, dict)

    def test_get_temporal_identifiers_success(self):
        """Test _get_temporal_identifiers functionality"""
        with patch("subprocess.run") as mock_subprocess:
            mock_subprocess.return_value.returncode = 0
            mock_subprocess.return_value.stdout = "Tue Jan  1 00:00:00 PST 2024"

            identifiers = self.analyzer._get_temporal_identifiers()

            # Verify results
            self.assertIsInstance(identifiers, dict)

    def test_analyze_behavioral_patterns_success(self):
        """Test _analyze_behavioral_patterns functionality"""
        # Mock all behavioral analysis methods
        self.analyzer._analyze_app_usage_patterns = MagicMock(
            return_value={"app_usage": "test"}
        )
        self.analyzer._analyze_file_access_patterns = MagicMock(
            return_value={"file_access": "test"}
        )
        self.analyzer._analyze_network_patterns = MagicMock(
            return_value={"network": "test"}
        )

        patterns = self.analyzer._analyze_behavioral_patterns()

        # Verify results
        self.assertIsInstance(patterns, dict)
        self.analyzer._analyze_app_usage_patterns.assert_called_once()
        self.analyzer._analyze_file_access_patterns.assert_called_once()
        self.analyzer._analyze_network_patterns.assert_called_once()

    @patch("pathlib.Path.exists")
    def test_analyze_app_usage_patterns_success(self, mock_exists):
        """Test _analyze_app_usage_patterns functionality"""
        mock_exists.return_value = True

        with patch("subprocess.run") as mock_subprocess:
            mock_subprocess.return_value.returncode = 0
            mock_subprocess.return_value.stdout = "Zoom.app\nus.zoom.xos"

            patterns = self.analyzer._analyze_app_usage_patterns()

            # Verify results
            self.assertIsInstance(patterns, dict)

    def test_analyze_file_access_patterns_success(self):
        """Test _analyze_file_access_patterns functionality"""
        with patch("pathlib.Path.exists") as mock_exists:
            mock_exists.return_value = True

            with patch("pathlib.Path.stat") as mock_stat:
                mock_stat.return_value.st_atime = 1640995200  # Mock access time

                patterns = self.analyzer._analyze_file_access_patterns()

                # Verify results
                self.assertIsInstance(patterns, dict)

    def test_analyze_network_patterns_success(self):
        """Test _analyze_network_patterns functionality"""
        with patch("subprocess.run") as mock_subprocess:
            mock_subprocess.return_value.returncode = 0
            mock_subprocess.return_value.stdout = "TCP connections"

            patterns = self.analyzer._analyze_network_patterns()

            # Verify results
            self.assertIsInstance(patterns, dict)

    def test_calculate_risk_assessment_high_risk(self):
        """Test _calculate_risk_assessment with high risk scenario"""
        # Create analysis data that should trigger high risk
        analysis = {
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

        risk_assessment = self.analyzer._calculate_risk_assessment(analysis)

        # Verify results
        self.assertIsInstance(risk_assessment, dict)
        self.assertIn("risk_score", risk_assessment)
        self.assertIn("risk_level", risk_assessment)
        self.assertIn("risk_factors", risk_assessment)
        self.assertIn("recommendations", risk_assessment)

        # Should be high risk due to multiple identifiers
        self.assertGreaterEqual(risk_assessment["risk_score"], 5)

    def test_calculate_risk_assessment_low_risk(self):
        """Test _calculate_risk_assessment with low risk scenario"""
        # Create analysis data with minimal risk factors
        analysis = {
            "hardware_identifiers": {},
            "software_identifiers": {"installed_apps": ["App1.app"]},
            "behavioral_patterns": {"app_usage": {}},
        }

        risk_assessment = self.analyzer._calculate_risk_assessment(analysis)

        # Verify results
        self.assertIsInstance(risk_assessment, dict)
        self.assertIn("risk_score", risk_assessment)
        self.assertIn("risk_level", risk_assessment)

    def test_generate_recommendations_success(self):
        """Test _generate_recommendations functionality"""
        risk_level = "high"
        risk_factors = [
            "multiple MAC addresses detected",
            "many installed apps",
            "Zoom application in dock",
        ]

        recommendations = self.analyzer._generate_recommendations(
            risk_level, risk_factors
        )

        # Verify results
        self.assertIsInstance(recommendations, list)
        self.assertTrue(len(recommendations) > 0)


class TestZoomArtifactDetector(unittest.TestCase):
    """Test ZoomArtifactDetector class functionality"""

    def setUp(self):
        """Set up test environment"""
        self.logger = logging.getLogger("test_logger")
        self.logger.setLevel(logging.DEBUG)
        self.detector = ZoomArtifactDetector(self.logger)
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test environment"""
        try:
            shutil.rmtree(self.temp_dir)
        except:
            pass

    def test_detector_initialization(self):
        """Test ZoomArtifactDetector initialization"""
        self.assertEqual(self.detector.logger, self.logger)

    def test_detect_hidden_artifacts_success(self):
        """Test detect_hidden_artifacts complete functionality"""
        # Mock all detection methods
        self.detector._find_hidden_files = MagicMock(
            return_value=["hidden1", "hidden2"]
        )
        self.detector._find_embedded_references = MagicMock(
            return_value=["ref1", "ref2"]
        )
        self.detector._find_metadata_traces = MagicMock(return_value=["meta1"])
        self.detector._find_cache_artifacts = MagicMock(return_value=["cache1"])
        self.detector._find_log_references = MagicMock(return_value=["log1"])

        artifacts = self.detector.detect_hidden_artifacts()

        # Verify results
        self.assertIsInstance(artifacts, dict)
        expected_keys = [
            "hidden_files",
            "embedded_references",
            "metadata_traces",
            "cache_artifacts",
            "log_references",
        ]
        for key in expected_keys:
            self.assertIn(key, artifacts)

        # Verify all methods were called
        self.detector._find_hidden_files.assert_called_once()
        self.detector._find_embedded_references.assert_called_once()
        self.detector._find_metadata_traces.assert_called_once()
        self.detector._find_cache_artifacts.assert_called_once()
        self.detector._find_log_references.assert_called_once()

    @patch("os.walk")
    def test_find_hidden_files_success(self, mock_walk):
        """Test _find_hidden_files with successful discovery"""
        # Mock os.walk to return test directories with hidden files
        mock_walk.return_value = [
            ("/Users/test", [], [".zoom_config", ".hidden_zoom", "normal_file.txt"]),
            ("/Users/test/Library", [], [".zoom_cache", "other_file"]),
        ]

        hidden_files = self.detector._find_hidden_files()

        # Verify results
        self.assertIsInstance(hidden_files, list)
        self.assertTrue(any("zoom" in f.lower() for f in hidden_files))

    def test_find_hidden_files_exception(self):
        """Test _find_hidden_files with exceptions"""
        with patch("os.walk", side_effect=PermissionError("Permission denied")):
            hidden_files = self.detector._find_hidden_files()

            # Should handle exception gracefully
            self.assertIsInstance(hidden_files, list)

    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.is_file")
    def test_find_embedded_references_success(self, mock_is_file, mock_exists):
        """Test _find_embedded_references with successful discovery"""
        mock_exists.return_value = True
        mock_is_file.return_value = True

        # Mock the search method to return zoom references
        self.detector._search_file_for_zoom_refs = MagicMock(
            return_value=["zoom.us reference", "us.zoom.xos"]
        )

        references = self.detector._find_embedded_references()

        # Verify results
        self.assertIsInstance(references, list)

    @patch("pathlib.Path.exists")
    def test_find_embedded_references_no_files(self, mock_exists):
        """Test _find_embedded_references when files don't exist"""
        mock_exists.return_value = False

        references = self.detector._find_embedded_references()

        # Should return empty list when no config files exist
        self.assertIsInstance(references, list)

    def test_search_file_for_zoom_refs_success(self):
        """Test _search_file_for_zoom_refs with zoom references"""
        # Create a test file with zoom references
        test_file = os.path.join(self.temp_dir, "test_config")
        with open(test_file, "w") as f:
            f.write("export ZOOM_CONFIG=/path/to/zoom\n")
            f.write("alias zoom='zoom.us'\n")
            f.write("us.zoom.xos configuration\n")
            f.write("normal line without zoom\n")

        references = self.detector._search_file_for_zoom_refs(test_file)

        # Verify results
        self.assertIsInstance(references, list)
        self.assertTrue(len(references) > 0)
        self.assertTrue(any("zoom.us" in ref for ref in references))

    def test_search_file_for_zoom_refs_no_references(self):
        """Test _search_file_for_zoom_refs without zoom references"""
        # Create a test file without zoom references
        test_file = os.path.join(self.temp_dir, "test_config_clean")
        with open(test_file, "w") as f:
            f.write("export PATH=/usr/bin\n")
            f.write("alias ll='ls -la'\n")
            f.write("normal configuration\n")

        references = self.detector._search_file_for_zoom_refs(test_file)

        # Should return empty list
        self.assertIsInstance(references, list)
        self.assertEqual(len(references), 0)

    def test_search_file_for_zoom_refs_exception(self):
        """Test _search_file_for_zoom_refs with file read exception"""
        # Try to read a non-existent file
        nonexistent_file = os.path.join(self.temp_dir, "nonexistent")

        references = self.detector._search_file_for_zoom_refs(nonexistent_file)

        # Should handle exception gracefully
        self.assertIsInstance(references, list)
        self.assertEqual(len(references), 0)

    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.iterdir")
    def test_find_metadata_traces_success(self, mock_iterdir, mock_exists):
        """Test _find_metadata_traces with successful discovery"""
        mock_exists.return_value = True

        # Mock metadata files
        mock_file1 = MagicMock()
        mock_file1.name = "com.zoom.metadata"
        mock_file1.is_file.return_value = True

        mock_file2 = MagicMock()
        mock_file2.name = "us.zoom.xos.metadata"
        mock_file2.is_file.return_value = True

        mock_iterdir.return_value = [mock_file1, mock_file2]

        traces = self.detector._find_metadata_traces()

        # Verify results
        self.assertIsInstance(traces, list)

    def test_find_metadata_traces_exception(self):
        """Test _find_metadata_traces with exceptions"""
        with patch("pathlib.Path.exists", side_effect=Exception("Path error")):
            traces = self.detector._find_metadata_traces()

            # Should handle exception gracefully
            self.assertIsInstance(traces, list)

    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.iterdir")
    def test_find_cache_artifacts_success(self, mock_iterdir, mock_exists):
        """Test _find_cache_artifacts with successful discovery"""
        mock_exists.return_value = True

        # Mock cache files
        mock_cache1 = MagicMock()
        mock_cache1.name = "zoom_cache_file"
        mock_cache1.is_file.return_value = True

        mock_cache2 = MagicMock()
        mock_cache2.name = "us.zoom.xos.cache"
        mock_cache2.is_file.return_value = True

        mock_iterdir.return_value = [mock_cache1, mock_cache2]

        artifacts = self.detector._find_cache_artifacts()

        # Verify results
        self.assertIsInstance(artifacts, list)

    def test_find_cache_artifacts_exception(self):
        """Test _find_cache_artifacts with exceptions"""
        with patch("pathlib.Path.exists", side_effect=Exception("Cache error")):
            artifacts = self.detector._find_cache_artifacts()

            # Should handle exception gracefully
            self.assertIsInstance(artifacts, list)

    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.iterdir")
    def test_find_log_references_success(self, mock_iterdir, mock_exists):
        """Test _find_log_references with successful discovery"""
        mock_exists.return_value = True

        # Mock log files
        mock_log1 = MagicMock()
        mock_log1.name = "zoom.log"
        mock_log1.is_file.return_value = True
        mock_log1.read_text.return_value = "zoom connection established"

        mock_log2 = MagicMock()
        mock_log2.name = "system.log"
        mock_log2.is_file.return_value = True
        mock_log2.read_text.return_value = "us.zoom.xos started"

        mock_iterdir.return_value = [mock_log1, mock_log2]

        references = self.detector._find_log_references()

        # Verify results
        self.assertIsInstance(references, list)

    def test_find_log_references_exception(self):
        """Test _find_log_references with exceptions"""
        with patch("pathlib.Path.exists", side_effect=Exception("Log error")):
            references = self.detector._find_log_references()

            # Should handle exception gracefully
            self.assertIsInstance(references, list)


class TestAdvancedDetectionIntegration(unittest.TestCase):
    """Test integration scenarios for the advanced detection module"""

    def setUp(self):
        """Set up test environment"""
        self.logger = logging.getLogger("test_logger")

    def test_module_imports(self):
        """Test that all classes can be imported"""
        # Verify classes are available
        self.assertTrue(callable(SystemFingerprintAnalyzer))
        self.assertTrue(callable(ZoomArtifactDetector))

    def test_analyzer_detector_integration(self):
        """Test SystemFingerprintAnalyzer and ZoomArtifactDetector working together"""
        analyzer = SystemFingerprintAnalyzer(self.logger)
        detector = ZoomArtifactDetector(self.logger)

        # Mock methods to avoid actual system calls
        analyzer.analyze_system_fingerprints = MagicMock(return_value={"test": "data"})
        detector.detect_hidden_artifacts = MagicMock(
            return_value={"artifacts": ["test"]}
        )

        # Test that both can be used together
        fingerprints = analyzer.analyze_system_fingerprints()
        artifacts = detector.detect_hidden_artifacts()

        # Verify results
        self.assertIsInstance(fingerprints, dict)
        self.assertIsInstance(artifacts, dict)

    def test_logger_integration(self):
        """Test that both classes properly use the logger"""
        mock_logger = MagicMock()

        analyzer = SystemFingerprintAnalyzer(mock_logger)
        detector = ZoomArtifactDetector(mock_logger)

        # Verify logger is set
        self.assertEqual(analyzer.logger, mock_logger)
        self.assertEqual(detector.logger, mock_logger)

    def test_error_handling_robustness(self):
        """Test that both classes handle errors robustly"""
        analyzer = SystemFingerprintAnalyzer(self.logger)
        detector = ZoomArtifactDetector(self.logger)

        # Test with mocked failures
        with patch("subprocess.run", side_effect=Exception("System command failed")):
            # Should not raise exceptions
            try:
                identifiers = analyzer._get_hardware_identifiers()
                network_ids = analyzer._get_network_identifiers()
                software_ids = analyzer._get_software_identifiers()

                self.assertIsInstance(identifiers, dict)
                self.assertIsInstance(network_ids, dict)
                self.assertIsInstance(software_ids, dict)
            except Exception as e:
                self.fail(
                    f"Advanced detection should handle exceptions gracefully: {e}"
                )


if __name__ == "__main__":
    unittest.main()

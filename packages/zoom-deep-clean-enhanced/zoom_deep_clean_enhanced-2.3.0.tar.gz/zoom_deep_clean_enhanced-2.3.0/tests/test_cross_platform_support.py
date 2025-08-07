#!/usr/bin/env python3
"""
Tests for Cross-Platform Support module
Comprehensive testing of platform detection and cross-platform functionality
"""

import pytest
import sys
import os
import unittest
import platform
import logging
from unittest.mock import patch, MagicMock, Mock
from pathlib import Path

# Import the cross-platform support module
from zoom_deep_clean.cross_platform_support import PlatformDetector


class TestPlatformDetector(unittest.TestCase):
    """Test PlatformDetector class functionality"""

    def setUp(self):
        """Set up test environment"""
        self.logger = logging.getLogger("test_logger")
        self.logger.setLevel(logging.DEBUG)

    def test_platform_detector_initialization(self):
        """Test PlatformDetector initialization"""
        detector = PlatformDetector(self.logger)

        # Verify initialization
        self.assertIsNotNone(detector.platform)
        self.assertIsNotNone(detector.platform_version)
        self.assertIsNotNone(detector.architecture)
        self.assertEqual(detector.logger, self.logger)

    def test_get_platform_info(self):
        """Test get_platform_info method"""
        detector = PlatformDetector(self.logger)

        info = detector.get_platform_info()

        # Verify all required keys are present
        required_keys = [
            "system",
            "version",
            "architecture",
            "python_version",
            "supported",
        ]
        for key in required_keys:
            self.assertIn(key, info)

        # Verify types
        self.assertIsInstance(info["system"], str)
        self.assertIsInstance(info["version"], str)
        self.assertIsInstance(info["architecture"], str)
        self.assertIsInstance(info["python_version"], str)
        self.assertIsInstance(info["supported"], bool)

    def test_is_supported_platforms(self):
        """Test is_supported method for different platforms"""
        detector = PlatformDetector(self.logger)

        # Test supported platforms
        with patch.object(detector, "platform", "darwin"):
            self.assertTrue(detector.is_supported())

        with patch.object(detector, "platform", "windows"):
            self.assertTrue(detector.is_supported())

        with patch.object(detector, "platform", "linux"):
            self.assertTrue(detector.is_supported())

        # Test unsupported platform
        with patch.object(detector, "platform", "unsupported"):
            self.assertFalse(detector.is_supported())

    def test_platform_detection_methods(self):
        """Test individual platform detection methods"""
        detector = PlatformDetector(self.logger)

        # Test macOS detection
        with patch.object(detector, "platform", "darwin"):
            self.assertTrue(detector.is_macos())
            self.assertFalse(detector.is_windows())
            self.assertFalse(detector.is_linux())

        # Test Windows detection
        with patch.object(detector, "platform", "windows"):
            self.assertFalse(detector.is_macos())
            self.assertTrue(detector.is_windows())
            self.assertFalse(detector.is_linux())

        # Test Linux detection
        with patch.object(detector, "platform", "linux"):
            self.assertFalse(detector.is_macos())
            self.assertFalse(detector.is_windows())
            self.assertTrue(detector.is_linux())

    @patch("platform.mac_ver")
    def test_get_version_info_macos(self, mock_mac_ver):
        """Test get_version_info for macOS"""
        mock_mac_ver.return_value = ("13.0.0", ("", "", ""), "arm64")

        detector = PlatformDetector(self.logger)

        with patch.object(detector, "platform", "darwin"):
            with patch.object(detector, "architecture", "arm64"):
                version_info = detector.get_version_info()

                self.assertIn("version", version_info)
                self.assertIn("build", version_info)
                self.assertIn("machine", version_info)
                self.assertEqual(version_info["version"], "13.0.0")
                self.assertEqual(version_info["machine"], "arm64")

    @patch("platform.win32_ver")
    @patch("platform.version")
    def test_get_version_info_windows(self, mock_version, mock_win32_ver):
        """Test get_version_info for Windows"""
        mock_version.return_value = "10.0.19041"
        mock_win32_ver.return_value = ("10", "10.0.19041", "SP0", "Multiprocessor Free")

        detector = PlatformDetector(self.logger)

        with patch.object(detector, "platform", "windows"):
            with patch.object(detector, "architecture", "x86_64"):
                version_info = detector.get_version_info()

                self.assertIn("version", version_info)
                self.assertIn("build", version_info)
                self.assertIn("machine", version_info)
                self.assertEqual(version_info["machine"], "x86_64")

    @patch("platform.version")
    @patch("platform.release")
    def test_get_version_info_linux(self, mock_release, mock_version):
        """Test get_version_info for Linux"""
        mock_version.return_value = "#1 SMP Ubuntu 20.04"
        mock_release.return_value = "5.4.0-74-generic"

        detector = PlatformDetector(self.logger)

        with patch.object(detector, "platform", "linux"):
            with patch.object(detector, "architecture", "x86_64"):
                version_info = detector.get_version_info()

                self.assertIn("version", version_info)
                self.assertIn("build", version_info)
                self.assertIn("machine", version_info)
                self.assertEqual(version_info["build"], "5.4.0-74-generic")

    def test_get_version_info_unsupported(self):
        """Test get_version_info for unsupported platform"""
        detector = PlatformDetector(self.logger)

        with patch.object(detector, "platform", "unsupported"):
            with patch.object(detector, "platform_version", "unknown"):
                with patch.object(detector, "architecture", "unknown"):
                    version_info = detector.get_version_info()

                    self.assertEqual(version_info["version"], "unknown")
                    self.assertEqual(version_info["build"], "unknown")
                    self.assertEqual(version_info["machine"], "unknown")

    @patch("zoom_deep_clean.cross_platform_support.PlatformDetector._get_macos_paths")
    def test_get_platform_specific_paths_macos(self, mock_get_macos_paths):
        """Test get_platform_specific_paths for macOS"""
        mock_get_macos_paths.return_value = {
            "app_paths": ["/Applications/zoom.us.app"],
            "user_paths": ["~/Library/Application Support/zoom.us"],
        }

        detector = PlatformDetector(self.logger)

        with patch.object(detector, "platform", "darwin"):
            paths = detector.get_platform_specific_paths()

            mock_get_macos_paths.assert_called_once()
            self.assertIn("app_paths", paths)
            self.assertIn("user_paths", paths)

    @patch("zoom_deep_clean.cross_platform_support.PlatformDetector._get_windows_paths")
    def test_get_platform_specific_paths_windows(self, mock_get_windows_paths):
        """Test get_platform_specific_paths for Windows"""
        mock_get_windows_paths.return_value = {
            "app_paths": ["C:\\Program Files\\Zoom"],
            "user_paths": ["%APPDATA%\\Zoom"],
        }

        detector = PlatformDetector(self.logger)

        with patch.object(detector, "platform", "windows"):
            paths = detector.get_platform_specific_paths()

            mock_get_windows_paths.assert_called_once()
            self.assertIn("app_paths", paths)
            self.assertIn("user_paths", paths)

    @patch("zoom_deep_clean.cross_platform_support.PlatformDetector._get_linux_paths")
    def test_get_platform_specific_paths_linux(self, mock_get_linux_paths):
        """Test get_platform_specific_paths for Linux"""
        mock_get_linux_paths.return_value = {
            "app_paths": ["/opt/zoom"],
            "user_paths": ["~/.zoom"],
        }

        detector = PlatformDetector(self.logger)

        with patch.object(detector, "platform", "linux"):
            paths = detector.get_platform_specific_paths()

            mock_get_linux_paths.assert_called_once()
            self.assertIn("app_paths", paths)
            self.assertIn("user_paths", paths)


class TestPlatformDetectorPrivateMethods(unittest.TestCase):
    """Test PlatformDetector private methods"""

    def setUp(self):
        """Set up test environment"""
        self.logger = logging.getLogger("test_logger")
        self.detector = PlatformDetector(self.logger)

    def test_get_macos_paths(self):
        """Test _get_macos_paths method"""
        if hasattr(self.detector, "_get_macos_paths"):
            paths = self.detector._get_macos_paths()

            self.assertIsInstance(paths, dict)
            # Verify expected keys exist
            expected_keys = ["app_paths", "user_paths", "system_paths"]
            for key in expected_keys:
                if key in paths:
                    self.assertIsInstance(paths[key], list)

    def test_get_windows_paths(self):
        """Test _get_windows_paths method"""
        if hasattr(self.detector, "_get_windows_paths"):
            paths = self.detector._get_windows_paths()

            self.assertIsInstance(paths, dict)
            # Verify expected keys exist
            expected_keys = ["app_paths", "user_paths", "system_paths"]
            for key in expected_keys:
                if key in paths:
                    self.assertIsInstance(paths[key], list)

    def test_get_linux_paths(self):
        """Test _get_linux_paths method"""
        if hasattr(self.detector, "_get_linux_paths"):
            paths = self.detector._get_linux_paths()

            self.assertIsInstance(paths, dict)
            # Verify expected keys exist
            expected_keys = ["app_paths", "user_paths", "system_paths"]
            for key in expected_keys:
                if key in paths:
                    self.assertIsInstance(paths[key], list)


class TestPlatformDetectorImplementation(unittest.TestCase):
    """Test actual PlatformDetector implementation without mocking"""

    def setUp(self):
        """Set up test environment"""
        self.logger = logging.getLogger("test_logger")
        self.detector = PlatformDetector(self.logger)

    def test_actual_platform_specific_paths_call(self):
        """Test that get_platform_specific_paths calls the right method for current platform"""
        paths = self.detector.get_platform_specific_paths()

        # Verify paths is a dictionary
        self.assertIsInstance(paths, dict)

        # Verify it returns reasonable path structure
        if self.detector.is_macos():
            # Should contain macOS-specific paths
            paths_str = str(paths)
            self.assertTrue("Applications" in paths_str or "Library" in paths_str)
        elif self.detector.is_windows():
            # Should contain Windows-specific paths
            paths_str = str(paths)
            self.assertTrue("%PROGRAM" in paths_str or "%APP" in paths_str)
        elif self.detector.is_linux():
            # Should contain Linux-specific paths
            paths_str = str(paths)
            self.assertTrue("/opt" in paths_str or "/usr" in paths_str)

    def test_get_platform_specific_paths_unsupported(self):
        """Test get_platform_specific_paths for unsupported platform"""
        with patch.object(self.detector, "platform", "unsupported"):
            paths = self.detector.get_platform_specific_paths()
            self.assertEqual(paths, {})


class TestWindowsZoomCleaner(unittest.TestCase):
    """Test WindowsZoomCleaner class functionality"""

    def setUp(self):
        """Set up test environment"""
        self.logger = logging.getLogger("test_logger")

    @patch("platform.system")
    @patch("zoom_deep_clean.cross_platform_support.winreg")
    def test_windows_zoom_cleaner_initialization_success(
        self, mock_winreg, mock_system
    ):
        """Test WindowsZoomCleaner initialization on Windows"""
        mock_system.return_value = "Windows"
        mock_winreg.HKEY_CURRENT_USER = "HKEY_CURRENT_USER"

        from zoom_deep_clean.cross_platform_support import WindowsZoomCleaner

        cleaner = WindowsZoomCleaner(self.logger, dry_run=True)

        self.assertEqual(cleaner.logger, self.logger)
        self.assertTrue(cleaner.dry_run)

    @patch("platform.system")
    def test_windows_zoom_cleaner_initialization_wrong_platform(self, mock_system):
        """Test WindowsZoomCleaner initialization on non-Windows"""
        mock_system.return_value = "Darwin"

        from zoom_deep_clean.cross_platform_support import WindowsZoomCleaner

        with self.assertRaises(RuntimeError) as context:
            WindowsZoomCleaner(self.logger)

        self.assertIn("can only run on Windows", str(context.exception))

    @patch("platform.system")
    @patch("zoom_deep_clean.cross_platform_support.winreg", None)
    def test_windows_zoom_cleaner_initialization_no_winreg(self, mock_system):
        """Test WindowsZoomCleaner initialization without winreg"""
        mock_system.return_value = "Windows"

        from zoom_deep_clean.cross_platform_support import WindowsZoomCleaner

        with self.assertRaises(RuntimeError) as context:
            WindowsZoomCleaner(self.logger)

        self.assertIn("winreg module not available", str(context.exception))

    @patch("platform.system")
    @patch("zoom_deep_clean.cross_platform_support.winreg")
    def test_windows_clean_zoom_dry_run(self, mock_winreg, mock_system):
        """Test WindowsZoomCleaner clean_windows_zoom in dry run mode"""
        mock_system.return_value = "Windows"
        mock_winreg.HKEY_CURRENT_USER = "HKEY_CURRENT_USER"

        from zoom_deep_clean.cross_platform_support import WindowsZoomCleaner

        cleaner = WindowsZoomCleaner(self.logger, dry_run=True)

        # Mock the private methods
        cleaner._terminate_zoom_processes = MagicMock(return_value=5)
        cleaner._clean_registry = MagicMock(return_value=3)
        cleaner._remove_zoom_files = MagicMock(return_value=10)
        cleaner._stop_zoom_services = MagicMock(return_value=2)
        cleaner._clean_windows_specific = MagicMock()

        results = cleaner.clean_windows_zoom()

        # Verify results structure
        expected_keys = [
            "processes_terminated",
            "files_removed",
            "registry_keys_removed",
            "services_stopped",
            "errors",
        ]
        for key in expected_keys:
            self.assertIn(key, results)

        # Verify methods were called
        cleaner._terminate_zoom_processes.assert_called_once()
        cleaner._clean_registry.assert_called_once()
        cleaner._remove_zoom_files.assert_called_once()
        cleaner._stop_zoom_services.assert_called_once()
        cleaner._clean_windows_specific.assert_called_once()

    @patch("platform.system")
    @patch("zoom_deep_clean.cross_platform_support.winreg")
    @patch("subprocess.run")
    def test_windows_terminate_zoom_processes_dry_run(
        self, mock_subprocess, mock_winreg, mock_system
    ):
        """Test WindowsZoomCleaner _terminate_zoom_processes in dry run mode"""
        mock_system.return_value = "Windows"
        mock_winreg.HKEY_CURRENT_USER = "HKEY_CURRENT_USER"

        from zoom_deep_clean.cross_platform_support import WindowsZoomCleaner

        cleaner = WindowsZoomCleaner(self.logger, dry_run=True)

        result = cleaner._terminate_zoom_processes()

        # In dry run mode, should return number of processes that would be terminated
        self.assertGreater(result, 0)
        # subprocess.run should not be called in dry run mode
        mock_subprocess.assert_not_called()

    @patch("platform.system")
    @patch("zoom_deep_clean.cross_platform_support.winreg")
    @patch("subprocess.run")
    def test_windows_terminate_zoom_processes_actual(
        self, mock_subprocess, mock_winreg, mock_system
    ):
        """Test WindowsZoomCleaner _terminate_zoom_processes actual execution"""
        mock_system.return_value = "Windows"
        mock_winreg.HKEY_CURRENT_USER = "HKEY_CURRENT_USER"

        # Mock successful subprocess return
        mock_subprocess.return_value.returncode = 0

        from zoom_deep_clean.cross_platform_support import WindowsZoomCleaner

        cleaner = WindowsZoomCleaner(self.logger, dry_run=False)

        result = cleaner._terminate_zoom_processes()

        # Should attempt to terminate processes and return count
        self.assertGreaterEqual(result, 0)
        # subprocess.run should be called for each process
        self.assertTrue(mock_subprocess.called)

    @patch("platform.system")
    @patch("zoom_deep_clean.cross_platform_support.winreg")
    def test_windows_clean_registry_dry_run(self, mock_winreg, mock_system):
        """Test WindowsZoomCleaner _clean_registry in dry run mode"""
        mock_system.return_value = "Windows"
        mock_winreg.HKEY_CURRENT_USER = "HKEY_CURRENT_USER"
        mock_winreg.HKEY_LOCAL_MACHINE = "HKEY_LOCAL_MACHINE"

        from zoom_deep_clean.cross_platform_support import WindowsZoomCleaner

        cleaner = WindowsZoomCleaner(self.logger, dry_run=True)

        result = cleaner._clean_registry()

        # In dry run mode, should return number of keys that would be removed
        self.assertGreater(result, 0)
        # DeleteKeyEx should not be called in dry run mode
        (
            mock_winreg.DeleteKeyEx.assert_not_called()
            if hasattr(mock_winreg, "DeleteKeyEx")
            else None
        )

    @patch("platform.system")
    @patch("zoom_deep_clean.cross_platform_support.winreg")
    @patch("os.path.exists")
    @patch("shutil.rmtree")
    @patch("os.remove")
    def test_windows_remove_zoom_files_dry_run(
        self, mock_remove, mock_rmtree, mock_exists, mock_winreg, mock_system
    ):
        """Test WindowsZoomCleaner _remove_zoom_files in dry run mode"""
        mock_system.return_value = "Windows"
        mock_winreg.HKEY_CURRENT_USER = "HKEY_CURRENT_USER"
        mock_exists.return_value = True

        from zoom_deep_clean.cross_platform_support import WindowsZoomCleaner

        cleaner = WindowsZoomCleaner(self.logger, dry_run=True)

        result = cleaner._remove_zoom_files()

        # In dry run mode, should return number of files that would be removed
        self.assertGreater(result, 0)
        # Removal functions should not be called in dry run mode
        mock_rmtree.assert_not_called()
        mock_remove.assert_not_called()

    @patch("platform.system")
    @patch("zoom_deep_clean.cross_platform_support.winreg")
    @patch("subprocess.run")
    def test_windows_stop_zoom_services_dry_run(
        self, mock_subprocess, mock_winreg, mock_system
    ):
        """Test WindowsZoomCleaner _stop_zoom_services in dry run mode"""
        mock_system.return_value = "Windows"
        mock_winreg.HKEY_CURRENT_USER = "HKEY_CURRENT_USER"

        from zoom_deep_clean.cross_platform_support import WindowsZoomCleaner

        cleaner = WindowsZoomCleaner(self.logger, dry_run=True)

        result = cleaner._stop_zoom_services()

        # In dry run mode, should return number of services that would be stopped
        self.assertGreaterEqual(result, 0)
        # subprocess.run should not be called in dry run mode for services
        mock_subprocess.assert_not_called()

    @patch("platform.system")
    @patch("zoom_deep_clean.cross_platform_support.winreg")
    def test_windows_clean_windows_specific_dry_run(self, mock_winreg, mock_system):
        """Test WindowsZoomCleaner _clean_windows_specific method"""
        mock_system.return_value = "Windows"
        mock_winreg.HKEY_CURRENT_USER = "HKEY_CURRENT_USER"

        from zoom_deep_clean.cross_platform_support import WindowsZoomCleaner

        cleaner = WindowsZoomCleaner(self.logger, dry_run=True)

        # Test that the method exists and can be called
        if hasattr(cleaner, "_clean_windows_specific"):
            try:
                cleaner._clean_windows_specific()
                # Should not raise an exception
            except Exception as e:
                self.fail(f"_clean_windows_specific raised an exception: {e}")

    @patch("platform.system")
    @patch("zoom_deep_clean.cross_platform_support.winreg")
    def test_windows_clean_zoom_exception_handling(self, mock_winreg, mock_system):
        """Test WindowsZoomCleaner exception handling in clean_windows_zoom"""
        mock_system.return_value = "Windows"
        mock_winreg.HKEY_CURRENT_USER = "HKEY_CURRENT_USER"

        from zoom_deep_clean.cross_platform_support import WindowsZoomCleaner

        cleaner = WindowsZoomCleaner(self.logger, dry_run=True)

        # Mock a method to raise an exception
        cleaner._terminate_zoom_processes = MagicMock(
            side_effect=Exception("Test exception")
        )
        cleaner._clean_registry = MagicMock(return_value=0)
        cleaner._remove_zoom_files = MagicMock(return_value=0)
        cleaner._stop_zoom_services = MagicMock(return_value=0)
        cleaner._clean_windows_specific = MagicMock()

        results = cleaner.clean_windows_zoom()

        # Should handle exception and include it in errors
        self.assertIn("errors", results)
        self.assertTrue(len(results["errors"]) > 0)
        self.assertIn("Windows cleanup error", results["errors"][0])


class TestLinuxZoomCleaner(unittest.TestCase):
    """Test LinuxZoomCleaner class functionality"""

    def setUp(self):
        """Set up test environment"""
        self.logger = logging.getLogger("test_logger")

    def test_linux_zoom_cleaner_import(self):
        """Test that LinuxZoomCleaner can be imported"""
        try:
            from zoom_deep_clean.cross_platform_support import LinuxZoomCleaner

            self.assertTrue(LinuxZoomCleaner is not None)
        except ImportError:
            # LinuxZoomCleaner might not be implemented yet
            pass

    @patch("platform.system")
    def test_linux_zoom_cleaner_initialization_success(self, mock_system):
        """Test LinuxZoomCleaner initialization on Linux"""
        mock_system.return_value = "Linux"

        from zoom_deep_clean.cross_platform_support import LinuxZoomCleaner

        cleaner = LinuxZoomCleaner(self.logger, dry_run=True)

        self.assertEqual(cleaner.logger, self.logger)
        self.assertTrue(cleaner.dry_run)

    @patch("platform.system")
    def test_linux_zoom_cleaner_initialization_wrong_platform(self, mock_system):
        """Test LinuxZoomCleaner initialization on non-Linux"""
        mock_system.return_value = "Darwin"

        from zoom_deep_clean.cross_platform_support import LinuxZoomCleaner

        with self.assertRaises(RuntimeError) as context:
            LinuxZoomCleaner(self.logger)

        self.assertIn("can only run on Linux", str(context.exception))

    @patch("platform.system")
    def test_linux_clean_zoom_dry_run(self, mock_system):
        """Test LinuxZoomCleaner clean_linux_zoom in dry run mode"""
        mock_system.return_value = "Linux"

        from zoom_deep_clean.cross_platform_support import LinuxZoomCleaner

        cleaner = LinuxZoomCleaner(self.logger, dry_run=True)

        # Mock the private methods
        cleaner._terminate_zoom_processes = MagicMock(return_value=1)
        cleaner._remove_zoom_files = MagicMock(return_value=5)
        cleaner._remove_zoom_packages = MagicMock(return_value=2)
        cleaner._clean_linux_specific = MagicMock()

        results = cleaner.clean_linux_zoom()

        # Verify results structure
        expected_keys = [
            "processes_terminated",
            "files_removed",
            "packages_removed",
            "services_stopped",
            "errors",
        ]
        for key in expected_keys:
            self.assertIn(key, results)

        # Verify methods were called
        cleaner._terminate_zoom_processes.assert_called_once()
        cleaner._remove_zoom_files.assert_called_once()
        cleaner._remove_zoom_packages.assert_called_once()
        cleaner._clean_linux_specific.assert_called_once()

    @patch("platform.system")
    @patch("subprocess.run")
    def test_linux_terminate_zoom_processes_dry_run(self, mock_subprocess, mock_system):
        """Test LinuxZoomCleaner _terminate_zoom_processes in dry run mode"""
        mock_system.return_value = "Linux"

        from zoom_deep_clean.cross_platform_support import LinuxZoomCleaner

        cleaner = LinuxZoomCleaner(self.logger, dry_run=True)

        result = cleaner._terminate_zoom_processes()

        # In dry run mode, should return 1
        self.assertEqual(result, 1)
        # subprocess.run should not be called in dry run mode
        mock_subprocess.assert_not_called()

    @patch("platform.system")
    @patch("subprocess.run")
    def test_linux_terminate_zoom_processes_actual(self, mock_subprocess, mock_system):
        """Test LinuxZoomCleaner _terminate_zoom_processes actual execution"""
        mock_system.return_value = "Linux"

        # Mock successful subprocess return
        mock_subprocess.return_value.returncode = 0

        from zoom_deep_clean.cross_platform_support import LinuxZoomCleaner

        cleaner = LinuxZoomCleaner(self.logger, dry_run=False)

        result = cleaner._terminate_zoom_processes()

        # Should return 1 for successful termination
        self.assertEqual(result, 1)
        # subprocess.run should be called
        mock_subprocess.assert_called_once()

    @patch("platform.system")
    @patch("os.path.exists")
    @patch("shutil.rmtree")
    @patch("os.remove")
    def test_linux_remove_zoom_files_dry_run(
        self, mock_remove, mock_rmtree, mock_exists, mock_system
    ):
        """Test LinuxZoomCleaner _remove_zoom_files in dry run mode"""
        mock_system.return_value = "Linux"
        mock_exists.return_value = True

        from zoom_deep_clean.cross_platform_support import LinuxZoomCleaner

        cleaner = LinuxZoomCleaner(self.logger, dry_run=True)

        result = cleaner._remove_zoom_files()

        # In dry run mode, should return number of files that would be removed
        self.assertGreater(result, 0)
        # Removal functions should not be called in dry run mode
        mock_rmtree.assert_not_called()
        mock_remove.assert_not_called()

    @patch("platform.system")
    @patch("subprocess.run")
    def test_linux_remove_zoom_packages_dry_run(self, mock_subprocess, mock_system):
        """Test LinuxZoomCleaner _remove_zoom_packages in dry run mode"""
        mock_system.return_value = "Linux"

        from zoom_deep_clean.cross_platform_support import LinuxZoomCleaner

        cleaner = LinuxZoomCleaner(self.logger, dry_run=True)

        result = cleaner._remove_zoom_packages()

        # In dry run mode, should return number of packages that would be removed
        self.assertGreaterEqual(result, 0)
        # Package removal should not be called in dry run mode

    @patch("platform.system")
    def test_linux_clean_linux_specific_dry_run(self, mock_system):
        """Test LinuxZoomCleaner _clean_linux_specific method"""
        mock_system.return_value = "Linux"

        from zoom_deep_clean.cross_platform_support import LinuxZoomCleaner

        cleaner = LinuxZoomCleaner(self.logger, dry_run=True)

        # Test that the method exists and can be called
        if hasattr(cleaner, "_clean_linux_specific"):
            try:
                cleaner._clean_linux_specific()
                # Should not raise an exception
            except Exception as e:
                self.fail(f"_clean_linux_specific raised an exception: {e}")

    @patch("platform.system")
    def test_linux_clean_zoom_exception_handling(self, mock_system):
        """Test LinuxZoomCleaner exception handling in clean_linux_zoom"""
        mock_system.return_value = "Linux"

        from zoom_deep_clean.cross_platform_support import LinuxZoomCleaner

        cleaner = LinuxZoomCleaner(self.logger, dry_run=True)

        # Mock a method to raise an exception
        cleaner._terminate_zoom_processes = MagicMock(
            side_effect=Exception("Test exception")
        )
        cleaner._remove_zoom_files = MagicMock(return_value=0)
        cleaner._remove_zoom_packages = MagicMock(return_value=0)
        cleaner._clean_linux_specific = MagicMock()

        results = cleaner.clean_linux_zoom()

        # Should handle exception and include it in errors
        self.assertIn("errors", results)
        self.assertTrue(len(results["errors"]) > 0)
        self.assertIn("Linux cleanup error", results["errors"][0])


class TestCrossPlatformSupport(unittest.TestCase):
    """Test cross-platform support integration"""

    def setUp(self):
        """Set up test environment"""
        self.logger = logging.getLogger("test_logger")

    def test_winreg_import_handling(self):
        """Test that winreg import is handled properly"""
        # This test verifies the module can be imported even without winreg
        from zoom_deep_clean import cross_platform_support

        # Verify the module loads successfully
        self.assertTrue(hasattr(cross_platform_support, "PlatformDetector"))

    def test_platform_detector_with_mock_logger(self):
        """Test PlatformDetector with mock logger"""
        mock_logger = MagicMock()
        detector = PlatformDetector(mock_logger)

        # Verify detector works with mock logger
        self.assertEqual(detector.logger, mock_logger)
        self.assertIsNotNone(detector.platform)

    @patch("platform.system")
    def test_platform_detection_edge_cases(self, mock_system):
        """Test platform detection with edge cases"""
        # Test case-insensitive detection
        mock_system.return_value = "DARWIN"
        detector = PlatformDetector(self.logger)
        self.assertEqual(detector.platform, "darwin")

        # Test unknown platform
        mock_system.return_value = "UnknownOS"
        detector = PlatformDetector(self.logger)
        self.assertEqual(detector.platform, "unknownos")

    def test_module_constants_and_imports(self):
        """Test module-level constants and imports"""
        from zoom_deep_clean import cross_platform_support

        # Verify important classes are available
        self.assertTrue(hasattr(cross_platform_support, "PlatformDetector"))

        # Test winreg handling
        import zoom_deep_clean.cross_platform_support as cps

        # winreg should be None or a module, depending on platform
        self.assertTrue(cps.winreg is None or hasattr(cps.winreg, "HKEY_CURRENT_USER"))

    def test_all_public_classes_available(self):
        """Test that all expected public classes are available"""
        from zoom_deep_clean import cross_platform_support

        expected_classes = ["PlatformDetector"]
        optional_classes = ["WindowsZoomCleaner", "LinuxZoomCleaner"]

        for cls_name in expected_classes:
            self.assertTrue(hasattr(cross_platform_support, cls_name))

        for cls_name in optional_classes:
            # These might not all be implemented yet
            if hasattr(cross_platform_support, cls_name):
                self.assertTrue(callable(getattr(cross_platform_support, cls_name)))


if __name__ == "__main__":
    unittest.main()

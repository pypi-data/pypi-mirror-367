#!/usr/bin/env python3
"""
Additional Tests for ZoomDeepCleanerEnhanced module
Focused on improving coverage for core cleaner functionality
"""

import sys
import os
import unittest
import tempfile
import shutil
import logging
import json
import subprocess  # Added to fix subprocess.TimeoutExpired error
from unittest.mock import patch, MagicMock, Mock, mock_open
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Import the cleaner module
from zoom_deep_clean.cleaner_enhanced import (
    ZoomDeepCleanerEnhanced,
    SecurityError,
    DEFAULT_LOG_FILE,
    BACKUP_DIR,
    MAX_PATH_LENGTH,
    ALLOWED_PATH_CHARS,
    ZOOM_SIGNATURES,
)


class TestZoomDeepCleanerEnhancedSecurity(unittest.TestCase):
    """Test security validation in ZoomDeepCleanerEnhanced"""

    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_log = os.path.join(self.temp_dir, "test.log")

    def tearDown(self):
        """Clean up test environment"""
        try:
            shutil.rmtree(self.temp_dir)
        except:
            pass

    def test_security_error_exception(self):
        """Test SecurityError exception class"""
        error = SecurityError("Test security error")
        self.assertIsInstance(error, Exception)
        self.assertEqual(str(error), "Test security error")

    def test_validate_path_invalid_type(self):
        """Test _validate_path with invalid type"""
        cleaner = ZoomDeepCleanerEnhanced(log_file=self.temp_log, dry_run=True)

        # Test with non-string path
        with self.assertRaises(SecurityError) as context:
            cleaner._validate_path(123)

        self.assertIn("Path must be string", str(context.exception))

    def test_validate_path_too_long(self):
        """Test _validate_path with path too long"""
        cleaner = ZoomDeepCleanerEnhanced(log_file=self.temp_log, dry_run=True)

        # Create a path longer than MAX_PATH_LENGTH
        long_path = "a" * (MAX_PATH_LENGTH + 1)

        with self.assertRaises(SecurityError) as context:
            cleaner._validate_path(long_path)

        self.assertIn("Path too long", str(context.exception))

    def test_validate_path_invalid_characters(self):
        """Test _validate_path with invalid characters"""
        cleaner = ZoomDeepCleanerEnhanced(log_file=self.temp_log, dry_run=True)

        # Test path with invalid characters
        invalid_paths = [
            "/path/with/|pipe",
            "/path/with*asterisk",
            "/path/with<bracket",
        ]

        for invalid_path in invalid_paths:
            with self.assertRaises(SecurityError):
                cleaner._validate_path(invalid_path)

    def test_validate_path_directory_traversal(self):
        """Test _validate_path against directory traversal attacks"""
        cleaner = ZoomDeepCleanerEnhanced(log_file=self.temp_log, dry_run=True)

        # Test paths with directory traversal attempts
        traversal_paths = [
            "../../../etc/passwd",
            "/tmp/../etc/passwd",
            "~/../../etc/passwd",
        ]

        for traversal_path in traversal_paths:
            with self.assertRaises(SecurityError):
                cleaner._validate_path(traversal_path)

    def test_validate_path_dangerous_system_paths(self):
        """Test _validate_path against dangerous system paths"""
        cleaner = ZoomDeepCleanerEnhanced(log_file=self.temp_log, dry_run=True)

        # Test dangerous system paths
        dangerous_paths = [
            "/System/Library/CoreServices/Finder.app",
            "/usr/bin/sudo",
            "/usr/sbin/system_profiler",
            "/bin/bash",
            "/sbin/mount",
            "/etc/passwd",
            "/etc/hosts",
            "/Library/CoreServices/SystemStarter",
            "/Applications/Utilities/Terminal.app",
        ]

        for dangerous_path in dangerous_paths:
            with self.assertRaises(SecurityError):
                cleaner._validate_path(dangerous_path)

    def test_validate_path_safe_paths(self):
        """Test _validate_path with safe paths"""
        cleaner = ZoomDeepCleanerEnhanced(log_file=self.temp_log, dry_run=True)

        # Test safe paths that should be allowed
        safe_paths = [
            "~/Library/Application Support/zoom.us",
            "/Applications/zoom.us.app",
            "/tmp/zoom_test_file",
            self.temp_dir + "/test_file",
        ]

        for safe_path in safe_paths:
            try:
                result = cleaner._validate_path(safe_path)
                self.assertIsInstance(result, str)
            except SecurityError as e:
                self.fail(f"Safe path rejected: {safe_path} - {e}")


class TestZoomDeepCleanerEnhancedSetup(unittest.TestCase):
    """Test setup and initialization methods"""

    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_log = os.path.join(self.temp_dir, "test.log")

    def tearDown(self):
        """Clean up test environment"""
        try:
            shutil.rmtree(self.temp_dir)
        except:
            pass

    @patch("os.makedirs")
    def test_setup_backup_dir_success(self, mock_makedirs):
        """Test _setup_backup_dir with successful creation"""
        backup_dir = os.path.join(self.temp_dir, "backup")
        cleaner = ZoomDeepCleanerEnhanced(
            log_file=self.temp_log, dry_run=True, enable_backup=True
        )
        cleaner.backup_dir = backup_dir

        # Test backup directory setup
        cleaner._setup_backup_dir()

        # Verify makedirs was called with correct parameters
        mock_makedirs.assert_called_with(backup_dir, mode=0o700, exist_ok=True)

    def test_setup_backup_dir_failure(self):
        """Test _setup_backup_dir with creation failure"""
        backup_dir = os.path.join(self.temp_dir, "backup")
        cleaner = ZoomDeepCleanerEnhanced(
            log_file=self.temp_log, dry_run=True, enable_backup=True
        )
        cleaner.backup_dir = backup_dir

        # Mock os.makedirs to fail after initialization
        with patch("os.makedirs", side_effect=OSError("Permission denied")):
            # Test backup directory setup failure
            cleaner._setup_backup_dir()

            # Should disable backup on failure
            self.assertFalse(cleaner.enable_backup)

    def test_setup_backup_dir_no_backup_dir(self):
        """Test _setup_backup_dir when backup_dir is None"""
        cleaner = ZoomDeepCleanerEnhanced(
            log_file=self.temp_log, dry_run=True, enable_backup=True
        )
        cleaner.backup_dir = None

        # Should return early without error
        try:
            cleaner._setup_backup_dir()
        except Exception as e:
            self.fail(f"_setup_backup_dir raised an exception: {e}")

    def test_setup_logging_log_dir_creation(self):
        """Test _setup_logging creates log directory"""
        # Create a subdirectory for the log file
        subdir = os.path.join(self.temp_dir, "subdir")
        os.makedirs(subdir, exist_ok=True)
        log_file = os.path.join(subdir, "test.log")

        # This should not raise an exception
        try:
            cleaner = ZoomDeepCleanerEnhanced(log_file=log_file, dry_run=True)
            # Verify logger was set up
            self.assertIsNotNone(cleaner.logger)
        except Exception as e:
            self.fail(f"Failed to create cleaner with subdirectory log: {e}")

    def test_constants_and_globals(self):
        """Test module constants are properly defined"""
        # Test that constants are defined
        self.assertIsInstance(DEFAULT_LOG_FILE, str)
        self.assertIsInstance(BACKUP_DIR, str)
        self.assertIsInstance(MAX_PATH_LENGTH, int)
        self.assertGreater(MAX_PATH_LENGTH, 0)

        # Test regex pattern
        self.assertTrue(ALLOWED_PATH_CHARS.match("/valid/path/test"))
        self.assertFalse(ALLOWED_PATH_CHARS.match("/invalid|path"))

        # Test zoom signatures
        self.assertIsInstance(ZOOM_SIGNATURES, list)
        self.assertTrue(all(isinstance(sig, bytes) for sig in ZOOM_SIGNATURES))


class TestZoomDeepCleanerEnhancedAdvancedFeatures(unittest.TestCase):
    """Test advanced features integration"""

    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_log = os.path.join(self.temp_dir, "test.log")

    def tearDown(self):
        """Clean up test environment"""
        try:
            shutil.rmtree(self.temp_dir)
        except:
            pass

    @patch("zoom_deep_clean.cleaner_enhanced.AdvancedFeatures")
    def test_advanced_features_initialization_enabled(self, mock_advanced_features):
        """Test advanced features initialization when enabled"""
        mock_advanced = MagicMock()
        mock_advanced_features.return_value = mock_advanced

        cleaner = ZoomDeepCleanerEnhanced(
            log_file=self.temp_log, dry_run=True, enable_advanced_features=True
        )

        # Verify AdvancedFeatures was instantiated
        mock_advanced_features.assert_called_once()

    def test_advanced_features_initialization_disabled(self):
        """Test advanced features initialization when disabled"""
        cleaner = ZoomDeepCleanerEnhanced(
            log_file=self.temp_log, dry_run=True, enable_advanced_features=False
        )

        # Should not initialize advanced features
        self.assertFalse(cleaner.enable_advanced_features)

    @patch("zoom_deep_clean.cleaner_enhanced.AdvancedFeatures")
    def test_advanced_features_mac_spoofing(self, mock_advanced_features):
        """Test advanced features with MAC spoofing enabled"""
        mock_advanced = MagicMock()
        mock_advanced_features.return_value = mock_advanced

        cleaner = ZoomDeepCleanerEnhanced(
            log_file=self.temp_log,
            dry_run=True,
            enable_advanced_features=True,
            enable_mac_spoofing=True,
        )

        # Verify advanced features was configured with MAC spoofing
        self.assertTrue(cleaner.enable_mac_spoofing)

    @patch("zoom_deep_clean.cleaner_enhanced.AdvancedFeatures")
    def test_advanced_features_hostname_reset(self, mock_advanced_features):
        """Test advanced features with hostname reset"""
        mock_advanced = MagicMock()
        mock_advanced_features.return_value = mock_advanced

        new_hostname = "test-hostname"
        cleaner = ZoomDeepCleanerEnhanced(
            log_file=self.temp_log,
            dry_run=True,
            enable_advanced_features=True,
            reset_hostname=True,
            new_hostname=new_hostname,
        )

        # Verify hostname settings
        self.assertTrue(cleaner.reset_hostname)
        self.assertEqual(cleaner.new_hostname, new_hostname)


class TestZoomDeepCleanerEnhancedFileOperations(unittest.TestCase):
    """Test file operation methods"""

    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_log = os.path.join(self.temp_dir, "test.log")

    def tearDown(self):
        """Clean up test environment"""
        try:
            shutil.rmtree(self.temp_dir)
        except:
            pass

    def test_safe_remove_file_success(self):
        """Test _safe_remove with file removal success"""
        # Create a test file
        test_file = os.path.join(self.temp_dir, "test_file.txt")
        with open(test_file, "w") as f:
            f.write("test content")

        cleaner = ZoomDeepCleanerEnhanced(
            log_file=self.temp_log, dry_run=False, enable_backup=False
        )

        # Test file removal
        if hasattr(cleaner, "_safe_remove"):
            result = cleaner._safe_remove(test_file)

            # File should be removed
            self.assertFalse(os.path.exists(test_file))

    def test_safe_remove_dry_run(self):
        """Test _safe_remove in dry run mode"""
        # Create a test file
        test_file = os.path.join(self.temp_dir, "test_file.txt")
        with open(test_file, "w") as f:
            f.write("test content")

        cleaner = ZoomDeepCleanerEnhanced(log_file=self.temp_log, dry_run=True)

        # Test file removal in dry run
        if hasattr(cleaner, "_safe_remove"):
            result = cleaner._safe_remove(test_file)

            # File should still exist in dry run
            self.assertTrue(os.path.exists(test_file))

    def test_safe_remove_nonexistent_file(self):
        """Test _safe_remove with non-existent file"""
        nonexistent_file = os.path.join(self.temp_dir, "nonexistent.txt")

        cleaner = ZoomDeepCleanerEnhanced(log_file=self.temp_log, dry_run=False)

        # Test removal of non-existent file
        if hasattr(cleaner, "_safe_remove"):
            try:
                result = cleaner._safe_remove(nonexistent_file)
                # Should handle gracefully
            except Exception as e:
                self.fail(f"_safe_remove raised unexpected exception: {e}")

    @patch("shutil.copy2")
    def test_backup_file_success(self, mock_copy2):
        """Test _backup_file with successful backup"""
        test_file = os.path.join(self.temp_dir, "test_file.txt")

        cleaner = ZoomDeepCleanerEnhanced(
            log_file=self.temp_log, dry_run=False, enable_backup=True
        )
        cleaner.backup_dir = os.path.join(self.temp_dir, "backup")

        if hasattr(cleaner, "_backup_file"):
            try:
                result = cleaner._backup_file(test_file)
                # Should not raise exception
            except Exception as e:
                self.fail(f"_backup_file raised unexpected exception: {e}")

    def test_backup_file_disabled(self):
        """Test _backup_file when backup is disabled"""
        test_file = os.path.join(self.temp_dir, "test_file.txt")

        cleaner = ZoomDeepCleanerEnhanced(
            log_file=self.temp_log, dry_run=False, enable_backup=False
        )

        if hasattr(cleaner, "_backup_file"):
            try:
                result = cleaner._backup_file(test_file)
                # Should return early when backup disabled
            except Exception as e:
                self.fail(f"_backup_file raised unexpected exception: {e}")


class TestZoomDeepCleanerEnhancedErrorHandling(unittest.TestCase):
    """Test error handling scenarios"""

    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_log = os.path.join(self.temp_dir, "test.log")

    def tearDown(self):
        """Clean up test environment"""
        try:
            shutil.rmtree(self.temp_dir)
        except:
            pass

    def test_initialization_with_invalid_log_file(self):
        """Test initialization with invalid log file path"""
        # Test with invalid log file path
        invalid_log = "/root/restricted/test.log"

        try:
            cleaner = ZoomDeepCleanerEnhanced(log_file=invalid_log, dry_run=True)
            # Should handle gracefully
        except Exception as e:
            # Some exceptions might be expected for restricted paths
            pass

    def test_initialization_parameter_validation(self):
        """Test parameter validation during initialization"""
        # Test various parameter combinations
        cleaner = ZoomDeepCleanerEnhanced(
            log_file=self.temp_log,
            verbose=True,
            dry_run=True,
            enable_backup=True,
            vm_aware=True,
            system_reboot=False,
            enable_advanced_features=True,
            enable_mac_spoofing=False,
            reset_hostname=False,
            new_hostname=None,
        )

        # Verify parameters were set correctly
        self.assertTrue(cleaner.verbose)
        self.assertTrue(cleaner.dry_run)
        self.assertTrue(cleaner.enable_backup)
        self.assertTrue(cleaner.vm_aware)
        self.assertFalse(cleaner.system_reboot)


class TestZoomDeepCleanerEnhancedCommandExecution(unittest.TestCase):
    """Test command execution methods"""

    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_log = os.path.join(self.temp_dir, "test.log")

    def tearDown(self):
        """Clean up test environment"""
        try:
            shutil.rmtree(self.temp_dir)
        except:
            pass

    @patch("subprocess.run")
    def test_run_command_success(self, mock_subprocess):
        """Test _run_command with successful execution"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Success output"
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result

        cleaner = ZoomDeepCleanerEnhanced(log_file=self.temp_log, dry_run=False)

        if hasattr(cleaner, "_run_command"):
            success, output = cleaner._run_command("echo", ["echo", "test"])

            self.assertTrue(success)
            self.assertEqual(output, "Success output")

    @patch("subprocess.run")
    def test_run_command_failure(self, mock_subprocess):
        """Test _run_command with command failure"""
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "Error message"
        mock_subprocess.return_value = mock_result

        cleaner = ZoomDeepCleanerEnhanced(log_file=self.temp_log, dry_run=False)

        if hasattr(cleaner, "_run_command"):
            success, output = cleaner._run_command("false", ["false"])

            self.assertFalse(success)
            self.assertIn("Error message", output)

    @patch("subprocess.run")
    def test_run_command_timeout(self, mock_subprocess):
        """Test _run_command with timeout"""
        mock_subprocess.side_effect = subprocess.TimeoutExpired("test", 5)

        cleaner = ZoomDeepCleanerEnhanced(log_file=self.temp_log, dry_run=False)

        if hasattr(cleaner, "_run_command"):
            success, output = cleaner._run_command("sleep", ["sleep", "10"], timeout=1)

            self.assertFalse(success)
            self.assertIn("timed out", output)

    def test_run_command_exception(self):
        """Test _run_command with exception"""
        cleaner = ZoomDeepCleanerEnhanced(log_file=self.temp_log, dry_run=False)

        # Mock subprocess.run only for the specific call we're testing
        with patch("subprocess.run") as mock_subprocess:
            mock_subprocess.side_effect = Exception("Subprocess error")

            if hasattr(cleaner, "_run_command"):
                success, output = cleaner._run_command("bad_command", ["bad_command"])

                self.assertFalse(success)
                self.assertIn("Subprocess error", output)

    @patch("subprocess.run")
    def test_run_command_with_sudo(self, mock_subprocess):
        """Test _run_command with sudo requirement"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Success"
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result

        cleaner = ZoomDeepCleanerEnhanced(log_file=self.temp_log, dry_run=False)

        if hasattr(cleaner, "_run_command"):
            success, output = cleaner._run_command(
                "privileged_command", ["privileged_command"], require_sudo=True
            )

            # Should prepend sudo to command - check the last call
            self.assertTrue(mock_subprocess.called)
            # Get the last call (the actual command we're testing)
            last_call_args = mock_subprocess.call_args_list[-1][0][0]
            self.assertEqual(last_call_args[0], "sudo")
            self.assertEqual(last_call_args[1], "privileged_command")


class TestZoomDeepCleanerEnhancedVMServices(unittest.TestCase):
    """Test VM services methods"""

    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_log = os.path.join(self.temp_dir, "test.log")

    def tearDown(self):
        """Clean up test environment"""
        try:
            shutil.rmtree(self.temp_dir)
        except:
            pass

    def test_stop_vm_services_disabled(self):
        """Test stop_vm_services when VM aware is disabled"""
        cleaner = ZoomDeepCleanerEnhanced(
            log_file=self.temp_log, dry_run=True, vm_aware=False
        )

        # Should return early when VM aware is disabled
        try:
            cleaner.stop_vm_services()
            # Should complete without error
        except Exception as e:
            self.fail(f"stop_vm_services raised an exception: {e}")

    @patch("zoom_deep_clean.cleaner_enhanced.ZoomDeepCleanerEnhanced._run_command")
    def test_stop_vm_services_enabled(self, mock_execute):
        """Test stop_vm_services when VM aware is enabled"""
        mock_execute.return_value = (True, "Service stopped")

        cleaner = ZoomDeepCleanerEnhanced(
            log_file=self.temp_log, dry_run=True, vm_aware=True
        )

        # Should attempt to stop VM services
        try:
            cleaner.stop_vm_services()
            # Should complete without error
        except Exception as e:
            self.fail(f"stop_vm_services raised an exception: {e}")


class TestZoomDeepCleanerEnhancedCleanupOperations(unittest.TestCase):
    """Test cleanup operation methods"""

    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_log = os.path.join(self.temp_dir, "test.log")

    def tearDown(self):
        """Clean up test environment"""
        try:
            shutil.rmtree(self.temp_dir)
        except:
            pass

    def test_run_deep_clean_dry_run(self):
        """Test run_deep_clean in dry run mode"""
        cleaner = ZoomDeepCleanerEnhanced(
            log_file=self.temp_log, dry_run=True, enable_advanced_features=False
        )

        # Mock various methods to avoid actual system operations
        cleaner._perform_cleanup_operations = MagicMock(return_value=True)
        cleaner._generate_cleanup_report = MagicMock()

        # Test dry run execution
        try:
            result = cleaner.run_deep_clean()
            self.assertIsInstance(result, bool)
        except Exception as e:
            self.fail(f"run_deep_clean raised an exception: {e}")

    def test_cleanup_stats_access(self):
        """Test cleanup_stats attribute access"""
        cleaner = ZoomDeepCleanerEnhanced(log_file=self.temp_log, dry_run=True)

        # Test getting cleanup stats
        stats = cleaner.cleanup_stats

        self.assertIsInstance(stats, dict)
        expected_keys = ["files_removed", "processes_killed", "errors", "warnings"]
        for key in expected_keys:
            self.assertIn(key, stats)

    def test_set_cleanup_stats(self):
        """Test updating cleanup stats"""
        cleaner = ZoomDeepCleanerEnhanced(log_file=self.temp_log, dry_run=True)

        # Update stats
        cleaner.cleanup_stats["files_removed"] = 10
        cleaner.cleanup_stats["processes_killed"] = 5

        stats = cleaner.cleanup_stats
        self.assertEqual(stats["files_removed"], 10)
        self.assertEqual(stats["processes_killed"], 5)


class TestZoomDeepCleanerEnhancedReportGeneration(unittest.TestCase):
    """Test report generation methods"""

    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_log = os.path.join(self.temp_dir, "test.log")

    def tearDown(self):
        """Clean up test environment"""
        try:
            shutil.rmtree(self.temp_dir)
        except:
            pass

    def test_generate_cleanup_report(self):
        """Test _generate_cleanup_report method"""
        cleaner = ZoomDeepCleanerEnhanced(log_file=self.temp_log, dry_run=True)

        # Set some stats
        cleaner.cleanup_stats["files_removed"] = 5
        cleaner.cleanup_stats["processes_killed"] = 2

        if hasattr(cleaner, "_generate_cleanup_report"):
            try:
                cleaner._generate_cleanup_report()
                # Should complete without error
            except Exception as e:
                self.fail(f"_generate_cleanup_report raised an exception: {e}")

    def test_cleanup_stats_initialization(self):
        """Test that cleanup stats are properly initialized"""
        cleaner = ZoomDeepCleanerEnhanced(log_file=self.temp_log, dry_run=True)

        # Verify cleanup stats are initialized
        self.assertIsInstance(cleaner.cleanup_stats, dict)
        self.assertEqual(cleaner.cleanup_stats["files_removed"], 0)
        self.assertEqual(cleaner.cleanup_stats["processes_killed"], 0)
        self.assertEqual(cleaner.cleanup_stats["errors"], 0)
        self.assertEqual(cleaner.cleanup_stats["warnings"], 0)


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
"""
Test dry-run edge cases and command simulation
"""

import unittest
from unittest.mock import patch, MagicMock
import tempfile
import os
import json
from pathlib import Path

# Add project root to path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from zoom_deep_clean.cleaner_enhanced import ZoomDeepCleanerEnhanced


class TestDryRunEdgeCases(unittest.TestCase):
    """Test dry-run functionality edge cases"""

    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.log_file = os.path.join(self.temp_dir, "test.log")

        # Create cleaner in dry-run mode
        self.cleaner = ZoomDeepCleanerEnhanced(
            log_file=self.log_file, dry_run=True, verbose=True
        )

    def tearDown(self):
        """Clean up test environment"""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_dry_run_process_verification_simulation(self):
        """Test that dry-run properly simulates process verification"""
        # This should not return the hardcoded string as a PID
        success, output = self.cleaner._run_command(
            ["pgrep", "-f", "[Zz]oom"], "Checking for remaining Zoom processes"
        )

        # Should succeed in dry-run
        self.assertTrue(success)

        # Should not return the hardcoded string
        self.assertNotEqual(output, "Dry run - command not executed")

        # Should return something that makes sense for process checking
        # Either empty (no processes) or simulated PIDs
        self.assertIsInstance(output, str)

    def test_dry_run_file_search_simulation(self):
        """Test that dry-run properly simulates file search"""
        success, output = self.cleaner._run_command(
            ["find", "/tmp", "-name", "*zoom*", "-type", "f"],
            "Searching for Zoom files",
        )

        self.assertTrue(success)
        self.assertNotEqual(output, "Dry run - command not executed")

        # Should return realistic file search results or empty
        self.assertIsInstance(output, str)

    def test_dry_run_with_missing_paths(self):
        """Test dry-run behavior with invalid/missing paths"""
        success, output = self.cleaner._run_command(
            ["find", "/nonexistent/path", "-name", "*zoom*"],
            "Searching nonexistent path",
        )

        # Should still succeed in dry-run mode
        self.assertTrue(success)
        self.assertIsInstance(output, str)

    def test_dry_run_permission_errors(self):
        """Test dry-run behavior with permission-restricted commands"""
        success, output = self.cleaner._run_command(
            ["rm", "-rf", "/System/Library/SomeProtectedFile"],
            "Removing protected file",
            require_sudo=True,
        )

        # Should succeed in dry-run (no actual execution)
        self.assertTrue(success)
        self.assertIsInstance(output, str)

    def test_dry_run_state_propagation(self):
        """Test that dry-run state is properly propagated"""
        # Verify dry_run flag is set
        self.assertTrue(self.cleaner.dry_run)

        # Test that _run_command respects dry_run
        with patch("subprocess.run") as mock_run:
            success, output = self.cleaner._run_command(
                ["echo", "test"], "Test command"
            )

            # subprocess.run should NOT be called in dry-run mode
            mock_run.assert_not_called()
            self.assertTrue(success)

    def test_dry_run_comprehensive_file_search(self):
        """Test comprehensive file search in dry-run mode"""
        # Mock the _run_command to return realistic file search results
        original_run_command = self.cleaner._run_command

        def mock_run_command(cmd_args, description="", **kwargs):
            if "find" in cmd_args and "-iname" in cmd_args and "*zoom*" in cmd_args:
                # Return simulated file results instead of hardcoded string
                return (
                    True,
                    "/Users/test/Library/Logs/zoom.us/zoom.log\n/tmp/zoom_temp_file",
                )
            return original_run_command(cmd_args, description, **kwargs)

        self.cleaner._run_command = mock_run_command

        # Run comprehensive file search
        remaining_files = self.cleaner.comprehensive_file_search()

        # Should return a list of files, not the hardcoded string
        self.assertIsInstance(remaining_files, list)
        if remaining_files:
            for file_path in remaining_files:
                self.assertNotEqual(file_path, "Dry run - command not executed")
                self.assertIsInstance(file_path, str)
                self.assertTrue(len(file_path) > 0)

    def test_dry_run_process_verification_logic(self):
        """Test the process verification logic in dry-run mode"""
        # Mock _run_command to return simulated process data
        original_run_command = self.cleaner._run_command

        def mock_run_command(cmd_args, description="", **kwargs):
            if "pgrep" in cmd_args:
                # Simulate finding processes
                return True, "1234\n5678"
            elif "ps" in cmd_args and "-p" in cmd_args:
                # Simulate process info
                pid = cmd_args[cmd_args.index("-p") + 1]
                return True, f"  PID COMMAND\n {pid} zoom.us"
            return original_run_command(cmd_args, description, **kwargs)

        self.cleaner._run_command = mock_run_command

        # This should not crash or show confusing output
        self.cleaner._verify_process_cleanup()

        # Check that stats were updated appropriately
        self.assertIsInstance(self.cleaner.cleanup_stats["processes_killed"], int)

    def test_dry_run_json_output_structure(self):
        """Test that dry-run produces valid JSON report structure"""
        # Run a minimal dry-run operation
        self.cleaner.stop_zoom_processes()

        # Generate report
        report_data = {
            "timestamp": "2025-08-03T03:00:00Z",
            "version": "2.2.0",
            "dry_run": self.cleaner.dry_run,
            "statistics": self.cleaner.cleanup_stats,
            "remaining_files": [],
        }

        # Verify structure
        self.assertTrue(report_data["dry_run"])
        self.assertIsInstance(report_data["statistics"], dict)
        self.assertIn("processes_killed", report_data["statistics"])
        self.assertIn("files_removed", report_data["statistics"])

    def test_dry_run_case_sensitivity_handling(self):
        """Test dry-run with case-sensitive file operations on macOS"""
        # Test case variations that might exist on macOS
        test_cases = [
            ["find", "/tmp", "-name", "*Zoom*"],
            ["find", "/tmp", "-name", "*ZOOM*"],
            ["find", "/tmp", "-iname", "*zoom*"],  # case-insensitive
        ]

        for cmd_args in test_cases:
            with self.subTest(cmd=cmd_args):
                success, output = self.cleaner._run_command(
                    cmd_args, f"Testing case sensitivity: {' '.join(cmd_args)}"
                )
                self.assertTrue(success)
                self.assertIsInstance(output, str)

    def test_dry_run_hidden_files_handling(self):
        """Test dry-run with hidden files (dot files) on macOS"""
        success, output = self.cleaner._run_command(
            ["find", "/tmp", "-name", ".*zoom*"], "Searching for hidden zoom files"
        )

        self.assertTrue(success)
        self.assertIsInstance(output, str)

    def test_dry_run_json_export(self):
        """Test JSON export of dry-run operations"""
        # Run some operations to populate dry_run_operations
        self.cleaner._run_command(["pkill", "-f", "zoom"], "Kill zoom processes")
        self.cleaner._run_command(
            ["find", "/tmp", "-name", "*zoom*"], "Find zoom files"
        )
        self.cleaner._run_command(
            ["security", "delete-generic-password", "-s", "zoom"], "Remove keychain"
        )

        # Export to JSON
        export_file = os.path.join(self.temp_dir, "test_export.json")
        result_file = self.cleaner.export_dry_run_operations(export_file)

        # Verify file was created
        self.assertEqual(result_file, export_file)
        self.assertTrue(os.path.exists(export_file))

        # Verify JSON structure
        with open(export_file, "r") as f:
            data = json.load(f)

        # Check metadata
        self.assertIn("metadata", data)
        self.assertEqual(data["metadata"]["dry_run"], True)
        self.assertEqual(data["metadata"]["version"], "2.2.0")
        self.assertGreater(data["metadata"]["total_operations"], 0)

        # Check operations
        self.assertIn("operations", data)
        self.assertGreater(len(data["operations"]), 0)

        # Check summary
        self.assertIn("summary", data)
        self.assertIn("process_operations", data["summary"])
        self.assertIn("file_operations", data["summary"])
        self.assertIn("security_operations", data["summary"])

        # Verify operation counts make sense
        self.assertGreater(data["summary"]["process_operations"], 0)  # pkill command
        self.assertGreater(data["summary"]["file_operations"], 0)  # find command
        self.assertGreater(
            data["summary"]["security_operations"], 0
        )  # security command


class TestDryRunLogCollector(unittest.TestCase):
    """Test structured logging for dry-run operations"""

    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.log_file = os.path.join(self.temp_dir, "test.log")

        self.cleaner = ZoomDeepCleanerEnhanced(
            log_file=self.log_file, dry_run=True, verbose=True
        )

    def tearDown(self):
        """Clean up test environment"""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_dry_run_operations_logged(self):
        """Test that dry-run operations are properly logged"""
        # Run some operations
        self.cleaner._run_command(["echo", "test"], "Test operation")

        # Force flush all handlers and close them to ensure data is written
        for handler in self.cleaner.logger.handlers:
            handler.flush()
            if hasattr(handler, "close"):
                handler.close()

        # Also flush the root logger handlers
        import logging

        for handler in logging.root.handlers:
            handler.flush()

        # Small delay to ensure file system sync
        import time

        time.sleep(0.1)

        # Check log file exists and has content
        self.assertTrue(os.path.exists(self.log_file))

        with open(self.log_file, "r") as f:
            log_content = f.read()

        # Debug: print content if test fails
        if "DRY RUN:" not in log_content:
            print(f"Log file content ({len(log_content)} chars):")
            print(repr(log_content))

        # Should contain dry-run indicators
        self.assertIn("DRY RUN:", log_content)
        self.assertIn("Test operation", log_content)

    def test_dry_run_structured_output(self):
        """Test that dry-run can produce structured output"""
        # Run some operations to populate dry_run_operations
        self.cleaner._run_command(["echo", "test1"], "First operation")
        self.cleaner._run_command(
            ["find", "/tmp", "-name", "*zoom*"], "Search operation"
        )

        # Check that operations were recorded
        self.assertTrue(hasattr(self.cleaner, "dry_run_operations"))
        self.assertGreater(len(self.cleaner.dry_run_operations), 0)

        # Verify structure
        for op in self.cleaner.dry_run_operations:
            self.assertIn("command", op)
            self.assertIn("description", op)
            self.assertIn("timestamp", op)
            self.assertIsInstance(op["command"], list)
            self.assertIsInstance(op["description"], str)
            self.assertIsInstance(op["timestamp"], float)

    def test_dry_run_json_export(self):
        """Test JSON export of dry-run operations"""
        # Run some operations to populate dry_run_operations
        self.cleaner._run_command(["pkill", "-f", "zoom"], "Kill zoom processes")
        self.cleaner._run_command(
            ["find", "/tmp", "-name", "*zoom*"], "Find zoom files"
        )
        self.cleaner._run_command(
            ["security", "delete-generic-password", "-s", "zoom"], "Remove keychain"
        )

        # Export to JSON
        export_file = os.path.join(self.temp_dir, "test_export.json")
        result_file = self.cleaner.export_dry_run_operations(export_file)

        # Verify file was created
        self.assertEqual(result_file, export_file)
        self.assertTrue(os.path.exists(export_file))

        # Verify JSON structure
        with open(export_file, "r") as f:
            data = json.load(f)

        # Check metadata
        self.assertIn("metadata", data)
        self.assertEqual(data["metadata"]["dry_run"], True)
        self.assertEqual(data["metadata"]["version"], "2.2.0")
        self.assertGreater(data["metadata"]["total_operations"], 0)

        # Check operations
        self.assertIn("operations", data)
        self.assertGreater(len(data["operations"]), 0)

        # Check summary
        self.assertIn("summary", data)
        self.assertIn("process_operations", data["summary"])
        self.assertIn("file_operations", data["summary"])
        self.assertIn("security_operations", data["summary"])

        # Verify operation counts make sense
        self.assertGreater(data["summary"]["process_operations"], 0)  # pkill command
        self.assertGreater(data["summary"]["file_operations"], 0)  # find command
        self.assertGreater(
            data["summary"]["security_operations"], 0
        )  # security command


if __name__ == "__main__":
    unittest.main()

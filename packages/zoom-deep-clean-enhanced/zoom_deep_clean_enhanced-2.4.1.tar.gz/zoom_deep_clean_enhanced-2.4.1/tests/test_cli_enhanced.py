import pytest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from zoom_deep_clean.cli_enhanced import main


class TestCLIBasicFunctionality:
    """Test basic CLI functionality and argument parsing"""

    def test_help_argument(self):
        """Test --help argument displays help and exits"""
        with patch("sys.argv", ["cli_enhanced.py", "--help"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            # argparse --help exits with code 2 due to our exception handling
            assert exc_info.value.code == 2

    def test_version_argument(self):
        """Test --version argument displays version and exits"""
        with patch("sys.argv", ["cli_enhanced.py", "--version"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            # argparse --version exits with code 2 due to our exception handling
            assert exc_info.value.code == 2

    @patch("zoom_deep_clean.cli_enhanced.ZoomDeepCleanerEnhanced")
    def test_dry_run_mode(self, mock_cleaner_class):
        """Test --dry-run argument execution"""
        mock_cleaner = MagicMock()
        mock_cleaner.run_deep_clean.return_value = True
        mock_cleaner.was_cancelled_by_user.return_value = False
        mock_cleaner_class.return_value = mock_cleaner

        with patch("sys.argv", ["cli_enhanced.py", "--dry-run"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0

        # Verify cleaner was called with dry_run=True
        call_args = mock_cleaner_class.call_args
        assert call_args[1]["dry_run"] is True
        mock_cleaner.run_deep_clean.assert_called_once()

    @patch("zoom_deep_clean.cli_enhanced.ZoomDeepCleanerEnhanced")
    def test_verbose_mode(self, mock_cleaner_class):
        """Test --verbose argument execution"""
        mock_cleaner = MagicMock()
        mock_cleaner.run_deep_clean.return_value = True
        mock_cleaner.was_cancelled_by_user.return_value = False
        mock_cleaner_class.return_value = mock_cleaner

        with patch("sys.argv", ["cli_enhanced.py", "--dry-run", "--verbose"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0

        # Verify cleaner was called with verbose=True
        call_args = mock_cleaner_class.call_args
        assert call_args[1]["verbose"] is True
        mock_cleaner.run_deep_clean.assert_called_once()

    @patch("zoom_deep_clean.cli_enhanced.ZoomDeepCleanerEnhanced")
    def test_verbose_short_flag(self, mock_cleaner_class):
        """Test -v short form of verbose"""
        mock_cleaner = MagicMock()
        mock_cleaner.run_deep_clean.return_value = True
        mock_cleaner.was_cancelled_by_user.return_value = False
        mock_cleaner_class.return_value = mock_cleaner

        with patch("sys.argv", ["cli_enhanced.py", "--dry-run", "-v"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0

        call_args = mock_cleaner_class.call_args
        assert call_args[1]["verbose"] is True
        mock_cleaner.run_deep_clean.assert_called_once()

    @patch("zoom_deep_clean.cli_enhanced.ZoomDeepCleanerEnhanced")
    def test_force_mode(self, mock_cleaner_class):
        """Test --force argument execution"""
        mock_cleaner = MagicMock()
        mock_cleaner.run_deep_clean.return_value = True
        mock_cleaner.was_cancelled_by_user.return_value = False
        mock_cleaner_class.return_value = mock_cleaner

        with patch("sys.argv", ["cli_enhanced.py", "--force"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0

        # Verify cleaner was called with dry_run=False
        call_args = mock_cleaner_class.call_args
        assert call_args[1]["dry_run"] is False
        mock_cleaner.run_deep_clean.assert_called_once()

    @patch("zoom_deep_clean.cli_enhanced.ZoomDeepCleanerEnhanced")
    def test_force_short_flag(self, mock_cleaner_class):
        """Test -f short form of force"""
        mock_cleaner = MagicMock()
        mock_cleaner.run_deep_clean.return_value = True
        mock_cleaner.was_cancelled_by_user.return_value = False
        mock_cleaner_class.return_value = mock_cleaner

        with patch("sys.argv", ["cli_enhanced.py", "-f"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0

        call_args = mock_cleaner_class.call_args
        assert call_args[1]["dry_run"] is False
        mock_cleaner.run_deep_clean.assert_called_once()

    @patch("zoom_deep_clean.cli_enhanced.ZoomDeepCleanerEnhanced")
    def test_no_backup_mode(self, mock_cleaner_class):
        """Test --no-backup argument execution"""
        mock_cleaner = MagicMock()
        mock_cleaner.run_deep_clean.return_value = True
        mock_cleaner.was_cancelled_by_user.return_value = False
        mock_cleaner_class.return_value = mock_cleaner

        with patch("sys.argv", ["cli_enhanced.py", "--dry-run", "--no-backup"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0

        call_args = mock_cleaner_class.call_args
        assert call_args[1]["enable_backup"] is False
        mock_cleaner.run_deep_clean.assert_called_once()

    @patch("zoom_deep_clean.cli_enhanced.ZoomDeepCleanerEnhanced")
    def test_vm_aware_mode(self, mock_cleaner_class):
        """Test --vm-aware argument execution"""
        mock_cleaner = MagicMock()
        mock_cleaner.run_deep_clean.return_value = True
        mock_cleaner.was_cancelled_by_user.return_value = False
        mock_cleaner_class.return_value = mock_cleaner

        with patch("sys.argv", ["cli_enhanced.py", "--dry-run", "--vm-aware"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0

        call_args = mock_cleaner_class.call_args
        assert call_args[1]["vm_aware"] is True
        mock_cleaner.run_deep_clean.assert_called_once()

    @patch("zoom_deep_clean.cli_enhanced.ZoomDeepCleanerEnhanced")
    def test_no_vm_mode(self, mock_cleaner_class):
        """Test --no-vm argument execution"""
        mock_cleaner = MagicMock()
        mock_cleaner.run_deep_clean.return_value = True
        mock_cleaner.was_cancelled_by_user.return_value = False
        mock_cleaner_class.return_value = mock_cleaner

        with patch("sys.argv", ["cli_enhanced.py", "--dry-run", "--no-vm"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0

        call_args = mock_cleaner_class.call_args
        assert call_args[1]["vm_aware"] is False
        mock_cleaner.run_deep_clean.assert_called_once()

    def test_system_reboot_mode(self):
        """Test --system-reboot requires --comprehensive"""
        with patch("sys.argv", ["cli_enhanced.py", "--force", "--system-reboot"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            # parser.error() exits with code 2
            assert exc_info.value.code == 2

    @patch("zoom_deep_clean.cli_enhanced.ZoomDeepCleanerEnhanced")
    def test_custom_log_file(self, mock_cleaner_class):
        """Test --log-file argument"""
        mock_cleaner = MagicMock()
        mock_cleaner.run_deep_clean.return_value = True
        mock_cleaner.was_cancelled_by_user.return_value = False
        mock_cleaner_class.return_value = mock_cleaner

        with patch(
            "sys.argv", ["cli_enhanced.py", "--dry-run", "--log-file", "/tmp/test.log"]
        ):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0

        call_args = mock_cleaner_class.call_args
        assert call_args[1]["log_file"] == "/tmp/test.log"
        mock_cleaner.run_deep_clean.assert_called_once()

    @patch("zoom_deep_clean.cli_enhanced.ZoomDeepCleanerEnhanced")
    def test_advanced_features_enabled(self, mock_cleaner_class):
        """Test --enable-advanced-features argument"""
        mock_cleaner = MagicMock()
        mock_cleaner.run_deep_clean.return_value = True
        mock_cleaner.was_cancelled_by_user.return_value = False
        mock_cleaner_class.return_value = mock_cleaner

        with patch(
            "sys.argv", ["cli_enhanced.py", "--dry-run", "--enable-advanced-features"]
        ):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0

        call_args = mock_cleaner_class.call_args
        assert call_args[1]["enable_advanced_features"] is True
        mock_cleaner.run_deep_clean.assert_called_once()

    @patch("zoom_deep_clean.cli_enhanced.ZoomDeepCleanerEnhanced")
    def test_advanced_features_disabled(self, mock_cleaner_class):
        """Test --disable-advanced-features argument"""
        mock_cleaner = MagicMock()
        mock_cleaner.run_deep_clean.return_value = True
        mock_cleaner.was_cancelled_by_user.return_value = False
        mock_cleaner_class.return_value = mock_cleaner

        with patch(
            "sys.argv", ["cli_enhanced.py", "--dry-run", "--disable-advanced-features"]
        ):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0

        call_args = mock_cleaner_class.call_args
        assert call_args[1]["enable_advanced_features"] is False
        mock_cleaner.run_deep_clean.assert_called_once()

    @patch("zoom_deep_clean.cli_enhanced.ZoomDeepCleanerEnhanced")
    def test_mac_spoofing_enabled(self, mock_cleaner_class):
        """Test --enable-mac-spoofing argument"""
        mock_cleaner = MagicMock()
        mock_cleaner.run_deep_clean.return_value = True
        mock_cleaner.was_cancelled_by_user.return_value = False
        mock_cleaner_class.return_value = mock_cleaner

        with patch(
            "sys.argv", ["cli_enhanced.py", "--dry-run", "--enable-mac-spoofing"]
        ):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0

        call_args = mock_cleaner_class.call_args
        assert call_args[1]["enable_mac_spoofing"] is True
        mock_cleaner.run_deep_clean.assert_called_once()

    @patch("zoom_deep_clean.cli_enhanced.ZoomDeepCleanerEnhanced")
    def test_hostname_reset(self, mock_cleaner_class):
        """Test --reset-hostname argument"""
        mock_cleaner = MagicMock()
        mock_cleaner.run_deep_clean.return_value = True
        mock_cleaner.was_cancelled_by_user.return_value = False
        mock_cleaner_class.return_value = mock_cleaner

        with patch("sys.argv", ["cli_enhanced.py", "--dry-run", "--reset-hostname"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0

        call_args = mock_cleaner_class.call_args
        assert call_args[1]["reset_hostname"] is True
        mock_cleaner.run_deep_clean.assert_called_once()

    @patch("zoom_deep_clean.cli_enhanced.ZoomDeepCleanerEnhanced")
    def test_custom_hostname(self, mock_cleaner_class):
        """Test --new-hostname with --reset-hostname"""
        mock_cleaner = MagicMock()
        mock_cleaner.run_deep_clean.return_value = True
        mock_cleaner.was_cancelled_by_user.return_value = False
        mock_cleaner_class.return_value = mock_cleaner

        with patch(
            "sys.argv",
            [
                "cli_enhanced.py",
                "--dry-run",
                "--reset-hostname",
                "--new-hostname",
                "test-host",
            ],
        ):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0

        call_args = mock_cleaner_class.call_args
        assert call_args[1]["new_hostname"] == "test-host"
        mock_cleaner.run_deep_clean.assert_called_once()

    @patch("zoom_deep_clean.cli_enhanced.ZoomDeepCleanerEnhanced")
    def test_combined_arguments(self, mock_cleaner_class):
        """Test multiple compatible arguments together"""
        mock_cleaner = MagicMock()
        mock_cleaner.run_deep_clean.return_value = True
        mock_cleaner.was_cancelled_by_user.return_value = False
        mock_cleaner_class.return_value = mock_cleaner

        with patch(
            "sys.argv",
            ["cli_enhanced.py", "--dry-run", "--verbose", "--no-backup", "--no-vm"],
        ):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0

        call_args = mock_cleaner_class.call_args
        assert call_args[1]["dry_run"] is True
        assert call_args[1]["verbose"] is True
        assert call_args[1]["enable_backup"] is False
        assert call_args[1]["vm_aware"] is False
        mock_cleaner.run_deep_clean.assert_called_once()


class TestCLIErrorHandling:
    """Test CLI error handling and validation"""

    def test_invalid_arguments(self):
        """Test invalid argument combinations"""
        # Test mutually exclusive arguments
        with patch("sys.argv", ["cli_enhanced.py", "--force", "--dry-run"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            # argparse exits with code 2 for argument errors
            assert exc_info.value.code == 2

    def test_hostname_without_reset_flag(self):
        """Test --new-hostname without --reset-hostname"""
        with patch(
            "sys.argv", ["cli_enhanced.py", "--dry-run", "--new-hostname", "test"]
        ):
            with pytest.raises(SystemExit) as exc_info:
                main()
            # parser.error() exits with code 2
            assert exc_info.value.code == 2

    def test_install_fresh_without_comprehensive(self):
        """Test --install-fresh without --comprehensive"""
        with patch("sys.argv", ["cli_enhanced.py", "--force", "--install-fresh"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            # parser.error() exits with code 2
            assert exc_info.value.code == 2

    def test_system_reboot_without_comprehensive(self):
        """Test --system-reboot without --comprehensive"""
        with patch("sys.argv", ["cli_enhanced.py", "--force", "--system-reboot"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            # parser.error() exits with code 2
            assert exc_info.value.code == 2

    def test_no_force_or_dry_run(self):
        """Test missing both --force and --dry-run"""
        with patch("sys.argv", ["cli_enhanced.py", "--verbose"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            # Required mutually exclusive group missing exits with code 2
            assert exc_info.value.code == 2

    @patch("zoom_deep_clean.cli_enhanced.ZoomDeepCleanerEnhanced")
    def test_cleaner_failure(self, mock_cleaner_class):
        """Test cleaner failure handling"""
        mock_cleaner = MagicMock()
        mock_cleaner.run_deep_clean.return_value = False
        mock_cleaner.was_cancelled_by_user.return_value = False
        mock_cleaner_class.return_value = mock_cleaner

        with patch("sys.argv", ["cli_enhanced.py", "--dry-run"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1

    @patch("zoom_deep_clean.cli_enhanced.ZoomDeepCleanerEnhanced")
    def test_user_cancellation(self, mock_cleaner_class):
        """Test user cancellation handling"""
        mock_cleaner = MagicMock()
        mock_cleaner.run_deep_clean.return_value = False
        mock_cleaner.was_cancelled_by_user.return_value = True
        mock_cleaner_class.return_value = mock_cleaner

        with patch("sys.argv", ["cli_enhanced.py", "--dry-run"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 130

    @patch("zoom_deep_clean.cli_enhanced.ZoomDeepCleanerEnhanced")
    def test_security_error(self, mock_cleaner_class):
        """Test security error handling"""
        from zoom_deep_clean.cleaner_enhanced import SecurityError

        mock_cleaner_class.side_effect = SecurityError("Test security error")

        with patch("sys.argv", ["cli_enhanced.py", "--dry-run"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 2

    @patch("zoom_deep_clean.cli_enhanced.ZoomDeepCleanerEnhanced")
    def test_keyboard_interrupt(self, mock_cleaner_class):
        """Test keyboard interrupt handling"""
        mock_cleaner_class.side_effect = KeyboardInterrupt()

        with patch("sys.argv", ["cli_enhanced.py", "--dry-run"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 130

    @patch("zoom_deep_clean.cli_enhanced.ZoomDeepCleanerEnhanced")
    def test_unexpected_exception(self, mock_cleaner_class):
        """Test unexpected exception handling"""
        mock_cleaner_class.side_effect = Exception("Unexpected error")

        with patch("sys.argv", ["cli_enhanced.py", "--dry-run"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1


class TestCLIIntegration:
    """Test CLI integration scenarios"""

    @patch("zoom_deep_clean.cli_enhanced.ZoomDeepCleanerEnhanced")
    def test_export_dry_run_success(self, mock_cleaner_class):
        """Test --export-dry-run functionality"""
        mock_cleaner = MagicMock()
        mock_cleaner.run_deep_clean.return_value = True
        mock_cleaner.was_cancelled_by_user.return_value = False
        mock_cleaner.export_dry_run_operations.return_value = "/tmp/export.json"
        mock_cleaner_class.return_value = mock_cleaner

        with patch(
            "sys.argv",
            ["cli_enhanced.py", "--dry-run", "--export-dry-run", "/tmp/export.json"],
        ):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0

        mock_cleaner.export_dry_run_operations.assert_called_once_with(
            "/tmp/export.json"
        )

    @patch("zoom_deep_clean.cli_enhanced.ZoomDeepCleanerEnhanced")
    def test_export_dry_run_without_dry_run_mode(self, mock_cleaner_class):
        """Test --export-dry-run without --dry-run shows warning"""
        mock_cleaner = MagicMock()
        mock_cleaner.run_deep_clean.return_value = True
        mock_cleaner.was_cancelled_by_user.return_value = False
        mock_cleaner_class.return_value = mock_cleaner

        with patch(
            "sys.argv",
            ["cli_enhanced.py", "--force", "--export-dry-run", "/tmp/export.json"],
        ):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0

    @patch("zoom_deep_clean.cli_enhanced.ZoomDeepCleanerEnhanced")
    def test_successful_completion_message(self, mock_cleaner_class):
        """Test successful completion message"""
        mock_cleaner = MagicMock()
        mock_cleaner.run_deep_clean.return_value = True
        mock_cleaner.was_cancelled_by_user.return_value = False
        mock_cleaner_class.return_value = mock_cleaner

        with patch("sys.argv", ["cli_enhanced.py", "--dry-run"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0

        mock_cleaner.run_deep_clean.assert_called_once()

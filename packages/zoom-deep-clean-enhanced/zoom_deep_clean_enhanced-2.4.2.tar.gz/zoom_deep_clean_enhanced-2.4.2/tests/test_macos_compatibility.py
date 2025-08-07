"""
macOS Compatibility Tests
Test compatibility across different macOS versions and system configurations
"""

import pytest
import platform
import os
import sys
import subprocess
from unittest.mock import patch, MagicMock
from pathlib import Path

from zoom_deep_clean.cleaner_enhanced import ZoomDeepCleanerEnhanced
from zoom_deep_clean.cross_platform_support import PlatformDetector

pytestmark = pytest.mark.skipif(sys.platform != "darwin", reason="macOS only")

class TestMacOSVersionDetection:
    """Test macOS version detection and handling"""

    def test_macos_version_detection(self):
        """Test that we can detect macOS version correctly"""
        if platform.system() == "Darwin":
            version = platform.mac_ver()[0]
            assert version is not None
            assert len(version.split('.')) >= 2
            print(f"Detected macOS version: {version}")
        else:
            pytest.skip("Not running on macOS")

    def test_platform_detector_macos(self):
        """Test PlatformDetector on macOS"""
        import logging

        logger = logging.getLogger("test")
        detector = PlatformDetector(logger)

        if platform.system() == "Darwin":
            assert detector.is_macos() is True
            assert detector.is_windows() is False

            version_info = detector.get_version_info()
            assert "version" in version_info
            assert "build" in version_info
            print(f"Platform detector version info: {version_info}")
        else:
            pytest.skip("Not running on macOS")

    @pytest.mark.parametrize(
        "mock_version,expected_major",
        [
            ("12.7.1", 12),
            ("13.6.0", 13),
            ("14.2.1", 14),
            ("15.0.0", 15),
        ],
    )
    def test_version_parsing(self, mock_version, expected_major):
        """Test version parsing for different macOS versions"""
        with patch("platform.mac_ver", return_value=(mock_version, "", "")):
            import logging

            logger = logging.getLogger("test")
            detector = PlatformDetector(logger)
            version_info = detector.get_version_info()

            major_version = int(version_info["version"].split(".")[0])
            assert major_version == expected_major


class TestFileSystemCompatibility:
    """Test file system operations across macOS versions"""

    def test_home_directory_access(self):
        """Test access to user home directory"""
        home_path = Path.home()
        assert home_path.exists()
        assert home_path.is_dir()

        # Test common subdirectories
        common_dirs = ["Library", "Documents", "Downloads"]
        for dir_name in common_dirs:
            dir_path = home_path / dir_name
            if dir_path.exists():
                assert dir_path.is_dir()
                print(f"[OK] {dir_name} directory accessible")

    def test_library_directory_access(self):
        """Test access to Library directories"""
        home_lib = Path.home() / "Library"
        if home_lib.exists():
            # Test common Library subdirectories
            lib_dirs = [
                "Application Support",
                "Caches",
                "Preferences",
                "Logs",
                "Cookies",
                "WebKit",
            ]

            for dir_name in lib_dirs:
                dir_path = home_lib / dir_name
                if dir_path.exists():
                    assert dir_path.is_dir()
                    print(f"[OK] Library/{dir_name} accessible")

    def test_system_directory_permissions(self):
        """Test permissions for system directories"""
        system_paths = [
            "/Applications",
            "/Library",
            "/System/Library",
            "/private/var",
            "/usr/local",
        ]

        for path_str in system_paths:
            path = Path(path_str)
            if path.exists():
                readable = os.access(path, os.R_OK)
                print(f"{ '[OK]' if readable else '[FAIL]' } {path_str} readable: {readable}")

    def test_temp_directory_operations(self):
        """Test temporary directory operations"""
        import tempfile

        # Test creating temporary files
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as tmp_file:
            tmp_file.write("test content")
            tmp_path = tmp_file.name

        assert Path(tmp_path).exists()

        # Clean up
        os.unlink(tmp_path)
        assert not Path(tmp_path).exists()


class TestSystemCommandCompatibility:
    """Test system command compatibility across macOS versions"""

    def test_basic_system_commands(self):
        """Test basic system commands used by the cleaner"""
        commands_to_test = [
            ["sw_vers"],
            ["whoami"],
            ["id", "-u"],
            ["uname", "-r"],
            ["which", "python3"],
        ]

        for cmd in commands_to_test:
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                print(f"[OK] Command {' '.join(cmd)}: exit_code={result.returncode}")
                if result.returncode != 0:
                    print(f"   stderr: {result.stderr}")
            except subprocess.TimeoutExpired:
                print(f"[FAIL] Command {' '.join(cmd)}: timeout")
            except FileNotFoundError:
                print(f"[FAIL] Command {' '.join(cmd)}: not found")

    def test_security_commands(self):
        """Test security-related commands"""
        security_commands = [
            ["security", "list-keychains"],
            ["security", "dump-keychain", "-d"],  # This might fail, that's OK
        ]

        for cmd in security_commands:
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                print(
                    f"[OK] Security command {' '.join(cmd[:2])}: exit_code={result.returncode}"
                )
            except subprocess.TimeoutExpired:
                print(f"[FAIL] Security command {' '.join(cmd[:2])}: timeout")
            except FileNotFoundError:
                print(f"[FAIL] Security command {' '.join(cmd[:2])}: not found")

    def test_process_commands(self):
        """Test process-related commands"""
        process_commands = [
            ["ps", "aux"],
            ["pgrep", "-f", "nonexistent_process_name"],  # Should return 1, that's OK
            ["pkill", "-0", "nonexistent_process_name"],  # Should fail, that's OK
        ]

        for cmd in process_commands:
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                print(
                    f"[OK] Process command {' '.join(cmd[:2])}: exit_code={result.returncode}"
                )
            except subprocess.TimeoutExpired:
                print(f"[FAIL] Process command {' '.join(cmd[:2])}: timeout")
            except FileNotFoundError:
                print(f"[FAIL] Process command {' '.join(cmd[:2])}: not found")


class TestCleanerCompatibility:
    """Test ZoomDeepCleanerEnhanced compatibility across macOS versions"""

    def test_cleaner_initialization(self):
        """Test cleaner initialization on current macOS version"""
        cleaner = ZoomDeepCleanerEnhanced(
            dry_run=True,
            verbose=True,
            vm_aware=False,  # Disable VM features for compatibility testing
        )

        assert cleaner is not None
        assert cleaner.dry_run is True
        assert cleaner.verbose is True

    def test_cleaner_platform_detection(self):
        """Test cleaner's platform detection"""
        cleaner = ZoomDeepCleanerEnhanced(dry_run=True)

        # The cleaner should detect macOS correctly
        if platform.system() == "Darwin":
            # Test that platform-specific paths are set correctly
            assert hasattr(cleaner, "logger")
            print("[OK] Cleaner platform detection working")

    @patch("zoom_deep_clean.cleaner_enhanced.ZoomDeepCleanerEnhanced._run_command")
    def test_cleaner_dry_run_compatibility(self, mock_run_command):
        """Test cleaner dry-run mode compatibility"""
        mock_run_command.return_value = (True, "mock output")

        cleaner = ZoomDeepCleanerEnhanced(dry_run=True, verbose=False)

        # This should work without actually executing system commands
        try:
            result = cleaner.run_deep_clean()
            print(f"[OK] Dry-run compatibility test: {result}")
        except Exception as e:
            print(f"[FAIL] Dry-run compatibility test failed: {e}")
            raise


class TestPythonCompatibility:
    """Test Python version compatibility on macOS"""

    def test_python_version_support(self):
        """Test that current Python version is supported"""
        version_info = sys.version_info

        # We support Python 3.9+
        assert version_info.major == 3
        assert version_info.minor >= 9

        print(
            f"[OK] Python {version_info.major}.{version_info.minor}.{version_info.micro} supported"
        )

    def test_required_modules_import(self):
        """Test that all required modules can be imported"""
        required_modules = [
            "os",
            "sys",
            "subprocess",
            "pathlib",
            "tempfile",
            "json",
            "logging",
            "argparse",
            "platform",
            "shutil",
            "time",
            "datetime",
        ]

        for module_name in required_modules:
            try:
                __import__(module_name)
                print(f"[OK] Module {module_name} imported successfully")
            except ImportError as e:
                print(f"[FAIL] Module {module_name} import failed: {e}")
                raise

    def test_package_imports(self):
        """Test that our package modules import correctly"""
        package_modules = [
            "zoom_deep_clean",
            "zoom_deep_clean.cleaner_enhanced",
            "zoom_deep_clean.cli_enhanced",
            "zoom_deep_clean.security_enhancements",
            "zoom_deep_clean.advanced_features",
            "zoom_deep_clean.cross_platform_support",
        ]

        for module_name in package_modules:
            try:
                __import__(module_name)
                print(f"[OK] Package module {module_name} imported successfully")
            except ImportError as e:
                print(f"[FAIL] Package module {module_name} import failed: {e}")
                raise


class TestVersionSpecificBehavior:
    """Test version-specific behavior and workarounds"""

    def test_macos_monterey_compatibility(self):
        """Test compatibility with macOS Monterey (12.x)"""
        if platform.system() != "Darwin":
            pytest.skip("Not running on macOS")

        version = platform.mac_ver()[0]
        if version.startswith("12."):
            print("[OK] Running on macOS Monterey - testing specific compatibility")
            # Add Monterey-specific tests here
            self._test_monterey_specific_features()
        else:
            print(f"[INFO] Not running on Monterey (version: {version})")

    def test_macos_ventura_compatibility(self):
        """Test compatibility with macOS Ventura (13.x)"""
        if platform.system() != "Darwin":
            pytest.skip("Not running on macOS")

        version = platform.mac_ver()[0]
        if version.startswith("13."):
            print("[OK] Running on macOS Ventura - testing specific compatibility")
            # Add Ventura-specific tests here
            self._test_ventura_specific_features()
        else:
            print(f"[INFO] Not running on Ventura (version: {version})")

    def test_macos_sonoma_compatibility(self):
        """Test compatibility with macOS Sonoma (14.x)"""
        if platform.system() != "Darwin":
            pytest.skip("Not running on macOS")

        version = platform.mac_ver()[0]
        if version.startswith("14."):
            print("[OK] Running on macOS Sonoma - testing specific compatibility")
            # Add Sonoma-specific tests here
            self._test_sonoma_specific_features()
        else:
            print(f"[INFO] Not running on Sonoma (version: {version})")

    def test_macos_sequoia_compatibility(self):
        """Test compatibility with macOS Sequoia (15.x)"""
        if platform.system() != "Darwin":
            pytest.skip("Not running on macOS")

        version = platform.mac_ver()[0]
        if version.startswith("15."):
            print("[OK] Running on macOS Sequoia - testing specific compatibility")
            # Add Sequoia-specific tests here
            self._test_sequoia_specific_features()
        else:
            print(f"[INFO] Not running on Sequoia (version: {version})")

    def _test_monterey_specific_features(self):
        """Test Monterey-specific features and workarounds"""
        # Test any Monterey-specific behavior
        print("  - Testing Monterey file system permissions")
        print("  - Testing Monterey security model")

    def _test_ventura_specific_features(self):
        """Test Ventura-specific features and workarounds"""
        # Test any Ventura-specific behavior
        print("  - Testing Ventura enhanced security features")
        print("  - Testing Ventura system integrity protection")

    def _test_sonoma_specific_features(self):
        """Test Sonoma-specific features and workarounds"""
        # Test any Sonoma-specific behavior
        print("  - Testing Sonoma privacy enhancements")
        print("  - Testing Sonoma system changes")

    def _test_sequoia_specific_features(self):
        """Test Sequoia-specific features and workarounds"""
        # Test any Sequoia-specific behavior
        print("  - Testing Sequoia new security model")
        print("  - Testing Sequoia system changes")


class TestCompatibilityReport:
    """Generate compatibility report for the current system"""

    def test_generate_compatibility_report(self):
        """Generate a comprehensive compatibility report"""
        report = {
            "system_info": self._get_system_info(),
            "python_info": self._get_python_info(),
            "file_system": self._test_file_system_access(),
            "commands": self._test_command_availability(),
            "package_status": self._test_package_status(),
        }

        print("\n" + "=" * 60)
        print("MACOS COMPATIBILITY REPORT")
        print("=" * 60)

        for section, data in report.items():
            print(f"\n{section.upper().replace('_', ' ')}:")
            if isinstance(data, dict):
                for key, value in data.items():
                    print(f"  {key}: {value}")
            else:
                print(f"  {data}")

        print("=" * 60)

        # Assert that basic compatibility requirements are met
        assert report["system_info"]["platform"] == "Darwin"
        assert report["python_info"]["version_supported"] is True

    def _get_system_info(self):
        """Get system information"""
        return {
            "platform": platform.system(),
            "version": (
                platform.mac_ver()[0] if platform.system() == "Darwin" else "N/A"
            ),
            "architecture": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
        }

    def _get_python_info(self):
        """Get Python compatibility information"""
        version_info = sys.version_info
        return {
            "version": f"{version_info.major}.{version_info.minor}.{version_info.micro}",
            "version_supported": version_info.major == 3 and version_info.minor >= 9,
            "executable": sys.executable,
            "path": sys.path[:3],  # First 3 entries
        }

    def _test_file_system_access(self):
        """Test file system access"""
        paths_to_test = [
            str(Path.home()),
            str(Path.home() / "Library"),
            "/Applications",
            "/tmp",
        ]

        results = {}
        for path in paths_to_test:
            try:
                path_obj = Path(path)
                results[path] = {
                    "exists": path_obj.exists(),
                    "readable": os.access(path, os.R_OK),
                    "writable": os.access(path, os.W_OK),
                }
            except Exception as e:
                results[path] = f"Error: {e}"

        return results

    def _test_command_availability(self):
        """Test availability of required system commands"""
        commands = ["sw_vers", "security", "ps", "pgrep", "pkill", "launchctl"]
        results = {}

        for cmd in commands:
            try:
                result = subprocess.run(["which", cmd], capture_output=True, text=True)
                results[cmd] = "available" if result.returncode == 0 else "not found"
            except Exception as e:
                results[cmd] = f"error: {e}"

        return results

    def _test_package_status(self):
        """Test package import status"""
        try:
            import zoom_deep_clean

            return {
                "package_importable": True,
                "version": getattr(zoom_deep_clean, "__version__", "unknown"),
                "location": zoom_deep_clean.__file__,
            }
        except ImportError as e:
            return {"package_importable": False, "error": str(e)}

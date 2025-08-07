#!/usr/bin/env python3
"""
Cross-Platform Support Module
Extending Zoom Deep Clean Enhanced to Windows and Linux

Created by: PHLthy215 (Enhanced by Amazon Q)
Version: 2.3.0 - Cross-Platform
"""

import os
import sys
import platform
import subprocess
import shutil
from typing import List, Dict, Tuple, Optional, Any
from pathlib import Path
import logging

# Conditional Windows import
try:
    import winreg
except ImportError:
    winreg = None  # Not available on non-Windows platforms


class PlatformDetector:
    """Detect and validate platform capabilities"""

    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.platform = platform.system().lower()
        self.platform_version = platform.version()
        self.architecture = platform.machine()

    def get_platform_info(self) -> Dict[str, str]:
        """Get comprehensive platform information"""
        return {
            "system": self.platform,
            "version": self.platform_version,
            "architecture": self.architecture,
            "python_version": platform.python_version(),
            "supported": self.is_supported(),
        }

    def is_supported(self) -> bool:
        """Check if platform is supported"""
        return self.platform in ["darwin", "windows", "linux"]

    def is_macos(self) -> bool:
        """Check if current platform is macOS"""
        return self.platform == "darwin"

    def is_windows(self) -> bool:
        """Check if current platform is Windows"""
        return self.platform == "windows"

    def is_linux(self) -> bool:
        """Check if current platform is Linux"""
        return self.platform == "linux"

    def get_version_info(self) -> Dict[str, str]:
        """Get detailed version information for the current platform"""
        if self.platform == "darwin":
            mac_ver = platform.mac_ver()
            return {
                "version": mac_ver[0],
                "build": mac_ver[2] if mac_ver[2] else "unknown",
                "machine": self.architecture,
            }
        elif self.platform == "windows":
            return {
                "version": platform.version(),
                "build": (
                    platform.win32_ver()[1]
                    if hasattr(platform, "win32_ver")
                    else "unknown"
                ),
                "machine": self.architecture,
            }
        elif self.platform == "linux":
            return {
                "version": platform.version(),
                "build": platform.release(),
                "machine": self.architecture,
            }
        else:
            return {
                "version": self.platform_version,
                "build": "unknown",
                "machine": self.architecture,
            }

    def get_platform_specific_paths(self) -> Dict[str, List[str]]:
        """Get platform-specific paths for Zoom cleanup"""
        if self.platform == "darwin":
            return self._get_macos_paths()
        elif self.platform == "windows":
            return self._get_windows_paths()
        elif self.platform == "linux":
            return self._get_linux_paths()
        else:
            return {}

    def _get_macos_paths(self) -> Dict[str, List[str]]:
        """macOS-specific paths"""
        return {
            "applications": ["/Applications/zoom.us.app"],
            "user_data": [
                "~/Library/Application Support/zoom.us",
                "~/Library/Preferences/us.zoom.xos.plist",
                "~/Library/Caches/us.zoom.xos",
                "~/Library/Logs/zoom.us",
            ],
            "system_data": [
                "/Library/Application Support/zoom.us",
                "/Library/LaunchAgents/us.zoom.*",
                "/Library/LaunchDaemons/us.zoom.*",
            ],
        }

    def _get_windows_paths(self) -> Dict[str, List[str]]:
        """Windows-specific paths"""
        return {
            "applications": [
                "%PROGRAMFILES%\\Zoom\\bin\\Zoom.exe",
                "%PROGRAMFILES(X86)%\\Zoom\\bin\\Zoom.exe",
                "%LOCALAPPDATA%\\Zoom\\bin\\Zoom.exe",
            ],
            "user_data": [
                "%APPDATA%\\Zoom",
                "%LOCALAPPDATA%\\Zoom",
                "%USERPROFILE%\\Documents\\Zoom",
            ],
            "system_data": ["%PROGRAMDATA%\\Zoom", "%ALLUSERSPROFILE%\\Zoom"],
            "registry_keys": [
                "HKEY_CURRENT_USER\\Software\\Zoom",
                "HKEY_LOCAL_MACHINE\\Software\\Zoom",
                "HKEY_LOCAL_MACHINE\\Software\\WOW6432Node\\Zoom",
            ],
        }

    def _get_linux_paths(self) -> Dict[str, List[str]]:
        """Linux-specific paths"""
        return {
            "applications": [
                "/opt/zoom",
                "/usr/bin/zoom",
                "/usr/local/bin/zoom",
                "~/.local/share/applications/Zoom.desktop",
            ],
            "user_data": [
                "~/.zoom",
                "~/.config/zoomus.conf",
                "~/.cache/zoom",
                "~/.local/share/zoom",
            ],
            "system_data": [
                "/etc/zoom",
                "/var/lib/zoom",
                "/usr/share/applications/Zoom.desktop",
            ],
        }


class WindowsZoomCleaner:
    """Windows-specific Zoom cleanup implementation"""

    def __init__(self, logger: logging.Logger, dry_run: bool = False):
        self.logger = logger
        self.dry_run = dry_run

        if platform.system() != "Windows":
            raise RuntimeError("WindowsZoomCleaner can only run on Windows")

        if winreg is None:
            raise RuntimeError(
                "winreg module not available - required for Windows registry operations"
            )

    def clean_windows_zoom(self) -> Dict[str, Any]:
        """Perform Windows-specific Zoom cleanup"""
        self.logger.info("🪟 Starting Windows Zoom cleanup...")

        results = {
            "processes_terminated": 0,
            "files_removed": 0,
            "registry_keys_removed": 0,
            "services_stopped": 0,
            "errors": [],
        }

        try:
            # Stop Zoom processes
            results["processes_terminated"] = self._terminate_zoom_processes()

            # Clean registry
            results["registry_keys_removed"] = self._clean_registry()

            # Remove files
            results["files_removed"] = self._remove_zoom_files()

            # Stop services
            results["services_stopped"] = self._stop_zoom_services()

            # Clean Windows-specific locations
            self._clean_windows_specific()

        except Exception as e:
            error_msg = f"Windows cleanup error: {e}"
            self.logger.error(error_msg)
            results["errors"].append(error_msg)

        return results

    def _terminate_zoom_processes(self) -> int:
        """Terminate Zoom processes on Windows"""
        zoom_processes = [
            "Zoom.exe",
            "ZoomLauncher.exe",
            "ZoomPhone.exe",
            "ZoomChat.exe",
            "ZoomClips.exe",
            "ZoomPresence.exe",
        ]

        terminated = 0
        for process in zoom_processes:
            try:
                if self.dry_run:
                    self.logger.info(f"DRY RUN: Would terminate {process}")
                    terminated += 1
                else:
                    result = subprocess.run(
                        ["taskkill", "/F", "/IM", process],
                        capture_output=True,
                        text=True,
                    )
                    if result.returncode == 0:
                        self.logger.info(f"Terminated process: {process}")
                        terminated += 1
            except Exception as e:
                self.logger.warning(f"Could not terminate {process}: {e}")

        return terminated

    def _clean_registry(self) -> int:
        """Clean Zoom-related registry entries"""
        registry_keys = [
            (winreg.HKEY_CURRENT_USER, "Software\\Zoom"),
            (winreg.HKEY_LOCAL_MACHINE, "Software\\Zoom"),
            (winreg.HKEY_LOCAL_MACHINE, "Software\\WOW6432Node\\Zoom"),
        ]

        removed = 0
        for hive, key_path in registry_keys:
            try:
                if self.dry_run:
                    self.logger.info(f"DRY RUN: Would remove registry key {key_path}")
                    removed += 1
                else:
                    winreg.DeleteKeyEx(hive, key_path)
                    self.logger.info(f"Removed registry key: {key_path}")
                    removed += 1
            except FileNotFoundError:
                # Key doesn't exist, which is fine
                pass
            except Exception as e:
                self.logger.warning(f"Could not remove registry key {key_path}: {e}")

        return removed

    def _remove_zoom_files(self) -> int:
        """Remove Zoom files on Windows"""
        zoom_paths = [
            os.path.expandvars("%PROGRAMFILES%\\Zoom"),
            os.path.expandvars("%PROGRAMFILES(X86)%\\Zoom"),
            os.path.expandvars("%LOCALAPPDATA%\\Zoom"),
            os.path.expandvars("%APPDATA%\\Zoom"),
            os.path.expandvars("%PROGRAMDATA%\\Zoom"),
        ]

        removed = 0
        for path in zoom_paths:
            if os.path.exists(path):
                try:
                    if self.dry_run:
                        self.logger.info(f"DRY RUN: Would remove {path}")
                        removed += 1
                    else:
                        if os.path.isdir(path):
                            shutil.rmtree(path)
                        else:
                            os.remove(path)
                        self.logger.info(f"Removed: {path}")
                        removed += 1
                except Exception as e:
                    self.logger.warning(f"Could not remove {path}: {e}")

        return removed

    def _stop_zoom_services(self) -> int:
        """Stop Zoom-related Windows services"""
        zoom_services = ["ZoomCptService", "ZoomCptInstaller"]

        stopped = 0
        for service in zoom_services:
            try:
                if self.dry_run:
                    self.logger.info(f"DRY RUN: Would stop service {service}")
                    stopped += 1
                else:
                    result = subprocess.run(
                        ["sc", "stop", service], capture_output=True, text=True
                    )
                    if result.returncode == 0:
                        self.logger.info(f"Stopped service: {service}")
                        stopped += 1
            except Exception as e:
                self.logger.warning(f"Could not stop service {service}: {e}")

        return stopped

    def _clean_windows_specific(self):
        """Clean Windows-specific Zoom artifacts"""
        # Clean Windows Event Logs
        try:
            if not self.dry_run:
                subprocess.run(["wevtutil", "cl", "Application"], check=False)
                self.logger.info("Cleared Application event log")
        except Exception as e:
            self.logger.warning(f"Could not clear event logs: {e}")

        # Clean Windows prefetch
        prefetch_path = os.path.expandvars("%WINDIR%\\Prefetch")
        if os.path.exists(prefetch_path):
            try:
                for file in os.listdir(prefetch_path):
                    if "zoom" in file.lower():
                        file_path = os.path.join(prefetch_path, file)
                        if self.dry_run:
                            self.logger.info(
                                f"DRY RUN: Would remove prefetch {file_path}"
                            )
                        else:
                            os.remove(file_path)
                            self.logger.info(f"Removed prefetch: {file_path}")
            except Exception as e:
                self.logger.warning(f"Could not clean prefetch: {e}")


class LinuxZoomCleaner:
    """Linux-specific Zoom cleanup implementation"""

    def __init__(self, logger: logging.Logger, dry_run: bool = False):
        self.logger = logger
        self.dry_run = dry_run

        if platform.system() != "Linux":
            raise RuntimeError("LinuxZoomCleaner can only run on Linux")

    def clean_linux_zoom(self) -> Dict[str, Any]:
        """Perform Linux-specific Zoom cleanup"""
        self.logger.info("🐧 Starting Linux Zoom cleanup...")

        results = {
            "processes_terminated": 0,
            "files_removed": 0,
            "packages_removed": 0,
            "services_stopped": 0,
            "errors": [],
        }

        try:
            # Stop Zoom processes
            results["processes_terminated"] = self._terminate_zoom_processes()

            # Remove files
            results["files_removed"] = self._remove_zoom_files()

            # Remove packages
            results["packages_removed"] = self._remove_zoom_packages()

            # Clean Linux-specific locations
            self._clean_linux_specific()

        except Exception as e:
            error_msg = f"Linux cleanup error: {e}"
            self.logger.error(error_msg)
            results["errors"].append(error_msg)

        return results

    def _terminate_zoom_processes(self) -> int:
        """Terminate Zoom processes on Linux"""
        try:
            if self.dry_run:
                self.logger.info("DRY RUN: Would terminate Zoom processes")
                return 1
            else:
                result = subprocess.run(
                    ["pkill", "-f", "zoom"], capture_output=True, text=True
                )
                if result.returncode == 0:
                    self.logger.info("Terminated Zoom processes")
                    return 1
        except Exception as e:
            self.logger.warning(f"Could not terminate Zoom processes: {e}")

        return 0

    def _remove_zoom_files(self) -> int:
        """Remove Zoom files on Linux"""
        zoom_paths = [
            "/opt/zoom",
            "/usr/bin/zoom",
            "/usr/local/bin/zoom",
            os.path.expanduser("~/.zoom"),
            os.path.expanduser("~/.config/zoomus.conf"),
            os.path.expanduser("~/.cache/zoom"),
            os.path.expanduser("~/.local/share/zoom"),
            "/usr/share/applications/Zoom.desktop",
            os.path.expanduser("~/.local/share/applications/Zoom.desktop"),
        ]

        removed = 0
        for path in zoom_paths:
            if os.path.exists(path):
                try:
                    if self.dry_run:
                        self.logger.info(f"DRY RUN: Would remove {path}")
                        removed += 1
                    else:
                        if os.path.isdir(path):
                            shutil.rmtree(path)
                        else:
                            os.remove(path)
                        self.logger.info(f"Removed: {path}")
                        removed += 1
                except Exception as e:
                    self.logger.warning(f"Could not remove {path}: {e}")

        return removed

    def _remove_zoom_packages(self) -> int:
        """Remove Zoom packages on Linux"""
        package_managers = [
            (["dpkg", "-l"], ["apt-get", "remove", "--purge", "-y"]),  # Debian/Ubuntu
            (["rpm", "-qa"], ["yum", "remove", "-y"]),  # RHEL/CentOS
            (["rpm", "-qa"], ["dnf", "remove", "-y"]),  # Fedora
            (["pacman", "-Q"], ["pacman", "-R", "--noconfirm"]),  # Arch
        ]

        removed = 0
        for list_cmd, remove_cmd in package_managers:
            try:
                # Check if package manager exists
                if not shutil.which(list_cmd[0]):
                    continue

                # List packages
                result = subprocess.run(list_cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    packages = result.stdout.lower()
                    if "zoom" in packages:
                        if self.dry_run:
                            self.logger.info(
                                f"DRY RUN: Would remove Zoom package with {remove_cmd[0]}"
                            )
                            removed += 1
                        else:
                            # Remove zoom package
                            remove_result = subprocess.run(
                                remove_cmd + ["zoom"], capture_output=True, text=True
                            )
                            if remove_result.returncode == 0:
                                self.logger.info(
                                    f"Removed Zoom package with {remove_cmd[0]}"
                                )
                                removed += 1
                        break  # Only use one package manager
            except Exception as e:
                self.logger.warning(f"Package removal error with {list_cmd[0]}: {e}")

        return removed

    def _clean_linux_specific(self):
        """Clean Linux-specific Zoom artifacts"""
        # Clean systemd user services
        systemd_user_dir = os.path.expanduser("~/.config/systemd/user")
        if os.path.exists(systemd_user_dir):
            try:
                for file in os.listdir(systemd_user_dir):
                    if "zoom" in file.lower():
                        file_path = os.path.join(systemd_user_dir, file)
                        if self.dry_run:
                            self.logger.info(
                                f"DRY RUN: Would remove systemd service {file_path}"
                            )
                        else:
                            os.remove(file_path)
                            self.logger.info(f"Removed systemd service: {file_path}")
            except Exception as e:
                self.logger.warning(f"Could not clean systemd services: {e}")

        # Clean desktop entries
        desktop_dirs = [
            "/usr/share/applications",
            os.path.expanduser("~/.local/share/applications"),
        ]

        for desktop_dir in desktop_dirs:
            if os.path.exists(desktop_dir):
                try:
                    for file in os.listdir(desktop_dir):
                        if "zoom" in file.lower() and file.endswith(".desktop"):
                            file_path = os.path.join(desktop_dir, file)
                            if self.dry_run:
                                self.logger.info(
                                    f"DRY RUN: Would remove desktop entry {file_path}"
                                )
                            else:
                                os.remove(file_path)
                                self.logger.info(f"Removed desktop entry: {file_path}")
                except Exception as e:
                    self.logger.warning(
                        f"Could not clean desktop entries in {desktop_dir}: {e}"
                    )


class CrossPlatformZoomCleaner:
    """Unified cross-platform Zoom cleaner"""

    def __init__(self, logger: logging.Logger, dry_run: bool = False):
        self.logger = logger
        self.dry_run = dry_run
        self.platform_detector = PlatformDetector(logger)

        # Initialize platform-specific cleaner
        platform_name = self.platform_detector.platform
        if platform_name == "windows":
            self.platform_cleaner = WindowsZoomCleaner(logger, dry_run)
        elif platform_name == "linux":
            self.platform_cleaner = LinuxZoomCleaner(logger, dry_run)
        elif platform_name == "darwin":
            # Use existing macOS cleaner
            self.platform_cleaner = None
        else:
            raise RuntimeError(f"Unsupported platform: {platform_name}")

    def run_cross_platform_cleanup(self) -> Dict[str, Any]:
        """Run platform-appropriate cleanup"""
        platform_info = self.platform_detector.get_platform_info()
        self.logger.info(
            f"🌍 Running cleanup on {platform_info['system']} {platform_info['version']}"
        )

        if not platform_info["supported"]:
            raise RuntimeError(f"Platform {platform_info['system']} is not supported")

        results = {"platform_info": platform_info, "cleanup_results": {}}

        if self.platform_detector.platform == "darwin":
            # Use existing macOS implementation
            results["cleanup_results"] = {
                "message": "Use existing macOS ZoomDeepCleanerEnhanced"
            }
        else:
            # Use platform-specific cleaner
            results["cleanup_results"] = (
                self.platform_cleaner.clean_linux_zoom()
                if self.platform_detector.platform == "linux"
                else self.platform_cleaner.clean_windows_zoom()
            )

        return results

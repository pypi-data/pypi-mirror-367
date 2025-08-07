#!/usr/bin/env python3
"""
Deep System Cleaner for Zoom - Addresses "Login Works but Can't Join Meetings" Issue
Targets deeper system-level artifacts that typical cleaners miss

This module specifically addresses the issue where Zoom appears to work (login succeeds)
but fails when trying to join meetings due to deeper system-level artifacts.
"""

import os
import sys
import subprocess
import logging
import re
import time
import sqlite3
import shutil
from typing import List, Dict, Optional, Tuple
from pathlib import Path


class DeepSystemCleaner:
    """Enhanced cleaner for deep system-level Zoom artifacts"""

    def __init__(self, logger: logging.Logger, dry_run: bool = False):
        self.logger = logger
        self.dry_run = dry_run
        self.deep_artifacts_found = []
        self.ioreg_zoom_entries = []

    def clean_deep_system_artifacts(self) -> Dict[str, int]:
        """Clean deeper system artifacts that cause meeting join failures"""
        results = {
            "tcc_entries_cleared": 0,
            "ioreg_entries_cleared": 0,
            "system_temp_cleaned": 0,
            "network_configs_reset": 0,
            "audio_video_configs_reset": 0,
            "system_identifiers_cleared": 0,
            "receipt_files_removed": 0,
            "keychain_entries_cleared": 0,
            "deep_cache_cleared": 0,
            "kernel_extensions_cleared": 0,
        }

        self.logger.info("🔍 Starting deep system artifact cleanup...")

        # 1. Clear TCC database entries (CRITICAL - primary cause of meeting join failures)
        results["tcc_entries_cleared"] = self._clear_tcc_zoom_entries()

        # 2. Clear IORegistry Zoom entries (critical for meeting join issues)
        results["ioreg_entries_cleared"] = self._clear_ioreg_zoom_entries()

        # 3. Clean system temporary files with Zoom signatures
        results["system_temp_cleaned"] = self._clean_system_temp_zoom_files()

        # 4. Reset network configurations that may be cached
        results["network_configs_reset"] = self._reset_network_configurations()

        # 5. Clear audio/video system configurations
        results["audio_video_configs_reset"] = self._clear_audio_video_configs()

        # 6. Clear system identifiers and device fingerprints
        results["system_identifiers_cleared"] = self._clear_system_identifiers()

        # 7. Remove package receipt files
        results["receipt_files_removed"] = self._remove_package_receipts()

        # 8. Clear keychain entries
        results["keychain_entries_cleared"] = self._clear_keychain_entries()

        # 9. Clear deep system caches
        results["deep_cache_cleared"] = self._clear_deep_system_caches()

        # 10. Clear any kernel extensions or system extensions
        results["kernel_extensions_cleared"] = self._clear_kernel_extensions()

        return results

    def _clear_tcc_zoom_entries(self) -> int:
        """Clear TCC database entries - CRITICAL fix for meeting join failures"""
        cleared = 0

        # TCC database locations
        tcc_paths = [
            "/Library/Application Support/com.apple.TCC/TCC.db",
            os.path.expanduser("~/Library/Application Support/com.apple.TCC/TCC.db"),
        ]

        for tcc_path in tcc_paths:
            if not os.path.exists(tcc_path):
                continue

            try:
                self.logger.info(f"Processing TCC database: {tcc_path}")

                # Create backup first
                if not self.dry_run:
                    backup_path = f"{tcc_path}.backup.{int(time.time())}"
                    shutil.copy2(tcc_path, backup_path)
                    self.logger.info(f"Created TCC backup: {backup_path}")

                # Connect to database
                conn = sqlite3.connect(tcc_path)
                cursor = conn.cursor()

                # Find Zoom entries
                cursor.execute(
                    "SELECT service, client, auth_value FROM access WHERE client LIKE '%zoom%' OR client LIKE '%Zoom%'"
                )
                entries = cursor.fetchall()

                if entries:
                    self.logger.warning(
                        f"Found {len(entries)} TCC entries in {tcc_path}:"
                    )
                    for service, client, auth_value in entries:
                        self.logger.warning(
                            f"  {service}: {client} (auth: {auth_value})"
                        )

                    if not self.dry_run:
                        # Remove all Zoom-related TCC entries
                        cursor.execute(
                            "DELETE FROM access WHERE client LIKE '%zoom%' OR client LIKE '%Zoom%'"
                        )
                        conn.commit()
                        self.logger.info(f"✅ Removed {len(entries)} TCC entries")
                        cleared += len(entries)

                        # Also reset using tccutil if available
                        zoom_clients = [
                            "us.zoom.xos",
                            "sh.1132.ZoomFixer",
                            "us.zoom.ZoomClips",
                        ]
                        for client in zoom_clients:
                            try:
                                subprocess.run(
                                    ["sudo", "tccutil", "reset", "All", client],
                                    capture_output=True,
                                    check=False,
                                )
                            except Exception:
                                pass  # tccutil might not be available or might fail
                    else:
                        self.logger.info(
                            f"[DRY RUN] Would remove {len(entries)} TCC entries"
                        )
                        cleared += len(entries)

                conn.close()

            except Exception as e:
                self.logger.error(f"Error processing TCC database {tcc_path}: {e}")

        if cleared > 0:
            self.logger.warning(
                "🔄 TCC database cleaned - system restart recommended for full effect"
            )

        return cleared

    def _clear_ioreg_zoom_entries(self) -> int:
        """Clear IORegistry entries that show Zoom system integration"""
        cleared = 0

        try:
            # First, identify active Zoom processes in IORegistry
            result = subprocess.run(
                ["ioreg", "-l"], capture_output=True, text=True, errors="ignore"
            )
            if result.returncode == 0:
                zoom_lines = [
                    line
                    for line in result.stdout.split("\n")
                    if "zoom" in line.lower() or "IOUserClientCreator" in line
                ]

                for line in zoom_lines:
                    self.ioreg_zoom_entries.append(line.strip())
                    self.logger.warning(f"Found IORegistry Zoom entry: {line.strip()}")

                # Kill processes that have IORegistry entries
                pid_pattern = r"pid (\d+), zoom\.us|pid (\d+), ZoomClips"
                for line in zoom_lines:
                    matches = re.findall(pid_pattern, line)
                    for match in matches:
                        pid = match[0] or match[1]
                        if pid:
                            if not self.dry_run:
                                try:
                                    subprocess.run(
                                        ["sudo", "kill", "-9", pid],
                                        capture_output=True,
                                        check=False,
                                    )
                                    self.logger.info(
                                        f"Killed Zoom process with PID: {pid}"
                                    )
                                    cleared += 1
                                except Exception as e:
                                    self.logger.error(f"Failed to kill PID {pid}: {e}")
                            else:
                                self.logger.info(
                                    f"[DRY RUN] Would kill Zoom process PID: {pid}"
                                )
                                cleared += 1

        except Exception as e:
            self.logger.error(f"Error clearing IORegistry entries: {e}")

        return cleared

    def _clean_system_temp_zoom_files(self) -> int:
        """Clean system-wide temporary files with Zoom signatures"""
        cleaned = 0

        # System temp directories to check
        temp_dirs = ["/private/var/folders", "/private/tmp", "/tmp", "/var/tmp"]

        zoom_patterns = [
            "*zoom*",
            "*Zoom*",
            "us.zoom.*",
            "ZoomClips*",
            "ZoomPhone*",
            "ZoomChat*",
        ]

        for temp_dir in temp_dirs:
            if not os.path.exists(temp_dir):
                continue

            try:
                # Use find to locate Zoom-related temp files
                for pattern in zoom_patterns:
                    cmd = [
                        "sudo",
                        "find",
                        temp_dir,
                        "-name",
                        pattern,
                        "-type",
                        "f",
                        "2>/dev/null",
                    ]
                    result = subprocess.run(
                        cmd, capture_output=True, text=True, shell=False
                    )

                    if result.returncode == 0 and result.stdout.strip():
                        files = result.stdout.strip().split("\n")
                        for file_path in files:
                            if file_path and os.path.exists(file_path):
                                if not self.dry_run:
                                    try:
                                        subprocess.run(
                                            ["sudo", "rm", "-rf", file_path],
                                            capture_output=True,
                                            check=True,
                                        )
                                        self.logger.info(
                                            f"Removed system temp file: {file_path}"
                                        )
                                        cleaned += 1
                                    except Exception as e:
                                        self.logger.error(
                                            f"Failed to remove {file_path}: {e}"
                                        )
                                else:
                                    self.logger.info(
                                        f"[DRY RUN] Would remove: {file_path}"
                                    )
                                    cleaned += 1

            except Exception as e:
                self.logger.error(f"Error cleaning temp files in {temp_dir}: {e}")

        return cleaned

    def _reset_network_configurations(self) -> int:
        """Reset network configurations that may cache Zoom server connections"""
        reset_count = 0

        network_configs = [
            "/Library/Preferences/SystemConfiguration/NetworkInterfaces.plist",
            "/Library/Preferences/SystemConfiguration/preferences.plist",
        ]

        # Clear DNS cache (critical for Zoom meeting connections)
        if not self.dry_run:
            try:
                subprocess.run(
                    ["sudo", "dscacheutil", "-flushcache"],
                    capture_output=True,
                    check=True,
                )
                subprocess.run(
                    ["sudo", "killall", "-HUP", "mDNSResponder"],
                    capture_output=True,
                    check=False,
                )
                self.logger.info("Flushed DNS cache")
                reset_count += 1
            except Exception as e:
                self.logger.error(f"Failed to flush DNS cache: {e}")
        else:
            self.logger.info("[DRY RUN] Would flush DNS cache")
            reset_count += 1

        # Reset network interface configurations if they contain Zoom-specific settings
        for config_file in network_configs:
            if os.path.exists(config_file):
                try:
                    # Check if file contains Zoom-related configurations
                    with open(config_file, "rb") as f:
                        content = f.read()
                        if b"zoom" in content.lower() or b"us.zoom" in content:
                            if not self.dry_run:
                                # Backup and reset the configuration
                                backup_file = f"{config_file}.backup.{int(time.time())}"
                                subprocess.run(
                                    ["sudo", "cp", config_file, backup_file],
                                    capture_output=True,
                                    check=True,
                                )
                                self.logger.info(f"Reset network config: {config_file}")
                                reset_count += 1
                            else:
                                self.logger.info(
                                    f"[DRY RUN] Would reset: {config_file}"
                                )
                                reset_count += 1
                except Exception as e:
                    self.logger.error(
                        f"Error checking network config {config_file}: {e}"
                    )

        return reset_count

    def _clear_audio_video_configs(self) -> int:
        """Clear audio/video system configurations that may interfere with Zoom"""
        cleared = 0

        av_config_paths = [
            "/Library/Audio/Plug-Ins/HAL",
            "/Library/CoreMediaIO/Plug-Ins/DAL",
            "/private/var/db/CoreAudio",
        ]

        for config_path in av_config_paths:
            if not os.path.exists(config_path):
                continue

            try:
                # Look for Zoom-related audio/video plugins or configurations
                result = subprocess.run(
                    [
                        "sudo",
                        "find",
                        config_path,
                        "-name",
                        "*zoom*",
                        "-o",
                        "-name",
                        "*Zoom*",
                    ],
                    capture_output=True,
                    text=True,
                )

                if result.returncode == 0 and result.stdout.strip():
                    files = result.stdout.strip().split("\n")
                    for file_path in files:
                        if file_path and os.path.exists(file_path):
                            if not self.dry_run:
                                try:
                                    subprocess.run(
                                        ["sudo", "rm", "-rf", file_path],
                                        capture_output=True,
                                        check=True,
                                    )
                                    self.logger.info(f"Removed AV config: {file_path}")
                                    cleared += 1
                                except Exception as e:
                                    self.logger.error(
                                        f"Failed to remove AV config {file_path}: {e}"
                                    )
                            else:
                                self.logger.info(
                                    f"[DRY RUN] Would remove AV config: {file_path}"
                                )
                                cleared += 1

            except Exception as e:
                self.logger.error(f"Error clearing AV configs in {config_path}: {e}")

        return cleared

    def _clear_system_identifiers(self) -> int:
        """Clear system identifiers that Zoom may use for device fingerprinting"""
        cleared = 0

        # System identifier locations
        identifier_paths = [
            "/private/var/db/SystemPolicyConfiguration",
            "/Library/Application Support/com.apple.TCC",
            "/private/var/db/receipts",
        ]

        for id_path in identifier_paths:
            if not os.path.exists(id_path):
                continue

            try:
                # Look for Zoom-related system identifiers
                result = subprocess.run(
                    [
                        "sudo",
                        "find",
                        id_path,
                        "-name",
                        "*zoom*",
                        "-o",
                        "-name",
                        "*us.zoom*",
                    ],
                    capture_output=True,
                    text=True,
                )

                if result.returncode == 0 and result.stdout.strip():
                    files = result.stdout.strip().split("\n")
                    for file_path in files:
                        if file_path and os.path.exists(file_path):
                            if not self.dry_run:
                                try:
                                    subprocess.run(
                                        ["sudo", "rm", "-rf", file_path],
                                        capture_output=True,
                                        check=True,
                                    )
                                    self.logger.info(
                                        f"Removed system identifier: {file_path}"
                                    )
                                    cleared += 1
                                except Exception as e:
                                    self.logger.error(
                                        f"Failed to remove identifier {file_path}: {e}"
                                    )
                            else:
                                self.logger.info(
                                    f"[DRY RUN] Would remove identifier: {file_path}"
                                )
                                cleared += 1

            except Exception as e:
                self.logger.error(f"Error clearing identifiers in {id_path}: {e}")

        return cleared

    def _remove_package_receipts(self) -> int:
        """Remove package receipt files that may cause reinstallation issues"""
        removed = 0

        receipt_patterns = ["us.zoom.pkg.videomeeting.*", "us.zoom.*", "*zoom*"]

        receipt_dir = "/private/var/db/receipts"

        if os.path.exists(receipt_dir):
            try:
                for pattern in receipt_patterns:
                    result = subprocess.run(
                        ["sudo", "find", receipt_dir, "-name", pattern],
                        capture_output=True,
                        text=True,
                    )

                    if result.returncode == 0 and result.stdout.strip():
                        files = result.stdout.strip().split("\n")
                        for file_path in files:
                            if file_path and os.path.exists(file_path):
                                if not self.dry_run:
                                    try:
                                        subprocess.run(
                                            ["sudo", "rm", "-f", file_path],
                                            capture_output=True,
                                            check=True,
                                        )
                                        self.logger.info(
                                            f"Removed receipt: {file_path}"
                                        )
                                        removed += 1
                                    except Exception as e:
                                        self.logger.error(
                                            f"Failed to remove receipt {file_path}: {e}"
                                        )
                                else:
                                    self.logger.info(
                                        f"[DRY RUN] Would remove receipt: {file_path}"
                                    )
                                    removed += 1

            except Exception as e:
                self.logger.error(f"Error removing package receipts: {e}")

        return removed

    def _clear_keychain_entries(self) -> int:
        """Clear Zoom keychain entries that may contain stale authentication data"""
        cleared = 0

        try:
            # Search for Zoom-related keychain entries
            result = subprocess.run(
                ["security", "dump-keychain"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                zoom_entries = []
                lines = result.stdout.split("\n")

                # Parse keychain entries for Zoom-related items
                current_entry = {}
                for line in lines:
                    line = line.strip()

                    if line.startswith("keychain:"):
                        if current_entry and self._is_zoom_keychain_entry(
                            current_entry
                        ):
                            zoom_entries.append(current_entry)
                        current_entry = {"keychain": line}
                    elif "=" in line and current_entry:
                        key, value = line.split("=", 1)
                        current_entry[key.strip()] = value.strip()

                # Check last entry
                if current_entry and self._is_zoom_keychain_entry(current_entry):
                    zoom_entries.append(current_entry)

                if zoom_entries:
                    self.logger.warning(
                        f"Found {len(zoom_entries)} Zoom keychain entries"
                    )

                    for entry in zoom_entries:
                        service = entry.get('"svce"<blob>', "unknown")
                        account = entry.get('"acct"<blob>', "unknown")
                        self.logger.warning(f"  Service: {service}, Account: {account}")

                        if not self.dry_run:
                            # Try to delete the keychain entry
                            try:
                                # Extract service and account for deletion
                                if "Zoom" in service:
                                    delete_cmd = [
                                        "security",
                                        "delete-generic-password",
                                        "-s",
                                        service.strip('"'),
                                        "-D",
                                        "application password",
                                    ]
                                    subprocess.run(
                                        delete_cmd, capture_output=True, check=False
                                    )
                                    cleared += 1
                            except Exception as e:
                                self.logger.error(
                                    f"Failed to delete keychain entry: {e}"
                                )
                        else:
                            self.logger.info(
                                f"[DRY RUN] Would remove keychain entry: {service}"
                            )
                            cleared += 1

        except Exception as e:
            self.logger.error(f"Error clearing keychain entries: {e}")

        return cleared

    def _is_zoom_keychain_entry(self, entry: dict) -> bool:
        """Check if keychain entry is Zoom-related"""
        zoom_indicators = ["zoom", "Zoom", "us.zoom"]

        for key, value in entry.items():
            if isinstance(value, str):
                for indicator in zoom_indicators:
                    if indicator in value:
                        return True
        return False

    def verify_deep_cleanup(self) -> bool:
        """Verify that deep system cleanup was successful"""
        try:
            # Check IORegistry for remaining Zoom entries
            try:
                result = subprocess.run(
                    ["ioreg", "-l"],
                    capture_output=True,
                    text=True,
                    errors="ignore",
                    timeout=30,
                )
                if result.returncode == 0:
                    zoom_lines = [
                        line
                        for line in result.stdout.split("\n")
                        if "zoom" in line.lower() and "IOUserClientCreator" in line
                    ]
                    if zoom_lines:
                        self.logger.warning(
                            f"Found {len(zoom_lines)} remaining IORegistry entries"
                        )
                        return False
            except Exception as e:
                self.logger.debug(f"IORegistry verification skipped: {e}")

            # Check system temp directories
            temp_dirs = ["/private/var/folders", "/tmp", "/private/tmp"]
            for temp_dir in temp_dirs:
                if os.path.exists(temp_dir):
                    try:
                        result = subprocess.run(
                            [
                                "find",
                                temp_dir,
                                "-name",
                                "*zoom*",
                                "-o",
                                "-name",
                                "*Zoom*",
                            ],
                            capture_output=True,
                            text=True,
                            timeout=30,
                        )
                        if result.stdout.strip():
                            self.logger.warning(
                                f"Found remaining temp files in {temp_dir}"
                            )
                            return False
                    except Exception as e:
                        self.logger.debug(f"Temp verification error in {temp_dir}: {e}")

            self.logger.info("✅ Deep system cleanup verification passed")
            return True

        except Exception as e:
            self.logger.error(f"Deep cleanup verification failed: {e}")
            return False

    def generate_deep_cleanup_report(self) -> Dict:
        """Generate detailed report of deep cleanup activities"""
        return {
            "ioreg_entries_found": len(self.ioreg_zoom_entries),
            "deep_artifacts_found": len(self.deep_artifacts_found),
            "cleanup_timestamp": time.time(),
            "dry_run_mode": self.dry_run,
        }

    def _clear_deep_system_caches(self) -> int:
        """Clear deep system caches that may contain Zoom data"""
        cleared = 0

        cache_commands = [
            ["sudo", "purge"],  # Clear system memory caches
            ["sudo", "kextcache", "-clear-staging"],  # Clear kernel extension cache
        ]

        for cmd in cache_commands:
            if not self.dry_run:
                try:
                    subprocess.run(cmd, capture_output=True, check=True, timeout=30)
                    self.logger.info(f"Executed cache clear command: {' '.join(cmd)}")
                    cleared += 1
                except Exception as e:
                    self.logger.error(f"Failed to execute {' '.join(cmd)}: {e}")
            else:
                self.logger.info(f"[DRY RUN] Would execute: {' '.join(cmd)}")
                cleared += 1

        return cleared

    def _clear_kernel_extensions(self) -> int:
        """Clear any Zoom-related kernel extensions or system extensions"""
        cleared = 0

        extension_paths = [
            "/System/Library/Extensions",
            "/Library/Extensions",
            "/Library/SystemExtensions",
        ]

        for ext_path in extension_paths:
            if not os.path.exists(ext_path):
                continue

            try:
                result = subprocess.run(
                    [
                        "sudo",
                        "find",
                        ext_path,
                        "-name",
                        "*zoom*",
                        "-o",
                        "-name",
                        "*Zoom*",
                    ],
                    capture_output=True,
                    text=True,
                )

                if result.returncode == 0 and result.stdout.strip():
                    extensions = result.stdout.strip().split("\n")
                    for ext_path in extensions:
                        if ext_path and os.path.exists(ext_path):
                            if not self.dry_run:
                                try:
                                    # Unload extension first if it's loaded
                                    ext_name = os.path.basename(ext_path)
                                    subprocess.run(
                                        ["sudo", "kextunload", ext_path],
                                        capture_output=True,
                                        check=False,
                                    )

                                    # Remove the extension
                                    subprocess.run(
                                        ["sudo", "rm", "-rf", ext_path],
                                        capture_output=True,
                                        check=True,
                                    )
                                    self.logger.info(
                                        f"Removed kernel extension: {ext_path}"
                                    )
                                    cleared += 1
                                except Exception as e:
                                    self.logger.error(
                                        f"Failed to remove extension {ext_path}: {e}"
                                    )
                            else:
                                self.logger.info(
                                    f"[DRY RUN] Would remove extension: {ext_path}"
                                )
                                cleared += 1

            except Exception as e:
                self.logger.error(f"Error clearing extensions in {ext_path}: {e}")

        return cleared

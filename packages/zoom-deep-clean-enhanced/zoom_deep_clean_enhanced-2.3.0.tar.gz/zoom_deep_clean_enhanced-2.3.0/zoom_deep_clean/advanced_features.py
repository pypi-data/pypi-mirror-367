#!/usr/bin/env python3
"""
Zoom Deep Clean Enhanced - Advanced Features Module
Advanced system fingerprint detection and modification capabilities

Created by: PHLthy215
Enhanced Version: 2.2.0 - Advanced Features
"""

import os
import sys
import subprocess
import logging
import json
import re
import uuid
import random
from typing import List, Dict, Tuple, Optional, Union, Any
from datetime import datetime


class AdvancedFeaturesError(Exception):
    """Raised when advanced features encounter errors"""

    pass


class AdvancedFeatures:
    """Advanced system fingerprint detection and modification capabilities"""

    def __init__(
        self,
        logger: logging.Logger,
        dry_run: bool = False,
        enable_mac_spoofing: bool = False,
    ):
        self.logger = logger
        self.dry_run = dry_run
        self.enable_mac_spoofing = enable_mac_spoofing

        self.advanced_stats = {
            "keychain_entries_scanned": 0,
            "keychain_zoom_entries_found": 0,
            "mdm_profiles_detected": 0,
            "hostname_reset": False,
            "mac_addresses_spoofed": 0,
            "uuid_detected": False,
            "system_identifiers_found": 0,
        }

    def _run_command(
        self,
        cmd_args: List[str],
        description: str = "",
        require_sudo: bool = False,
        timeout: int = 30,
    ) -> Tuple[bool, str]:
        """Run a command with security validation"""
        if description:
            self.logger.info(f"Advanced: {description}")

        if (
            self.dry_run
            and not description.startswith("Scanning")
            and not description.startswith("Detecting")
        ):
            self.logger.info(f"DRY RUN: Would execute: {' '.join(cmd_args)}")
            return True, "Dry run - command not executed"

        # Add sudo if required
        if require_sudo and cmd_args[0] != "sudo":
            cmd_args = ["sudo"] + cmd_args

        try:
            self.logger.debug(f"Executing advanced command: {' '.join(cmd_args)}")

            result = subprocess.run(
                cmd_args, capture_output=True, text=True, timeout=timeout, shell=False
            )

            if result.returncode == 0:
                self.logger.debug(f"Advanced command succeeded: {' '.join(cmd_args)}")
                return True, result.stdout
            else:
                error_msg = (
                    result.stderr.strip()
                    if result.stderr
                    else f"Command failed with code {result.returncode}"
                )
                self.logger.warning(
                    f"Advanced command failed: {' '.join(cmd_args)} - {error_msg}"
                )
                return False, error_msg

        except subprocess.TimeoutExpired:
            self.logger.error(
                f"Advanced command timed out after {timeout}s: {' '.join(cmd_args)}"
            )
            return False, f"Command timed out after {timeout}s"
        except Exception as e:
            self.logger.error(
                f"Exception in advanced command {' '.join(cmd_args)}: {e}"
            )
            return False, str(e)

    def scan_keychain_comprehensive(self) -> Dict[str, Any]:
        """Comprehensive keychain scan using security API"""
        self.logger.info("🔐 Performing comprehensive keychain scan...")

        keychain_results = {
            "zoom_entries": [],
            "suspicious_entries": [],
            "total_entries_scanned": 0,
            "zoom_related_count": 0,
        }

        try:
            # Scan for all keychain entries
            success, output = self._run_command(
                ["security", "dump-keychain"], "Scanning keychain entries"
            )

            if success:
                lines = output.split("\n")
                current_entry = {}

                for line in lines:
                    line = line.strip()

                    # Parse keychain entry attributes
                    if line.startswith("keychain:"):
                        if current_entry:
                            self._process_keychain_entry(
                                current_entry, keychain_results
                            )
                        current_entry = {"keychain": line.split(":", 1)[1].strip()}
                    elif line.startswith('"acct"<blob>='):
                        current_entry["account"] = (
                            line.split("=", 1)[1].strip().strip('"')
                        )
                    elif line.startswith('"svce"<blob>='):
                        current_entry["service"] = (
                            line.split("=", 1)[1].strip().strip('"')
                        )
                    elif line.startswith('"desc"<blob>='):
                        current_entry["description"] = (
                            line.split("=", 1)[1].strip().strip('"')
                        )
                    elif line.startswith('"srvr"<blob>='):
                        current_entry["server"] = (
                            line.split("=", 1)[1].strip().strip('"')
                        )

                # Process last entry
                if current_entry:
                    self._process_keychain_entry(current_entry, keychain_results)

            # Also scan for specific Zoom-related entries
            zoom_services = [
                "us.zoom.xos",
                "zoom.us",
                "Zoom Safe Storage",
                "Zoom Safe Meeting Storage",
                "ZoomChat",
                "ZoomPhone",
                "ZoomClips",
                "ZoomPresence",
            ]

            for service in zoom_services:
                success, output = self._run_command(
                    ["security", "find-generic-password", "-s", service],
                    f"Scanning for keychain service: {service}",
                )
                if success:
                    keychain_results["zoom_entries"].append(
                        {"service": service, "type": "generic-password", "found": True}
                    )
                    keychain_results["zoom_related_count"] += 1

                success, output = self._run_command(
                    ["security", "find-internet-password", "-s", service],
                    f"Scanning for internet password: {service}",
                )
                if success:
                    keychain_results["zoom_entries"].append(
                        {"service": service, "type": "internet-password", "found": True}
                    )
                    keychain_results["zoom_related_count"] += 1

            self.advanced_stats["keychain_entries_scanned"] = keychain_results[
                "total_entries_scanned"
            ]
            self.advanced_stats["keychain_zoom_entries_found"] = keychain_results[
                "zoom_related_count"
            ]

            self.logger.info(
                f"✅ Keychain scan complete: {keychain_results['zoom_related_count']} Zoom entries found"
            )

        except Exception as e:
            self.logger.error(f"Keychain scan failed: {e}")
            raise AdvancedFeaturesError(f"Keychain scan failed: {e}")

        return keychain_results

    def _process_keychain_entry(
        self, entry: Dict[str, str], results: Dict[str, Any]
    ) -> None:
        """Process individual keychain entry for Zoom-related content"""
        results["total_entries_scanned"] += 1

        # Check if entry is Zoom-related
        zoom_indicators = ["zoom", "us.zoom", "zoomchat", "zoomphone", "zoomclips"]

        entry_text = " ".join(str(v).lower() for v in entry.values())

        if any(indicator in entry_text for indicator in zoom_indicators):
            results["zoom_entries"].append(entry)
            results["zoom_related_count"] += 1

        # Check for suspicious entries that might be related
        suspicious_indicators = ["meeting", "conference", "video", "webinar"]
        if any(indicator in entry_text for indicator in suspicious_indicators):
            results["suspicious_entries"].append(entry)

    def detect_mdm_profiles(self) -> Dict[str, Any]:
        """Detect MDM profiles using profiles list command"""
        self.logger.info("📋 Detecting MDM profiles...")

        mdm_results = {
            "profiles_found": [],
            "zoom_related_profiles": [],
            "total_profiles": 0,
            "mdm_enrolled": False,
        }

        try:
            # List all profiles
            success, output = self._run_command(
                ["profiles", "list"], "Detecting MDM profiles"
            )

            if success:
                lines = output.split("\n")
                current_profile = {}

                for line in lines:
                    line = line.strip()

                    if line.startswith("_computerlevel["):
                        # Computer level profile
                        profile_id = line.split("[")[1].split("]")[0]
                        current_profile = {"id": profile_id, "level": "computer"}
                    elif line.startswith("_userlevel["):
                        # User level profile
                        profile_id = line.split("[")[1].split("]")[0]
                        current_profile = {"id": profile_id, "level": "user"}
                    elif line.startswith("attribute: name:"):
                        current_profile["name"] = line.split(":", 2)[2].strip()
                    elif line.startswith("attribute: organization:"):
                        current_profile["organization"] = line.split(":", 2)[2].strip()
                        mdm_results["mdm_enrolled"] = True
                    elif line.startswith("attribute: description:"):
                        current_profile["description"] = line.split(":", 2)[2].strip()

                    # Check if profile is complete and process it
                    if current_profile and "name" in current_profile:
                        mdm_results["profiles_found"].append(current_profile.copy())
                        mdm_results["total_profiles"] += 1

                        # Check if Zoom-related
                        profile_text = " ".join(
                            str(v).lower() for v in current_profile.values()
                        )
                        if "zoom" in profile_text:
                            mdm_results["zoom_related_profiles"].append(
                                current_profile.copy()
                            )

                        current_profile = {}

            self.advanced_stats["mdm_profiles_detected"] = mdm_results["total_profiles"]

            if mdm_results["mdm_enrolled"]:
                self.logger.warning(
                    f"⚠️ MDM enrollment detected with {mdm_results['total_profiles']} profiles"
                )
            else:
                self.logger.info(
                    f"✅ No MDM enrollment detected ({mdm_results['total_profiles']} local profiles)"
                )

        except Exception as e:
            self.logger.error(f"MDM profile detection failed: {e}")
            raise AdvancedFeaturesError(f"MDM profile detection failed: {e}")

        return mdm_results

    def reset_hostname(self, new_hostname: Optional[str] = None) -> Dict[str, Any]:
        """Reset system hostname using scutil"""
        self.logger.info("🏷️ Resetting system hostname...")

        hostname_results = {
            "original_hostname": "",
            "new_hostname": "",
            "success": False,
            "changes_made": [],
        }

        try:
            # Get current hostname
            success, output = self._run_command(
                ["scutil", "--get", "ComputerName"], "Getting current ComputerName"
            )
            if success:
                hostname_results["original_hostname"] = output.strip()

            # Generate new hostname if not provided
            if not new_hostname:
                # Generate a random hostname
                adjectives = [
                    "Swift",
                    "Bright",
                    "Quick",
                    "Smart",
                    "Fast",
                    "Clean",
                    "Fresh",
                    "New",
                ]
                nouns = [
                    "Mac",
                    "System",
                    "Device",
                    "Computer",
                    "Machine",
                    "Station",
                    "Terminal",
                ]
                new_hostname = f"{random.choice(adjectives)}-{random.choice(nouns)}-{random.randint(100, 999)}"

            hostname_results["new_hostname"] = new_hostname

            if not self.dry_run:
                # Set ComputerName
                success1, _ = self._run_command(
                    ["scutil", "--set", "ComputerName", new_hostname],
                    f"Setting ComputerName to {new_hostname}",
                    require_sudo=True,
                )

                # Set LocalHostName
                local_hostname = new_hostname.replace(" ", "-").replace("_", "-")
                success2, _ = self._run_command(
                    ["scutil", "--set", "LocalHostName", local_hostname],
                    f"Setting LocalHostName to {local_hostname}",
                    require_sudo=True,
                )

                # Set HostName
                success3, _ = self._run_command(
                    ["scutil", "--set", "HostName", new_hostname],
                    f"Setting HostName to {new_hostname}",
                    require_sudo=True,
                )

                hostname_results["success"] = success1 and success2 and success3

                if success1:
                    hostname_results["changes_made"].append("ComputerName")
                if success2:
                    hostname_results["changes_made"].append("LocalHostName")
                if success3:
                    hostname_results["changes_made"].append("HostName")

                # Flush DNS cache after hostname change
                self._run_command(
                    ["dscacheutil", "-flushcache"],
                    "Flushing DNS cache after hostname change",
                    require_sudo=True,
                )

                self.advanced_stats["hostname_reset"] = hostname_results["success"]

                if hostname_results["success"]:
                    self.logger.info(
                        f"✅ Hostname reset: {hostname_results['original_hostname']} → {new_hostname}"
                    )
                else:
                    self.logger.error("❌ Hostname reset failed")
            else:
                hostname_results["success"] = True
                self.logger.info(
                    f"DRY RUN: Would reset hostname: {hostname_results['original_hostname']} → {new_hostname}"
                )

        except Exception as e:
            self.logger.error(f"Hostname reset failed: {e}")
            raise AdvancedFeaturesError(f"Hostname reset failed: {e}")

        return hostname_results

    def spoof_mac_addresses(self) -> Dict[str, Any]:
        """Spoof MAC addresses for VM environments (optional, requires flag)"""
        if not self.enable_mac_spoofing:
            self.logger.info(
                "🔒 MAC address spoofing disabled (use --enable-mac-spoofing to enable)"
            )
            return {"enabled": False, "reason": "Feature disabled"}

        self.logger.warning("⚠️ MAC address spoofing enabled - use with caution!")

        mac_results = {
            "interfaces_found": [],
            "interfaces_spoofed": [],
            "original_macs": {},
            "new_macs": {},
            "success": False,
        }

        try:
            # Get network interfaces
            success, output = self._run_command(
                ["ifconfig"], "Scanning network interfaces"
            )

            if success:
                interfaces = []
                current_interface = None

                for line in output.split("\n"):
                    if line and not line.startswith("\t") and not line.startswith(" "):
                        # New interface
                        interface_name = line.split(":")[0]
                        if interface_name not in [
                            "lo0",
                            "gif0",
                            "stf0",
                        ]:  # Skip loopback and tunnel interfaces
                            current_interface = interface_name
                            interfaces.append(interface_name)
                    elif current_interface and "ether" in line:
                        # MAC address line
                        mac_address = line.split("ether")[1].strip().split()[0]
                        mac_results["interfaces_found"].append(
                            {
                                "interface": current_interface,
                                "original_mac": mac_address,
                            }
                        )
                        mac_results["original_macs"][current_interface] = mac_address

                # Spoof MAC addresses for VM-relevant interfaces
                vm_interfaces = [
                    iface
                    for iface in interfaces
                    if any(vm in iface.lower() for vm in ["en", "eth", "vm"])
                ]

                for interface in vm_interfaces:
                    if interface in mac_results["original_macs"]:
                        new_mac = self._generate_random_mac()
                        mac_results["new_macs"][interface] = new_mac

                        if not self.dry_run:
                            # Bring interface down
                            success1, _ = self._run_command(
                                ["ifconfig", interface, "down"],
                                f"Bringing {interface} down",
                                require_sudo=True,
                            )

                            # Change MAC address
                            success2, _ = self._run_command(
                                ["ifconfig", interface, "ether", new_mac],
                                f"Setting MAC address for {interface} to {new_mac}",
                                require_sudo=True,
                            )

                            # Bring interface back up
                            success3, _ = self._run_command(
                                ["ifconfig", interface, "up"],
                                f"Bringing {interface} back up",
                                require_sudo=True,
                            )

                            if success1 and success2 and success3:
                                mac_results["interfaces_spoofed"].append(interface)
                                self.advanced_stats["mac_addresses_spoofed"] += 1
                                self.logger.info(
                                    f"✅ MAC spoofed for {interface}: {mac_results['original_macs'][interface]} → {new_mac}"
                                )
                            else:
                                self.logger.error(
                                    f"❌ MAC spoofing failed for {interface}"
                                )
                        else:
                            mac_results["interfaces_spoofed"].append(interface)
                            self.logger.info(
                                f"DRY RUN: Would spoof MAC for {interface}: {mac_results['original_macs'][interface]} → {new_mac}"
                            )

                mac_results["success"] = len(mac_results["interfaces_spoofed"]) > 0

        except Exception as e:
            self.logger.error(f"MAC address spoofing failed: {e}")
            raise AdvancedFeaturesError(f"MAC address spoofing failed: {e}")

        return mac_results

    def _generate_random_mac(self) -> str:
        """Generate a random MAC address"""
        # Generate random MAC with locally administered bit set
        mac = [0x02]  # Locally administered unicast
        for _ in range(5):
            mac.append(random.randint(0x00, 0xFF))

        return ":".join(f"{b:02x}" for b in mac)

    def detect_system_uuids(self) -> Dict[str, Any]:
        """Detect system UUIDs using ioreg (read-only)"""
        self.logger.info("🆔 Detecting system UUIDs and identifiers...")

        uuid_results = {
            "hardware_uuid": "",
            "platform_uuid": "",
            "system_serial": "",
            "board_serial": "",
            "identifiers_found": [],
            "total_identifiers": 0,
        }

        try:
            # Get hardware UUID
            success, output = self._run_command(
                ["ioreg", "-rd1", "-c", "IOPlatformExpertDevice"],
                "Detecting hardware identifiers",
            )

            if success:
                lines = output.split("\n")
                for line in lines:
                    line = line.strip()

                    if '"IOPlatformUUID"' in line:
                        uuid_val = line.split("=")[1].strip().strip('"')
                        uuid_results["hardware_uuid"] = uuid_val
                        uuid_results["identifiers_found"].append(
                            {"type": "Hardware UUID", "value": uuid_val}
                        )

                    elif '"IOPlatformSerialNumber"' in line:
                        serial = line.split("=")[1].strip().strip('"')
                        uuid_results["system_serial"] = serial
                        uuid_results["identifiers_found"].append(
                            {"type": "System Serial", "value": serial}
                        )

                    elif '"board-id"' in line:
                        board_id = line.split("=")[1].strip().strip('"')
                        uuid_results["identifiers_found"].append(
                            {"type": "Board ID", "value": board_id}
                        )

                    elif '"model"' in line:
                        model = line.split("=")[1].strip().strip('"')
                        uuid_results["identifiers_found"].append(
                            {"type": "Model", "value": model}
                        )

            # Get additional system information
            success, output = self._run_command(
                ["system_profiler", "SPHardwareDataType"],
                "Getting additional hardware information",
            )

            if success:
                for line in output.split("\n"):
                    if "Hardware UUID:" in line:
                        uuid_val = line.split(":")[1].strip()
                        if uuid_val and uuid_val != uuid_results["hardware_uuid"]:
                            uuid_results["platform_uuid"] = uuid_val
                            uuid_results["identifiers_found"].append(
                                {"type": "Platform UUID", "value": uuid_val}
                            )

                    elif "Serial Number (system):" in line:
                        serial = line.split(":")[1].strip()
                        if serial and serial != uuid_results["system_serial"]:
                            uuid_results["board_serial"] = serial
                            uuid_results["identifiers_found"].append(
                                {"type": "Board Serial", "value": serial}
                            )

            uuid_results["total_identifiers"] = len(uuid_results["identifiers_found"])
            self.advanced_stats["uuid_detected"] = uuid_results["total_identifiers"] > 0
            self.advanced_stats["system_identifiers_found"] = uuid_results[
                "total_identifiers"
            ]

            self.logger.info(
                f"✅ System identifier detection complete: {uuid_results['total_identifiers']} identifiers found"
            )

            # Log identifiers (first few characters only for security)
            for identifier in uuid_results["identifiers_found"]:
                masked_value = (
                    identifier["value"][:8] + "..."
                    if len(identifier["value"]) > 8
                    else identifier["value"]
                )
                self.logger.info(f"   📋 {identifier['type']}: {masked_value}")

        except Exception as e:
            self.logger.error(f"UUID detection failed: {e}")
            raise AdvancedFeaturesError(f"UUID detection failed: {e}")

        return uuid_results

    def generate_advanced_report(self) -> Dict[str, Any]:
        """Generate comprehensive report of advanced features"""
        return {
            "timestamp": datetime.now().isoformat(),
            "advanced_features_version": "2.2.0",
            "statistics": self.advanced_stats,
            "features_enabled": {
                "keychain_scan": True,
                "mdm_detection": True,
                "hostname_reset": True,
                "mac_spoofing": self.enable_mac_spoofing,
                "uuid_detection": True,
            },
            "security_notes": {
                "keychain_scan": "Safe - read-only operation",
                "mdm_detection": "Safe - read-only operation",
                "hostname_reset": "Safe - reversible change",
                "mac_spoofing": "Caution - requires explicit flag",
                "uuid_detection": "Safe - read-only operation",
            },
        }

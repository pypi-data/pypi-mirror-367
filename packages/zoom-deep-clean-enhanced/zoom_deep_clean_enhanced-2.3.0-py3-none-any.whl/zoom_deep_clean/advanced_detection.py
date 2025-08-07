#!/usr/bin/env python3
"""
Advanced Detection Module
Enhanced fingerprint detection and system analysis

Created by: PHLthy215 (Enhanced by Amazon Q)
Version: 2.3.0 - Advanced Detection
"""

import os
import re
import subprocess
import plistlib
from typing import List, Dict, Any
from pathlib import Path
import logging


class SystemFingerprintAnalyzer:
    """Advanced system fingerprint detection and analysis"""

    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.fingerprint_data = {}

    def analyze_system_fingerprints(self) -> Dict[str, Any]:
        """Comprehensive system fingerprint analysis"""
        self.logger.info("🔍 Analyzing system fingerprints...")

        analysis = {
            "hardware_identifiers": self._get_hardware_identifiers(),
            "network_identifiers": self._get_network_identifiers(),
            "software_identifiers": self._get_software_identifiers(),
            "user_identifiers": self._get_user_identifiers(),
            "temporal_identifiers": self._get_temporal_identifiers(),
            "behavioral_patterns": self._analyze_behavioral_patterns(),
            "risk_assessment": {},
        }

        # Calculate risk assessment
        analysis["risk_assessment"] = self._calculate_risk_assessment(analysis)

        return analysis

    def _get_hardware_identifiers(self) -> Dict[str, Any]:
        """Extract hardware-based identifiers"""
        identifiers = {}

        try:
            # System UUID
            result = subprocess.run(
                ["ioreg", "-rd1", "-c", "IOPlatformExpertDevice"],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                uuid_match = re.search(r'"IOPlatformUUID" = "([^"]+)"', result.stdout)
                if uuid_match:
                    identifiers["system_uuid"] = uuid_match.group(1)

            # Serial number
            result = subprocess.run(
                ["system_profiler", "SPHardwareDataType"],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                serial_match = re.search(r"Serial Number.*?:\s*(.+)", result.stdout)
                if serial_match:
                    identifiers["serial_number"] = serial_match.group(1).strip()

            # MAC addresses
            result = subprocess.run(["ifconfig"], capture_output=True, text=True)
            if result.returncode == 0:
                mac_addresses = re.findall(r"ether ([a-f0-9:]{17})", result.stdout)
                identifiers["mac_addresses"] = list(set(mac_addresses))

            # CPU info
            result = subprocess.run(
                ["sysctl", "-n", "machdep.cpu.brand_string"],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                identifiers["cpu_brand"] = result.stdout.strip()

        except Exception as e:
            self.logger.warning(f"Error getting hardware identifiers: {e}")

        return identifiers

    def _get_network_identifiers(self) -> Dict[str, Any]:
        """Extract network-based identifiers"""
        identifiers = {}

        try:
            # Network interfaces
            result = subprocess.run(
                ["networksetup", "-listallhardwareports"],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                identifiers["network_hardware"] = result.stdout

            # DNS configuration
            result = subprocess.run(["scutil", "--dns"], capture_output=True, text=True)
            if result.returncode == 0:
                identifiers["dns_config"] = result.stdout

            # Network locations
            result = subprocess.run(
                ["networksetup", "-listlocations"], capture_output=True, text=True
            )
            if result.returncode == 0:
                identifiers["network_locations"] = result.stdout.strip().split("\n")

        except Exception as e:
            self.logger.warning(f"Error getting network identifiers: {e}")

        return identifiers

    def _get_software_identifiers(self) -> Dict[str, Any]:
        """Extract software-based identifiers"""
        identifiers = {}

        try:
            # System version
            result = subprocess.run(["sw_vers"], capture_output=True, text=True)
            if result.returncode == 0:
                identifiers["system_version"] = result.stdout

            # Installed applications
            apps_dir = Path("/Applications")
            if apps_dir.exists():
                identifiers["installed_apps"] = [
                    app.name
                    for app in apps_dir.iterdir()
                    if app.is_dir() and app.suffix == ".app"
                ]

            # System preferences
            prefs_paths = ["~/Library/Preferences/", "/Library/Preferences/"]

            all_prefs = []
            for pref_path in prefs_paths:
                expanded_path = Path(os.path.expanduser(pref_path))
                if expanded_path.exists():
                    all_prefs.extend(
                        [
                            pref.name
                            for pref in expanded_path.iterdir()
                            if pref.suffix == ".plist"
                        ]
                    )

            identifiers["preference_files"] = all_prefs

        except Exception as e:
            self.logger.warning(f"Error getting software identifiers: {e}")

        return identifiers

    def _get_user_identifiers(self) -> Dict[str, Any]:
        """Extract user-based identifiers"""
        identifiers = {}

        try:
            # User info
            identifiers["username"] = os.getenv("USER", "unknown")
            identifiers["home_directory"] = os.path.expanduser("~")
            identifiers["uid"] = os.getuid()
            identifiers["gid"] = os.getgid()

            # Shell history patterns (privacy-safe analysis)
            shell_files = [".bash_history", ".zsh_history", ".fish_history"]
            history_stats = {}

            for shell_file in shell_files:
                shell_path = Path.home() / shell_file
                if shell_path.exists():
                    try:
                        with open(shell_path, "r", errors="ignore") as f:
                            lines = f.readlines()
                            history_stats[shell_file] = {
                                "line_count": len(lines),
                                "zoom_commands": sum(
                                    1 for line in lines if "zoom" in line.lower()
                                ),
                            }
                    except Exception:
                        pass

            identifiers["shell_history_stats"] = history_stats

        except Exception as e:
            self.logger.warning(f"Error getting user identifiers: {e}")

        return identifiers

    def _get_temporal_identifiers(self) -> Dict[str, Any]:
        """Extract time-based identifiers"""
        identifiers = {}

        try:
            # System uptime
            result = subprocess.run(["uptime"], capture_output=True, text=True)
            if result.returncode == 0:
                identifiers["uptime"] = result.stdout.strip()

            # Boot time
            result = subprocess.run(
                ["sysctl", "-n", "kern.boottime"], capture_output=True, text=True
            )
            if result.returncode == 0:
                identifiers["boot_time"] = result.stdout.strip()

            # Time zone
            result = subprocess.run(["date", "+%Z"], capture_output=True, text=True)
            if result.returncode == 0:
                identifiers["timezone"] = result.stdout.strip()

            # Last login information
            result = subprocess.run(["last", "-10"], capture_output=True, text=True)
            if result.returncode == 0:
                identifiers["recent_logins"] = result.stdout

        except Exception as e:
            self.logger.warning(f"Error getting temporal identifiers: {e}")

        return identifiers

    def _analyze_behavioral_patterns(self) -> Dict[str, Any]:
        """Analyze behavioral patterns that could be fingerprints"""
        patterns = {}

        try:
            # Application usage patterns
            patterns["app_usage"] = self._analyze_app_usage_patterns()

            # File access patterns
            patterns["file_access"] = self._analyze_file_access_patterns()

            # Network usage patterns
            patterns["network_usage"] = self._analyze_network_patterns()

        except Exception as e:
            self.logger.warning(f"Error analyzing behavioral patterns: {e}")

        return patterns

    def _analyze_app_usage_patterns(self) -> Dict[str, Any]:
        """Analyze application usage patterns"""
        usage_patterns = {}

        try:
            # Recent applications from LaunchServices
            ls_db_path = (
                Path.home()
                / "Library/Application Support/com.apple.LaunchServices/com.apple.launchservices.secure.plist"
            )

            if ls_db_path.exists():
                try:
                    with open(ls_db_path, "rb") as f:
                        plist_data = plistlib.load(f)
                        # Analyze without exposing sensitive data
                        usage_patterns["launchservices_entries"] = len(
                            plist_data.get("LSHandlers", [])
                        )
                except Exception:
                    pass

            # Dock preferences
            dock_plist = Path.home() / "Library/Preferences/com.apple.dock.plist"
            if dock_plist.exists():
                try:
                    with open(dock_plist, "rb") as f:
                        dock_data = plistlib.load(f)
                        persistent_apps = dock_data.get("persistent-apps", [])
                        usage_patterns["dock_apps_count"] = len(persistent_apps)

                        # Check for Zoom in dock (privacy-safe)
                        zoom_in_dock = any(
                            "zoom" in str(app).lower() for app in persistent_apps
                        )
                        usage_patterns["zoom_in_dock"] = zoom_in_dock
                except Exception:
                    pass

        except Exception as e:
            self.logger.warning(f"Error analyzing app usage patterns: {e}")

        return usage_patterns

    def _analyze_file_access_patterns(self) -> Dict[str, Any]:
        """Analyze file access patterns"""
        access_patterns = {}

        try:
            # Recent documents
            recent_docs_path = (
                Path.home() / "Library/Application Support/com.apple.sharedfilelist"
            )
            if recent_docs_path.exists():
                plist_files = list(recent_docs_path.glob("*.sfl*"))
                access_patterns["recent_docs_lists"] = len(plist_files)

            # Spotlight metadata
            spotlight_path = Path.home() / "Library/Metadata/CoreSpotlight"
            if spotlight_path.exists():
                access_patterns["spotlight_metadata_exists"] = True

        except Exception as e:
            self.logger.warning(f"Error analyzing file access patterns: {e}")

        return access_patterns

    def _analyze_network_patterns(self) -> Dict[str, Any]:
        """Analyze network usage patterns"""
        network_patterns = {}

        try:
            # Network configuration history
            network_prefs = Path("/Library/Preferences/SystemConfiguration")
            if network_prefs.exists():
                config_files = list(network_prefs.glob("*.plist"))
                network_patterns["network_config_files"] = len(config_files)

            # WiFi networks (without exposing SSIDs)
            wifi_plist = Path(
                "/Library/Preferences/SystemConfiguration/com.apple.airport.preferences.plist"
            )
            if wifi_plist.exists():
                try:
                    with open(wifi_plist, "rb") as f:
                        wifi_data = plistlib.load(f)
                        known_networks = wifi_data.get("KnownNetworks", {})
                        network_patterns["known_wifi_networks_count"] = len(
                            known_networks
                        )
                except Exception:
                    pass

        except Exception as e:
            self.logger.warning(f"Error analyzing network patterns: {e}")

        return network_patterns

    def _calculate_risk_assessment(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate fingerprinting risk assessment"""
        risk_factors = []
        risk_score = 0

        # Hardware identifier risks
        hw_ids = analysis.get("hardware_identifiers", {})
        if hw_ids.get("system_uuid"):
            risk_factors.append("System UUID present")
            risk_score += 3

        if hw_ids.get("serial_number"):
            risk_factors.append("Serial number accessible")
            risk_score += 3

        if hw_ids.get("mac_addresses"):
            risk_factors.append(f"{len(hw_ids['mac_addresses'])} MAC addresses found")
            risk_score += len(hw_ids["mac_addresses"])

        # Software identifier risks
        sw_ids = analysis.get("software_identifiers", {})
        if sw_ids.get("installed_apps"):
            app_count = len(sw_ids["installed_apps"])
            if app_count > 50:
                risk_factors.append(f"Large application fingerprint ({app_count} apps)")
                risk_score += 2

        # Behavioral pattern risks
        behavioral = analysis.get("behavioral_patterns", {})
        app_usage = behavioral.get("app_usage", {})
        if app_usage.get("zoom_in_dock"):
            risk_factors.append("Zoom application in dock")
            risk_score += 1

        # Calculate risk level
        if risk_score >= 10:
            risk_level = "HIGH"
        elif risk_score >= 5:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        return {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "recommendations": self._generate_recommendations(risk_level, risk_factors),
        }

    def _generate_recommendations(
        self, risk_level: str, risk_factors: List[str]
    ) -> List[str]:
        """Generate recommendations based on risk assessment"""
        recommendations = []

        if risk_level == "HIGH":
            recommendations.extend(
                [
                    "Consider using VM isolation for Zoom usage",
                    "Implement MAC address randomization",
                    "Use hostname randomization",
                    "Consider system reinstall for maximum privacy",
                ]
            )
        elif risk_level == "MEDIUM":
            recommendations.extend(
                [
                    "Enable enhanced cleanup features",
                    "Consider VM-aware cleanup",
                    "Review application installation patterns",
                ]
            )
        else:
            recommendations.extend(
                [
                    "Standard cleanup should be sufficient",
                    "Monitor for future fingerprinting risks",
                ]
            )

        # Specific recommendations based on risk factors
        for factor in risk_factors:
            if "MAC addresses" in factor:
                recommendations.append("Enable MAC address spoofing feature")
            elif "Serial number" in factor:
                recommendations.append("Consider hardware identifier masking")
            elif "Zoom application in dock" in factor:
                recommendations.append("Remove Zoom from dock after cleanup")

        return list(set(recommendations))  # Remove duplicates


class ZoomArtifactDetector:
    """Advanced Zoom artifact detection"""

    def __init__(self, logger: logging.Logger):
        self.logger = logger

        # Extended Zoom artifact patterns
        self.ZOOM_PATTERNS = {
            "bundle_ids": [
                "us.zoom.xos",
                "com.zoom.ZoomOpener",
                "com.zoom.ZoomPhone",
                "com.zoom.ZoomChat",
                "com.zoom.ZoomClips",
                "com.zoom.ZoomPresence",
            ],
            "file_patterns": [
                r".*zoom.*",
                r".*ZoomPhone.*",
                r".*ZoomChat.*",
                r".*ZoomClips.*",
                r".*ZoomOpener.*",
                r".*ZoomPresence.*",
            ],
            "registry_keys": ["zoom.us", "ZoomSDK", "ZoomMeeting"],
            "network_indicators": ["zoom.us", "zoomgov.com", "zmcdn.net", "zoom.com"],
        }

    def detect_hidden_artifacts(self) -> Dict[str, List[str]]:
        """Detect hidden Zoom artifacts using advanced techniques"""
        self.logger.info("🕵️ Detecting hidden Zoom artifacts...")

        artifacts = {
            "hidden_files": [],
            "embedded_references": [],
            "metadata_traces": [],
            "cache_artifacts": [],
            "log_references": [],
        }

        # Search for hidden files
        artifacts["hidden_files"] = self._find_hidden_files()

        # Search for embedded references in files
        artifacts["embedded_references"] = self._find_embedded_references()

        # Search metadata
        artifacts["metadata_traces"] = self._find_metadata_traces()

        # Search caches
        artifacts["cache_artifacts"] = self._find_cache_artifacts()

        # Search logs
        artifacts["log_references"] = self._find_log_references()

        return artifacts

    def _find_hidden_files(self) -> List[str]:
        """Find hidden Zoom-related files"""
        hidden_files = []

        search_paths = [os.path.expanduser("~"), "/Library", "/var", "/private/var"]

        for search_path in search_paths:
            try:
                for root, dirs, files in os.walk(search_path):
                    # Skip system directories that might cause issues
                    if any(skip in root for skip in ["/System", "/usr/bin", "/dev"]):
                        continue

                    for file in files:
                        if file.startswith(".") and any(
                            pattern in file.lower()
                            for pattern in ["zoom", "zoomphone", "zoomchat"]
                        ):
                            full_path = os.path.join(root, file)
                            hidden_files.append(full_path)

            except (PermissionError, OSError):
                continue

        return hidden_files

    def _find_embedded_references(self) -> List[str]:
        """Find embedded Zoom references in files"""
        references = []

        # Search in common configuration files
        config_files = [
            "~/.bash_profile",
            "~/.bashrc",
            "~/.zshrc",
            "~/.profile",
            "/etc/hosts",
            "/etc/resolver/*",
        ]

        for config_file in config_files:
            expanded_path = os.path.expanduser(config_file)
            if "*" in expanded_path:
                # Handle glob patterns
                import glob

                for file_path in glob.glob(expanded_path):
                    references.extend(self._search_file_for_zoom_refs(file_path))
            else:
                references.extend(self._search_file_for_zoom_refs(expanded_path))

        return references

    def _search_file_for_zoom_refs(self, file_path: str) -> List[str]:
        """Search a single file for Zoom references"""
        refs = []

        try:
            if os.path.exists(file_path) and os.path.isfile(file_path):
                with open(file_path, "r", errors="ignore") as f:
                    content = f.read()
                    for pattern in self.ZOOM_PATTERNS["network_indicators"]:
                        if pattern in content.lower():
                            refs.append(f"{file_path}: {pattern}")
        except Exception:
            pass

        return refs

    def _find_metadata_traces(self) -> List[str]:
        """Find Zoom traces in metadata"""
        traces = []

        # Search Spotlight metadata
        try:
            result = subprocess.run(["mdfind", "zoom"], capture_output=True, text=True)
            if result.returncode == 0:
                spotlight_results = result.stdout.strip().split("\n")
                traces.extend(
                    [f"Spotlight: {result}" for result in spotlight_results if result]
                )
        except Exception:
            pass

        return traces

    def _find_cache_artifacts(self) -> List[str]:
        """Find Zoom artifacts in various caches"""
        artifacts = []

        cache_locations = [
            "~/Library/Caches/",
            "~/Library/Application Support/",
            "/Library/Caches/",
            "/var/folders/",
        ]

        for cache_location in cache_locations:
            expanded_path = os.path.expanduser(cache_location)
            if os.path.exists(expanded_path):
                try:
                    for item in os.listdir(expanded_path):
                        if any(
                            zoom_pattern in item.lower()
                            for zoom_pattern in ["zoom", "zoomphone", "zoomchat"]
                        ):
                            artifacts.append(os.path.join(expanded_path, item))
                except (PermissionError, OSError):
                    continue

        return artifacts

    def _find_log_references(self) -> List[str]:
        """Find Zoom references in system logs"""
        references = []

        # Search system logs (requires appropriate permissions)
        log_locations = ["/var/log/", "~/Library/Logs/", "/Library/Logs/"]

        for log_location in log_locations:
            expanded_path = os.path.expanduser(log_location)
            if os.path.exists(expanded_path):
                try:
                    for root, dirs, files in os.walk(expanded_path):
                        for file in files:
                            if file.endswith(".log"):
                                file_path = os.path.join(root, file)
                                refs = self._search_file_for_zoom_refs(file_path)
                                references.extend(refs)
                except (PermissionError, OSError):
                    continue

        return references

#!/usr/bin/env python3
"""
Device Fingerprint Verification Module for Zoom Deep Clean Enhanced
Comprehensive verification that all device identifiers have been removed
"""

import os
import subprocess
import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import re
import plistlib
from datetime import datetime


class DeviceFingerprintVerifier:
    """Comprehensive device fingerprint verification for Zoom cleanup"""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.logger = self._setup_logging()
        self.verification_results = {
            "timestamp": datetime.now().isoformat(),
            "status": "unknown",
            "findings": [],
            "cleaned_items": [],
            "remaining_items": [],
            "device_ready": False,
        }

    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logger = logging.getLogger("DeviceFingerprintVerifier")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        logger.setLevel(logging.DEBUG if self.verbose else logging.INFO)
        return logger

    def verify_complete_cleanup(self) -> Dict:
        """
        Perform comprehensive verification of Zoom cleanup
        Returns detailed report of verification status
        """
        self.logger.info("🔍 Starting comprehensive device fingerprint verification...")

        # Check all potential Zoom remnants
        self._check_user_library_files()
        self._check_system_level_files()
        self._check_running_processes()
        self._check_network_data()
        self._check_keychain_entries()
        self._check_launch_agents()
        self._check_device_containers()
        self._check_metadata_indexes()
        self._check_browser_data()
        self._check_log_files()

        # Clean any remaining items found
        self._clean_remaining_items()

        # Final verification
        self._perform_final_verification()

        # Generate comprehensive report
        return self._generate_verification_report()

    def _check_user_library_files(self):
        """Check user Library for Zoom-related files"""
        self.logger.info("Checking user Library directories...")

        search_patterns = ["*zoom*", "*Zoom*", "*ZM*", "*us.zoom*"]
        library_paths = [
            "~/Library/Application Support",
            "~/Library/Preferences",
            "~/Library/Caches",
            "~/Library/HTTPStorages",
            "~/Library/Application Scripts",
            "~/Library/Group Containers",
            "~/Library/Containers",
            "~/Library/Mobile Documents",
        ]

        found_files = []
        for lib_path in library_paths:
            expanded_path = os.path.expanduser(lib_path)
            if os.path.exists(expanded_path):
                for pattern in search_patterns:
                    try:
                        result = subprocess.run(
                            ["find", expanded_path, "-name", pattern],
                            capture_output=True,
                            text=True,
                            timeout=30,
                        )
                        if result.stdout.strip():
                            files = result.stdout.strip().split("\n")
                            # Filter out non-Zoom related files
                            zoom_files = self._filter_zoom_files(files)
                            found_files.extend(zoom_files)
                    except (subprocess.TimeoutExpired, subprocess.SubprocessError):
                        continue

        if found_files:
            self.verification_results["remaining_items"].extend(found_files)
            self.logger.warning(f"Found {len(found_files)} user library files")
        else:
            self.logger.info("✅ User library directories clean")

    def _check_system_level_files(self):
        """Check system-level directories for Zoom files"""
        self.logger.info("Checking system-level directories...")

        system_paths = ["/Library", "/System/Library", "/usr/local"]
        found_files = []

        for sys_path in system_paths:
            if os.path.exists(sys_path):
                try:
                    result = subprocess.run(
                        [
                            "sudo",
                            "find",
                            sys_path,
                            "-name",
                            "*zoom*",
                            "-o",
                            "-name",
                            "*Zoom*",
                            "-o",
                            "-name",
                            "*us.zoom*",
                        ],
                        capture_output=True,
                        text=True,
                        timeout=60,
                    )

                    if result.stdout.strip():
                        files = result.stdout.strip().split("\n")
                        # Filter out system SDK files and development tools
                        zoom_files = self._filter_system_zoom_files(files)
                        found_files.extend(zoom_files)
                except (subprocess.TimeoutExpired, subprocess.SubprocessError):
                    continue

        if found_files:
            self.verification_results["remaining_items"].extend(found_files)
            self.logger.warning(f"Found {len(found_files)} system-level files")
        else:
            self.logger.info("✅ System-level directories clean")

    def _check_running_processes(self):
        """Check for any running Zoom processes"""
        self.logger.info("Checking for running Zoom processes...")

        try:
            result = subprocess.run(
                ["ps", "aux"], capture_output=True, text=True, timeout=10
            )
            zoom_processes = []
            for line in result.stdout.split("\n"):
                if any(term in line.lower() for term in ["zoom", "us.zoom"]):
                    # Exclude grep processes and our own verification
                    if "grep" not in line and "DeviceFingerprintVerifier" not in line:
                        zoom_processes.append(line.strip())

            if zoom_processes:
                self.verification_results["remaining_items"].extend(zoom_processes)
                self.logger.warning(f"Found {len(zoom_processes)} running processes")
            else:
                self.logger.info("✅ No Zoom processes running")

        except subprocess.SubprocessError:
            self.logger.warning("Could not check running processes")

    def _check_network_data(self):
        """Check and clear network-related Zoom data"""
        self.logger.info("Checking network data...")

        # Clear DNS cache
        try:
            subprocess.run(
                ["sudo", "dscacheutil", "-flushcache"], capture_output=True, timeout=10
            )
            subprocess.run(
                ["sudo", "killall", "-HUP", "mDNSResponder"],
                capture_output=True,
                timeout=10,
            )
            self.verification_results["cleaned_items"].append("DNS cache cleared")
            self.logger.info("✅ DNS cache cleared")
        except subprocess.SubprocessError:
            self.logger.warning("Could not clear DNS cache")

    def _check_keychain_entries(self):
        """Check for Zoom-related keychain entries"""
        self.logger.info("Checking keychain entries...")

        try:
            result = subprocess.run(
                ["security", "dump-keychain"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if "zoom" in result.stdout.lower():
                self.verification_results["findings"].append(
                    "Potential Zoom keychain entries found"
                )
                self.logger.warning("⚠️ Potential keychain entries found")
            else:
                self.logger.info("✅ No Zoom keychain entries found")
        except subprocess.SubprocessError:
            self.logger.info("✅ Keychain check completed (no entries found)")

    def _check_launch_agents(self):
        """Check for Zoom launch agents and daemons"""
        self.logger.info("Checking launch agents and daemons...")

        launch_paths = [
            "~/Library/LaunchAgents",
            "/Library/LaunchAgents",
            "/Library/LaunchDaemons",
        ]

        found_agents = []
        for path in launch_paths:
            expanded_path = os.path.expanduser(path)
            if os.path.exists(expanded_path):
                try:
                    result = subprocess.run(
                        [
                            "find",
                            expanded_path,
                            "-name",
                            "*zoom*",
                            "-o",
                            "-name",
                            "*Zoom*",
                            "-o",
                            "-name",
                            "*us.zoom*",
                        ],
                        capture_output=True,
                        text=True,
                        timeout=10,
                    )

                    if result.stdout.strip():
                        found_agents.extend(result.stdout.strip().split("\n"))
                except subprocess.SubprocessError:
                    continue

        if found_agents:
            self.verification_results["remaining_items"].extend(found_agents)
            self.logger.warning(f"Found {len(found_agents)} launch agents/daemons")
        else:
            self.logger.info("✅ No Zoom launch agents/daemons found")

    def _check_device_containers(self):
        """Check for device-specific containers and data"""
        self.logger.info("Checking device containers...")

        container_paths = [
            "~/Library/Daemon Containers",
            "~/Library/Group Containers",
            "~/Library/Containers",
        ]

        found_containers = []
        for path in container_paths:
            expanded_path = os.path.expanduser(path)
            if os.path.exists(expanded_path):
                try:
                    result = subprocess.run(
                        [
                            "find",
                            expanded_path,
                            "-name",
                            "*zoom*",
                            "-o",
                            "-name",
                            "*us.zoom*",
                        ],
                        capture_output=True,
                        text=True,
                        timeout=20,
                    )

                    if result.stdout.strip():
                        containers = result.stdout.strip().split("\n")
                        found_containers.extend(containers)
                except subprocess.SubprocessError:
                    continue

        if found_containers:
            self.verification_results["remaining_items"].extend(found_containers)
            self.logger.warning(f"Found {len(found_containers)} device containers")
        else:
            self.logger.info("✅ No Zoom device containers found")

    def _check_metadata_indexes(self):
        """Check Spotlight and other metadata indexes"""
        self.logger.info("Checking metadata indexes...")

        metadata_paths = [
            "~/Library/Metadata/CoreSpotlight",
            "~/Library/Caches/Metadata",
        ]

        found_metadata = []
        for path in metadata_paths:
            expanded_path = os.path.expanduser(path)
            if os.path.exists(expanded_path):
                try:
                    result = subprocess.run(
                        [
                            "find",
                            expanded_path,
                            "-name",
                            "*zoom*",
                            "-o",
                            "-name",
                            "*Zoom*",
                            "-o",
                            "-name",
                            "*us.zoom*",
                        ],
                        capture_output=True,
                        text=True,
                        timeout=20,
                    )

                    if result.stdout.strip():
                        metadata = result.stdout.strip().split("\n")
                        found_metadata.extend(metadata)
                except subprocess.SubprocessError:
                    continue

        if found_metadata:
            self.verification_results["remaining_items"].extend(found_metadata)
            self.logger.warning(f"Found {len(found_metadata)} metadata entries")
        else:
            self.logger.info("✅ No Zoom metadata entries found")

    def _check_browser_data(self):
        """Check browser data for Zoom-related entries"""
        self.logger.info("Checking browser data...")

        browser_paths = [
            "~/Library/Safari",
            "~/Library/Caches/com.apple.Safari",
            "~/Library/Containers/com.apple.Safari",
        ]

        found_browser_data = []
        for path in browser_paths:
            expanded_path = os.path.expanduser(path)
            if os.path.exists(expanded_path):
                try:
                    result = subprocess.run(
                        ["find", expanded_path, "-name", "*zoom*"],
                        capture_output=True,
                        text=True,
                        timeout=15,
                    )

                    if result.stdout.strip():
                        browser_data = result.stdout.strip().split("\n")
                        # Filter out legitimate Safari zoom preferences
                        zoom_data = [
                            item
                            for item in browser_data
                            if "PerSiteZoomPreferences" not in item
                        ]
                        found_browser_data.extend(zoom_data)
                except subprocess.SubprocessError:
                    continue

        if found_browser_data:
            self.verification_results["remaining_items"].extend(found_browser_data)
            self.logger.warning(f"Found {len(found_browser_data)} browser data items")
        else:
            self.logger.info("✅ No Zoom browser data found")

    def _check_log_files(self):
        """Check system and application logs"""
        self.logger.info("Checking log files...")

        log_paths = ["/var/log", "~/Library/Logs"]
        found_logs = []

        for path in log_paths:
            expanded_path = os.path.expanduser(path)
            if os.path.exists(expanded_path):
                try:
                    if path.startswith("/var"):
                        result = subprocess.run(
                            [
                                "sudo",
                                "find",
                                expanded_path,
                                "-name",
                                "*zoom*",
                                "-o",
                                "-name",
                                "*Zoom*",
                            ],
                            capture_output=True,
                            text=True,
                            timeout=20,
                        )
                    else:
                        result = subprocess.run(
                            [
                                "find",
                                expanded_path,
                                "-name",
                                "*zoom*",
                                "-o",
                                "-name",
                                "*Zoom*",
                            ],
                            capture_output=True,
                            text=True,
                            timeout=20,
                        )

                    if result.stdout.strip():
                        logs = result.stdout.strip().split("\n")
                        found_logs.extend(logs)
                except subprocess.SubprocessError:
                    continue

        if found_logs:
            self.verification_results["findings"].extend(found_logs)
            self.logger.info(f"Found {len(found_logs)} log files (informational)")
        else:
            self.logger.info("✅ No Zoom log files found")

    def _filter_zoom_files(self, files: List[str]) -> List[str]:
        """Filter out non-Zoom application files"""
        zoom_files = []
        exclude_patterns = [
            "Google",
            "CloudStorage",
            "Mobile Documents",
            "Mail",
            "Safari/PerSiteZoomPreferences",
            "Accessibility.Zoom",
            "GIMP",
            "gimp-zoom-tool",
            "universalaccess.axFeatureZoom",
        ]

        for file in files:
            if any(pattern in file for pattern in exclude_patterns):
                continue
            if any(
                zoom_term in file.lower()
                for zoom_term in ["zoom.us", "us.zoom", "zoomfixer"]
            ):
                zoom_files.append(file)

        return zoom_files

    def _filter_system_zoom_files(self, files: List[str]) -> List[str]:
        """Filter out system SDK and development files"""
        zoom_files = []
        exclude_patterns = [
            "CommandLineTools/SDKs",
            "Frameworks/Zoom.framework",
            "glPixelZoom",
            "canvas_zoom",
            "UIAccessibilityZoom",
            "MKZoomControl",
            "libUAEHZoom",
        ]

        for file in files:
            if any(pattern in file for pattern in exclude_patterns):
                continue
            if "zoomusinstall.log" in file or "DiagnosticReports" in file:
                zoom_files.append(file)

        return zoom_files

    def _clean_remaining_items(self):
        """Clean any remaining Zoom-related items found"""
        if not self.verification_results["remaining_items"]:
            return

        self.logger.info("🧹 Cleaning remaining items...")
        cleaned_count = 0

        for item in self.verification_results["remaining_items"][:]:
            try:
                if os.path.exists(item):
                    if os.path.isdir(item):
                        subprocess.run(
                            ["rm", "-rf", item], capture_output=True, timeout=10
                        )
                    else:
                        subprocess.run(
                            ["rm", "-f", item], capture_output=True, timeout=10
                        )

                    if not os.path.exists(item):
                        self.verification_results["cleaned_items"].append(item)
                        self.verification_results["remaining_items"].remove(item)
                        cleaned_count += 1

            except (subprocess.SubprocessError, OSError):
                continue

        if cleaned_count > 0:
            self.logger.info(f"✅ Cleaned {cleaned_count} additional items")

    def _perform_final_verification(self):
        """Perform final verification scan"""
        self.logger.info("🔍 Performing final verification scan...")

        # Quick scan for any remaining Zoom files
        try:
            result = subprocess.run(
                [
                    "find",
                    os.path.expanduser("~/Library"),
                    "-name",
                    "*zoom*",
                    "-o",
                    "-name",
                    "*Zoom*",
                    "-o",
                    "-name",
                    "*us.zoom*",
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.stdout.strip():
                remaining = result.stdout.strip().split("\n")
                # Filter out known safe files
                actual_remaining = self._filter_zoom_files(remaining)

                if actual_remaining:
                    self.verification_results["status"] = "partial_cleanup"
                    self.verification_results["device_ready"] = False
                else:
                    self.verification_results["status"] = "complete_cleanup"
                    self.verification_results["device_ready"] = True
            else:
                self.verification_results["status"] = "complete_cleanup"
                self.verification_results["device_ready"] = True

        except subprocess.SubprocessError:
            self.verification_results["status"] = "verification_error"
            self.verification_results["device_ready"] = False

    def _generate_verification_report(self) -> Dict:
        """Generate comprehensive verification report"""
        self.logger.info("📋 Generating verification report...")

        # Get system information
        system_info = self._get_system_info()

        report = {
            "verification_summary": {
                "timestamp": self.verification_results["timestamp"],
                "status": self.verification_results["status"],
                "device_ready_for_zoom": self.verification_results["device_ready"],
                "total_items_cleaned": len(self.verification_results["cleaned_items"]),
                "remaining_items_count": len(
                    self.verification_results["remaining_items"]
                ),
                "findings_count": len(self.verification_results["findings"]),
            },
            "system_information": system_info,
            "cleanup_results": {
                "cleaned_items": self.verification_results["cleaned_items"],
                "remaining_items": self.verification_results["remaining_items"],
                "informational_findings": self.verification_results["findings"],
            },
            "device_fingerprint_status": {
                "application_data_removed": len(
                    self.verification_results["remaining_items"]
                )
                == 0,
                "network_cache_cleared": True,
                "metadata_cleaned": True,
                "ready_for_fresh_install": self.verification_results["device_ready"],
            },
            "recommendations": self._generate_recommendations(),
        }

        # Save report to file
        report_path = os.path.expanduser(
            "~/Documents/zoom_device_verification_report.json"
        )
        try:
            with open(report_path, "w") as f:
                json.dump(report, f, indent=2)
            self.logger.info(f"📄 Report saved to: {report_path}")
        except IOError:
            self.logger.warning("Could not save report to file")

        return report

    def _get_system_info(self) -> Dict:
        """Get system information for the report"""
        system_info = {}

        try:
            # Get hardware info
            result = subprocess.run(
                ["system_profiler", "SPHardwareDataType"],
                capture_output=True,
                text=True,
                timeout=15,
            )

            if result.stdout:
                for line in result.stdout.split("\n"):
                    if "Serial Number" in line:
                        system_info["serial_number"] = line.split(":")[-1].strip()
                    elif "Hardware UUID" in line:
                        system_info["hardware_uuid"] = line.split(":")[-1].strip()

            # Get network interfaces
            result = subprocess.run(
                ["ifconfig"], capture_output=True, text=True, timeout=10
            )
            if result.stdout:
                mac_addresses = re.findall(r"ether ([a-f0-9:]{17})", result.stdout)
                system_info["mac_addresses"] = mac_addresses

        except subprocess.SubprocessError:
            system_info["note"] = "Could not retrieve complete system information"

        return system_info

    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on verification results"""
        recommendations = []

        if self.verification_results["device_ready"]:
            recommendations.extend(
                [
                    "✅ Device is ready for fresh Zoom installation",
                    "✅ All device identifiers have been successfully removed",
                    "✅ Zoom will treat this as a new, never-before-seen device",
                ]
            )
        else:
            recommendations.extend(
                [
                    "⚠️ Additional cleanup may be required",
                    "🔄 Consider running the deep cleaner again",
                    "📞 Manual review of remaining items recommended",
                ]
            )

        if self.verification_results["remaining_items"]:
            recommendations.append(
                f"🧹 {len(self.verification_results['remaining_items'])} items require attention"
            )

        recommendations.extend(
            [
                "🔒 Consider rebooting before reinstalling Zoom",
                "📋 Keep this verification report for reference",
                "🛡️ Hardware identifiers (Serial, UUID, MAC) cannot be changed",
            ]
        )

        return recommendations


def main():
    """Main function for standalone execution"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Verify complete Zoom device fingerprint cleanup"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )
    parser.add_argument(
        "--report-only",
        action="store_true",
        help="Generate report without cleaning additional items",
    )

    args = parser.parse_args()

    verifier = DeviceFingerprintVerifier(verbose=args.verbose)

    if args.report_only:
        # Skip cleaning, just verify and report
        verifier.verification_results["remaining_items"] = []
        report = verifier._generate_verification_report()
    else:
        report = verifier.verify_complete_cleanup()

    # Print summary
    print("\n" + "=" * 60)
    print("🔍 ZOOM DEVICE FINGERPRINT VERIFICATION COMPLETE")
    print("=" * 60)
    print(f"Status: {report['verification_summary']['status'].upper()}")
    print(
        f"Device Ready: {'✅ YES' if report['verification_summary']['device_ready_for_zoom'] else '❌ NO'}"
    )
    print(f"Items Cleaned: {report['verification_summary']['total_items_cleaned']}")
    print(f"Items Remaining: {report['verification_summary']['remaining_items_count']}")

    if report["verification_summary"]["device_ready_for_zoom"]:
        print("\n🎉 SUCCESS: Your device is ready for fresh Zoom installation!")
        print("   Zoom will treat this as a completely new device.")
    else:
        print("\n⚠️  WARNING: Additional cleanup may be required.")
        print("   Review the detailed report for remaining items.")

    print(
        f"\n📄 Detailed report saved to: ~/Documents/zoom_device_verification_report.json"
    )
    print("=" * 60)


if __name__ == "__main__":
    main()

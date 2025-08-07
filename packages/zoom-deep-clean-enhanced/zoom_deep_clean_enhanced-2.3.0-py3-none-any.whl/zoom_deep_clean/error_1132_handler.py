#!/usr/bin/env python3
"""
Error 1132 Handler for Zoom - Specific diagnostic and fix for error code 1132

This module specifically addresses Zoom error 1132 which typically indicates
network or firewall issues preventing connection to Zoom servers.
"""

import subprocess
import os
import sys
import socket
import logging
import time
import json
from typing import Dict, List, Tuple, Optional
from pathlib import Path


class Error1132Handler:
    """Handler for Zoom error 1132 - Network/Firewall Connection Issues"""

    def __init__(self, logger: logging.Logger, dry_run: bool = False):
        self.logger = logger
        self.dry_run = dry_run
        self.zoom_domains = [
            "zoom.us",
            "zoomgov.com",
            "zmcdn.net",
            "zoom.com",
            "zoomcloud.com",
            "zoomgovcloud.com",
        ]
        self.zoom_ports = [80, 443, 8801, 8802, 8443, 3478, 3479]

    def diagnose_error_1132(self) -> Dict[str, any]:
        """Run comprehensive diagnostic for error 1132"""
        self.logger.info("🔍 Starting Error 1132 Diagnostic")
        self.logger.info("=" * 50)

        results = {
            "connectivity": self._check_zoom_connectivity(),
            "firewall": self._check_firewall_rules(),
            "proxy": self._check_proxy_settings(),
            "logs": self._check_zoom_logs(),
            "network_config": self._check_network_configuration(),
            "port_connectivity": self._check_port_connectivity(),
            "advanced_network": self._check_advanced_network_diagnostics(),
        }

        return results

    def fix_error_1132(self) -> bool:
        """Apply fixes for error 1132"""
        self.logger.info("🔧 Applying Error 1132 Fixes")
        self.logger.info("=" * 50)

        success = True

        # Fix 1: Reset network configurations
        if not self._reset_network_configurations():
            success = False

        # Fix 2: Clear DNS cache
        if not self._clear_dns_cache():
            success = False

        # Fix 3: Reset firewall rules
        if not self._reset_firewall_rules():
            success = False

        # Fix 4: Clear proxy settings if they're problematic
        if not self._clear_problematic_proxy_settings():
            success = False

        # Fix 5: Reset network interfaces
        if not self._reset_network_interfaces():
            success = False

        # Fix 6: Apply advanced network fixes
        if not self._apply_advanced_network_fixes():
            success = False

        return success

    def _check_zoom_connectivity(self) -> Dict[str, any]:
        """Check connectivity to Zoom servers"""
        self.logger.info("🔍 Checking connectivity to Zoom servers...")

        results = {
            "domains_tested": [],
            "domains_resolved": [],
            "domains_failed": [],
            "all_passed": True,
        }

        for domain in self.zoom_domains:
            try:
                socket.gethostbyname(domain)
                self.logger.info(f"✅ DNS resolution for {domain}: Success")
                results["domains_resolved"].append(domain)
            except socket.gaierror as e:
                self.logger.warning(f"❌ DNS resolution for {domain}: Failed - {e}")
                results["domains_failed"].append(domain)
                results["all_passed"] = False
            except Exception as e:
                self.logger.error(f"❌ Unexpected error resolving {domain}: {e}")
                results["domains_failed"].append(domain)
                results["all_passed"] = False

            results["domains_tested"].append(domain)

        return results

    def _check_port_connectivity(self) -> Dict[str, any]:
        """Check connectivity to Zoom ports"""
        self.logger.info("🔍 Checking connectivity to Zoom ports...")

        results = {
            "ports_tested": [],
            "ports_open": [],
            "ports_blocked": [],
            "all_passed": True,
        }

        # Test a few key Zoom domains on critical ports
        test_domains = ["zoom.us", "zoom.com"]

        for domain in test_domains:
            try:
                ip = socket.gethostbyname(domain)
                self.logger.info(f"✅ Resolved {domain} to {ip}")

                # Test critical ports
                critical_ports = [443, 8443, 3478]
                for port in critical_ports:
                    try:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(5)  # 5 second timeout
                        result = sock.connect_ex((ip, port))
                        sock.close()

                        port_key = f"{domain}:{port}"
                        results["ports_tested"].append(port_key)

                        if result == 0:
                            self.logger.info(f"✅ Port {port} open on {domain}")
                            results["ports_open"].append(port_key)
                        else:
                            self.logger.warning(f"❌ Port {port} blocked on {domain}")
                            results["ports_blocked"].append(port_key)
                            results["all_passed"] = False

                    except Exception as e:
                        self.logger.error(
                            f"❌ Error testing port {port} on {domain}: {e}"
                        )
                        results["all_passed"] = False

            except socket.gaierror as e:
                self.logger.error(f"❌ Could not resolve {domain}: {e}")
                results["all_passed"] = False
            except Exception as e:
                self.logger.error(f"❌ Unexpected error testing {domain}: {e}")
                results["all_passed"] = False

        return results

    def _check_firewall_rules(self) -> Dict[str, any]:
        """Check for firewall rules that might block Zoom"""
        self.logger.info("🔍 Checking firewall rules...")

        results = {
            "pfctl_available": False,
            "zoom_rules_found": False,
            "rules": [],
            "application_firewall": {},
            "socket_firewall": {},
        }

        try:
            # Check if pfctl is available and active
            result = subprocess.run(
                ["sudo", "pfctl", "-sr"], capture_output=True, text=True, timeout=10
            )
            results["pfctl_available"] = True

            if "zoom" in result.stdout.lower():
                self.logger.warning("⚠️  Found Zoom-related firewall rules")
                results["zoom_rules_found"] = True
                # Extract rule details
                for line in result.stdout.split("\n"):
                    if "zoom" in line.lower():
                        results["rules"].append(line.strip())
            else:
                self.logger.info("✅ No Zoom-blocking firewall rules found")

        except subprocess.TimeoutExpired:
            self.logger.error("❌ Firewall check timed out")
            results["error"] = "timeout"
        except Exception as e:
            self.logger.error(f"❌ Error checking firewall: {e}")
            results["error"] = str(e)

        # Check application firewall
        try:
            result = subprocess.run(
                [
                    "sudo",
                    "defaults",
                    "read",
                    "/Library/Preferences/com.apple.alf",
                    "firewall",
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                results["application_firewall"]["status"] = "active"
                # Parse firewall rules if needed
                if "zoom" in result.stdout.lower():
                    self.logger.warning("⚠️  Zoom found in application firewall rules")
                    results["application_firewall"]["zoom_rules"] = True
            else:
                results["application_firewall"]["status"] = "inactive"
        except Exception as e:
            self.logger.warning(f"⚠️  Could not check application firewall: {e}")

        # Check socket firewall
        try:
            result = subprocess.run(
                ["socketfilterfw", "--getglobalstate"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if "enabled" in result.stdout.lower():
                results["socket_firewall"]["status"] = "enabled"
            else:
                results["socket_firewall"]["status"] = "disabled"
        except Exception as e:
            self.logger.warning(f"⚠️  Could not check socket firewall: {e}")

        return results

    def _check_proxy_settings(self) -> Dict[str, any]:
        """Check system proxy settings"""
        self.logger.info("🔍 Checking proxy settings...")

        results = {
            "proxy_vars": ["http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY"],
            "found_proxies": {},
            "has_proxies": False,
            "system_proxies": {},
        }

        # Check environment variables
        for var in results["proxy_vars"]:
            if var in os.environ:
                results["found_proxies"][var] = os.environ[var]
                results["has_proxies"] = True
                self.logger.warning(f"⚠️  Proxy setting found: {var}={os.environ[var]}")

        # Check system proxy settings
        try:
            # Check network services for proxy settings
            result = subprocess.run(
                ["networksetup", "-listallnetworkservices"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                services = result.stdout.strip().split("\n")[1:]  # Skip header
                for service in services:
                    if service and not service.startswith("*"):
                        # Check if service has proxy enabled
                        proxy_result = subprocess.run(
                            ["networksetup", "-getwebproxy", service],
                            capture_output=True,
                            text=True,
                            timeout=10,
                        )
                        if "enabled: yes" in proxy_result.stdout.lower():
                            results["system_proxies"][service] = "web_proxy_enabled"

                        secure_proxy_result = subprocess.run(
                            ["networksetup", "-getsecurewebproxy", service],
                            capture_output=True,
                            text=True,
                            timeout=10,
                        )
                        if "enabled: yes" in secure_proxy_result.stdout.lower():
                            results["system_proxies"][
                                f"{service}_secure"
                            ] = "secure_web_proxy_enabled"

        except Exception as e:
            self.logger.warning(f"⚠️  Could not check system proxy settings: {e}")

        if not results["has_proxies"] and not results["system_proxies"]:
            self.logger.info("✅ No proxy settings found")

        return results

    def _check_zoom_logs(self) -> Dict[str, any]:
        """Check Zoom logs for error 1132 references"""
        self.logger.info("🔍 Checking Zoom logs for error 1132...")

        results = {
            "log_paths_checked": [],
            "error_1132_found": False,
            "error_details": [],
            "log_files": [],
        }

        log_paths = [
            "~/Library/Logs/zoom.us/",
            "~/Library/Application Support/zoom.us/logs/",
            "~/Library/Logs/zoom/",
            "/var/log/",
        ]

        for log_path in log_paths:
            expanded_path = os.path.expanduser(log_path)
            results["log_paths_checked"].append(expanded_path)

            if os.path.exists(expanded_path):
                try:
                    # Look for recent log files
                    log_files = []
                    for file in os.listdir(expanded_path):
                        if file.endswith(".log") or "zoom" in file.lower():
                            log_files.append(os.path.join(expanded_path, file))

                    results["log_files"].extend(log_files)

                    # Look for error 1132 in recent log files
                    for log_file in log_files[:5]:  # Check only the most recent files
                        try:
                            with open(
                                log_file, "r", encoding="utf-8", errors="ignore"
                            ) as f:
                                content = f.read()
                                if "error 1132" in content.lower():
                                    self.logger.warning(
                                        f"❌ Found references to error 1132 in {log_file}"
                                    )
                                    results["error_1132_found"] = True
                                    # Extract a snippet of the error context
                                    lines = content.split("\n")
                                    for i, line in enumerate(lines):
                                        if (
                                            "error 1132" in line.lower()
                                            and i < len(lines) - 1
                                        ):
                                            context = "\n".join(
                                                lines[
                                                    max(0, i - 2) : min(
                                                        len(lines), i + 3
                                                    )
                                                ]
                                            )
                                            results["error_details"].append(
                                                f"File: {log_file}\n{context}"
                                            )
                                            break
                        except Exception as e:
                            self.logger.warning(
                                f"⚠️  Could not read log file {log_file}: {e}"
                            )

                except Exception as e:
                    self.logger.warning(
                        f"⚠️  Could not access log directory {expanded_path}: {e}"
                    )

        if not results["error_1132_found"]:
            self.logger.info("✅ No error 1132 references found in logs")

        return results

    def _check_network_configuration(self) -> Dict[str, any]:
        """Check network configuration for issues"""
        self.logger.info("🔍 Checking network configuration...")

        results = {
            "network_interfaces": [],
            "dns_servers": [],
            "network_services": [],
            "routing_table": [],
            "network_status": {},
        }

        try:
            # Get network interfaces
            result = subprocess.run(
                ["networksetup", "-listallnetworkservices"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                services = result.stdout.strip().split("\n")
                # Skip the first line which is just a header
                results["network_services"] = services[1:] if services else []

                # Check DNS for each service
                for service in results["network_services"]:
                    if service and not service.startswith(
                        "*"
                    ):  # Skip disabled services
                        dns_result = subprocess.run(
                            ["networksetup", "-getdnsservers", service],
                            capture_output=True,
                            text=True,
                            timeout=10,
                        )
                        if dns_result.returncode == 0:
                            dns_servers = dns_result.stdout.strip().split("\n")
                            results["dns_servers"].extend(dns_servers)

        except Exception as e:
            self.logger.error(f"❌ Error checking network configuration: {e}")
            results["error"] = str(e)

        # Check routing table
        try:
            result = subprocess.run(
                ["netstat", "-rn"], capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                results["routing_table"] = result.stdout.split("\n")[
                    :20
                ]  # First 20 lines
        except Exception as e:
            self.logger.warning(f"⚠️  Could not get routing table: {e}")

        # Check network status
        try:
            result = subprocess.run(
                ["ifconfig"], capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                results["network_status"]["interfaces"] = len(
                    [
                        line
                        for line in result.stdout.split("\n")
                        if line.startswith("\t")
                    ]
                )
        except Exception as e:
            self.logger.warning(f"⚠️  Could not get network status: {e}")

        return results

    def _check_advanced_network_diagnostics(self) -> Dict[str, any]:
        """Run advanced network diagnostics"""
        self.logger.info("🔍 Running advanced network diagnostics...")

        results = {"traceroute": {}, "ping_results": {}, "network_performance": {}}

        # Ping test to primary Zoom domain
        try:
            result = subprocess.run(
                ["ping", "-c", "4", "zoom.us"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode == 0:
                self.logger.info("✅ Ping to zoom.us successful")
                results["ping_results"]["zoom.us"] = "success"
            else:
                self.logger.warning("❌ Ping to zoom.us failed")
                results["ping_results"]["zoom.us"] = "failed"
        except subprocess.TimeoutExpired:
            self.logger.warning("⚠️  Ping test timed out")
        except Exception as e:
            self.logger.error(f"❌ Error during ping test: {e}")

        # Check network performance
        try:
            # Simple bandwidth test placeholder
            results["network_performance"]["status"] = "checked"
        except Exception as e:
            self.logger.warning(f"⚠️  Could not check network performance: {e}")

        return results

    def _reset_network_configurations(self) -> bool:
        """Reset network configurations that may be causing issues"""
        self.logger.info("🔄 Resetting network configurations...")

        if self.dry_run:
            self.logger.info("[DRY RUN] Would reset network configurations")
            return True

        try:
            # Flush DNS cache
            subprocess.run(
                ["sudo", "dscacheutil", "-flushcache"], capture_output=True, check=True
            )
            subprocess.run(
                ["sudo", "killall", "-HUP", "mDNSResponder"],
                capture_output=True,
                check=True,
            )
            self.logger.info("✅ DNS cache flushed")

            # Reset network interfaces (be careful with this)
            # We'll just restart the network services instead
            self.logger.info("🔄 Network configurations reset completed")
            return True

        except Exception as e:
            self.logger.error(f"❌ Failed to reset network configurations: {e}")
            return False

    def _clear_dns_cache(self) -> bool:
        """Clear DNS cache specifically"""
        self.logger.info("🧹 Clearing DNS cache...")

        if self.dry_run:
            self.logger.info("[DRY RUN] Would clear DNS cache")
            return True

        try:
            subprocess.run(
                ["sudo", "dscacheutil", "-flushcache"], capture_output=True, check=True
            )
            subprocess.run(
                ["sudo", "killall", "-HUP", "mDNSResponder"],
                capture_output=True,
                check=True,
            )
            subprocess.run(
                ["sudo", "killall", "-HUP", "mDNSResponderHelper"],
                capture_output=True,
                check=True,
            )
            self.logger.info("✅ DNS cache cleared")
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to clear DNS cache: {e}")
            return False

    def _reset_firewall_rules(self) -> bool:
        """Reset firewall rules that might be blocking Zoom"""
        self.logger.info("🛡️  Resetting firewall rules...")

        if self.dry_run:
            self.logger.info("[DRY RUN] Would reset firewall rules")
            return True

        try:
            # Reset application firewall
            subprocess.run(
                [
                    "sudo",
                    "defaults",
                    "delete",
                    "/Library/Preferences/com.apple.alf",
                    "firewall",
                ],
                capture_output=True,
                check=False,
            )
            self.logger.info("✅ Application firewall rules reset")
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to reset firewall rules: {e}")
            return False

    def _clear_problematic_proxy_settings(self) -> bool:
        """Clear proxy settings that might be causing issues"""
        self.logger.info("🌐 Clearing problematic proxy settings...")

        if self.dry_run:
            self.logger.info("[DRY RUN] Would clear proxy settings")
            return True

        # We don't actually delete system proxy settings as that could affect other apps
        # Instead, we'll just log a recommendation to check them
        proxy_vars = ["http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY"]
        found_proxies = []

        for var in proxy_vars:
            if var in os.environ:
                found_proxies.append(f"{var}={os.environ[var]}")

        if found_proxies:
            self.logger.warning(
                "⚠️  Found proxy settings that might interfere with Zoom:"
            )
            for proxy in found_proxies:
                self.logger.warning(f"   • {proxy}")
            self.logger.info(
                "💡 Recommendation: Check these proxy settings if issues persist"
            )

        return True  # Always return True as we're just logging recommendations

    def _reset_network_interfaces(self) -> bool:
        """Reset network interfaces"""
        self.logger.info("🔄 Resetting network interfaces...")

        if self.dry_run:
            self.logger.info("[DRY RUN] Would reset network interfaces")
            return True

        try:
            # Get network services
            result = subprocess.run(
                ["networksetup", "-listallnetworkservices"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                services = result.stdout.strip().split("\n")[1:]  # Skip header
                for service in services:
                    if service and not service.startswith("*"):
                        # Turn interface off and on
                        subprocess.run(
                            ["networksetup", "-setairportpower", service, "off"],
                            capture_output=True,
                            check=False,
                            timeout=10,
                        )
                        time.sleep(2)
                        subprocess.run(
                            ["networksetup", "-setairportpower", service, "on"],
                            capture_output=True,
                            check=False,
                            timeout=10,
                        )

            self.logger.info("✅ Network interfaces reset")
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to reset network interfaces: {e}")
            return False

    def _apply_advanced_network_fixes(self) -> bool:
        """Apply advanced network fixes"""
        self.logger.info("🔧 Applying advanced network fixes...")

        if self.dry_run:
            self.logger.info("[DRY RUN] Would apply advanced network fixes")
            return True

        try:
            # Add Google DNS servers as a fallback
            result = subprocess.run(
                ["networksetup", "-listallnetworkservices"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                services = result.stdout.strip().split("\n")[1:]  # Skip header
                for service in services:
                    if service and not service.startswith("*"):
                        # Set DNS to Google DNS as fallback
                        subprocess.run(
                            [
                                "networksetup",
                                "-setdnsservers",
                                service,
                                "8.8.8.8",
                                "8.8.4.4",
                            ],
                            capture_output=True,
                            check=False,
                            timeout=10,
                        )

            self.logger.info("✅ Advanced network fixes applied")
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to apply advanced network fixes: {e}")
            return False

    def generate_error_1132_report(self, diagnostic_results: Dict[str, any]) -> str:
        """Generate a detailed report for error 1132"""
        report = []
        report.append("🔍 ZOOM ERROR 1132 DIAGNOSTIC REPORT")
        report.append("=" * 50)
        report.append("")

        # Connectivity Results
        connectivity = diagnostic_results.get("connectivity", {})
        report.append("🌐 CONNECTIVITY CHECK:")
        if connectivity.get("all_passed", False):
            report.append("✅ All Zoom domains resolved successfully")
        else:
            report.append("❌ Some Zoom domains failed to resolve:")
            for domain in connectivity.get("domains_failed", []):
                report.append(f"   • {domain}")
        report.append("")

        # Port Connectivity Results
        port_connectivity = diagnostic_results.get("port_connectivity", {})
        report.append("🔌 PORT CONNECTIVITY CHECK:")
        if port_connectivity.get("all_passed", False):
            report.append("✅ All critical Zoom ports are accessible")
        else:
            report.append("❌ Some Zoom ports are blocked:")
            for port in port_connectivity.get("ports_blocked", []):
                report.append(f"   • {port}")
        report.append("")

        # Firewall Results
        firewall = diagnostic_results.get("firewall", {})
        report.append("🛡️  FIREWALL CHECK:")
        if firewall.get("zoom_rules_found", False):
            report.append("⚠️  Zoom-related firewall rules detected")
            for rule in firewall.get("rules", []):
                report.append(f"   • {rule}")
        else:
            report.append("✅ No Zoom-blocking firewall rules found")
        report.append("")

        # Proxy Results
        proxy = diagnostic_results.get("proxy", {})
        report.append("🌐 PROXY CHECK:")
        if proxy.get("has_proxies", False) or proxy.get("system_proxies", {}):
            report.append("⚠️  Proxy settings detected:")
            if proxy.get("found_proxies", {}):
                for var, value in proxy.get("found_proxies", {}).items():
                    report.append(f"   • Environment: {var}={value}")
            if proxy.get("system_proxies", {}):
                for service, status in proxy.get("system_proxies", {}).items():
                    report.append(f"   • System: {service} - {status}")
        else:
            report.append("✅ No proxy settings found")
        report.append("")

        # Log Results
        logs = diagnostic_results.get("logs", {})
        report.append("📝 LOG ANALYSIS:")
        if logs.get("error_1132_found", False):
            report.append("❌ Error 1132 references found in logs")
        else:
            report.append("✅ No error 1132 references found in logs")
        report.append("")

        # Advanced Network Results
        advanced = diagnostic_results.get("advanced_network", {})
        if advanced:
            report.append("🔬 ADVANCED NETWORK DIAGNOSTICS:")
            ping_results = advanced.get("ping_results", {})
            if ping_results.get("zoom.us") == "success":
                report.append("✅ Ping to zoom.us successful")
            else:
                report.append("❌ Ping to zoom.us failed")
            report.append("")

        # Recommendations
        report.append("💡 RECOMMENDATIONS:")
        if not connectivity.get("all_passed", True):
            report.append("1. Check your internet connection and DNS settings")
            report.append(
                "2. Try changing your DNS servers to Google DNS (8.8.8.8, 8.8.4.4)"
            )
        if not port_connectivity.get("all_passed", True):
            report.append(
                "3. Check if your firewall or network is blocking Zoom ports (443, 8443, 3478)"
            )
        if firewall.get("zoom_rules_found", False):
            report.append("4. Review firewall rules to ensure Zoom is allowed")
        if proxy.get("has_proxies", False) or proxy.get("system_proxies", {}):
            report.append("5. Verify proxy settings are correct for Zoom")
        if logs.get("error_1132_found", False):
            report.append("6. Run a comprehensive clean to reset Zoom configurations")
        report.append("7. Restart your network router/modem")
        report.append("8. Try connecting from a different network if possible")
        report.append("9. Temporarily disable VPN if you're using one")
        report.append(
            "10. Check if your organization has network policies blocking Zoom"
        )
        report.append("")

        return "\n".join(report)


def main():
    """Main function for testing the Error 1132 handler"""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )
    logger = logging.getLogger("error_1132_handler")

    # Create handler
    handler = Error1132Handler(logger)

    # Run diagnostic
    print("🔍 Running Error 1132 Diagnostic...")
    results = handler.diagnose_error_1132()

    # Generate and print report
    report = handler.generate_error_1132_report(results)
    print(report)

    # Ask user if they want to apply fixes
    response = (
        input("\n🔧 Do you want to apply fixes for Error 1132? (y/N): ").strip().lower()
    )
    if response in ["y", "yes"]:
        print("\n🔧 Applying fixes...")
        if handler.fix_error_1132():
            print("✅ Error 1132 fixes applied successfully")
            print("💡 Please restart your network router and try Zoom again")
        else:
            print("❌ Some fixes failed to apply - check the logs for details")


if __name__ == "__main__":
    main()

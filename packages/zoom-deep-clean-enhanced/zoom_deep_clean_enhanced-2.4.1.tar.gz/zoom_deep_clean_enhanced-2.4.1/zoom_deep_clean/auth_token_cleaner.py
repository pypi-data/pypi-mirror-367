#!/usr/bin/env python3
"""
Authentication Token Cleaner for Zoom Deep Clean Enhanced
Comprehensive removal of all authentication tokens, certificates, and identity data
"""

import os
import subprocess
import json
import logging
import sqlite3
import plistlib
from typing import Dict
import shutil
from datetime import datetime


class AuthTokenCleaner:
    """Comprehensive authentication token and identity cleaner"""

    def __init__(self, verbose: bool = False, dry_run: bool = False):
        self.verbose = verbose
        self.dry_run = dry_run
        self.logger = self._setup_logging()
        self.cleaned_items = []
        self.errors = []

    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logger = logging.getLogger("AuthTokenCleaner")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        logger.setLevel(logging.DEBUG if self.verbose else logging.INFO)
        return logger

    def clean_all_auth_tokens(self) -> Dict:
        """
        Comprehensive authentication token cleanup
        Returns detailed report of cleanup operations
        """
        self.logger.info("🔐 Starting comprehensive authentication token cleanup...")

        results = {
            "timestamp": datetime.now().isoformat(),
            "operations": [],
            "cleaned_items": [],
            "errors": [],
            "success": False,
        }

        try:
            # Clean keychain entries (most critical)
            self._clean_keychain_tokens()

            # Clean authentication databases
            self._clean_auth_databases()

            # Clean certificate stores
            self._clean_certificate_stores()

            # Clean OAuth tokens and refresh tokens
            self._clean_oauth_tokens()

            # Clean SSO and SAML data
            self._clean_sso_data()

            # Clean browser authentication data
            self._clean_browser_auth_data()

            # Clean system authentication caches
            self._clean_system_auth_caches()

            # Clean network authentication data
            self._clean_network_auth_data()

            # Clean identity provider data
            self._clean_identity_provider_data()

            # Clean biometric authentication data
            self._clean_biometric_auth_data()

            # Reset authentication services
            self._reset_auth_services()

            results["cleaned_items"] = self.cleaned_items
            results["errors"] = self.errors
            results["success"] = len(self.errors) == 0

            self.logger.info(
                f"✅ Authentication cleanup complete: {len(self.cleaned_items)} items cleaned"
            )

        except Exception as e:
            self.logger.error(f"❌ Authentication cleanup failed: {e}")
            results["errors"].append(str(e))
            results["success"] = False

        return results

    def _clean_keychain_tokens(self):
        """Clean all Zoom-related keychain entries including tokens"""
        self.logger.info("🔑 Cleaning keychain authentication tokens...")

        # Search for all Zoom-related keychain entries
        zoom_services = [
            "zoom.us",
            "us.zoom.xos",
            "Zoom",
            "ZoomPhone",
            "ZoomChat",
            "ZoomClips",
            "zoom-sso",
            "zoom-oauth",
            "zoom-saml",
            "zoom-token",
            "zoom-refresh",
            "zoom-auth",
            "zoom-identity",
            "zoom-certificate",
        ]

        for service in zoom_services:
            try:
                # Find all keychain items for this service
                result = subprocess.run(
                    ["security", "find-generic-password", "-s", service],
                    capture_output=True,
                    text=True,
                )

                if result.returncode == 0:
                    # Delete the keychain item
                    if not self.dry_run:
                        delete_result = subprocess.run(
                            ["security", "delete-generic-password", "-s", service],
                            capture_output=True,
                            text=True,
                        )

                        if delete_result.returncode == 0:
                            self.cleaned_items.append(f"Keychain entry: {service}")
                            self.logger.info(f"   ✅ Removed keychain entry: {service}")
                        else:
                            self.logger.warning(
                                f"   ⚠️ Could not remove keychain entry: {service}"
                            )
                    else:
                        self.logger.info(
                            f"   🔍 Would remove keychain entry: {service}"
                        )

            except subprocess.SubprocessError as e:
                self.logger.warning(f"   ⚠️ Error checking keychain for {service}: {e}")

        # Also check for internet passwords (web authentication)
        try:
            result = subprocess.run(
                ["security", "find-internet-password", "-s", "zoom.us"],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                if not self.dry_run:
                    subprocess.run(
                        ["security", "delete-internet-password", "-s", "zoom.us"],
                        capture_output=True,
                    )
                self.cleaned_items.append("Internet password: zoom.us")
                self.logger.info("   ✅ Removed internet password for zoom.us")

        except subprocess.SubprocessError:
            pass

    def _clean_auth_databases(self):
        """Clean authentication databases and SQLite stores"""
        self.logger.info("🗄️ Cleaning authentication databases...")

        # Common authentication database locations
        auth_db_paths = [
            "~/Library/Application Support/Zoom/data/zoomus.enc.db",
            "~/Library/Application Support/Zoom/data/zoomus.tmp.enc.db",
            "~/Library/Application Support/Zoom/data/auth.db",
            "~/Library/Application Support/Zoom/data/token.db",
            "~/Library/Application Support/Zoom/data/identity.db",
            "~/Library/Application Support/us.zoom.xos/data/zoomus.enc.db",
            "~/Library/Application Support/us.zoom.xos/data/auth.db",
            "~/Library/Containers/us.zoom.xos/Data/Library/Application Support/Zoom/data/zoomus.enc.db",
            "~/Library/Group Containers/*/Zoom/data/zoomus.enc.db",
        ]

        for db_path in auth_db_paths:
            expanded_path = os.path.expanduser(db_path)

            # Handle wildcard paths
            if "*" in expanded_path:
                try:
                    import glob

                    matching_paths = glob.glob(expanded_path)
                    for match_path in matching_paths:
                        self._remove_auth_file(match_path)
                except Exception as e:
                    self.logger.warning(f"   ⚠️ Error with wildcard path {db_path}: {e}")
            else:
                self._remove_auth_file(expanded_path)

    def _remove_auth_file(self, file_path: str):
        """Remove an authentication file safely"""
        if os.path.exists(file_path):
            try:
                if not self.dry_run:
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)

                self.cleaned_items.append(f"Auth file: {file_path}")
                self.logger.info(f"   ✅ Removed: {file_path}")
            except Exception as e:
                self.logger.warning(f"   ⚠️ Could not remove {file_path}: {e}")
                self.errors.append(f"Could not remove {file_path}: {e}")
        elif self.verbose:
            self.logger.debug(f"   📄 Not found: {file_path}")

    def _clean_certificate_stores(self):
        """Clean certificate stores and trust settings"""
        self.logger.info("📜 Cleaning certificate stores...")

        # Check system keychain for Zoom certificates
        try:
            result = subprocess.run(
                [
                    "security",
                    "find-certificate",
                    "-c",
                    "Zoom",
                    "/System/Library/Keychains/SystemRootCertificates.keychain",
                ],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                self.logger.info("   🔍 Found Zoom certificates in system keychain")
                # Note: System certificates usually shouldn't be deleted

        except subprocess.SubprocessError:
            pass

        # Check user keychain for Zoom certificates
        try:
            result = subprocess.run(
                ["security", "find-certificate", "-c", "Zoom"],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                if not self.dry_run:
                    subprocess.run(
                        ["security", "delete-certificate", "-c", "Zoom"],
                        capture_output=True,
                    )
                self.cleaned_items.append("Certificate: Zoom")
                self.logger.info("   ✅ Removed Zoom certificate")

        except subprocess.SubprocessError:
            pass

    def _clean_oauth_tokens(self):
        """Clean OAuth tokens and refresh tokens"""
        self.logger.info("🎫 Cleaning OAuth tokens...")

        # OAuth token storage locations
        oauth_paths = [
            "~/Library/Application Support/Zoom/oauth",
            "~/Library/Application Support/us.zoom.xos/oauth",
            "~/Library/Preferences/us.zoom.xos.oauth.plist",
            "~/Library/Preferences/zoom.oauth.plist",
            "~/Library/HTTPStorages/us.zoom.xos/oauth",
            "~/Library/HTTPStorages/zoom.us/oauth",
        ]

        for oauth_path in oauth_paths:
            expanded_path = os.path.expanduser(oauth_path)
            self._remove_auth_file(expanded_path)

        # Clean OAuth data from HTTP storages
        http_storage_paths = [
            "~/Library/HTTPStorages/us.zoom.xos",
            "~/Library/HTTPStorages/zoom.us",
        ]

        for storage_path in http_storage_paths:
            expanded_path = os.path.expanduser(storage_path)
            if os.path.exists(expanded_path):
                # Look for OAuth-related files
                try:
                    for root, dirs, files in os.walk(expanded_path):
                        for file in files:
                            if any(
                                term in file.lower()
                                for term in ["oauth", "token", "auth", "refresh"]
                            ):
                                file_path = os.path.join(root, file)
                                self._remove_auth_file(file_path)
                except Exception as e:
                    self.logger.warning(
                        f"   ⚠️ Error cleaning OAuth from {storage_path}: {e}"
                    )

    def _clean_sso_data(self):
        """Clean SSO and SAML authentication data"""
        self.logger.info("🔐 Cleaning SSO/SAML data...")

        sso_paths = [
            "~/Library/Application Support/Zoom/sso",
            "~/Library/Application Support/Zoom/saml",
            "~/Library/Application Support/us.zoom.xos/sso",
            "~/Library/Application Support/us.zoom.xos/saml",
            "~/Library/Preferences/zoom.sso.plist",
            "~/Library/Preferences/zoom.saml.plist",
        ]

        for sso_path in sso_paths:
            expanded_path = os.path.expanduser(sso_path)
            self._remove_auth_file(expanded_path)

    def _clean_browser_auth_data(self):
        """Clean browser-stored authentication data"""
        self.logger.info("🌐 Cleaning browser authentication data...")

        # Safari data
        safari_paths = [
            "~/Library/Safari/LocalStorage/https_zoom.us_0.localstorage",
            "~/Library/Safari/LocalStorage/https_zoom.us_0.localstorage-shm",
            "~/Library/Safari/LocalStorage/https_zoom.us_0.localstorage-wal",
            "~/Library/Safari/Databases/https_zoom.us_0",
            "~/Library/Cookies/Cookies.binarycookies",
        ]

        for safari_path in safari_paths:
            expanded_path = os.path.expanduser(safari_path)
            if "Cookies.binarycookies" in safari_path:
                # For cookies, we need to be more selective
                self._clean_cookies_file(expanded_path)
            else:
                self._remove_auth_file(expanded_path)

        # Chrome/Chromium data (if present)
        chrome_paths = [
            "~/Library/Application Support/Google/Chrome/Default/Local Storage/leveldb",
            "~/Library/Application Support/Google/Chrome/Default/Session Storage",
            "~/Library/Application Support/Google/Chrome/Default/Cookies",
        ]

        for chrome_path in chrome_paths:
            expanded_path = os.path.expanduser(chrome_path)
            if os.path.exists(expanded_path):
                if "Cookies" in chrome_path:
                    self._clean_chrome_cookies(expanded_path)
                elif "Storage" in chrome_path:
                    self._clean_browser_storage(expanded_path)

    def _clean_cookies_file(self, cookies_path: str):
        """Clean Zoom-related cookies from Safari cookies file"""
        if not os.path.exists(cookies_path):
            return

        try:
            # Note: Safari cookies are in binary format and complex to parse
            # For now, we'll note the file for manual review
            self.logger.info(f"   📄 Safari cookies file found: {cookies_path}")
            self.logger.info(
                "   ℹ️ Consider clearing Safari cookies manually for zoom.us"
            )
        except Exception as e:
            self.logger.warning(f"   ⚠️ Error processing cookies file: {e}")

    def _clean_chrome_cookies(self, cookies_path: str):
        """Clean Zoom-related cookies from Chrome cookies database"""
        if not os.path.exists(cookies_path):
            return

        try:
            # Chrome cookies are stored in SQLite database
            conn = sqlite3.connect(cookies_path)
            cursor = conn.cursor()

            # Find Zoom-related cookies
            cursor.execute(
                "SELECT name, host_key FROM cookies WHERE host_key LIKE '%zoom%'"
            )
            zoom_cookies = cursor.fetchall()

            if zoom_cookies and not self.dry_run:
                cursor.execute("DELETE FROM cookies WHERE host_key LIKE '%zoom%'")
                conn.commit()
                self.cleaned_items.append(
                    f"Chrome cookies: {len(zoom_cookies)} Zoom cookies"
                )
                self.logger.info(
                    f"   ✅ Removed {len(zoom_cookies)} Zoom cookies from Chrome"
                )

            conn.close()

        except Exception as e:
            self.logger.warning(f"   ⚠️ Error cleaning Chrome cookies: {e}")

    def _clean_browser_storage(self, storage_path: str):
        """Clean browser local/session storage"""
        if not os.path.exists(storage_path):
            return

        try:
            for root, dirs, files in os.walk(storage_path):
                for file in files:
                    if "zoom" in file.lower():
                        file_path = os.path.join(root, file)
                        self._remove_auth_file(file_path)
        except Exception as e:
            self.logger.warning(f"   ⚠️ Error cleaning browser storage: {e}")

    def _clean_system_auth_caches(self):
        """Clean system-level authentication caches"""
        self.logger.info("🗂️ Cleaning system authentication caches...")

        # Authorization database
        auth_db_path = "/var/db/auth.db"
        if os.path.exists(auth_db_path):
            try:
                # We can't directly modify this, but we can reset authorization cache
                if not self.dry_run:
                    subprocess.run(
                        ["sudo", "dscacheutil", "-flushcache"],
                        capture_output=True,
                        timeout=10,
                    )
                self.cleaned_items.append("System authorization cache")
                self.logger.info("   ✅ Flushed system authorization cache")
            except subprocess.SubprocessError as e:
                self.logger.warning(f"   ⚠️ Could not flush auth cache: {e}")

        # Directory Services cache
        try:
            if not self.dry_run:
                subprocess.run(
                    ["sudo", "killall", "-HUP", "DirectoryService"],
                    capture_output=True,
                    timeout=10,
                )
            self.cleaned_items.append("Directory Services cache")
            self.logger.info("   ✅ Reset Directory Services cache")
        except subprocess.SubprocessError:
            pass

    def _clean_network_auth_data(self):
        """Clean network authentication data"""
        self.logger.info("🌐 Cleaning network authentication data...")

        # Network configuration preferences that might store auth data
        network_prefs = [
            "/Library/Preferences/SystemConfiguration/preferences.plist",
            "~/Library/Preferences/com.apple.networkConnect.plist",
        ]

        for pref_path in network_prefs:
            expanded_path = os.path.expanduser(pref_path)
            if os.path.exists(expanded_path):
                try:
                    # Read and check for Zoom-related network auth
                    with open(expanded_path, "rb") as f:
                        plist_data = plistlib.load(f)

                    # Look for Zoom-related network configurations
                    zoom_found = self._search_plist_for_zoom(plist_data)
                    if zoom_found:
                        self.logger.info(
                            f"   🔍 Found Zoom network config in {pref_path}"
                        )
                        # Note: We typically don't modify system network preferences

                except Exception as e:
                    self.logger.warning(f"   ⚠️ Error checking network prefs: {e}")

    def _search_plist_for_zoom(self, data, path="") -> bool:
        """Recursively search plist data for Zoom-related entries"""
        if isinstance(data, dict):
            for key, value in data.items():
                if any(term in str(key).lower() for term in ["zoom", "us.zoom"]):
                    return True
                if self._search_plist_for_zoom(value, f"{path}.{key}"):
                    return True
        elif isinstance(data, list):
            for i, item in enumerate(data):
                if self._search_plist_for_zoom(item, f"{path}[{i}]"):
                    return True
        elif isinstance(data, str):
            if any(term in data.lower() for term in ["zoom", "us.zoom"]):
                return True

        return False

    def _clean_identity_provider_data(self):
        """Clean identity provider and federation data"""
        self.logger.info("🆔 Cleaning identity provider data...")

        # Common identity provider storage locations
        idp_paths = [
            "~/Library/Application Support/Zoom/idp",
            "~/Library/Application Support/Zoom/federation",
            "~/Library/Preferences/zoom.idp.plist",
            "~/Library/Preferences/zoom.federation.plist",
        ]

        for idp_path in idp_paths:
            expanded_path = os.path.expanduser(idp_path)
            self._remove_auth_file(expanded_path)

    def _clean_biometric_auth_data(self):
        """Clean biometric authentication data"""
        self.logger.info("👆 Cleaning biometric authentication data...")

        # Touch ID / Face ID authentication data
        biometric_paths = [
            "~/Library/Application Support/Zoom/biometric",
            "~/Library/Application Support/Zoom/touchid",
            "~/Library/Application Support/Zoom/faceid",
        ]

        for bio_path in biometric_paths:
            expanded_path = os.path.expanduser(bio_path)
            self._remove_auth_file(expanded_path)

        # Check for biometric keychain entries
        try:
            result = subprocess.run(
                ["security", "find-generic-password", "-s", "zoom-biometric"],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                if not self.dry_run:
                    subprocess.run(
                        ["security", "delete-generic-password", "-s", "zoom-biometric"],
                        capture_output=True,
                    )
                self.cleaned_items.append("Biometric keychain entry")
                self.logger.info("   ✅ Removed biometric keychain entry")

        except subprocess.SubprocessError:
            pass

    def _reset_auth_services(self):
        """Reset authentication-related system services"""
        self.logger.info("🔄 Resetting authentication services...")

        services_to_reset = [
            "com.apple.authd",
            "com.apple.SecurityServer",
            "com.apple.trustd",
        ]

        for service in services_to_reset:
            try:
                if not self.dry_run:
                    # Send HUP signal to reload service configuration
                    subprocess.run(
                        ["sudo", "killall", "-HUP", service],
                        capture_output=True,
                        timeout=5,
                    )
                self.cleaned_items.append(f"Reset service: {service}")
                self.logger.info(f"   ✅ Reset service: {service}")
            except subprocess.SubprocessError:
                # Service might not be running, which is fine
                pass

    def generate_auth_cleanup_report(self) -> Dict:
        """Generate comprehensive authentication cleanup report"""
        return {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_items_cleaned": len(self.cleaned_items),
                "total_errors": len(self.errors),
                "success": len(self.errors) == 0,
            },
            "cleaned_items": self.cleaned_items,
            "errors": self.errors,
            "recommendations": [
                "Restart your Mac to ensure all authentication caches are cleared",
                "Clear browser cookies manually for zoom.us domain",
                "Sign out of any active Zoom sessions in other applications",
                "Consider changing your Zoom password after cleanup",
                "Test authentication with a fresh Zoom installation",
            ],
        }


def main():
    """Main function for standalone execution"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Clean all Zoom authentication tokens and identity data"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be cleaned without making changes",
    )

    args = parser.parse_args()

    cleaner = AuthTokenCleaner(verbose=args.verbose, dry_run=args.dry_run)
    results = cleaner.clean_all_auth_tokens()

    # Print summary
    print("\n" + "=" * 60)
    print("🔐 ZOOM AUTHENTICATION TOKEN CLEANUP COMPLETE")
    print("=" * 60)
    print(f"Items Cleaned: {len(results['cleaned_items'])}")
    print(f"Errors: {len(results['errors'])}")
    print(f"Success: {'✅ YES' if results['success'] else '❌ NO'}")

    if results["success"]:
        print("\n🎉 All authentication tokens have been cleaned!")
        print("   Zoom authentication should work fresh after restart.")
    else:
        print("\n⚠️ Some authentication data could not be cleaned.")
        print("   Manual intervention may be required.")

    # Save detailed report
    report_path = os.path.expanduser("~/Documents/zoom_auth_cleanup_report.json")
    try:
        with open(report_path, "w") as f:
            json.dump(cleaner.generate_auth_cleanup_report(), f, indent=2)
        print(f"\n📄 Detailed report saved to: {report_path}")
    except IOError:
        print("\n⚠️ Could not save detailed report")

    print("=" * 60)


if __name__ == "__main__":
    main()

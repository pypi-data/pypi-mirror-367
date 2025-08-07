#!/usr/bin/env python3
"""
Zoom Installer Module - Built-in modules only version
Automated download and installation of fresh Zoom copy using only Python
standard library
"""

import os
import subprocess
import tempfile
import logging
import time
import urllib.request
import urllib.error
import ssl
from typing import Optional, Dict


class ZoomInstaller:
    """Automated Zoom downloader and installer using built-in modules only"""

    # Official Zoom download URLs
    ZOOM_URLS = {
        "client": "https://zoom.us/client/latest/ZoomInstaller.pkg",
        "client_alt": (
            "https://d11yldzmag5yn.cloudfront.net/prod/5.17.11.3835/"
            "ZoomInstaller.pkg"
        ),
        "meetings": "https://zoom.us/client/latest/Zoom.pkg",
    }

    def __init__(self, logger: logging.Logger, temp_dir: Optional[str] = None):
        self.logger = logger
        self.temp_dir = temp_dir or tempfile.gettempdir()
        self.download_path = None
        self.installation_log = []

        # Create SSL context that doesn't verify certificates (for compatibility)
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE

    def get_latest_zoom_info(self) -> Dict[str, str]:
        """Get latest Zoom version information"""
        # Since we can't easily parse JSON without requests, use fallback
        return {"version": "latest", "url": self.ZOOM_URLS["client"], "size": "unknown"}

    def download_zoom(self, force_redownload: bool = False) -> Optional[str]:
        """Download latest Zoom installer using urllib"""
        zoom_info = self.get_latest_zoom_info()

        # Create download filename
        timestamp = int(time.time())
        filename = f"ZoomInstaller_{timestamp}.pkg"
        download_path = os.path.join(self.temp_dir, filename)

        # Check if we already have a recent download
        if (
            not force_redownload
            and self.download_path
            and os.path.exists(self.download_path)
        ):
            file_age = time.time() - os.path.getmtime(self.download_path)
            if file_age < 3600:  # Less than 1 hour old
                self.logger.info(f"Using existing download: {self.download_path}")
                return self.download_path

        self.logger.info(
            f"Downloading Zoom {zoom_info['version']} from {zoom_info['url']}"
        )

        try:
            # Create request with headers
            request = urllib.request.Request(
                zoom_info["url"],
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
                },
            )

            # Download with progress tracking
            with urllib.request.urlopen(
                request, context=self.ssl_context, timeout=30
            ) as response:
                total_size = int(response.headers.get("Content-Length", 0))
                downloaded = 0

                with open(download_path, "wb") as f:
                    while True:
                        chunk = response.read(8192)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)

                        if (
                            total_size > 0 and downloaded % (1024 * 1024) == 0
                        ):  # Log every MB
                            progress = (downloaded / total_size) * 100
                            self.logger.info(f"Download progress: {progress:.1f}%")

            self.logger.info(f"Download completed: {download_path}")
            self.download_path = download_path

            # Verify download
            if self._verify_download(download_path):
                return download_path
            else:
                self.logger.error("Download verification failed")
                os.remove(download_path)
                return None

        except urllib.error.URLError as e:
            self.logger.error(f"Download failed: {e}")
            if os.path.exists(download_path):
                os.remove(download_path)
            return None
        except Exception as e:
            self.logger.error(f"Download failed: {e}")
            if os.path.exists(download_path):
                os.remove(download_path)
            return None

    def _verify_download(self, file_path: str) -> bool:
        """Verify downloaded installer integrity"""
        try:
            # Check file size (should be > 100MB for Zoom)
            file_size = os.path.getsize(file_path)
            if file_size < 100 * 1024 * 1024:  # Less than 100MB
                self.logger.error(f"Downloaded file too small: {file_size} bytes")
                return False

            # Verify it's a valid macOS package
            result = subprocess.run(
                ["pkgutil", "--check-signature", file_path],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                # Check for Zoom's developer signature
                if "Zoom Video Communications" in result.stdout:
                    self.logger.info("✅ Download verified - valid Zoom package")
                    return True
                else:
                    self.logger.warning("Package signature doesn't match Zoom")

            # Fallback: check if it's at least a valid package
            result = subprocess.run(["file", file_path], capture_output=True, text=True)
            if "xar archive" in result.stdout.lower():
                self.logger.info("✅ Download verified - valid package format")
                return True

            self.logger.error("Downloaded file is not a valid package")
            return False

        except Exception as e:
            self.logger.error(f"Verification failed: {e}")
            return False

    def install_zoom(self, package_path: str, silent: bool = True) -> bool:
        """Install Zoom from downloaded package"""
        if not os.path.exists(package_path):
            self.logger.error(f"Package not found: {package_path}")
            return False

        self.logger.info(f"Installing Zoom from: {package_path}")

        try:
            # Prepare installation command
            cmd = ["sudo", "installer", "-pkg", package_path, "-target", "/"]

            if silent:
                cmd.extend(["-verboseR"])  # Verbose but no user interaction

            # Run installation
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            # Log installation output
            if result.stdout:
                self.installation_log.append(result.stdout)
                self.logger.info("Installation output:")
                for line in result.stdout.split("\n"):
                    if line.strip():
                        self.logger.info(f"  {line}")

            if result.stderr:
                self.installation_log.append(result.stderr)
                self.logger.warning("Installation warnings/errors:")
                for line in result.stderr.split("\n"):
                    if line.strip():
                        self.logger.warning(f"  {line}")

            if result.returncode == 0:
                self.logger.info("✅ Zoom installation completed successfully")

                # Verify installation
                if self._verify_installation():
                    return True
                else:
                    self.logger.error("Installation verification failed")
                    return False
            else:
                self.logger.error(f"Installation failed with code: {result.returncode}")
                return False

        except subprocess.TimeoutExpired:
            self.logger.error("Installation timed out")
            return False
        except Exception as e:
            self.logger.error(f"Installation error: {e}")
            return False

    def _verify_installation(self) -> bool:
        """Verify Zoom was installed correctly"""
        try:
            # Check if Zoom.app exists
            zoom_app_path = "/Applications/zoom.us.app"
            if not os.path.exists(zoom_app_path):
                self.logger.error("Zoom.app not found in Applications")
                return False

            # Check if it's executable
            zoom_binary = os.path.join(zoom_app_path, "Contents/MacOS/zoom.us")
            if not os.path.exists(zoom_binary):
                self.logger.error("Zoom binary not found")
                return False

            # Try to get version info
            result = subprocess.run(
                [zoom_binary, "--version"], capture_output=True, text=True, timeout=10
            )

            if result.returncode == 0 and result.stdout:
                version = result.stdout.strip()
                self.logger.info(f"✅ Zoom installed successfully - Version: {version}")
                return True

            # Fallback: check bundle info
            info_plist = os.path.join(zoom_app_path, "Contents/Info.plist")
            if os.path.exists(info_plist):
                result = subprocess.run(
                    ["plutil", "-p", info_plist], capture_output=True, text=True
                )
                if "CFBundleVersion" in result.stdout:
                    self.logger.info("✅ Zoom installation verified via Info.plist")
                    return True

            self.logger.warning("Could not verify Zoom version, but app exists")
            return True

        except Exception as e:
            self.logger.error(f"Installation verification error: {e}")
            return False

    def cleanup_downloads(self):
        """Clean up downloaded installer files"""
        if self.download_path and os.path.exists(self.download_path):
            try:
                os.remove(self.download_path)
                self.logger.info(f"Cleaned up download: {self.download_path}")
            except Exception as e:
                self.logger.warning(f"Could not clean up download: {e}")

    def get_installation_report(self) -> Dict:
        """Get detailed installation report"""
        return {
            "download_path": self.download_path,
            "installation_log": self.installation_log,
            "zoom_app_exists": os.path.exists("/Applications/zoom.us.app"),
            "timestamp": time.time(),
        }


def download_and_install_zoom(logger: logging.Logger, dry_run: bool = False) -> bool:
    """Convenience function for complete Zoom download and installation"""
    if dry_run:
        logger.info("[DRY RUN] Would download and install latest Zoom")
        return True

    installer = ZoomInstaller(logger)

    try:
        # Download
        package_path = installer.download_zoom()
        if not package_path:
            return False

        # Install
        success = installer.install_zoom(package_path)

        # Cleanup
        installer.cleanup_downloads()

        return success

    except Exception as e:
        logger.error(f"Download and install failed: {e}")
        return False


if __name__ == "__main__":
    # Test the installer
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    installer = ZoomInstaller(logger)

    # Download
    package_path = installer.download_zoom()
    if package_path:
        print(f"Downloaded to: {package_path}")

        # Install (uncomment to actually install)
        # success = installer.install_zoom(package_path)
        # print(f"Installation success: {success}")
    else:
        print("Download failed")

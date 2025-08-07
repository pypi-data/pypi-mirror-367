"""
macOS Compatibility Utilities
Handles version detection and compatibility checks across different macOS versions
"""

import platform
import logging
from typing import Dict, Tuple, Optional
from dataclasses import dataclass


@dataclass
class MacOSVersionInfo:
    """macOS version information"""

    major: int
    minor: int
    patch: int
    version_string: str
    codename: str
    supported: bool


class MacOSCompatibilityManager:
    """Manages macOS version compatibility and feature detection"""

    # macOS version codenames and support status
    MACOS_VERSIONS = {
        12: {"codename": "Monterey", "supported": True, "eol": False},
        13: {"codename": "Ventura", "supported": True, "eol": False},
        14: {"codename": "Sonoma", "supported": True, "eol": False},
        15: {"codename": "Sequoia", "supported": True, "eol": False},
        16: {"codename": "Unknown", "supported": True, "eol": False},  # Future versions
    }

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._version_info = None
        self._compatibility_cache = {}

    def get_macos_version(self) -> Optional[MacOSVersionInfo]:
        """Get detailed macOS version information"""
        if self._version_info is not None:
            return self._version_info

        if platform.system() != "Darwin":
            self.logger.warning("Not running on macOS")
            return None

        try:
            version_string = platform.mac_ver()[0]
            if not version_string:
                self.logger.error("Could not determine macOS version")
                return None

            # Parse version string (e.g., "14.2.1" -> major=14, minor=2, patch=1)
            # Use regex to handle non-numeric characters
            clean_string = "".join(filter(str.isdigit, version_string.split(".")[0]))
            if not clean_string:
                raise ValueError("Could not parse major version number")
            major = int(clean_string)

            version_parts = version_string.split(".")
            minor = (
                int("".join(filter(str.isdigit, version_parts[1])))
                if len(version_parts) > 1
                else 0
            )
            patch = (
                int("".join(filter(str.isdigit, version_parts[2])))
                if len(version_parts) > 2
                else 0
            )

            # Get version info
            version_data = self.MACOS_VERSIONS.get(
                major,
                {
                    "codename": "Unknown",
                    "supported": major >= 12,  # Support versions 12+
                    "eol": False,
                },
            )

            self._version_info = MacOSVersionInfo(
                major=major,
                minor=minor,
                patch=patch,
                version_string=version_string,
                codename=version_data["codename"],
                supported=version_data["supported"],
            )

            self.logger.info(
                f"Detected macOS {version_string} ({version_data['codename']})"
            )
            return self._version_info

        except Exception as e:
            self.logger.error(f"Error detecting macOS version: {e}")
            return None

    def is_supported_version(self) -> bool:
        """Check if current macOS version is supported"""
        version_info = self.get_macos_version()
        if not version_info:
            return False
        return version_info.supported

    def get_compatibility_warnings(self) -> list:
        """Get list of compatibility warnings for current version"""
        warnings = []
        version_info = self.get_macos_version()

        if not version_info:
            warnings.append("Could not detect macOS version")
            return warnings

        if not version_info.supported:
            warnings.append(
                f"macOS {version_info.version_string} may not be fully supported"
            )

        # Version-specific warnings
        if version_info.major == 12:
            warnings.extend(self._get_monterey_warnings())
        elif version_info.major == 13:
            warnings.extend(self._get_ventura_warnings())
        elif version_info.major == 14:
            warnings.extend(self._get_sonoma_warnings())
        elif version_info.major >= 15:
            warnings.extend(self._get_future_version_warnings())

        return warnings

    def _get_monterey_warnings(self) -> list:
        """Get Monterey-specific warnings"""
        return [
            "macOS Monterey: Enhanced privacy features may require additional permissions"
        ]

    def _get_ventura_warnings(self) -> list:
        """Get Ventura-specific warnings"""
        return [
            "macOS Ventura: System Integrity Protection enhancements may affect cleanup"
        ]

    def _get_sonoma_warnings(self) -> list:
        """Get Sonoma-specific warnings"""
        return [
            "macOS Sonoma: New privacy controls may require user approval for system access"
        ]

    def _get_future_version_warnings(self) -> list:
        """Get warnings for future/unknown versions"""
        return [
            "Newer macOS version detected: Some features may not work as expected",
            "Please report any issues to help improve compatibility",
        ]

    def check_feature_compatibility(self, feature: str) -> bool:
        """Check if a specific feature is compatible with current macOS version"""
        if feature in self._compatibility_cache:
            return self._compatibility_cache[feature]

        version_info = self.get_macos_version()
        if not version_info:
            return False

        # Feature compatibility matrix
        compatibility = self._check_feature_by_version(feature, version_info)
        self._compatibility_cache[feature] = compatibility
        return compatibility

    def _check_feature_by_version(
        self, feature: str, version_info: MacOSVersionInfo
    ) -> bool:
        """Check feature compatibility by version"""
        # Define feature compatibility
        feature_matrix = {
            "keychain_access": {
                "min_version": 12,
                "notes": "Keychain access available on all supported versions",
            },
            "system_commands": {
                "min_version": 12,
                "notes": "Basic system commands available",
            },
            "file_operations": {
                "min_version": 12,
                "notes": "File operations with enhanced security on newer versions",
            },
            "process_management": {
                "min_version": 12,
                "notes": "Process management available with security restrictions",
            },
            "vm_detection": {
                "min_version": 12,
                "notes": "VM detection works across all supported versions",
            },
        }

        feature_info = feature_matrix.get(feature)
        if not feature_info:
            self.logger.warning(f"Unknown feature: {feature}")
            return True  # Assume compatible if unknown

        compatible = version_info.major >= feature_info["min_version"]

        if not compatible:
            self.logger.warning(
                f"Feature '{feature}' not compatible with macOS {version_info.version_string}"
            )

        return compatible

    def get_system_info(self) -> Dict:
        """Get comprehensive system information"""
        version_info = self.get_macos_version()

        return {
            "platform": platform.system(),
            "version": version_info.version_string if version_info else "Unknown",
            "codename": version_info.codename if version_info else "Unknown",
            "major_version": version_info.major if version_info else 0,
            "supported": version_info.supported if version_info else False,
            "architecture": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "warnings": self.get_compatibility_warnings(),
        }

    def log_compatibility_info(self):
        """Log compatibility information"""
        system_info = self.get_system_info()

        self.logger.info("=== macOS Compatibility Information ===")
        self.logger.info(
            f"System: {system_info['platform']} {system_info['version']} ({system_info['codename']})"
        )
        self.logger.info(f"Architecture: {system_info['architecture']}")
        self.logger.info(f"Python: {system_info['python_version']}")
        self.logger.info(f"Supported: {system_info['supported']}")

        if system_info["warnings"]:
            self.logger.warning("Compatibility warnings:")
            for warning in system_info["warnings"]:
                self.logger.warning(f"  - {warning}")
        else:
            self.logger.info("No compatibility warnings")


# Global instance for easy access
compatibility_manager = MacOSCompatibilityManager()


def get_macos_version() -> Optional[MacOSVersionInfo]:
    """Convenience function to get macOS version"""
    return compatibility_manager.get_macos_version()


def is_supported_version() -> bool:
    """Convenience function to check if version is supported"""
    return compatibility_manager.is_supported_version()


def check_compatibility(feature: str) -> bool:
    """Convenience function to check feature compatibility"""
    return compatibility_manager.check_feature_compatibility(feature)


def log_system_info():
    """Convenience function to log system information"""
    compatibility_manager.log_compatibility_info()

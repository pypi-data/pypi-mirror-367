"""
Zoom Deep Clean Enhanced - Complete Zoom removal tool for macOS

This package provides comprehensive Zoom removal capabilities including:
- Standard application and file removal
- Deep system artifact cleaning (TCC database, IORegistry, etc.)
- VM-aware process detection and termination
- Automated fresh Zoom installation
- System-wide cleanup with device fingerprint elimination

Version: 2.2.0
"""

from .cleaner_enhanced import ZoomDeepCleanerEnhanced, SecurityError
from .deep_system_cleaner import DeepSystemCleaner
from .zoom_installer_builtin import ZoomInstaller, download_and_install_zoom
from .comprehensive_cli import ComprehensiveZoomCLI

__version__ = "2.2.0"
__author__ = "PHLthy215"
__email__ = "PHLthy215@example.com"
__description__ = (
    "Enhanced comprehensive Zoom cleanup utility for macOS with deep system cleaning"
)

__all__ = [
    "ZoomDeepCleanerEnhanced",
    "DeepSystemCleaner",
    "ZoomInstaller",
    "download_and_install_zoom",
    "ComprehensiveZoomCLI",
    "SecurityError",
    "__version__",
    "__author__",
    "__email__",
    "__description__",
]


# CLI main function available via lazy import to avoid warnings
def main():
    """Entry point for CLI - lazy import to avoid module loading issues"""
    from .cli_enhanced import main as cli_main

    return cli_main()

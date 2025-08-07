#!/usr/bin/env python3
"""
Enhanced CLI for Zoom Deep Clean with comprehensive system cleaning
"""

import argparse
import sys
import logging
import os
from pathlib import Path

# Handle both direct execution and package import
try:
    # Try relative import first (when run as package)
    from .cleaner_enhanced import ZoomDeepCleanerEnhanced
    from .comprehensive_cli import ComprehensiveZoomCLI
    from .auth_fix_cli import main as auth_fix_main
except ImportError:
    # Fall back to absolute import (when run directly)
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from zoom_deep_clean.cleaner_enhanced import ZoomDeepCleanerEnhanced
    from zoom_deep_clean.comprehensive_cli import ComprehensiveZoomCLI
    from zoom_deep_clean.auth_fix_cli import main as auth_fix_main


def setup_logging(verbose: bool = False) -> logging.Logger:
    """Setup logging configuration"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(levelname)s: %(message)s")
    return logging.getLogger(__name__)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Zoom Deep Clean Enhanced - Complete Zoom removal tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Standard deep clean
  %(prog)s --force
  
  # ZoomFixer-enhanced clean with secure shredding and network reset
  %(prog)s --force --zoomfixer-mode
  
  # Comprehensive clean with fresh install
  %(prog)s --comprehensive --install-fresh
  
  # Preview what would be cleaned (including ZoomFixer techniques)
  %(prog)s --dry-run --verbose --zoomfixer-mode
  
  # Network reset and hostname randomization only
  %(prog)s --force --network-reset --randomize-hostname
  
  # Deep system clean with reboot
  %(prog)s --comprehensive --system-reboot
        """,
    )

    # Version argument
    parser.add_argument("--version", action="version", version="%(prog)s 2.2.0")

    # Core cleaning options - use mutually exclusive group
    force_group = parser.add_mutually_exclusive_group(required=True)
    force_group.add_argument(
        "--force",
        "-f",
        action="store_true",
        help="Execute cleanup (required for actual cleaning)",
    )
    force_group.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview what would be cleaned without making changes",
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )

    # Backup options
    backup_group = parser.add_mutually_exclusive_group()
    backup_group.add_argument(
        "--backup",
        action="store_true",
        default=True,
        help="Create backups before removal (default: enabled)",
    )
    backup_group.add_argument(
        "--no-backup",
        action="store_true",
        help="Skip creating backups before removal",
    )

    # VM options
    vm_group = parser.add_mutually_exclusive_group()
    vm_group.add_argument(
        "--vm-aware",
        action="store_true",
        default=True,
        help="Enable VM-aware cleaning (default: enabled)",
    )
    vm_group.add_argument(
        "--no-vm",
        action="store_true",
        help="Disable VM-aware cleaning",
    )

    # Comprehensive cleaning mode
    parser.add_argument(
        "--comprehensive",
        action="store_true",
        help="Run comprehensive clean including deep system artifacts",
    )
    parser.add_argument(
        "--install-fresh",
        action="store_true",
        help="Download and install fresh Zoom after cleaning (requires --comprehensive)",
    )
    parser.add_argument(
        "--system-reboot",
        action="store_true",
        help="Automatically restart system after cleaning (requires --comprehensive)",
    )
    parser.add_argument(
        "--continue-on-error",
        action="store_true",
        help="Continue with next phase even if current phase fails",
    )

    # ZoomFixer-inspired options
    parser.add_argument(
        "--zoomfixer-mode",
        action="store_true",
        help="Enable ZoomFixer-inspired techniques (secure shredding, network reset, hostname randomization)",
    )
    parser.add_argument(
        "--network-reset",
        action="store_true",
        help="Reset Wi-Fi interface as part of device fingerprint cleaning",
    )
    parser.add_argument(
        "--randomize-hostname",
        action="store_true",
        help="Randomize system hostname for complete device identity reset",
    )

    # Advanced features
    advanced_group = parser.add_mutually_exclusive_group()
    advanced_group.add_argument(
        "--enable-advanced-features",
        action="store_true",
        default=True,
        help="Enable advanced cleaning features (default: enabled)",
    )
    advanced_group.add_argument(
        "--disable-advanced-features",
        action="store_true",
        help="Disable advanced cleaning features",
    )

    # MAC spoofing
    parser.add_argument(
        "--enable-mac-spoofing",
        action="store_true",
        help="Enable MAC address spoofing for network interface reset",
    )

    # Hostname options
    parser.add_argument(
        "--reset-hostname",
        action="store_true",
        help="Reset system hostname",
    )
    parser.add_argument(
        "--new-hostname",
        type=str,
        help="Set a new hostname (requires --reset-hostname)",
    )

    # Logging options
    parser.add_argument(
        "--log-file",
        type=str,
        help="Custom log file path",
    )

    # Export options
    parser.add_argument(
        "--export-dry-run",
        type=str,
        help="Export dry run results to a file",
    )

    try:
        args = parser.parse_args()
    except SystemExit as e:
        # argparse exits with code 2 for argument errors
        sys.exit(2)

    # Validate hostname arguments
    if args.new_hostname and not args.reset_hostname:
        parser.error("--new-hostname requires --reset-hostname")

    # Validate comprehensive mode requirements
    if (args.install_fresh or args.system_reboot) and not args.comprehensive:
        parser.error("--install-fresh and --system-reboot require --comprehensive")

    # Validate export dry run
    if args.export_dry_run and not args.dry_run:
        print("⚠️  Warning: --export-dry-run is most useful with --dry-run mode")

    # Setup logging
    logger = setup_logging(args.verbose)

    try:
        if args.comprehensive:
            # Run comprehensive cleaning
            logger.info("🚀 Starting Comprehensive Zoom Deep Clean")
            cli = ComprehensiveZoomCLI()
            success = cli.run_comprehensive_clean(args)
        else:
            # Run standard cleaning
            if args.zoomfixer_mode:
                logger.info("🎯 Starting ZoomFixer-Enhanced Deep Clean")
            else:
                logger.info("🚀 Starting Standard Zoom Deep Clean")

            # Configure options
            enable_network_reset = args.zoomfixer_mode or args.network_reset
            enable_hostname_randomization = (
                args.zoomfixer_mode or args.randomize_hostname or args.reset_hostname
            )
            enable_advanced_features = (
                not args.disable_advanced_features and args.enable_advanced_features
            )
            vm_aware = not args.no_vm and args.vm_aware
            backup_enabled = not args.no_backup and args.backup

            # Create cleaner with proper arguments
            cleaner_kwargs = {
                "verbose": args.verbose,
                "dry_run": args.dry_run,
                "enable_advanced_features": enable_advanced_features,
                "reset_hostname": enable_hostname_randomization,
                "vm_aware": vm_aware,
                "enable_backup": backup_enabled,
                "enable_mac_spoofing": getattr(args, "enable_mac_spoofing", False),
            }

            # Add log file if specified
            if args.log_file:
                cleaner_kwargs["log_file"] = args.log_file

            # Add new hostname if specified
            if args.new_hostname:
                cleaner_kwargs["new_hostname"] = args.new_hostname

            cleaner = ZoomDeepCleanerEnhanced(**cleaner_kwargs)
            success = cleaner.run_deep_clean()

            # Handle export dry run
            if args.export_dry_run and args.dry_run:
                try:
                    export_path = cleaner.export_dry_run_operations(args.export_dry_run)
                    logger.info(f"📄 Dry run results exported to: {export_path}")
                except Exception as e:
                    logger.warning(f"⚠️  Failed to export dry run results: {e}")

        if success:
            logger.info("✅ Zoom Deep Clean completed successfully")
            if not args.dry_run:
                logger.info("💡 Recommendation: Restart your system and reinstall Zoom")

            # Check if user was cancelled
            if (
                hasattr(cleaner, "was_cancelled_by_user")
                and cleaner.was_cancelled_by_user()
            ):
                sys.exit(130)  # User cancellation
        else:
            logger.error("❌ Zoom Deep Clean completed with errors")
            logger.info("📄 Check the log file for details")

            # Check if user was cancelled
            if (
                hasattr(cleaner, "was_cancelled_by_user")
                and cleaner.was_cancelled_by_user()
            ):
                sys.exit(130)  # User cancellation

        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        logger.error("❌ Operation cancelled by user")
        sys.exit(130)  # Standard exit code for SIGINT
    except Exception as e:
        from zoom_deep_clean.cleaner_enhanced import SecurityError

        if isinstance(e, SecurityError):
            logger.error(f"🔒 Security error: {e}")
            sys.exit(2)  # Security error
        else:
            logger.error(f"❌ Unexpected error: {e}")
            if getattr(args, "verbose", False):
                import traceback

                traceback.print_exc()
            sys.exit(1)  # General error


if __name__ == "__main__":
    main()

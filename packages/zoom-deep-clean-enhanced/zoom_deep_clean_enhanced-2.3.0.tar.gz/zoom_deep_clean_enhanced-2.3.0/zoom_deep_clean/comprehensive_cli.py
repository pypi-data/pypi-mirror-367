#!/usr/bin/env python3
"""
Comprehensive Zoom Deep Clean CLI
Complete removal, system cleaning, and automated fresh installation
"""

import argparse
import logging
import sys
import os
import time
import json
from pathlib import Path
from typing import Dict, Optional

# Import our modules
from .cleaner_enhanced import ZoomDeepCleanerEnhanced
from .deep_system_cleaner import DeepSystemCleaner
from .error_1132_handler import Error1132Handler
from .zoom_installer_builtin import ZoomInstaller, download_and_install_zoom


class ComprehensiveZoomCLI:
    """Complete Zoom removal and reinstallation CLI"""

    def __init__(self):
        self.logger = self._setup_logging()
        self.results = {}
        self.start_time = time.time()

    def _setup_logging(self) -> logging.Logger:
        """Setup comprehensive logging"""
        logger = logging.getLogger("zoom_comprehensive")
        logger.setLevel(logging.INFO)

        # Console handler
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter("%(levelname)s: %(message)s")
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        # File handler
        log_file = os.path.expanduser("~/Documents/zoom_comprehensive_clean.log")
        file_handler = logging.FileHandler(log_file)
        file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        return logger

    def run_comprehensive_clean(self, args) -> bool:
        """Run complete Zoom removal and reinstallation process"""

        self.logger.info("🚀 Starting Comprehensive Zoom Deep Clean")
        self.logger.info("=" * 60)

        success = True

        try:
            # Phase 1: Standard Deep Clean
            if not self._phase1_standard_clean(args):
                success = False
                if not args.continue_on_error:
                    return False

            # Phase 2: Deep System Artifacts Clean
            if not self._phase2_deep_system_clean(args):
                success = False
                if not args.continue_on_error:
                    return False

            # Phase 2.5: Error 1132 Specific Handling (if requested)
            if args.fix_error_1132 and not args.dry_run:
                if not self._phase2_5_error_1132_fix(args):
                    success = False
                    if not args.continue_on_error:
                        return False

            # Phase 3: System Restart (if requested)
            if args.system_reboot and not args.dry_run:
                self._phase3_system_restart(args)
                return True  # Process ends here

            # Phase 4: Fresh Zoom Installation (if requested)
            if args.install_fresh and not args.dry_run:
                if not self._phase4_fresh_installation(args):
                    success = False

            # Phase 5: Generate Report
            self._phase5_generate_report(args)

            return success

        except KeyboardInterrupt:
            self.logger.error("❌ Process interrupted by user")
            return False
        except Exception as e:
            self.logger.error(f"❌ Unexpected error: {e}")
            return False

    def _phase1_standard_clean(self, args) -> bool:
        """Phase 1: Standard Zoom deep cleaning"""
        self.logger.info("📋 Phase 1: Standard Deep Clean")
        self.logger.info("-" * 40)

        try:
            cleaner = ZoomDeepCleanerEnhanced(
                verbose=args.verbose, dry_run=args.dry_run
            )

            success = cleaner.run_deep_clean()
            self.results["phase1_standard_clean"] = {
                "success": success,
                "files_removed": getattr(cleaner, "files_removed", 0),
                "directories_removed": getattr(cleaner, "directories_removed", 0),
            }

            if success:
                self.logger.info("✅ Phase 1 completed successfully")
            else:
                self.logger.error("❌ Phase 1 had issues")

            return success

        except Exception as e:
            self.logger.error(f"❌ Phase 1 failed: {e}")
            self.results["phase1_standard_clean"] = {"success": False, "error": str(e)}
            return False

    def _phase2_deep_system_clean(self, args) -> bool:
        """Phase 2: Deep system artifacts cleaning"""
        self.logger.info("\n🔧 Phase 2: Deep System Artifacts Clean")
        self.logger.info("-" * 40)

        try:
            deep_cleaner = DeepSystemCleaner(self.logger, args.dry_run)
            results = deep_cleaner.clean_deep_system_artifacts()

            self.results["phase2_deep_system"] = results

            # Log results
            total_cleaned = sum(results.values())
            if total_cleaned > 0:
                self.logger.info(
                    f"✅ Phase 2 completed - {total_cleaned} deep artifacts cleaned"
                )
                for category, count in results.items():
                    if count > 0:
                        self.logger.info(f"  {category}: {count}")
            else:
                self.logger.info("✅ Phase 2 completed - no deep artifacts found")

            return True

        except Exception as e:
            self.logger.error(f"❌ Phase 2 failed: {e}")
            self.results["phase2_deep_system"] = {"error": str(e)}
            return False

    def _phase2_5_error_1132_fix(self, args) -> bool:
        """Phase 2.5: Error 1132 specific handling"""
        self.logger.info("\n🔧 Phase 2.5: Error 1132 Specific Fix")
        self.logger.info("-" * 40)

        try:
            error_1132_handler = Error1132Handler(self.logger, args.dry_run)

            # Run diagnostic first
            self.logger.info("🔍 Diagnosing Error 1132...")
            diagnostic_results = error_1132_handler.diagnose_error_1132()

            # Generate and log diagnostic report
            diagnostic_report = error_1132_handler.generate_error_1132_report(
                diagnostic_results
            )
            self.logger.info(f"📋 Error 1132 Diagnostic Report:\n{diagnostic_report}")

            # Apply fixes
            self.logger.info("🔧 Applying Error 1132 fixes...")
            fix_success = error_1132_handler.fix_error_1132()

            self.results["phase2_5_error_1132"] = {
                "diagnostic_results": diagnostic_results,
                "fix_success": fix_success,
            }

            if fix_success:
                self.logger.info("✅ Phase 2.5 completed - Error 1132 fixes applied")
            else:
                self.logger.warning(
                    "⚠️  Phase 2.5 completed with issues - Some Error 1132 fixes failed"
                )

            return True

        except Exception as e:
            self.logger.error(f"❌ Phase 2.5 failed: {e}")
            self.results["phase2_5_error_1132"] = {"error": str(e)}
            return False

    def _phase3_system_restart(self, args):
        """Phase 3: System restart"""
        self.logger.info("\n🔄 Phase 3: System Restart")
        self.logger.info("-" * 40)

        if args.dry_run:
            self.logger.info("[DRY RUN] Would restart system")
            return

        self.logger.info("⚠️  System will restart in 10 seconds...")
        self.logger.info("   Press Ctrl+C to cancel")

        try:
            time.sleep(10)
            self.logger.info("🔄 Restarting system...")
            os.system("sudo shutdown -r now")
        except KeyboardInterrupt:
            self.logger.info("❌ System restart cancelled")

    def _phase4_fresh_installation(self, args) -> bool:
        """Phase 4: Fresh Zoom installation"""
        self.logger.info("\n📦 Phase 4: Fresh Zoom Installation")
        self.logger.info("-" * 40)

        try:
            success = download_and_install_zoom(self.logger, args.dry_run)

            self.results["phase4_installation"] = {
                "success": success,
                "timestamp": time.time(),
            }

            if success:
                self.logger.info("✅ Phase 4 completed - Fresh Zoom installed")
            else:
                self.logger.error("❌ Phase 4 failed - Installation unsuccessful")

            return success

        except Exception as e:
            self.logger.error(f"❌ Phase 4 failed: {e}")
            self.results["phase4_installation"] = {"success": False, "error": str(e)}
            return False

    def _phase5_generate_report(self, args):
        """Phase 5: Generate comprehensive report"""
        self.logger.info("\n📊 Phase 5: Generating Report")
        self.logger.info("-" * 40)

        # Calculate total time
        total_time = time.time() - self.start_time

        # Create comprehensive report
        report = {
            "timestamp": time.time(),
            "total_duration_seconds": total_time,
            "arguments": vars(args),
            "results": self.results,
            "summary": self._generate_summary(),
        }

        # Save report
        report_file = os.path.expanduser("~/Documents/zoom_comprehensive_report.json")
        try:
            with open(report_file, "w") as f:
                json.dump(report, f, indent=2)
            self.logger.info(f"📄 Report saved: {report_file}")
        except Exception as e:
            self.logger.error(f"❌ Failed to save report: {e}")

        # Print summary
        self._print_summary(report)

    def _generate_summary(self) -> Dict:
        """Generate operation summary"""
        summary = {
            "phases_completed": 0,
            "phases_successful": 0,
            "total_artifacts_cleaned": 0,
            "critical_issues_fixed": 0,
        }

        for phase_name, phase_data in self.results.items():
            summary["phases_completed"] += 1

            if isinstance(phase_data, dict):
                if phase_data.get("success", False):
                    summary["phases_successful"] += 1

                # Count artifacts cleaned
                if phase_name == "phase2_deep_system":
                    for key, value in phase_data.items():
                        if isinstance(value, int):
                            summary["total_artifacts_cleaned"] += value
                            if key in ["tcc_entries_cleared", "ioreg_entries_cleared"]:
                                summary["critical_issues_fixed"] += value

        return summary

    def _print_summary(self, report: Dict):
        """Print operation summary"""
        summary = report["summary"]

        self.logger.info("\n" + "=" * 60)
        self.logger.info("📊 COMPREHENSIVE CLEAN SUMMARY")
        self.logger.info("=" * 60)

        self.logger.info(
            f"⏱️  Total Duration: {report['total_duration_seconds']:.1f} seconds"
        )
        self.logger.info(
            f"✅ Phases Successful: {summary['phases_successful']}/{summary['phases_completed']}"
        )
        self.logger.info(
            f"🧹 Total Artifacts Cleaned: {summary['total_artifacts_cleaned']}"
        )
        self.logger.info(
            f"🔧 Critical Issues Fixed: {summary['critical_issues_fixed']}"
        )

        # Recommendations
        self.logger.info("\n💡 RECOMMENDATIONS:")

        if summary["critical_issues_fixed"] > 0:
            self.logger.info("   ✅ Critical system issues were fixed")
            self.logger.info("   🔄 Restart your system for full effect")

        if report["arguments"].get("install_fresh"):
            self.logger.info("   📦 Fresh Zoom installation completed")
            self.logger.info("   🎯 Test meeting join functionality")
        else:
            self.logger.info("   📦 Install fresh Zoom from official website")

        self.logger.info("\n🎯 NEXT STEPS:")
        self.logger.info("   1. Restart your Mac (recommended)")
        self.logger.info("   2. Install/Launch Zoom")
        self.logger.info("   3. Grant permissions when prompted")
        self.logger.info("   4. Test meeting join functionality")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Comprehensive Zoom Deep Clean - Complete removal and fresh installation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Complete clean and reinstall
  %(prog)s --force --install-fresh
  
  # Deep clean with system restart
  %(prog)s --force --system-reboot
  
  # Preview what would be cleaned
  %(prog)s --dry-run --verbose
  
  # Clean and continue on errors
  %(prog)s --force --continue-on-error
        """,
    )

    # Core options
    parser.add_argument(
        "--force",
        action="store_true",
        help="Execute cleanup (required for actual cleaning)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview what would be cleaned without making changes",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )

    # Advanced options
    parser.add_argument(
        "--install-fresh",
        action="store_true",
        help="Download and install fresh Zoom after cleaning",
    )
    parser.add_argument(
        "--system-reboot",
        action="store_true",
        help="Automatically restart system after cleaning",
    )
    parser.add_argument(
        "--fix-error-1132",
        action="store_true",
        help="Apply specific fixes for Zoom Error 1132 (network/firewall issues)",
    )
    parser.add_argument(
        "--continue-on-error",
        action="store_true",
        help="Continue with next phase even if current phase fails",
    )

    args = parser.parse_args()

    # Validate arguments
    if not args.force and not args.dry_run:
        print("❌ Error: Must specify either --force or --dry-run")
        print("Use --help for more information")
        sys.exit(1)

    if args.force and args.dry_run:
        print("❌ Error: Cannot use both --force and --dry-run")
        sys.exit(1)

    # Run comprehensive clean
    cli = ComprehensiveZoomCLI()
    success = cli.run_comprehensive_clean(args)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

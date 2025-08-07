#!/usr/bin/env python3
"""
Authentication Fix CLI for Zoom Deep Clean Enhanced
Specialized command-line tool for fixing Zoom authentication issues
"""

import argparse
import sys
import os
import json
from datetime import datetime
from .auth_token_cleaner import AuthTokenCleaner
from .device_fingerprint_verifier import DeviceFingerprintVerifier


def main():
    """Main CLI function for authentication fixes"""
    parser = argparse.ArgumentParser(
        description="Fix Zoom authentication and login issues",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --fix-auth                    # Fix authentication issues
  %(prog)s --fix-auth --verify           # Fix auth + verify cleanup
  %(prog)s --fix-auth --dry-run          # Preview what would be fixed
  %(prog)s --verify-only                 # Only verify current state
  %(prog)s --full-reset                  # Complete authentication reset

Common Issues Fixed:
  • Cannot sign in to Zoom
  • Authentication tokens expired/corrupted
  • SSO/SAML login failures
  • OAuth token issues
  • Certificate problems
  • Keychain authentication errors
        """,
    )

    # Main action arguments
    parser.add_argument(
        "--fix-auth",
        action="store_true",
        help="Fix authentication issues by cleaning all auth tokens",
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify device fingerprint cleanup after auth fix",
    )
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Only verify current cleanup state without making changes",
    )
    parser.add_argument(
        "--full-reset",
        action="store_true",
        help="Complete authentication reset (auth fix + verification + recommendations)",
    )

    # Modifier arguments
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )
    parser.add_argument(
        "--report-path",
        type=str,
        default="~/Documents/zoom_auth_fix_report.json",
        help="Path to save detailed report (default: ~/Documents/zoom_auth_fix_report.json)",
    )

    args = parser.parse_args()

    # Validate arguments
    if not any([args.fix_auth, args.verify_only, args.full_reset]):
        parser.error("Must specify one of: --fix-auth, --verify-only, or --full-reset")

    if args.full_reset:
        args.fix_auth = True
        args.verify = True

    print("🔐 ZOOM AUTHENTICATION FIX TOOL")
    print("=" * 50)

    results = {
        "timestamp": datetime.now().isoformat(),
        "operations_performed": [],
        "auth_cleanup": None,
        "device_verification": None,
        "overall_success": False,
        "recommendations": [],
    }

    try:
        # Step 1: Authentication cleanup
        if args.fix_auth:
            print("\n🔧 STEP 1: Fixing Authentication Issues")
            print("-" * 40)

            auth_cleaner = AuthTokenCleaner(verbose=args.verbose, dry_run=args.dry_run)
            auth_results = auth_cleaner.clean_all_auth_tokens()
            results["auth_cleanup"] = auth_results
            results["operations_performed"].append("authentication_cleanup")

            if auth_results["success"]:
                print("✅ Authentication cleanup completed successfully!")
                print(
                    f"   • {len(auth_results['cleaned_items'])} authentication items cleaned"
                )
            else:
                print("⚠️ Authentication cleanup completed with some issues:")
                for error in auth_results["errors"][:3]:  # Show first 3 errors
                    print(f"   • {error}")
                if len(auth_results["errors"]) > 3:
                    print(f"   • ... and {len(auth_results['errors']) - 3} more errors")

        # Step 2: Device fingerprint verification
        if args.verify or args.verify_only:
            print("\n🔍 STEP 2: Verifying Device Fingerprint Cleanup")
            print("-" * 40)

            verifier = DeviceFingerprintVerifier(verbose=args.verbose)
            verification_results = verifier.verify_complete_cleanup()
            results["device_verification"] = verification_results
            results["operations_performed"].append("device_verification")

            device_ready = verification_results.get("verification_summary", {}).get(
                "device_ready_for_zoom", False
            )
            items_cleaned = verification_results.get("verification_summary", {}).get(
                "total_items_cleaned", 0
            )
            items_remaining = verification_results.get("verification_summary", {}).get(
                "remaining_items_count", 0
            )

            if device_ready:
                print("✅ Device fingerprint verification passed!")
                print("   • Device will appear as NEW to Zoom")
                if items_cleaned > 0:
                    print(f"   • {items_cleaned} additional items were cleaned")
            else:
                print("⚠️ Device fingerprint verification found issues:")
                print(f"   • {items_remaining} items still need attention")
                if items_cleaned > 0:
                    print(
                        f"   • {items_cleaned} items were cleaned during verification"
                    )

        # Step 3: Generate recommendations
        print("\n📋 STEP 3: Generating Recommendations")
        print("-" * 40)

        recommendations = generate_recommendations(results)
        results["recommendations"] = recommendations

        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec}")

        # Determine overall success
        auth_success = results.get("auth_cleanup", {}).get("success", True)
        device_ready = (
            results.get("device_verification", {})
            .get("verification_summary", {})
            .get("device_ready_for_zoom", True)
        )
        results["overall_success"] = auth_success and device_ready

        # Final summary
        print("\n🎯 FINAL SUMMARY")
        print("=" * 50)

        if results["overall_success"]:
            print("🎉 SUCCESS: Zoom authentication should now work properly!")
            print("   • All authentication tokens have been cleaned")
            print("   • Device will appear as new to Zoom")
            print("   • Ready for fresh Zoom installation/login")
        else:
            print("⚠️ PARTIAL SUCCESS: Some issues may remain")
            print("   • Review the recommendations above")
            print("   • Manual intervention may be required")
            print("   • Consider running with --verbose for more details")

        # Save detailed report
        report_path = os.path.expanduser(args.report_path)
        try:
            with open(report_path, "w") as f:
                json.dump(results, f, indent=2)
            print(f"\n📄 Detailed report saved to: {report_path}")
        except IOError as e:
            print(f"\n⚠️ Could not save report: {e}")

        print("=" * 50)

        # Exit with appropriate code
        sys.exit(0 if results["overall_success"] else 1)

    except KeyboardInterrupt:
        print("\n\n⚠️ Operation cancelled by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


def generate_recommendations(results: dict) -> list:
    """Generate personalized recommendations based on results"""
    recommendations = []

    auth_results = results.get("auth_cleanup")
    device_results = results.get("device_verification")

    # Authentication-specific recommendations
    if auth_results:
        if auth_results.get("success"):
            recommendations.append(
                "✅ Restart your Mac to ensure all authentication caches are cleared"
            )
            recommendations.append("🔄 Try signing into Zoom with a fresh installation")
        else:
            recommendations.append(
                "⚠️ Some authentication data could not be cleaned - try running as administrator"
            )
            recommendations.append(
                "🔧 Consider manually clearing browser cookies for zoom.us"
            )

    # Device fingerprint recommendations
    if device_results:
        device_ready = device_results.get("verification_summary", {}).get(
            "device_ready_for_zoom", False
        )
        if device_ready:
            recommendations.append(
                "🎉 Device is ready - Zoom will treat this as a completely new device"
            )
        else:
            remaining_count = device_results.get("verification_summary", {}).get(
                "remaining_items_count", 0
            )
            if remaining_count > 0:
                recommendations.append(
                    f"🧹 {remaining_count} device fingerprint items still need attention"
                )
                recommendations.append(
                    "🔄 Consider running the full deep cleaner for complete removal"
                )

    # General recommendations
    recommendations.extend(
        [
            "🔒 Consider changing your Zoom password after cleanup",
            "📱 Sign out of Zoom on all other devices before testing",
            "🌐 Clear browser cache and cookies for zoom.us domain",
            "⏰ Wait 5-10 minutes after cleanup before testing login",
            "📞 If issues persist, contact Zoom support with a fresh device claim",
        ]
    )

    return recommendations


if __name__ == "__main__":
    main()

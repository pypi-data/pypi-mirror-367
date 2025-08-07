#!/usr/bin/env python3
"""
Integration tests for Zoom Deep Clean Enhanced
Verify all modules can be imported and work together
"""

import unittest
import tempfile
import os


class TestModuleIntegration(unittest.TestCase):
    """Test that all modules can be imported and integrated"""

    def test_core_modules_import(self):
        """Verify all core modules can be imported"""
        # Core package
        import zoom_deep_clean

        self.assertIsNotNone(zoom_deep_clean.__version__)

        # Main cleaner
        from zoom_deep_clean.cleaner_enhanced import ZoomDeepCleanerEnhanced

        self.assertTrue(callable(ZoomDeepCleanerEnhanced))

        # CLI module
        from zoom_deep_clean.cli_enhanced import main

        self.assertTrue(callable(main))

        # Advanced features
        from zoom_deep_clean.advanced_features import AdvancedFeatures

        self.assertTrue(callable(AdvancedFeatures))

    def test_enhancement_modules_import(self):
        """Verify all enhancement modules can be imported"""
        # Security enhancements
        from zoom_deep_clean.security_enhancements import (
            SecurityValidator,
            FileIntegrityChecker,
        )

        self.assertTrue(callable(SecurityValidator))
        self.assertTrue(callable(FileIntegrityChecker))

        # Advanced detection
        from zoom_deep_clean.advanced_detection import (
            SystemFingerprintAnalyzer,
            ZoomArtifactDetector,
        )

        self.assertTrue(callable(SystemFingerprintAnalyzer))
        self.assertTrue(callable(ZoomArtifactDetector))

        # Cross-platform support
        from zoom_deep_clean.cross_platform_support import PlatformDetector

        self.assertTrue(callable(PlatformDetector))

        # Performance monitoring
        from zoom_deep_clean.performance_monitoring import PerformanceMonitor

        self.assertTrue(callable(PerformanceMonitor))

    def test_cleaner_with_enhancements(self):
        """Test that cleaner can be created with enhancement modules"""
        from zoom_deep_clean.cleaner_enhanced import ZoomDeepCleanerEnhanced

        # Create temporary log file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False) as f:
            log_file = f.name

        try:
            # Create cleaner instance
            cleaner = ZoomDeepCleanerEnhanced(
                log_file=log_file,
                verbose=True,
                dry_run=True,  # Safe for testing
                enable_backup=False,  # Don't create backup dirs in tests
                vm_aware=True,
                enable_advanced_features=True,
            )

            # Verify it was created successfully
            self.assertIsNotNone(cleaner)
            self.assertTrue(cleaner.dry_run)
            self.assertTrue(cleaner.vm_aware)
            self.assertTrue(cleaner.enable_advanced_features)

        finally:
            # Cleanup
            if os.path.exists(log_file):
                os.unlink(log_file)

    def test_security_integration(self):
        """Test security validation integration"""
        from zoom_deep_clean.cleaner_enhanced import (
            ZoomDeepCleanerEnhanced,
            SecurityError,
        )

        with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False) as f:
            log_file = f.name

        try:
            cleaner = ZoomDeepCleanerEnhanced(
                log_file=log_file, dry_run=True, enable_backup=False
            )

            # Test safe path validation
            safe_path = os.path.expanduser("~/Library/Application Support/zoom.us")
            validated = cleaner._validate_path(safe_path)
            self.assertIsInstance(validated, str)

            # Test dangerous path rejection
            dangerous_path = "/System/Library/CoreServices/Finder.app"
            with self.assertRaises(SecurityError):
                cleaner._validate_path(dangerous_path)

        finally:
            if os.path.exists(log_file):
                os.unlink(log_file)

    def test_no_circular_imports(self):
        """Test that there are no circular import issues"""
        # This test passes if we can import all modules without errors
        try:
            import zoom_deep_clean
            from zoom_deep_clean import cleaner_enhanced
            from zoom_deep_clean import cli_enhanced
            from zoom_deep_clean import advanced_features
            from zoom_deep_clean import security_enhancements
            from zoom_deep_clean import advanced_detection
            from zoom_deep_clean import cross_platform_support
            from zoom_deep_clean import performance_monitoring

            # Verify imports worked by checking they have expected attributes
            self.assertTrue(hasattr(zoom_deep_clean, "__version__"))
            self.assertTrue(hasattr(cleaner_enhanced, "ZoomDeepCleanerEnhanced"))
            self.assertTrue(hasattr(cli_enhanced, "main"))
            self.assertTrue(hasattr(advanced_features, "AdvancedFeatures"))
            self.assertTrue(hasattr(security_enhancements, "SecurityValidator"))
            self.assertTrue(hasattr(advanced_detection, "SystemFingerprintAnalyzer"))
            self.assertTrue(hasattr(cross_platform_support, "PlatformDetector"))
            self.assertTrue(hasattr(performance_monitoring, "PerformanceMonitor"))

        except ImportError as e:
            self.fail(f"Circular import detected: {e}")


if __name__ == "__main__":
    unittest.main()

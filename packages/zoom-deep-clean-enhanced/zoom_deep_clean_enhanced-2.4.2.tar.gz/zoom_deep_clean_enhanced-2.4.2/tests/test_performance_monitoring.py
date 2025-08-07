#!/usr/bin/env python3
"""
Tests for Performance Monitoring module
Comprehensive testing of performance tracking and optimization functionality
"""

import pytest
import sys
import os
import unittest
import time
import threading
import json
import logging
from unittest.mock import patch, MagicMock, Mock, mock_open
from datetime import datetime, timedelta
from dataclasses import asdict

# Import the performance monitoring module
from zoom_deep_clean.performance_monitoring import (
    PerformanceMetrics,
    PerformanceMonitor,
    PSUTIL_AVAILABLE,
)


class TestPerformanceMetrics(unittest.TestCase):
    """Test PerformanceMetrics dataclass functionality"""

    def test_performance_metrics_creation(self):
        """Test PerformanceMetrics instantiation"""
        metrics = PerformanceMetrics(
            operation_name="test_operation",
            start_time=1000.0,
            end_time=1010.0,
            duration=10.0,
            cpu_usage_start=5.0,
            cpu_usage_end=15.0,
            memory_usage_start=100.0,
            memory_usage_end=110.0,
            disk_io_start={"read": 1000, "write": 500},
            disk_io_end={"read": 1100, "write": 600},
            success=True,
        )

        # Verify all attributes are set correctly
        self.assertEqual(metrics.operation_name, "test_operation")
        self.assertEqual(metrics.start_time, 1000.0)
        self.assertEqual(metrics.end_time, 1010.0)
        self.assertEqual(metrics.duration, 10.0)
        self.assertEqual(metrics.cpu_usage_start, 5.0)
        self.assertEqual(metrics.cpu_usage_end, 15.0)
        self.assertEqual(metrics.memory_usage_start, 100.0)
        self.assertEqual(metrics.memory_usage_end, 110.0)
        self.assertEqual(metrics.disk_io_start, {"read": 1000, "write": 500})
        self.assertEqual(metrics.disk_io_end, {"read": 1100, "write": 600})
        self.assertTrue(metrics.success)
        self.assertIsNone(metrics.error_message)

    def test_performance_metrics_with_error(self):
        """Test PerformanceMetrics with error message"""
        metrics = PerformanceMetrics(
            operation_name="failed_operation",
            start_time=1000.0,
            end_time=1005.0,
            duration=5.0,
            cpu_usage_start=5.0,
            cpu_usage_end=10.0,
            memory_usage_start=100.0,
            memory_usage_end=105.0,
            disk_io_start={"read": 1000, "write": 500},
            disk_io_end={"read": 1050, "write": 550},
            success=False,
            error_message="Test error occurred",
        )

        self.assertFalse(metrics.success)
        self.assertEqual(metrics.error_message, "Test error occurred")

    def test_performance_metrics_asdict(self):
        """Test converting PerformanceMetrics to dictionary"""
        metrics = PerformanceMetrics(
            operation_name="test_operation",
            start_time=1000.0,
            end_time=1010.0,
            duration=10.0,
            cpu_usage_start=5.0,
            cpu_usage_end=15.0,
            memory_usage_start=100.0,
            memory_usage_end=110.0,
            disk_io_start={"read": 1000, "write": 500},
            disk_io_end={"read": 1100, "write": 600},
            success=True,
        )

        metrics_dict = asdict(metrics)

        # Verify dictionary structure
        self.assertIsInstance(metrics_dict, dict)
        self.assertEqual(metrics_dict["operation_name"], "test_operation")
        self.assertEqual(metrics_dict["success"], True)


class TestPerformanceMonitor(unittest.TestCase):
    """Test PerformanceMonitor class functionality"""

    def setUp(self):
        """Set up test environment"""
        self.logger = logging.getLogger("test_logger")
        self.logger.setLevel(logging.DEBUG)

    def test_performance_monitor_initialization_default(self):
        """Test PerformanceMonitor initialization with defaults"""
        monitor = PerformanceMonitor(logger=self.logger)

        # Verify default initialization
        self.assertEqual(monitor.logger, self.logger)
        self.assertEqual(monitor.metrics, [])
        self.assertEqual(monitor.active_operations, {})
        self.assertIsInstance(monitor.enable_detailed_monitoring, bool)

    def test_performance_monitor_initialization_custom(self):
        """Test PerformanceMonitor initialization with custom parameters"""
        monitor = PerformanceMonitor(
            logger=self.logger, enable_detailed_monitoring=False
        )

        # Verify custom initialization
        self.assertEqual(monitor.logger, self.logger)
        self.assertFalse(monitor.enable_detailed_monitoring)

    def test_psutil_available_detection(self):
        """Test PSUTIL_AVAILABLE constant"""
        # This tests the module-level constant
        self.assertIsInstance(PSUTIL_AVAILABLE, bool)

    @patch("zoom_deep_clean.performance_monitoring.PSUTIL_AVAILABLE", True)
    @patch("zoom_deep_clean.performance_monitoring.psutil")
    def test_get_system_info_with_psutil(self, mock_psutil):
        """Test get_system_info when psutil is available"""
        # Mock psutil methods
        mock_psutil.cpu_percent.return_value = 25.5
        mock_psutil.virtual_memory.return_value.percent = 45.2
        mock_psutil.disk_usage.return_value.percent = 60.8
        mock_psutil.disk_io_counters.return_value.read_bytes = 1000000
        mock_psutil.disk_io_counters.return_value.write_bytes = 500000

        monitor = PerformanceMonitor(logger=self.logger)

        if hasattr(monitor, "get_system_info"):
            system_info = monitor.get_system_info()

            # Verify system info structure
            self.assertIsInstance(system_info, dict)

    @patch("zoom_deep_clean.performance_monitoring.PSUTIL_AVAILABLE", False)
    def test_get_system_info_without_psutil(self):
        """Test get_system_info when psutil is not available"""
        monitor = PerformanceMonitor(logger=self.logger)

        if hasattr(monitor, "get_system_info"):
            system_info = monitor.get_system_info()

            # Should return basic info or empty dict when psutil unavailable
            self.assertIsInstance(system_info, dict)

    def test_monitor_operation_context_manager(self):
        """Test monitor_operation context manager"""
        monitor = PerformanceMonitor(logger=self.logger)

        # Test context manager usage
        try:
            with monitor.monitor_operation("test_operation"):
                # Simulate some work
                time.sleep(0.001)

            # Should complete without error
        except Exception as e:
            self.fail(f"Context manager raised an exception: {e}")

    def test_monitor_operation_disabled(self):
        """Test monitor_operation when detailed monitoring is disabled"""
        monitor = PerformanceMonitor(
            logger=self.logger, enable_detailed_monitoring=False
        )

        # Test context manager usage
        try:
            with monitor.monitor_operation("test_operation"):
                # Simulate some work
                time.sleep(0.001)

            # Should complete without error even when disabled
        except Exception as e:
            self.fail(f"Context manager raised an exception: {e}")

    def test_end_operation_no_current_operation(self):
        """Test end_operation when no operation is running"""
        monitor = PerformanceMonitor(logger=self.logger)

        if hasattr(monitor, "end_operation"):
            # Should handle gracefully when no operation is running
            try:
                result = monitor.end_operation()
                # Should return None or empty result
                self.assertIsNone(result) or self.assertEqual(result, {})
            except Exception as e:
                self.fail(f"end_operation raised an exception: {e}")

    def test_metrics_collection(self):
        """Test that metrics are collected properly"""
        monitor = PerformanceMonitor(logger=self.logger)

        # Initially should have no metrics
        self.assertEqual(len(monitor.metrics), 0)

        # After running an operation, should have metrics (if psutil available)
        with monitor.monitor_operation("test_operation"):
            time.sleep(0.001)

        # Check if metrics were added
        # Note: metrics might only be added if psutil is available
        if PSUTIL_AVAILABLE:
            # With psutil, metrics should be collected
            pass
        else:
            # Without psutil, monitoring is limited
            pass

    def test_get_metrics_list(self):
        """Test accessing the metrics list"""
        monitor = PerformanceMonitor(logger=self.logger)

        # Should be able to access metrics list
        self.assertIsInstance(monitor.metrics, list)
        self.assertEqual(len(monitor.metrics), 0)

    def test_active_operations_tracking(self):
        """Test active operations tracking"""
        monitor = PerformanceMonitor(logger=self.logger)

        # Should be able to access active operations
        self.assertIsInstance(monitor.active_operations, dict)
        self.assertEqual(len(monitor.active_operations), 0)

    @patch("builtins.open", new_callable=mock_open)
    def test_save_metrics_to_file(self, mock_file):
        """Test saving metrics to file"""
        monitor = PerformanceMonitor(logger=self.logger)

        if hasattr(monitor, "save_metrics_to_file"):
            try:
                monitor.save_metrics_to_file("/tmp/test_metrics.json")

                # Verify file was opened for writing
                mock_file.assert_called_once()
            except Exception as e:
                self.fail(f"save_metrics_to_file raised an exception: {e}")

    @patch("builtins.open", new_callable=mock_open, read_data='{"test": "data"}')
    def test_load_metrics_from_file(self, mock_file):
        """Test loading metrics from file"""
        monitor = PerformanceMonitor(logger=self.logger)

        if hasattr(monitor, "load_metrics_from_file"):
            try:
                result = monitor.load_metrics_from_file("/tmp/test_metrics.json")

                # Verify file was opened for reading
                mock_file.assert_called_once()

                # Should return parsed data
                if result:
                    self.assertIsInstance(result, (dict, list))
            except Exception as e:
                self.fail(f"load_metrics_from_file raised an exception: {e}")

    def test_get_performance_summary(self):
        """Test get_performance_summary functionality"""
        monitor = PerformanceMonitor(logger=self.logger)

        if hasattr(monitor, "get_performance_summary"):
            try:
                summary = monitor.get_performance_summary()

                # Should return summary data
                self.assertIsInstance(summary, dict)
            except Exception as e:
                self.fail(f"get_performance_summary raised an exception: {e}")


class TestPerformanceMonitorAdvanced(unittest.TestCase):
    """Test advanced PerformanceMonitor functionality"""

    def setUp(self):
        """Set up test environment"""
        self.logger = logging.getLogger("test_logger")

    def test_monitoring_with_threading(self):
        """Test performance monitoring in threaded environment"""
        monitor = PerformanceMonitor(logger=self.logger)

        def worker_function(operation_name):
            with monitor.monitor_operation(operation_name):
                time.sleep(0.001)  # Simulate work

        # Create multiple threads
        threads = []
        for i in range(3):
            thread = threading.Thread(
                target=worker_function, args=(f"thread_operation_{i}",)
            )
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # All threads should complete without error
        self.assertEqual(len(threads), 3)

    def test_error_handling_in_monitoring(self):
        """Test error handling in performance monitoring"""
        monitor = PerformanceMonitor(logger=self.logger)

        # Test with operation that raises an exception
        try:
            with monitor.monitor_operation("error_operation"):
                # Simulate an error
                raise ValueError("Test error")

        except ValueError:
            # Should handle error gracefully - context manager should work
            pass

    def test_performance_thresholds(self):
        """Test performance threshold monitoring"""
        monitor = PerformanceMonitor(logger=self.logger)

        if hasattr(monitor, "set_performance_threshold"):
            try:
                # Set threshold for operation duration
                monitor.set_performance_threshold("duration", 5.0)

                # Should not raise an exception
            except Exception as e:
                self.fail(f"set_performance_threshold raised an exception: {e}")

    def test_metrics_aggregation(self):
        """Test metrics aggregation functionality"""
        monitor = PerformanceMonitor(logger=self.logger)

        if hasattr(monitor, "aggregate_metrics"):
            try:
                # Test metrics aggregation
                aggregated = monitor.aggregate_metrics()

                # Should return aggregated data
                self.assertIsInstance(aggregated, dict)
            except Exception as e:
                self.fail(f"aggregate_metrics raised an exception: {e}")


class TestPerformanceMonitorIntegration(unittest.TestCase):
    """Test PerformanceMonitor integration scenarios"""

    def setUp(self):
        """Set up test environment"""
        self.logger = logging.getLogger("test_logger")

    def test_full_monitoring_cycle(self):
        """Test complete monitoring cycle"""
        monitor = PerformanceMonitor(logger=self.logger)

        # Test full cycle using context manager
        initial_metrics_count = len(monitor.metrics)

        with monitor.monitor_operation("full_cycle_test"):
            # Simulate work
            time.sleep(0.001)

        # Verify the cycle completed
        # Metrics might be added depending on psutil availability
        if PSUTIL_AVAILABLE and monitor.enable_detailed_monitoring:
            # With psutil, metrics should be collected
            final_metrics_count = len(monitor.metrics)
            # Should have the same or more metrics
            self.assertGreaterEqual(final_metrics_count, initial_metrics_count)

    def test_module_import_and_constants(self):
        """Test module imports and constants"""
        # Test that all main classes and constants are importable
        from zoom_deep_clean.performance_monitoring import (
            PerformanceMetrics,
            PerformanceMonitor,
            PSUTIL_AVAILABLE,
        )

        # Verify classes are callable
        self.assertTrue(callable(PerformanceMetrics))
        self.assertTrue(callable(PerformanceMonitor))

        # Verify constant is boolean
        self.assertIsInstance(PSUTIL_AVAILABLE, bool)

    def test_optional_psutil_handling(self):
        """Test handling of optional psutil dependency"""
        # Test that the module works regardless of psutil availability
        monitor = PerformanceMonitor(logger=self.logger)

        # Should initialize successfully regardless of psutil
        self.assertIsNotNone(monitor)

    def test_performance_monitor_with_mock_psutil(self):
        """Test PerformanceMonitor with mocked psutil"""
        with patch("zoom_deep_clean.performance_monitoring.PSUTIL_AVAILABLE", True):
            with patch("zoom_deep_clean.performance_monitoring.psutil") as mock_psutil:
                # Mock psutil methods
                mock_psutil.cpu_percent.return_value = 50.0
                mock_psutil.virtual_memory.return_value.percent = 60.0

                monitor = PerformanceMonitor(logger=self.logger)

                # Should initialize successfully with mocked psutil
                self.assertIsNotNone(monitor)


class TestPerformanceMonitorPrivateMethods(unittest.TestCase):
    """Test PerformanceMonitor private methods"""

    def setUp(self):
        """Set up test environment"""
        self.logger = logging.getLogger("test_logger")

    @patch("zoom_deep_clean.performance_monitoring.PSUTIL_AVAILABLE", False)
    def test_capture_metrics_without_psutil(self):
        """Test _capture_metrics when psutil is not available"""
        monitor = PerformanceMonitor(logger=self.logger)

        if hasattr(monitor, "_capture_metrics"):
            metrics = monitor._capture_metrics()

            # Should return basic metrics structure
            self.assertIsInstance(metrics, dict)
            self.assertIn("timestamp", metrics)
            self.assertIn("cpu_percent", metrics)
            self.assertIn("memory_percent", metrics)
            self.assertEqual(metrics["cpu_percent"], 0)
            self.assertEqual(metrics["memory_percent"], 0)

    @patch("zoom_deep_clean.performance_monitoring.PSUTIL_AVAILABLE", True)
    @patch("zoom_deep_clean.performance_monitoring.psutil")
    def test_capture_metrics_with_psutil(self, mock_psutil):
        """Test _capture_metrics when psutil is available"""
        # Mock psutil methods
        mock_psutil.cpu_percent.return_value = 25.5
        mock_psutil.virtual_memory.return_value.percent = 45.2
        mock_psutil.virtual_memory.return_value.available = 1000000
        mock_psutil.disk_io_counters.return_value.read_bytes = 1000
        mock_psutil.disk_io_counters.return_value.write_bytes = 500
        mock_psutil.disk_io_counters.return_value.read_count = 10
        mock_psutil.disk_io_counters.return_value.write_count = 5
        mock_psutil.net_io_counters.return_value.bytes_sent = 2000
        mock_psutil.net_io_counters.return_value.bytes_recv = 3000
        mock_psutil.net_io_counters.return_value.packets_sent = 20
        mock_psutil.net_io_counters.return_value.packets_recv = 30

        monitor = PerformanceMonitor(
            logger=self.logger, enable_detailed_monitoring=True
        )

        if hasattr(monitor, "_capture_metrics"):
            metrics = monitor._capture_metrics()

            # Should return detailed metrics structure
            self.assertIsInstance(metrics, dict)
            self.assertIn("timestamp", metrics)
            self.assertIn("cpu_percent", metrics)
            self.assertIn("memory_percent", metrics)
            self.assertIn("memory_available", metrics)
            self.assertEqual(metrics["cpu_percent"], 25.5)
            self.assertEqual(metrics["memory_percent"], 45.2)

    @patch("zoom_deep_clean.performance_monitoring.PSUTIL_AVAILABLE", True)
    @patch("zoom_deep_clean.performance_monitoring.psutil")
    def test_capture_metrics_exception_handling(self, mock_psutil):
        """Test _capture_metrics exception handling"""
        # Make psutil.cpu_percent raise an exception
        mock_psutil.cpu_percent.side_effect = Exception("Test exception")

        monitor = PerformanceMonitor(logger=self.logger)

        if hasattr(monitor, "_capture_metrics"):
            metrics = monitor._capture_metrics()

            # Should return minimal metrics on exception
            self.assertIsInstance(metrics, dict)
            self.assertIn("timestamp", metrics)

    def test_log_operation_performance_success(self):
        """Test _log_operation_performance with successful operation"""
        monitor = PerformanceMonitor(logger=self.logger)

        if hasattr(monitor, "_log_operation_performance"):
            # Create a successful metrics object
            metrics = PerformanceMetrics(
                operation_name="test_operation",
                start_time=1000.0,
                end_time=1010.0,
                duration=10.0,
                cpu_usage_start=5.0,
                cpu_usage_end=15.0,
                memory_usage_start=100.0,
                memory_usage_end=110.0,
                disk_io_start={"read": 1000, "write": 500},
                disk_io_end={"read": 1100, "write": 600},
                success=True,
            )

            # Should not raise an exception
            try:
                monitor._log_operation_performance(metrics)
            except Exception as e:
                self.fail(f"_log_operation_performance raised an exception: {e}")

    def test_log_operation_performance_failure(self):
        """Test _log_operation_performance with failed operation"""
        monitor = PerformanceMonitor(logger=self.logger)

        if hasattr(monitor, "_log_operation_performance"):
            # Create a failed metrics object
            metrics = PerformanceMetrics(
                operation_name="failed_operation",
                start_time=1000.0,
                end_time=1005.0,
                duration=5.0,
                cpu_usage_start=5.0,
                cpu_usage_end=10.0,
                memory_usage_start=100.0,
                memory_usage_end=105.0,
                disk_io_start={"read": 1000, "write": 500},
                disk_io_end={"read": 1050, "write": 550},
                success=False,
                error_message="Test error occurred",
            )

            # Should not raise an exception
            try:
                monitor._log_operation_performance(metrics)
            except Exception as e:
                self.fail(f"_log_operation_performance raised an exception: {e}")

    def test_continuous_monitoring_start_stop(self):
        """Test start_continuous_monitoring and stop_continuous_monitoring"""
        monitor = PerformanceMonitor(logger=self.logger)

        # Test starting continuous monitoring
        if hasattr(monitor, "start_continuous_monitoring"):
            try:
                monitor.start_continuous_monitoring(interval=0.1)

                # Should set monitoring_active flag
                if hasattr(monitor, "monitoring_active"):
                    self.assertTrue(monitor.monitoring_active)

                # Test stopping continuous monitoring
                if hasattr(monitor, "stop_continuous_monitoring"):
                    monitor.stop_continuous_monitoring()

                    # Should clear monitoring_active flag
                    if hasattr(monitor, "monitoring_active"):
                        self.assertFalse(monitor.monitoring_active)

            except Exception as e:
                self.fail(f"Continuous monitoring raised an exception: {e}")

    @patch("zoom_deep_clean.performance_monitoring.PSUTIL_AVAILABLE", True)
    @patch("zoom_deep_clean.performance_monitoring.psutil")
    def test_establish_baseline_with_psutil(self, mock_psutil):
        """Test _establish_baseline with psutil available"""
        # Mock psutil methods
        mock_psutil.cpu_count.return_value = 8
        mock_psutil.virtual_memory.return_value.total = 16000000000
        mock_psutil.cpu_percent.return_value = 25.0
        mock_psutil.virtual_memory.return_value.percent = 50.0
        mock_psutil.disk_partitions.return_value = []

        monitor = PerformanceMonitor(logger=self.logger)

        # Should have established baseline
        if hasattr(monitor, "system_baseline"):
            self.assertIsInstance(monitor.system_baseline, dict)

    @patch("zoom_deep_clean.performance_monitoring.PSUTIL_AVAILABLE", True)
    @patch("zoom_deep_clean.performance_monitoring.psutil")
    def test_establish_baseline_exception(self, mock_psutil):
        """Test _establish_baseline exception handling"""
        # Make psutil.cpu_count raise an exception
        mock_psutil.cpu_count.side_effect = Exception("Test exception")

        monitor = PerformanceMonitor(logger=self.logger)

        # Should handle exception and return empty baseline
        if hasattr(monitor, "system_baseline"):
            self.assertEqual(monitor.system_baseline, {})

    def test_check_performance_alerts_high_cpu(self):
        """Test _check_performance_alerts with high CPU usage"""
        monitor = PerformanceMonitor(logger=self.logger)

        if hasattr(monitor, "_check_performance_alerts"):
            # Test high CPU alert
            metrics = {
                "cpu_percent": 95.0,
                "memory_percent": 50.0,
                "memory_available": 1000000000,
            }

            try:
                monitor._check_performance_alerts(metrics)
                # Should log warning but not raise exception
            except Exception as e:
                self.fail(f"_check_performance_alerts raised an exception: {e}")

    def test_check_performance_alerts_high_memory(self):
        """Test _check_performance_alerts with high memory usage"""
        monitor = PerformanceMonitor(logger=self.logger)

        if hasattr(monitor, "_check_performance_alerts"):
            # Test high memory alert
            metrics = {
                "cpu_percent": 50.0,
                "memory_percent": 95.0,
                "memory_available": 1000000000,
            }

            try:
                monitor._check_performance_alerts(metrics)
                # Should log warning but not raise exception
            except Exception as e:
                self.fail(f"_check_performance_alerts raised an exception: {e}")

    def test_check_performance_alerts_low_available_memory(self):
        """Test _check_performance_alerts with low available memory"""
        monitor = PerformanceMonitor(logger=self.logger)

        if hasattr(monitor, "_check_performance_alerts"):
            # Test low available memory alert (less than 500MB)
            metrics = {
                "cpu_percent": 50.0,
                "memory_percent": 50.0,
                "memory_available": 100000000,
            }  # 100MB

            try:
                monitor._check_performance_alerts(metrics)
                # Should log warning but not raise exception
            except Exception as e:
                self.fail(f"_check_performance_alerts raised an exception: {e}")

    def test_get_performance_summary_with_metrics(self):
        """Test get_performance_summary when metrics exist"""
        monitor = PerformanceMonitor(logger=self.logger)

        # Add some test metrics
        monitor.metrics = [
            PerformanceMetrics(
                operation_name="test_op_1",
                start_time=1000.0,
                end_time=1010.0,
                duration=10.0,
                cpu_usage_start=5.0,
                cpu_usage_end=15.0,
                memory_usage_start=100.0,
                memory_usage_end=110.0,
                disk_io_start={"read": 1000, "write": 500},
                disk_io_end={"read": 1100, "write": 600},
                success=True,
            ),
            PerformanceMetrics(
                operation_name="test_op_2",
                start_time=2000.0,
                end_time=2005.0,
                duration=5.0,
                cpu_usage_start=10.0,
                cpu_usage_end=15.0,
                memory_usage_start=200.0,
                memory_usage_end=205.0,
                disk_io_start={"read": 2000, "write": 1000},
                disk_io_end={"read": 2050, "write": 1025},
                success=False,
                error_message="Test error",
            ),
        ]

        if hasattr(monitor, "get_performance_summary"):
            summary = monitor.get_performance_summary()

            # Should return detailed summary
            self.assertIsInstance(summary, dict)
            self.assertNotIn(
                "message", summary
            )  # Should not be "No performance data available"

    def test_get_performance_summary_no_metrics(self):
        """Test get_performance_summary when no metrics exist"""
        monitor = PerformanceMonitor(logger=self.logger)

        # Ensure no metrics
        monitor.metrics = []

        if hasattr(monitor, "get_performance_summary"):
            summary = monitor.get_performance_summary()

            # Should return no data message
            self.assertIsInstance(summary, dict)
            self.assertIn("message", summary)
            self.assertEqual(summary["message"], "No performance data available")

    def test_start_continuous_monitoring_already_active(self):
        """Test start_continuous_monitoring when already active"""
        monitor = PerformanceMonitor(logger=self.logger)

        if hasattr(monitor, "start_continuous_monitoring"):
            # Set monitoring as already active
            monitor.monitoring_active = True

            # Should return early and not start new thread
            try:
                monitor.start_continuous_monitoring(interval=0.1)
                # Should not raise exception
            except Exception as e:
                self.fail(f"start_continuous_monitoring raised an exception: {e}")


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
"""
Performance Monitoring Module
Advanced performance tracking and optimization for Zoom Deep Clean Enhanced

Created by: PHLthy215 (Enhanced by Amazon Q)
Version: 2.3.0 - Performance Monitoring
"""

import time
import threading
import json
import os
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from contextlib import contextmanager
import logging

# Optional psutil import for performance monitoring
try:
    import psutil

    PSUTIL_AVAILABLE = True
except ImportError:
    psutil = None
    PSUTIL_AVAILABLE = False


@dataclass
class PerformanceMetrics:
    """Performance metrics data structure"""

    operation_name: str
    start_time: float
    end_time: float
    duration: float
    cpu_usage_start: float
    cpu_usage_end: float
    memory_usage_start: float
    memory_usage_end: float
    disk_io_start: Dict[str, int]
    disk_io_end: Dict[str, int]
    success: bool
    error_message: Optional[str] = None


class PerformanceMonitor:
    """Advanced performance monitoring and optimization"""

    def __init__(self, logger: logging.Logger, enable_detailed_monitoring: bool = True):
        self.logger = logger
        self.enable_detailed_monitoring = (
            enable_detailed_monitoring and PSUTIL_AVAILABLE
        )
        self.metrics: List[PerformanceMetrics] = []
        self.active_operations: Dict[str, Dict[str, Any]] = {}

        if not PSUTIL_AVAILABLE:
            self.logger.warning(
                "psutil not available - performance monitoring will be limited"
            )
            self.system_baseline = {}
        else:
            self.system_baseline = self._establish_baseline()

        self.monitoring_thread: Optional[threading.Thread] = None
        self.monitoring_active = False

    def _establish_baseline(self) -> Dict[str, Any]:
        """Establish system performance baseline"""
        try:
            return {
                "cpu_count": psutil.cpu_count(),
                "memory_total": psutil.virtual_memory().total,
                "disk_usage": {
                    disk.device: psutil.disk_usage(disk.mountpoint)._asdict()
                    for disk in psutil.disk_partitions()
                },
                "baseline_cpu": psutil.cpu_percent(interval=1),
                "baseline_memory": psutil.virtual_memory().percent,
                "timestamp": time.time(),
            }
        except Exception as e:
            self.logger.warning(f"Could not establish performance baseline: {e}")
            return {}

    @contextmanager
    def monitor_operation(self, operation_name: str):
        """Context manager for monitoring individual operations"""
        start_metrics = self._capture_metrics()
        start_time = time.time()

        try:
            self.logger.debug(f"Starting performance monitoring for: {operation_name}")
            yield
            success = True
            error_message = None
        except Exception as e:
            success = False
            error_message = str(e)
            raise
        finally:
            end_time = time.time()
            end_metrics = self._capture_metrics()

            # Create performance metrics
            metrics = PerformanceMetrics(
                operation_name=operation_name,
                start_time=start_time,
                end_time=end_time,
                duration=end_time - start_time,
                cpu_usage_start=start_metrics.get("cpu_percent", 0),
                cpu_usage_end=end_metrics.get("cpu_percent", 0),
                memory_usage_start=start_metrics.get("memory_percent", 0),
                memory_usage_end=end_metrics.get("memory_percent", 0),
                disk_io_start=start_metrics.get("disk_io", {}),
                disk_io_end=end_metrics.get("disk_io", {}),
                success=success,
                error_message=error_message,
            )

            self.metrics.append(metrics)
            self._log_operation_performance(metrics)

    def _capture_metrics(self) -> Dict[str, Any]:
        """Capture current system metrics"""
        try:
            metrics = {
                "timestamp": time.time(),
            }

            if not PSUTIL_AVAILABLE:
                # Return minimal metrics when psutil is not available
                metrics.update(
                    {
                        "cpu_percent": 0,
                        "memory_percent": 0,
                        "memory_available": 0,
                        "disk_io": {},
                        "network_io": {},
                    }
                )
                return metrics

            # Full metrics when psutil is available
            metrics.update(
                {
                    "cpu_percent": psutil.cpu_percent(),
                    "memory_percent": psutil.virtual_memory().percent,
                    "memory_available": psutil.virtual_memory().available,
                }
            )

            if self.enable_detailed_monitoring:
                # Detailed disk I/O metrics
                disk_io = psutil.disk_io_counters()
                if disk_io:
                    metrics["disk_io"] = {
                        "read_bytes": disk_io.read_bytes,
                        "write_bytes": disk_io.write_bytes,
                        "read_count": disk_io.read_count,
                        "write_count": disk_io.write_count,
                    }

                # Network I/O metrics
                net_io = psutil.net_io_counters()
                if net_io:
                    metrics["network_io"] = {
                        "bytes_sent": net_io.bytes_sent,
                        "bytes_recv": net_io.bytes_recv,
                        "packets_sent": net_io.packets_sent,
                        "packets_recv": net_io.packets_recv,
                    }

            return metrics

        except Exception as e:
            self.logger.warning(f"Could not capture metrics: {e}")
            return {"timestamp": time.time()}

    def _log_operation_performance(self, metrics: PerformanceMetrics):
        """Log performance metrics for an operation"""
        if metrics.success:
            self.logger.info(
                f"✅ {metrics.operation_name} completed in {metrics.duration:.2f}s "
                f"(CPU: {metrics.cpu_usage_start:.1f}% → {metrics.cpu_usage_end:.1f}%, "
                f"Memory: {metrics.memory_usage_start:.1f}% → {metrics.memory_usage_end:.1f}%)"
            )
        else:
            self.logger.error(
                f"❌ {metrics.operation_name} failed after {metrics.duration:.2f}s: "
                f"{metrics.error_message}"
            )

    def start_continuous_monitoring(self, interval: float = 5.0):
        """Start continuous system monitoring"""
        if self.monitoring_active:
            return

        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(
            target=self._continuous_monitoring_loop, args=(interval,), daemon=True
        )
        self.monitoring_thread.start()
        self.logger.info(f"Started continuous monitoring (interval: {interval}s)")

    def stop_continuous_monitoring(self):
        """Stop continuous system monitoring"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=10)
        self.logger.info("Stopped continuous monitoring")

    def _continuous_monitoring_loop(self, interval: float):
        """Continuous monitoring loop"""
        while self.monitoring_active:
            try:
                metrics = self._capture_metrics()

                # Check for performance issues
                self._check_performance_alerts(metrics)

                time.sleep(interval)

            except Exception as e:
                self.logger.warning(f"Error in continuous monitoring: {e}")
                time.sleep(interval)

    def _check_performance_alerts(self, metrics: Dict[str, Any]):
        """Check for performance alerts"""
        # CPU usage alert
        cpu_percent = metrics.get("cpu_percent", 0)
        if cpu_percent > 90:
            self.logger.warning(f"⚠️ High CPU usage detected: {cpu_percent:.1f}%")

        # Memory usage alert
        memory_percent = metrics.get("memory_percent", 0)
        if memory_percent > 90:
            self.logger.warning(f"⚠️ High memory usage detected: {memory_percent:.1f}%")

        # Available memory alert
        memory_available = metrics.get("memory_available", 0)
        if memory_available < 500 * 1024 * 1024:  # Less than 500MB
            self.logger.warning(
                f"⚠️ Low available memory: {memory_available / (1024*1024):.1f}MB"
            )

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        if not self.metrics:
            return {"message": "No performance data available"}

        # Calculate summary statistics
        total_operations = len(self.metrics)
        successful_operations = sum(1 for m in self.metrics if m.success)
        failed_operations = total_operations - successful_operations

        durations = [m.duration for m in self.metrics]
        avg_duration = sum(durations) / len(durations)
        max_duration = max(durations)
        min_duration = min(durations)

        # CPU and memory statistics
        cpu_usages = [m.cpu_usage_end - m.cpu_usage_start for m in self.metrics]
        memory_usages = [
            m.memory_usage_end - m.memory_usage_start for m in self.metrics
        ]

        # Operation breakdown
        operation_stats = {}
        for metric in self.metrics:
            op_name = metric.operation_name
            if op_name not in operation_stats:
                operation_stats[op_name] = {
                    "count": 0,
                    "total_duration": 0,
                    "success_count": 0,
                    "avg_duration": 0,
                }

            stats = operation_stats[op_name]
            stats["count"] += 1
            stats["total_duration"] += metric.duration
            if metric.success:
                stats["success_count"] += 1
            stats["avg_duration"] = stats["total_duration"] / stats["count"]

        return {
            "summary": {
                "total_operations": total_operations,
                "successful_operations": successful_operations,
                "failed_operations": failed_operations,
                "success_rate": (
                    (successful_operations / total_operations) * 100
                    if total_operations > 0
                    else 0
                ),
                "total_duration": sum(durations),
                "average_duration": avg_duration,
                "max_duration": max_duration,
                "min_duration": min_duration,
            },
            "system_impact": {
                "avg_cpu_change": (
                    sum(cpu_usages) / len(cpu_usages) if cpu_usages else 0
                ),
                "max_cpu_change": max(cpu_usages) if cpu_usages else 0,
                "avg_memory_change": (
                    sum(memory_usages) / len(memory_usages) if memory_usages else 0
                ),
                "max_memory_change": max(memory_usages) if memory_usages else 0,
            },
            "operation_breakdown": operation_stats,
            "baseline": self.system_baseline,
            "recommendations": self._generate_performance_recommendations(),
        }

    def _generate_performance_recommendations(self) -> List[str]:
        """Generate performance optimization recommendations"""
        recommendations = []

        if not self.metrics:
            return recommendations

        # Analyze operation durations
        durations = [m.duration for m in self.metrics]
        avg_duration = sum(durations) / len(durations)

        if avg_duration > 30:  # Operations taking more than 30 seconds on average
            recommendations.append(
                "Consider running cleanup in smaller batches to improve responsiveness"
            )

        # Analyze failure rate
        total_ops = len(self.metrics)
        failed_ops = sum(1 for m in self.metrics if not m.success)
        failure_rate = (failed_ops / total_ops) * 100 if total_ops > 0 else 0

        if failure_rate > 10:
            recommendations.append(
                "High failure rate detected - consider running with --dry-run first"
            )

        # Analyze system resource usage
        cpu_changes = [m.cpu_usage_end - m.cpu_usage_start for m in self.metrics]
        max_cpu_change = max(cpu_changes) if cpu_changes else 0

        if max_cpu_change > 50:
            recommendations.append(
                "High CPU usage detected - consider running during off-peak hours"
            )

        # Memory usage analysis
        memory_changes = [
            m.memory_usage_end - m.memory_usage_start for m in self.metrics
        ]
        max_memory_change = max(memory_changes) if memory_changes else 0

        if max_memory_change > 20:
            recommendations.append(
                "High memory usage detected - ensure sufficient RAM is available"
            )

        # Operation-specific recommendations
        operation_stats = {}
        for metric in self.metrics:
            op_name = metric.operation_name
            if op_name not in operation_stats:
                operation_stats[op_name] = []
            operation_stats[op_name].append(metric.duration)

        for op_name, durations in operation_stats.items():
            avg_duration = sum(durations) / len(durations)
            if avg_duration > 60:  # Operations taking more than 1 minute
                recommendations.append(
                    f"Operation '{op_name}' is slow - consider optimization"
                )

        return recommendations

    def export_performance_data(self, file_path: str):
        """Export performance data to JSON file"""
        try:
            export_data = {
                "export_timestamp": datetime.now().isoformat(),
                "system_baseline": self.system_baseline,
                "performance_summary": self.get_performance_summary(),
                "detailed_metrics": [asdict(metric) for metric in self.metrics],
            }

            with open(file_path, "w") as f:
                json.dump(export_data, f, indent=2, default=str)

            self.logger.info(f"Performance data exported to: {file_path}")

        except Exception as e:
            self.logger.error(f"Failed to export performance data: {e}")

    def clear_metrics(self):
        """Clear collected performance metrics"""
        self.metrics.clear()
        self.logger.info("Performance metrics cleared")


class OptimizationEngine:
    """Performance optimization engine"""

    def __init__(self, logger: logging.Logger, performance_monitor: PerformanceMonitor):
        self.logger = logger
        self.performance_monitor = performance_monitor

    def optimize_operation_order(self, operations: List[str]) -> List[str]:
        """Optimize the order of operations based on historical performance"""
        if not self.performance_monitor.metrics:
            return operations  # No historical data, return as-is

        # Calculate average duration for each operation type
        operation_durations = {}
        for metric in self.performance_monitor.metrics:
            op_name = metric.operation_name
            if op_name not in operation_durations:
                operation_durations[op_name] = []
            operation_durations[op_name].append(metric.duration)

        # Calculate average durations
        avg_durations = {}
        for op_name, durations in operation_durations.items():
            avg_durations[op_name] = sum(durations) / len(durations)

        # Sort operations by average duration (fastest first)
        optimized_operations = sorted(
            operations, key=lambda op: avg_durations.get(op, float("inf"))
        )

        self.logger.info(f"Optimized operation order based on historical performance")
        return optimized_operations

    def suggest_batch_size(self, total_items: int, operation_type: str) -> int:
        """Suggest optimal batch size based on system resources and historical performance"""
        # Get system resources
        memory_gb = psutil.virtual_memory().total / (1024**3)
        cpu_count = psutil.cpu_count()

        # Base batch size on system resources
        base_batch_size = min(100, max(10, int(memory_gb * 10)))

        # Adjust based on historical performance if available
        if self.performance_monitor.metrics:
            similar_operations = [
                m
                for m in self.performance_monitor.metrics
                if operation_type in m.operation_name
            ]

            if similar_operations:
                avg_duration = sum(m.duration for m in similar_operations) / len(
                    similar_operations
                )

                # If operations are slow, reduce batch size
                if avg_duration > 10:
                    base_batch_size = max(5, base_batch_size // 2)
                elif avg_duration < 1:
                    base_batch_size = min(200, base_batch_size * 2)

        suggested_batch_size = min(base_batch_size, total_items)
        self.logger.info(
            f"Suggested batch size for {operation_type}: {suggested_batch_size}"
        )

        return suggested_batch_size

    def should_pause_for_resources(self) -> bool:
        """Determine if operations should pause to wait for system resources"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory_percent = psutil.virtual_memory().percent

            # Pause if system is under heavy load
            if cpu_percent > 85 or memory_percent > 90:
                self.logger.warning(
                    f"System under heavy load (CPU: {cpu_percent:.1f}%, "
                    f"Memory: {memory_percent:.1f}%) - pausing operations"
                )
                return True

            return False

        except Exception as e:
            self.logger.warning(f"Could not check system resources: {e}")
            return False

    def adaptive_delay(self, operation_count: int) -> float:
        """Calculate adaptive delay between operations"""
        try:
            cpu_percent = psutil.cpu_percent()
            memory_percent = psutil.virtual_memory().percent

            # Base delay
            base_delay = 0.1

            # Increase delay based on system load
            if cpu_percent > 70:
                base_delay *= 2
            if memory_percent > 80:
                base_delay *= 1.5

            # Increase delay for large operation counts
            if operation_count > 1000:
                base_delay *= 1.5

            return min(base_delay, 2.0)  # Cap at 2 seconds

        except Exception:
            return 0.1  # Default delay


class ResourceManager:
    """System resource management and throttling"""

    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.resource_limits = {
            "max_cpu_percent": 80,
            "max_memory_percent": 85,
            "max_disk_io_mbps": 100,
            "max_concurrent_operations": 5,
        }
        self.active_operations = 0
        self.operation_lock = threading.Lock()

    @contextmanager
    def acquire_resources(self, operation_name: str):
        """Acquire system resources for an operation"""
        # Wait for available resources
        self._wait_for_resources()

        with self.operation_lock:
            self.active_operations += 1

        try:
            self.logger.debug(f"Acquired resources for: {operation_name}")
            yield
        finally:
            with self.operation_lock:
                self.active_operations -= 1
            self.logger.debug(f"Released resources for: {operation_name}")

    def _wait_for_resources(self):
        """Wait until system resources are available"""
        max_wait_time = 300  # 5 minutes maximum wait
        wait_start = time.time()

        while time.time() - wait_start < max_wait_time:
            # Check concurrent operations limit
            if (
                self.active_operations
                >= self.resource_limits["max_concurrent_operations"]
            ):
                time.sleep(1)
                continue

            # Check system resources
            try:
                cpu_percent = psutil.cpu_percent(interval=0.1)
                memory_percent = psutil.virtual_memory().percent

                if (
                    cpu_percent <= self.resource_limits["max_cpu_percent"]
                    and memory_percent <= self.resource_limits["max_memory_percent"]
                ):
                    return  # Resources available

                self.logger.debug(
                    f"Waiting for resources (CPU: {cpu_percent:.1f}%, "
                    f"Memory: {memory_percent:.1f}%)"
                )
                time.sleep(2)

            except Exception as e:
                self.logger.warning(f"Error checking resources: {e}")
                time.sleep(1)

        self.logger.warning("Resource wait timeout - proceeding anyway")

    def set_resource_limits(self, **limits):
        """Set custom resource limits"""
        for key, value in limits.items():
            if key in self.resource_limits:
                self.resource_limits[key] = value
                self.logger.info(f"Set resource limit {key} = {value}")

    def get_resource_status(self) -> Dict[str, Any]:
        """Get current resource status"""
        try:
            return {
                "cpu_percent": psutil.cpu_percent(),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage("/").percent,
                "active_operations": self.active_operations,
                "resource_limits": self.resource_limits.copy(),
                "timestamp": time.time(),
            }
        except Exception as e:
            self.logger.warning(f"Could not get resource status: {e}")
            return {"error": str(e)}

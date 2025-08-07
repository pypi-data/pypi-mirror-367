#!/usr/bin/env python3
"""
Performance Optimizations Module
Async file scanning and parallel processing optimizations

Created by: PHLthy215 (Enhanced by Amazon Q)
Version: 2.3.0 - Performance Optimizations
"""

import os
import asyncio
import concurrent.futures
import threading
import time
from typing import List, Dict, Any, Optional, Callable, Set
from pathlib import Path
import logging
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
import subprocess
import fnmatch


@dataclass
class ScanResult:
    """Result of a file scan operation"""

    path: str
    size: int
    modified_time: float
    is_zoom_related: bool
    scan_time: float


class AsyncFileScanner:
    """High-performance async file scanner with parallel processing"""

    def __init__(self, logger: logging.Logger, max_workers: int = 8):
        self.logger = logger
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.cancelled = False

        # Zoom-related patterns for faster matching
        self.zoom_patterns = [
            "*zoom*",
            "*Zoom*",
            "*ZOOM*",
            "*us.zoom*",
            "*zoom.us*",
            "*zoomopener*",
            "*ZoomOpener*",
            "*zoomphone*",
            "*ZoomPhone*",
            "*zoomoutlook*",
            "*ZoomOutlook*",
            "*zoomrooms*",
            "*ZoomRooms*",
        ]

        # Directories to exclude for performance
        self.excluded_dirs = {
            ".Trash",
            "Trash",
            "Library/Caches",
            "Application Support/MobileSync",
            "Time Machine Backups",
            ".git",
            ".svn",
            "node_modules",
            "__pycache__",
            ".pytest_cache",
        }

        # File extensions to skip
        self.skip_extensions = {
            ".tmp",
            ".temp",
            ".log",
            ".cache",
            ".DS_Store",
            ".localized",
        }

    def should_skip_directory(self, dir_path: str) -> bool:
        """Check if directory should be skipped for performance"""
        dir_name = os.path.basename(dir_path)

        # Skip hidden directories (except specific ones we need)
        if dir_name.startswith(".") and dir_name not in {".zoom", ".zoomus"}:
            return True

        # Skip excluded directories
        for excluded in self.excluded_dirs:
            if excluded in dir_path:
                return True

        return False

    def is_zoom_related(self, file_path: str) -> bool:
        """Fast check if file is Zoom-related using pattern matching"""
        file_name = os.path.basename(file_path).lower()

        # Quick pattern matching
        for pattern in self.zoom_patterns:
            if fnmatch.fnmatch(file_name, pattern.lower()):
                return True

        # Check parent directories
        path_parts = file_path.lower().split(os.sep)
        for part in path_parts:
            if "zoom" in part:
                return True

        return False

    def scan_directory_sync(self, directory: str) -> List[ScanResult]:
        """Synchronous directory scan for use in thread pool"""
        results = []
        start_time = time.time()

        try:
            if not os.path.exists(directory) or self.should_skip_directory(directory):
                return results

            # Use os.scandir for better performance than os.listdir
            with os.scandir(directory) as entries:
                for entry in entries:
                    if self.cancelled:
                        break

                    try:
                        if entry.is_file():
                            # Skip files with certain extensions
                            if any(
                                entry.name.endswith(ext) for ext in self.skip_extensions
                            ):
                                continue

                            # Check if Zoom-related
                            is_zoom = self.is_zoom_related(entry.path)

                            if is_zoom:
                                stat_info = entry.stat()
                                results.append(
                                    ScanResult(
                                        path=entry.path,
                                        size=stat_info.st_size,
                                        modified_time=stat_info.st_mtime,
                                        is_zoom_related=True,
                                        scan_time=time.time() - start_time,
                                    )
                                )

                        elif entry.is_dir() and not self.should_skip_directory(
                            entry.path
                        ):
                            # Recursively scan subdirectories
                            sub_results = self.scan_directory_sync(entry.path)
                            results.extend(sub_results)

                    except (OSError, PermissionError) as e:
                        self.logger.debug(f"Skipping {entry.path}: {e}")
                        continue

        except (OSError, PermissionError) as e:
            self.logger.debug(f"Cannot scan directory {directory}: {e}")

        return results

    async def scan_directories_parallel(
        self, directories: List[str], progress_callback: Optional[Callable] = None
    ) -> List[ScanResult]:
        """Scan multiple directories in parallel using thread pool"""
        self.cancelled = False
        all_results = []

        self.logger.info(
            f"🔍 Starting parallel scan of {len(directories)} directories..."
        )

        # Submit all directory scans to thread pool
        future_to_dir = {}
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            for directory in directories:
                if os.path.exists(directory):
                    future = executor.submit(self.scan_directory_sync, directory)
                    future_to_dir[future] = directory

            # Collect results as they complete
            completed = 0
            for future in as_completed(future_to_dir):
                if self.cancelled:
                    break

                directory = future_to_dir[future]
                try:
                    results = future.result(
                        timeout=300
                    )  # 5 minute timeout per directory
                    all_results.extend(results)

                    completed += 1
                    if progress_callback:
                        progress = int((completed / len(directories)) * 100)
                        progress_callback(progress, f"Scanned {directory}")

                    self.logger.info(
                        f"✅ Scanned {directory}: {len(results)} Zoom files found"
                    )

                except concurrent.futures.TimeoutError:
                    self.logger.warning(f"⏰ Timeout scanning {directory}")
                except Exception as e:
                    self.logger.error(f"❌ Error scanning {directory}: {e}")

        self.logger.info(
            f"🎯 Parallel scan complete: {len(all_results)} total Zoom files found"
        )
        return all_results

    def cancel_scan(self):
        """Cancel ongoing scan operations"""
        self.cancelled = True
        self.logger.info("🛑 Cancelling file scan...")


class OptimizedProcessManager:
    """Optimized process management with batch operations"""

    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.process_cache = {}
        self.last_scan_time = 0
        self.cache_ttl = 5  # Cache for 5 seconds

    def get_zoom_processes_batch(self) -> List[Dict[str, Any]]:
        """Get all Zoom processes in a single batch operation"""
        current_time = time.time()

        # Use cache if recent
        if (current_time - self.last_scan_time) < self.cache_ttl and self.process_cache:
            return self.process_cache.get("zoom_processes", [])

        processes = []

        try:
            # Single pgrep command to find all Zoom processes
            result = subprocess.run(
                ["pgrep", "-fl", "zoom"], capture_output=True, text=True, timeout=10
            )

            if result.returncode == 0:
                for line in result.stdout.strip().split("\n"):
                    if line:
                        parts = line.split(" ", 1)
                        if len(parts) >= 2:
                            pid = parts[0]
                            command = parts[1]
                            processes.append(
                                {
                                    "pid": int(pid),
                                    "command": command,
                                    "name": os.path.basename(command.split()[0]),
                                }
                            )

            # Cache results
            self.process_cache["zoom_processes"] = processes
            self.last_scan_time = current_time

        except (
            subprocess.TimeoutExpired,
            subprocess.CalledProcessError,
            ValueError,
        ) as e:
            self.logger.warning(f"Error getting Zoom processes: {e}")

        return processes

    def terminate_processes_batch(
        self, processes: List[Dict[str, Any]]
    ) -> Dict[str, int]:
        """Terminate multiple processes efficiently"""
        results = {"terminated": 0, "failed": 0}

        if not processes:
            return results

        # Group processes by termination method
        pids_to_term = [p["pid"] for p in processes]

        try:
            # Try graceful termination first (SIGTERM)
            if pids_to_term:
                subprocess.run(
                    ["kill", "-TERM"] + [str(pid) for pid in pids_to_term],
                    capture_output=True,
                    timeout=5,
                )

                # Wait a moment for graceful shutdown
                time.sleep(2)

                # Check which processes are still running
                still_running = []
                for pid in pids_to_term:
                    try:
                        os.kill(pid, 0)  # Check if process exists
                        still_running.append(pid)
                    except OSError:
                        results["terminated"] += 1

                # Force kill remaining processes
                if still_running:
                    subprocess.run(
                        ["kill", "-KILL"] + [str(pid) for pid in still_running],
                        capture_output=True,
                        timeout=5,
                    )

                    # Final check
                    for pid in still_running:
                        try:
                            os.kill(pid, 0)
                            results["failed"] += 1
                        except OSError:
                            results["terminated"] += 1

        except (subprocess.TimeoutExpired, subprocess.CalledProcessError) as e:
            self.logger.error(f"Error terminating processes: {e}")
            results["failed"] = len(pids_to_term)

        return results


class PerformanceOptimizer:
    """Main performance optimization coordinator"""

    def __init__(self, logger: logging.Logger, max_workers: int = None):
        self.logger = logger

        # Auto-detect optimal worker count
        if max_workers is None:
            import multiprocessing

            max_workers = min(multiprocessing.cpu_count(), 8)

        self.max_workers = max_workers
        self.file_scanner = AsyncFileScanner(logger, max_workers)
        self.process_manager = OptimizedProcessManager(logger)

        self.logger.info(
            f"🚀 Performance optimizer initialized with {max_workers} workers"
        )

    async def optimized_file_search(
        self, search_locations: List[str], progress_callback: Optional[Callable] = None
    ) -> List[str]:
        """Perform optimized file search with parallel processing"""
        start_time = time.time()

        # Filter existing locations
        existing_locations = [loc for loc in search_locations if os.path.exists(loc)]

        if not existing_locations:
            self.logger.warning("No valid search locations found")
            return []

        self.logger.info(
            f"🔍 Starting optimized search in {len(existing_locations)} locations"
        )

        # Perform parallel scan
        scan_results = await self.file_scanner.scan_directories_parallel(
            existing_locations, progress_callback
        )

        # Extract file paths
        zoom_files = [result.path for result in scan_results if result.is_zoom_related]

        elapsed_time = time.time() - start_time
        self.logger.info(f"⚡ Optimized search completed in {elapsed_time:.2f}s")
        self.logger.info(f"📊 Found {len(zoom_files)} Zoom-related files")

        return zoom_files

    def optimized_process_cleanup(self) -> Dict[str, Any]:
        """Perform optimized process cleanup"""
        start_time = time.time()

        self.logger.info("🛑 Starting optimized process cleanup...")

        # Get all Zoom processes in batch
        processes = self.process_manager.get_zoom_processes_batch()

        if not processes:
            self.logger.info("✅ No Zoom processes found")
            return {"processes_found": 0, "processes_terminated": 0}

        self.logger.info(f"🎯 Found {len(processes)} Zoom processes")

        # Terminate processes in batch
        results = self.process_manager.terminate_processes_batch(processes)

        elapsed_time = time.time() - start_time
        self.logger.info(f"⚡ Process cleanup completed in {elapsed_time:.2f}s")
        self.logger.info(
            f"📊 Terminated: {results['terminated']}, Failed: {results['failed']}"
        )

        return {
            "processes_found": len(processes),
            "processes_terminated": results["terminated"],
            "processes_failed": results["failed"],
            "cleanup_time": elapsed_time,
        }

    def cancel_operations(self):
        """Cancel all ongoing operations"""
        self.file_scanner.cancel_scan()
        self.logger.info("🛑 All operations cancelled")

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get current performance statistics"""
        try:
            import psutil

            return {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_usage": {"/": psutil.disk_usage("/").percent},
                "active_threads": threading.active_count(),
                "max_workers": self.max_workers,
            }
        except ImportError:
            return {
                "active_threads": threading.active_count(),
                "max_workers": self.max_workers,
            }


# Utility functions for integration with existing code


def create_optimized_cleaner_mixin():
    """Create a mixin class to add performance optimizations to existing cleaner"""

    class OptimizedCleanerMixin:
        """Mixin to add performance optimizations to ZoomDeepCleanerEnhanced"""

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.performance_optimizer = PerformanceOptimizer(
                self.logger, max_workers=kwargs.get("max_workers", None)
            )

        async def optimized_comprehensive_file_search(
            self, progress_callback=None
        ) -> List[str]:
            """Optimized version of comprehensive_file_search"""
            search_locations = [
                "/Library",
                "/System/Library",
                "/private/var",
                "/Applications",
            ]

            # Add user directories
            try:
                user_dirs = [
                    d
                    for d in os.listdir("/Users")
                    if os.path.isdir(os.path.join("/Users", d))
                ]
                for user in user_dirs:
                    search_locations.append(f"/Users/{user}")
            except OSError as e:
                self.logger.warning(f"Could not list user directories: {e}")

            return await self.performance_optimizer.optimized_file_search(
                search_locations, progress_callback
            )

        def optimized_stop_zoom_processes(self) -> Dict[str, Any]:
            """Optimized version of stop_zoom_processes"""
            return self.performance_optimizer.optimized_process_cleanup()

        def cancel_optimized_operations(self):
            """Cancel optimized operations"""
            self.performance_optimizer.cancel_operations()

    return OptimizedCleanerMixin


# Example usage and testing
async def test_performance_optimizations():
    """Test the performance optimizations"""
    import logging

    # Setup logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Create optimizer
    optimizer = PerformanceOptimizer(logger)

    # Test file search
    test_locations = ["/Applications", "/Users"]

    def progress_callback(progress, message):
        print(f"Progress: {progress}% - {message}")

    results = await optimizer.optimized_file_search(test_locations, progress_callback)
    print(f"Found {len(results)} files")

    # Test process cleanup
    process_results = optimizer.optimized_process_cleanup()
    print(f"Process cleanup results: {process_results}")

    # Get performance stats
    stats = optimizer.get_performance_stats()
    print(f"Performance stats: {stats}")


if __name__ == "__main__":
    # Run test
    asyncio.run(test_performance_optimizations())

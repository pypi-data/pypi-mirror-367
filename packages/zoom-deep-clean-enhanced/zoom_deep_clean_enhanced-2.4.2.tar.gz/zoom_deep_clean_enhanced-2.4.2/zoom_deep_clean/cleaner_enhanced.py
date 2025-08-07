#!/usr/bin/env python3
"""
Zoom Deep Clean - Enhanced Core Cleaner Module (VM-Aware & System-Wide)
Complete device fingerprint removal for Zoom on macOS with VM support

Created by: PHLthy215
Enhanced Version: 2.2.0 - VM-Aware & System-Wide
"""

import os
import sys
import subprocess
import shutil
import logging
import json
import re
import time
from datetime import datetime
from typing import List, Dict, Tuple, Optional, Union, Any
from .advanced_features import AdvancedFeatures, AdvancedFeaturesError
from .deep_system_cleaner import DeepSystemCleaner
from .device_fingerprint_verifier import DeviceFingerprintVerifier
from .auth_token_cleaner import AuthTokenCleaner

# Configuration
DEFAULT_LOG_FILE = os.path.expanduser("~/Documents/zoom_deep_clean_enhanced.log")
BACKUP_DIR = os.path.expanduser("~/Documents/zoom_deep_clean_backup")

# Security Configuration
MAX_PATH_LENGTH = 1024
ALLOWED_PATH_CHARS = re.compile(r"^[a-zA-Z0-9._/\-\s~]+$")
ZOOM_SIGNATURES = [b"us.zoom.xos", b"zoom.us", b"ZoomPhone", b"ZoomClips", b"ZoomChat"]


class SecurityError(Exception):
    """Raised when security validation fails"""

    pass


class ZoomDeepCleanerEnhanced:
    """Enhanced VM-aware Zoom deep cleaner with comprehensive system-wide cleanup"""

    def __init__(
        self,
        log_file: str = DEFAULT_LOG_FILE,
        verbose: bool = False,
        dry_run: bool = False,
        enable_backup: bool = True,
        vm_aware: bool = True,
        system_reboot: bool = False,
        enable_advanced_features: bool = True,
        enable_mac_spoofing: bool = False,
        reset_hostname: bool = False,
        new_hostname: Optional[str] = None,
    ):
        # Input validation
        self.log_file = self._validate_path(log_file)
        self.verbose = bool(verbose)
        self.dry_run = bool(dry_run)
        self.enable_backup = bool(enable_backup)
        self.vm_aware = bool(vm_aware)
        self.system_reboot = bool(system_reboot)
        self.enable_advanced_features = bool(enable_advanced_features)
        self.enable_mac_spoofing = bool(enable_mac_spoofing)
        self.reset_hostname = bool(reset_hostname)
        self.new_hostname = new_hostname
        self.user_home = os.path.expanduser("~")
        self.backup_dir = BACKUP_DIR if enable_backup else None
        self.user_cancelled = False  # Track user cancellation separately from errors

        self.cleanup_stats = {
            "files_removed": 0,
            "directories_removed": 0,
            "processes_killed": 0,
            "vm_services_stopped": 0,
            "keychain_entries_removed": 0,
            "files_backed_up": 0,
            "errors": 0,
            "warnings": 0,
            "security_violations": 0,
            "remaining_files_found": 0,
            "system_locations_cleaned": 0,
            "advanced_features_executed": 0,
            "keychain_comprehensive_scan": False,
            "mdm_profiles_detected": 0,
            "hostname_reset_success": False,
            "mac_addresses_spoofed": 0,
            "system_identifiers_detected": 0,
            "encrypted_databases_shredded": 0,
            "fingerprint_files_shredded": 0,
            "network_interfaces_reset": 0,
            "wifi_cycles_completed": 0,
        }

        # Initialize advanced features if enabled
        if self.enable_advanced_features:
            self.advanced_features = AdvancedFeatures(
                logger=None,  # Will be set after logging setup
                dry_run=self.dry_run,
                enable_mac_spoofing=self.enable_mac_spoofing,
            )

        # Initialize deep system cleaner
        self.deep_system_cleaner = None  # Will be initialized after logging setup

        # Setup logging
        self._setup_logging()

        # Validate environment
        self._validate_environment()

        # Setup backup directory
        if self.enable_backup:
            self._setup_backup_dir()

    def _validate_path(self, path: str) -> str:
        """Enhanced path validation with security integration"""
        if not isinstance(path, str):
            raise SecurityError(f"Path must be string, got {type(path)}")

        if len(path) > MAX_PATH_LENGTH:
            raise SecurityError(f"Path too long: {len(path)} > {MAX_PATH_LENGTH}")

        if not ALLOWED_PATH_CHARS.match(path):
            raise SecurityError(f"Path contains invalid characters: {path}")

        # Resolve path and check for directory traversal
        resolved = os.path.abspath(os.path.expanduser(path))
        if ".." in path or not resolved.startswith(("/", os.path.expanduser("~"))):
            raise SecurityError(f"Suspicious path detected: {path}")

        # Enhanced security validation - check for dangerous system paths
        dangerous_paths = [
            "/System/",
            "/usr/bin/",
            "/usr/sbin/",
            "/bin/",
            "/sbin/",
            "/etc/passwd",
            "/etc/hosts",
            "/Library/CoreServices/",
            "/Applications/Utilities/",
        ]

        for dangerous in dangerous_paths:
            if resolved.startswith(dangerous):
                raise SecurityError(
                    f"Access to critical system path denied: {resolved}"
                )

        return resolved

    def _setup_backup_dir(self) -> None:
        """Setup secure backup directory"""
        if not self.backup_dir:
            return

        try:
            os.makedirs(self.backup_dir, mode=0o700, exist_ok=True)
            self.logger.info(f"Backup directory: {self.backup_dir}")
        except Exception as e:
            self.logger.error(f"Failed to create backup directory: {e}")
            self.enable_backup = False

    def _setup_logging(self) -> None:
        """Configure logging with both file and console output"""
        # Create logs directory if it doesn't exist
        log_dir = os.path.dirname(self.log_file)
        os.makedirs(log_dir, mode=0o755, exist_ok=True)

        # Get or create logger
        self.logger = logging.getLogger(__name__)

        # Clear any existing handlers to avoid duplicates
        self.logger.handlers.clear()

        # Set logging level
        self.logger.setLevel(logging.DEBUG if self.verbose else logging.INFO)

        # Create formatters
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
        )

        # Create file handler
        file_handler = logging.FileHandler(self.log_file, mode="a")
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        # Create console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # Prevent propagation to root logger to avoid duplicate messages
        self.logger.propagate = False

        self.logger.info(
            f"Zoom Deep Clean Enhanced v2.2.0 (VM-Aware & System-Wide) by PHLthy215 started"
        )
        self.logger.info(f"Dry run mode: {self.dry_run}")
        self.logger.info(f"Backup enabled: {self.enable_backup}")
        self.logger.info(f"VM-aware mode: {self.vm_aware}")
        self.logger.info(f"System reboot: {self.system_reboot}")
        self.logger.info(f"Advanced features: {self.enable_advanced_features}")
        if self.enable_advanced_features:
            self.logger.info(f"MAC spoofing: {self.enable_mac_spoofing}")
            self.logger.info(f"Hostname reset: {self.reset_hostname}")

        # Set logger for advanced features
        if self.enable_advanced_features:
            self.advanced_features.logger = self.logger

        # Initialize deep system cleaner
        self.deep_system_cleaner = DeepSystemCleaner(
            logger=self.logger, dry_run=self.dry_run
        )

    def _validate_environment(self) -> None:
        """Validate that we're running on macOS with proper permissions"""
        if sys.platform != "darwin":
            self.logger.error("This script is designed for macOS only")
            sys.exit(1)

        if os.geteuid() == 0:
            self.logger.warning(
                "Running as root - this may cause permission issues with user files"
            )

        # Validate user home directory
        if not os.path.isdir(self.user_home):
            raise SecurityError(f"Invalid user home directory: {self.user_home}")

        # Check if we can write to log file
        try:
            with open(self.log_file, "a") as f:
                f.write("")
        except PermissionError:
            print(f"Error: Cannot write to log file {self.log_file}")
            sys.exit(1)

        # Import and check macOS compatibility
        try:
            from .macos_compatibility import compatibility_manager

            # Log system compatibility information
            compatibility_manager.log_compatibility_info()

            # Check if current macOS version is supported
            if not compatibility_manager.is_supported_version():
                self.logger.warning(
                    "Running on unsupported macOS version - proceed with caution"
                )

            # Check feature compatibility
            critical_features = [
                "keychain_access",
                "system_commands",
                "file_operations",
            ]
            for feature in critical_features:
                if not compatibility_manager.check_feature_compatibility(feature):
                    self.logger.error(
                        f"Critical feature '{feature}' not compatible with current macOS version"
                    )
        except ImportError:
            self.logger.warning("macOS compatibility checking not available")

        # Log security settings
        self.logger.info(f"Security: Path validation enabled")
        self.logger.info(f"Security: Maximum path length: {MAX_PATH_LENGTH}")
        self.logger.info(f"Security: Backup enabled: {self.enable_backup}")

    def _sanitize_command_args(self, args: List[str]) -> List[str]:
        """Sanitize command arguments to prevent injection"""
        sanitized = []
        for arg in args:
            if not isinstance(arg, str):
                raise SecurityError(f"Command argument must be string: {arg}")

            # Basic validation - no shell metacharacters
            if any(
                char in arg
                for char in ["|", "&", ";", "`", "$", "(", ")", "<", ">", "\n", "\r"]
            ):
                raise SecurityError(f"Unsafe characters in command argument: {arg}")

            # Length check
            if len(arg) > 1024:
                raise SecurityError(f"Command argument too long: {len(arg)}")

            sanitized.append(arg)

        return sanitized

    def _simulate_process_commands(self, cmd_args: List[str]) -> Tuple[bool, str]:
        """Simulate process-related commands for dry-run"""
        if "pgrep" in cmd_args:
            return True, ""  # No processes found
        elif "ps" in cmd_args and "-p" in cmd_args:
            try:
                pid_index = cmd_args.index("-p") + 1
                if pid_index < len(cmd_args):
                    pid = cmd_args[pid_index]
                    return True, f"  PID COMMAND\n {pid} zoom.us"
            except (ValueError, IndexError):
                pass
            return True, "  PID COMMAND\n"
        return None, ""

    def _simulate_file_commands(self, cmd_args: List[str]) -> Tuple[bool, str]:
        """Simulate file-related commands for dry-run"""
        cmd_str = " ".join(cmd_args)
        if "find" in cmd_args and any(
            pattern in cmd_str for pattern in ["*zoom*", "*Zoom*", "*ZOOM*"]
        ):
            return True, ""  # No files found (clean system)
        return None, ""

    def _simulate_system_commands(self, cmd_args: List[str]) -> Tuple[bool, str]:
        """Simulate system information commands for dry-run"""
        if "system_profiler" in cmd_args:
            return (
                True,
                """Hardware:

    Hardware Overview:

      Model Name: MacBook Pro
      Model Identifier: MacBookPro18,1
      Chip: Apple M1 Pro
      Total Number of Cores: 10 (8 performance and 2 efficiency)
      Memory: 16 GB
      System Firmware Version: 8419.80.7
      OS Loader Version: 8419.80.7
      Serial Number (system): C02FWPME...
      Hardware UUID: EDDBC25E-...""",
            )
        elif "ioreg" in cmd_args:
            return (
                True,
                """+-o Root  <class IORegistryEntry, id 0x100000100, retain 8>
  +-o MacBookPro18,1  <class IOPlatformExpertDevice, id 0x100000110, registered, matched, active, busy 0 (1 ms), retain 15>
    {
      "IOPlatformSerialNumber" = "C02FWPME..."
      "IOPlatformUUID" = "EDDBC25E-..."
      "model" = <"MacBookPro18,1">
    }""",
            )
        return None, ""

    def _simulate_security_commands(self, cmd_args: List[str]) -> Tuple[bool, str]:
        """Simulate security/keychain commands for dry-run"""
        if "security" in cmd_args:
            if (
                "find-generic-password" in cmd_args
                or "find-internet-password" in cmd_args
            ):
                return (
                    False,
                    "security: SecKeychainSearchCopyNext: The specified item could not be found in the keychain.",
                )
            elif "dump-keychain" in cmd_args:
                return (
                    True,
                    'keychain: "/Users/user/Library/Keychains/login.keychain-db"\nversion: 512\nclass: 0x00000000\n',
                )
        elif "profiles" in cmd_args and "list" in cmd_args:
            return (
                True,
                "There are no configuration profiles installed in the system domain\nThere are no configuration profiles installed in the user domain",
            )
        return None, ""

    def _simulate_dry_run_output(
        self, cmd_args: List[str], description: str
    ) -> Tuple[bool, str]:
        """Simulate realistic command output for dry-run mode"""
        # Try each command type simulator
        simulators = [
            self._simulate_process_commands,
            self._simulate_file_commands,
            self._simulate_system_commands,
            self._simulate_security_commands,
        ]

        for simulator in simulators:
            success, output = simulator(cmd_args)
            if success is not None:  # Simulator handled this command
                return success, output

        # Default: return empty success for unhandled operations
        return True, ""

    def _run_command(
        self,
        cmd_args: Union[str, List[str]],
        args_or_description: Union[List[str], str, None] = None,
        description: str = "",
        require_sudo: bool = False,
        timeout: int = 30,
    ) -> Tuple[bool, str]:
        """Run a command with comprehensive security and error handling

        Args:
            cmd_args: Command to run (can be string or list)
            args_or_description: Either args list (for test compatibility) or description string
            description: Description of the command (when args_or_description is args list)
            require_sudo: Whether to run with sudo
            timeout: Command timeout in seconds

        Returns:
            Tuple of (success: bool, output: str)
        """
        # Handle different calling patterns
        if args_or_description is not None:
            if isinstance(args_or_description, list):
                # Test calling pattern: _run_command("echo", ["echo", "test"])
                cmd_args = args_or_description
                # description parameter is already set
            elif isinstance(args_or_description, str):
                # Dry-run test calling pattern: _run_command(["pkill", "-f", "zoom"], "Kill zoom processes")
                description = args_or_description
                # cmd_args is already set correctly

        if description:
            self.logger.info(f"Executing: {description}")

        # Convert string commands to list for security
        if isinstance(cmd_args, str):
            self.logger.warning(
                f"String command converted to list for security: {cmd_args}"
            )
            cmd_args = cmd_args.split()

        # Sanitize arguments
        try:
            cmd_args = self._sanitize_command_args(cmd_args)
        except SecurityError as e:
            self.logger.error(f"Command security validation failed: {e}")
            self.cleanup_stats["security_violations"] += 1
            return False, str(e)

        if self.dry_run:
            # Create comprehensive dry-run log message
            if description:
                dry_run_msg = f"DRY RUN: {description} | Command: {' '.join(cmd_args)}"
            else:
                dry_run_msg = f"DRY RUN: Would execute: {' '.join(cmd_args)}"
            self.logger.info(dry_run_msg)

            # Ensure the message is written to file immediately
            for handler in self.logger.handlers:
                if isinstance(handler, logging.FileHandler):
                    handler.flush()

            # Store dry-run operation for potential structured output
            if not hasattr(self, "dry_run_operations"):
                self.dry_run_operations = []
            self.dry_run_operations.append(
                {
                    "command": cmd_args,
                    "description": description,
                    "timestamp": time.time(),
                }
            )
            # Return contextually appropriate simulation data
            return self._simulate_dry_run_output(cmd_args, description)

        # Add sudo if required
        if require_sudo and cmd_args[0] != "sudo":
            cmd_args = ["sudo"] + cmd_args

        try:
            self.logger.debug(f"Executing command: {' '.join(cmd_args)}")

            result = subprocess.run(
                cmd_args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=timeout,
                shell=False,  # Critical: Never use shell=True
            )

            if result.returncode == 0:
                self.logger.debug(f"Command succeeded: {' '.join(cmd_args)}")
                if result.stdout.strip():
                    self.logger.debug(f"Output: {result.stdout.strip()}")
                return True, result.stdout
            else:
                error_msg = (
                    result.stderr.strip()
                    if result.stderr
                    else f"Command failed with code {result.returncode}"
                )
                self.logger.warning(
                    f"Command failed: {' '.join(cmd_args)} - {error_msg}"
                )
                self.cleanup_stats["warnings"] += 1
                return False, error_msg

        except subprocess.TimeoutExpired:
            timeout_msg = f"Command timed out after {timeout} seconds"
            self.logger.error(
                f"Command timed out after {timeout}s: {' '.join(cmd_args)}"
            )
            self.cleanup_stats["errors"] += 1
            return False, timeout_msg
        except Exception as e:
            self.logger.error(f"Exception running command {' '.join(cmd_args)}: {e}")
            self.cleanup_stats["errors"] += 1
            return False, str(e)

    def stop_vm_services(self) -> None:
        """Stop VM management services to prevent interference with cleanup"""
        if not self.vm_aware:
            return

        self.logger.info("🖥️ Stopping VM management services...")

        vm_services = [
            "com.vmware.fusion",
            "org.virtualbox.app.VBoxSVC",
            "com.parallels.desktop.launchdaemon",
            "com.vmware.fusion.services.VMware-Fusion-Helper",
            "org.virtualbox.app.VBoxXPCOMIPCD",
            "com.parallels.desktop.dispatcher",
            "com.vmware.fusion.services.VMware-Fusion-Application",
            "com.parallels.desktop.console",
        ]

        for service in vm_services:
            success, _ = self._run_command(
                ["launchctl", "stop", service],
                f"Stopping VM service: {service}",
                require_sudo=True,
            )
            if success:
                self.cleanup_stats["vm_services_stopped"] += 1

        # Also kill VM processes directly
        vm_processes = [
            "vmware-vmx",
            "VirtualBox",
            "VBoxSVC",
            "VBoxXPCOMIPCD",
            "VBoxHeadless",
            "prl_vm_app",
            "prl_disp_service",
            "VMware Fusion",
            "Parallels Desktop",
        ]

        for process in vm_processes:
            success, _ = self._run_command(
                ["pkill", "-f", process], f"Stopping VM process: {process}"
            )
            if success:
                self.cleanup_stats["processes_killed"] += 1

    def _verify_process_cleanup(self) -> bool:
        """Verify that all Zoom processes have been terminated"""
        self.logger.info("🔍 Verifying process cleanup...")

        # Check for remaining Zoom processes
        success, output = self._run_command(
            ["pgrep", "-f", "[Zz]oom"], "Checking for remaining Zoom processes"
        )

        if success and output.strip():
            remaining_processes = output.strip().split("\n")
            self.logger.warning(
                f"Found {len(remaining_processes)} remaining Zoom processes:"
            )
            for pid in remaining_processes:
                # Get process details
                proc_success, proc_info = self._run_command(
                    ["ps", "-p", pid, "-o", "pid,comm,args"],
                    f"Getting info for PID {pid}",
                )
                if proc_success:
                    self.logger.warning(f"  PID {pid}: {proc_info.strip()}")

            # Attempt final cleanup
            self.logger.info("🔥 Attempting final process cleanup...")
            for pid in remaining_processes:
                self._run_command(
                    ["kill", "-9", pid], f"Force killing PID {pid}", require_sudo=True
                )

            return False

        self.logger.info("✅ All Zoom processes successfully terminated")
        return True

    def stop_zoom_processes(self) -> None:
        """Enhanced Zoom process termination with VM awareness"""
        self.logger.info("🛑 Stopping all Zoom processes (VM-aware)...")

        # First stop VM services to prevent interference
        if self.vm_aware:
            self.stop_vm_services()

        # Enhanced Zoom process patterns including VM variants
        zoom_processes = [
            "zoom.us",
            "Zoom",
            "ZoomOpener",
            "ZoomUpdater",
            "ZoomClips",
            "ZoomPhone",
            "ZoomOutlookPlugin",
            "us.zoom.xos",
            "ZoomChat",
            "ZoomPresence",
        ]

        # VM-specific patterns if VM-aware mode is enabled
        if self.vm_aware:
            vm_zoom_patterns = [
                "VMware.*[Zz]oom",
                "VirtualBox.*[Zz]oom",
                "Parallels.*[Zz]oom",
                ".*vm.*[Zz]oom",
                ".*virtual.*[Zz]oom",
            ]
            zoom_processes.extend(vm_zoom_patterns)

        # Aggressive pattern-based killing first
        self.logger.info("🎯 Performing aggressive Zoom process cleanup...")
        success, _ = self._run_command(
            ["pkill", "-f", "[Zz]oom"],
            "Aggressive Zoom process cleanup",
            require_sudo=True,
        )
        if success:
            self.cleanup_stats["processes_killed"] += 1

        # Individual process cleanup
        for process in zoom_processes:
            success, _ = self._run_command(
                ["pkill", "-f", process], f"Stopping {process}"
            )
            if success:
                self.cleanup_stats["processes_killed"] += 1

        # Extended grace period for VM environments
        if not self.dry_run:
            grace_period = 5 if self.vm_aware else 2
            self.logger.info(
                f"⏳ Waiting {grace_period}s for processes to terminate gracefully..."
            )
            time.sleep(grace_period)

        # Force kill with enhanced patterns
        self.logger.info("💀 Force terminating any remaining Zoom processes...")
        force_patterns = ["[Zz]oom", "us.zoom", "zoom.us"]
        for pattern in force_patterns:
            self._run_command(
                ["pkill", "-9", "-f", pattern],
                f"Force killing pattern: {pattern}",
                require_sudo=True,
            )

        # Verify no processes remain
        self._verify_process_cleanup()

    def _verify_zoom_file(self, path: str) -> bool:
        """Verify that a file/directory is actually related to Zoom"""
        try:
            # Check if path contains zoom-related keywords
            path_lower = path.lower()
            zoom_keywords = [
                "zoom",
                "us.zoom",
                "zoomphone",
                "zoomclips",
                "zoomchat",
                "zoompresence",
            ]

            if not any(keyword in path_lower for keyword in zoom_keywords):
                self.logger.warning(f"Path does not appear Zoom-related: {path}")
                return False

            # For files, check content signatures
            if os.path.isfile(path) and os.path.getsize(path) > 0:
                try:
                    with open(path, "rb") as f:
                        header = f.read(1024)  # Read first 1KB

                    # Check for Zoom signatures
                    for signature in ZOOM_SIGNATURES:
                        if signature in header:
                            return True

                    # Check for binary plist signatures
                    if path.endswith(".plist") and header.startswith(b"bplist"):
                        return True

                except (PermissionError, OSError):
                    pass  # Can't read file, but path suggests it's Zoom-related

            return True  # Path appears Zoom-related

        except Exception as e:
            self.logger.warning(f"Could not verify Zoom file {path}: {e}")
            return False

    def _backup_path(self, path: str) -> bool:
        """Create backup of file/directory before removal"""
        if not self.enable_backup or not os.path.exists(path):
            return True

        try:
            # Create relative backup path
            rel_path = os.path.relpath(path, "/")
            backup_path = os.path.join(self.backup_dir, rel_path)
            backup_dir = os.path.dirname(backup_path)

            # Create backup directory structure
            os.makedirs(backup_dir, mode=0o700, exist_ok=True)

            if os.path.isdir(path):
                shutil.copytree(path, backup_path, dirs_exist_ok=True)
            else:
                shutil.copy2(path, backup_path)

            self.cleanup_stats["files_backed_up"] += 1
            self.logger.debug(f"Backed up: {path} -> {backup_path}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to backup {path}: {e}")
            return False

    def _secure_shred_file(self, file_path: str, description: str = "") -> bool:
        """Securely shred file using gshred (ZoomFixer-inspired method)"""
        if self.dry_run:
            self.logger.info(f"DRY RUN: Would securely shred: {file_path}")
            return True

        # Check if gshred is available (GNU coreutils)
        gshred_available = False
        success, _ = self._run_command(["which", "gshred"], "Checking for gshred")
        if success:
            gshred_available = True

        if gshred_available:
            # Use gshred for secure deletion (ZoomFixer method)
            success, output = self._run_command(
                ["gshred", "-n", "1", "-z", file_path],
                f"Secure shredding: {description or os.path.basename(file_path)}",
            )
            if success:
                self.logger.info(f"🔥 Securely shredded: {description or file_path}")
                return True
            else:
                self.logger.warning(
                    f"gshred failed for {file_path}, falling back to rm"
                )

        # Fallback to regular removal
        try:
            os.remove(file_path)
            self.logger.info(f"✅ Removed (standard): {description or file_path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to remove {file_path}: {e}")
            return False

    def _create_restricted_dummy_file(self, file_path: str) -> bool:
        """Create restricted dummy file (ZoomFixer technique)"""
        if self.dry_run:
            self.logger.info(f"DRY RUN: Would create restricted dummy: {file_path}")
            return True

        try:
            # Create empty file
            with open(file_path, "w") as f:
                pass

            # Set restricted permissions (read-only for owner)
            os.chmod(file_path, 0o400)
            self.logger.debug(f"Created restricted dummy file: {file_path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to create dummy file {file_path}: {e}")
            return False

    def _remove_path(
        self,
        path: str,
        description: str = "",
        force: bool = False,
        secure_shred: bool = False,
    ) -> bool:
        """Safely remove file or directory with security validation and backup"""
        try:
            # Validate path
            validated_path = self._validate_path(path)
        except SecurityError as e:
            self.logger.error(f"Path validation failed for {path}: {e}")
            self.cleanup_stats["security_violations"] += 1
            return False

        if not os.path.exists(validated_path):
            self.logger.debug(f"Path does not exist: {validated_path}")
            return False

        # Verify this is actually a Zoom file (unless forced)
        if not force and not self._verify_zoom_file(validated_path):
            self.logger.warning(f"Skipping non-Zoom file: {validated_path}")
            return False

        if self.dry_run:
            if os.path.isdir(validated_path):
                self.logger.info(f"DRY RUN: Would remove directory: {validated_path}")
            else:
                action = "securely shred" if secure_shred else "remove"
                self.logger.info(f"DRY RUN: Would {action} file: {validated_path}")
            return True

        # Create backup before removal
        if not self._backup_path(validated_path):
            self.logger.warning(
                f"Backup failed for {validated_path}, proceeding with removal"
            )

        try:
            if os.path.isdir(validated_path):
                shutil.rmtree(validated_path)
                self.cleanup_stats["directories_removed"] += 1
                self.logger.info(
                    f"✅ Removed directory: {description or validated_path}"
                )
            elif os.path.isfile(validated_path):
                if secure_shred:
                    # Use secure shredding for sensitive files
                    if self._secure_shred_file(validated_path, description):
                        self.cleanup_stats["files_removed"] += 1
                        # Create restricted dummy file (ZoomFixer technique)
                        self._create_restricted_dummy_file(validated_path)
                    else:
                        return False
                else:
                    # Standard removal
                    os.remove(validated_path)
                    self.cleanup_stats["files_removed"] += 1
                    self.logger.info(
                        f"✅ Removed file: {description or validated_path}"
                    )
            else:
                self.logger.warning(
                    f"Path exists but is neither file nor directory: {validated_path}"
                )
                return False

            return True

        except PermissionError:
            self.logger.error(f"Permission denied removing: {validated_path}")
            self.cleanup_stats["errors"] += 1
            return False
        except Exception as e:
            self.logger.error(f"Error removing {validated_path}: {e}")
            self.cleanup_stats["errors"] += 1
            return False

    def _check_sudo_access(self) -> bool:
        """Check if sudo access is available"""
        success, _ = self._run_command(["sudo", "-n", "true"], "Checking sudo access")
        return success

    def remove_keychain_entries(self) -> None:
        """Remove Zoom keychain entries with security validation"""
        self.logger.info("🔐 Removing Keychain entries...")

        keychain_entries = [
            "Zoom Safe Meeting Storage",
            "Zoom Safe Storage",
            "us.zoom.xos",
            "zoom.us",
            "ZoomChat",
            "Zoom Phone",
            "Zoom Clips",
            "ZoomPresence",
            "Zoom SSO",
        ]

        for entry in keychain_entries:
            # Validate keychain entry name
            if not isinstance(entry, str) or len(entry) > 256:
                self.logger.warning(f"Invalid keychain entry name: {entry}")
                continue

            # Try both generic and internet password removal
            for cmd_type in ["delete-generic-password", "delete-internet-password"]:
                try:
                    success, _ = self._run_command(
                        ["security", cmd_type, "-s", entry],
                        f"Removing keychain {cmd_type.split('-')[1]}: {entry}",
                    )
                    if success:
                        self.cleanup_stats["keychain_entries_removed"] += 1
                except Exception as e:
                    self.logger.debug(f"Keychain removal failed for {entry}: {e}")

    def remove_launch_agents(self) -> None:
        """Remove system-level launch agents"""
        self.logger.info("🚫 Removing system-level launch agents...")

        launch_agents = [
            "/Library/LaunchAgents/us.zoom.updater.login.check.plist",
            "/Library/LaunchAgents/us.zoom.updater.plist",
            "/Library/LaunchAgents/us.zoom.ZoomDaemon.plist",
            "/Library/LaunchAgents/us.zoom.ZoomAutoUpdater.plist",
        ]

        for agent in launch_agents:
            if os.path.exists(agent):
                # Unload first
                self._run_command(
                    ["launchctl", "unload", agent],
                    f"Unloading {os.path.basename(agent)}",
                    require_sudo=True,
                )
                # Then remove
                self._run_command(
                    ["rm", "-f", agent],
                    f"Removing {os.path.basename(agent)}",
                    require_sudo=True,
                )
                self.cleanup_stats["system_locations_cleaned"] += 1

    def remove_system_daemon(self) -> None:
        """Remove system daemon and privileged helper tools"""
        self.logger.info("🔧 Removing system daemon...")

        daemon_files = [
            "/Library/LaunchDaemons/us.zoom.ZoomDaemon.plist",
            "/Library/PrivilegedHelperTools/us.zoom.ZoomDaemon",
            "/Library/LaunchDaemons/us.zoom.updater.plist",
        ]

        for daemon_file in daemon_files:
            if os.path.exists(daemon_file):
                if daemon_file.endswith(".plist"):
                    self._run_command(
                        ["launchctl", "unload", daemon_file],
                        f"Unloading {os.path.basename(daemon_file)}",
                        require_sudo=True,
                    )

                self._run_command(
                    ["rm", "-f", daemon_file],
                    f"Removing {os.path.basename(daemon_file)}",
                    require_sudo=True,
                )
                self.cleanup_stats["system_locations_cleaned"] += 1

    def remove_audio_driver(self) -> None:
        """Remove Zoom audio driver"""
        self.logger.info("🔊 Removing audio driver...")

        audio_drivers = [
            "/Library/Audio/Plug-Ins/HAL/ZoomAudioDevice.driver",
            "/System/Library/Extensions/ZoomAudioDevice.kext",
            "/Library/Extensions/ZoomAudioDevice.kext",
        ]

        for driver in audio_drivers:
            if os.path.exists(driver):
                self._run_command(
                    ["rm", "-rf", driver],
                    f"Removing {os.path.basename(driver)}",
                    require_sudo=True,
                )
                self.cleanup_stats["system_locations_cleaned"] += 1

    def clean_webkit_storage(self) -> None:
        """Deep clean WebKit and HTTP storage"""
        self.logger.info("🌐 Deep cleaning WebKit storage...")

        webkit_paths = [
            f"{self.user_home}/Library/WebKit/us.zoom.xos",
            f"{self.user_home}/Library/HTTPStorages/us.zoom.xos",
            f"{self.user_home}/Library/HTTPStorages/us.zoom.xos.binarycookies",
            f"{self.user_home}/Library/Cookies/us.zoom.xos.binarycookies",
            f"{self.user_home}/Library/WebKit/NetworkProcess",
            f"{self.user_home}/Library/WebKit/WebProcess",
        ]

        for path in webkit_paths:
            self._remove_path(path, f"WebKit storage: {os.path.basename(path)}")

    def remove_group_containers(self) -> None:
        """Remove Group Containers"""
        self.logger.info("📦 Removing Group Containers...")

        group_containers = [
            f"{self.user_home}/Library/Group Containers/BJ4HAAB9B3.ZoomClient3rd",
            f"{self.user_home}/Library/Group Containers/us.zoom.xos",
            f"{self.user_home}/Library/Group Containers/zoom.us",
        ]

        for container in group_containers:
            self._remove_path(
                container, f"Group container: {os.path.basename(container)}"
            )

    def remove_zoom_applications(self) -> None:
        """Remove main Zoom applications from /Applications"""
        self.logger.info("🎯 Removing main Zoom applications...")

        # Common Zoom application paths
        zoom_app_paths = [
            "/Applications/zoom.us.app",
            "/Applications/Zoom.app",
            "/Applications/ZoomPhone.app",
            "/Applications/ZoomClips.app",
            "/Applications/ZoomChat.app",
            "/Applications/ZoomPresence.app",
            "/Applications/ZoomUpdater.app",
            "/Applications/ZoomInstaller.app",
        ]

        apps_found = 0
        for app_path in zoom_app_paths:
            if os.path.exists(app_path):
                self.logger.info(f"🎯 Found Zoom application: {app_path}")
                self._remove_path(
                    app_path, f"Zoom application: {os.path.basename(app_path)}"
                )
                apps_found += 1
            else:
                self.logger.debug(f"Zoom application not found: {app_path}")

        # Also check for any other Zoom-related apps in /Applications
        # but exclude our own cleanup tool
        try:
            if os.path.exists("/Applications"):
                for item in os.listdir("/Applications"):
                    if (
                        item.lower().startswith("zoom")
                        and item.endswith(".app")
                        and "deep clean" not in item.lower()
                        and "cleaner" not in item.lower()
                    ):

                        app_path = f"/Applications/{item}"
                        # Skip if already processed above
                        if app_path not in zoom_app_paths:
                            self.logger.info(
                                f"🎯 Found additional Zoom application: {app_path}"
                            )
                            self._remove_path(app_path, f"Additional Zoom app: {item}")
                            apps_found += 1
        except PermissionError:
            self.logger.warning("Permission denied accessing /Applications directory")
            self.cleanup_stats["warnings"] += 1
        except Exception as e:
            self.logger.error(f"Error scanning /Applications for Zoom apps: {e}")
            self.cleanup_stats["errors"] += 1

        if apps_found == 0:
            self.logger.info("ℹ️ No Zoom applications found in /Applications")
        else:
            self.logger.info(f"✅ Processed {apps_found} Zoom application(s)")

    def clean_zoom_encrypted_database(self) -> None:
        """Surgically target Zoom's encrypted database (ZoomFixer-inspired method)"""
        self.logger.info("🎯 Targeting Zoom encrypted database (ZoomFixer method)...")

        # Target the specific encrypted database file that stores device fingerprints
        encrypted_db_path = (
            f"{self.user_home}/Library/Application Support/zoom.us/data/zoomus.enc.db"
        )

        if os.path.exists(encrypted_db_path):
            self.logger.info(f"🔍 Found encrypted database: {encrypted_db_path}")
            # Use secure shredding for this critical file
            success = self._remove_path(
                encrypted_db_path,
                "Zoom encrypted database (device fingerprints)",
                force=True,  # Force removal even if verification fails
                secure_shred=True,  # Use secure shredding
            )
            if success:
                self.logger.info(
                    "✅ Encrypted database securely destroyed and replaced"
                )
                self.cleanup_stats["encrypted_databases_shredded"] += 1
            else:
                self.logger.error("❌ Failed to destroy encrypted database")
        else:
            self.logger.info("ℹ️ Encrypted database not found (may already be clean)")

        # Also target other fingerprint files in the data directory
        zoom_data_dir = f"{self.user_home}/Library/Application Support/zoom.us/data"
        if os.path.exists(zoom_data_dir):
            try:
                # Find all database, encrypted, and JSON files (ZoomFixer pattern)
                fingerprint_patterns = ["*.db", "*.enc", "*.json"]
                for pattern in fingerprint_patterns:
                    success, output = self._run_command(
                        ["find", zoom_data_dir, "-name", pattern, "-type", "f"],
                        f"Finding {pattern} files in Zoom data directory",
                    )
                    if success and output.strip():
                        files = output.strip().split("\n")
                        for file_path in files:
                            if file_path.strip():
                                self.logger.info(
                                    f"🎯 Found fingerprint file: {file_path}"
                                )
                                success = self._remove_path(
                                    file_path.strip(),
                                    f"Fingerprint file: {os.path.basename(file_path)}",
                                    force=True,
                                    secure_shred=True,
                                )
                                if success:
                                    self.cleanup_stats[
                                        "fingerprint_files_shredded"
                                    ] += 1
            except Exception as e:
                self.logger.error(f"Error scanning Zoom data directory: {e}")

    def clean_application_data(self) -> None:
        """Deep clean application data"""
        self.logger.info("🗄️ Deep cleaning application data...")

        # First, surgically target the encrypted database (ZoomFixer method)
        self.clean_zoom_encrypted_database()

        app_data_paths = [
            f"{self.user_home}/Library/Application Support/zoom.us",
            f"{self.user_home}/Library/Application Support/ZoomUpdater",
            f"{self.user_home}/Library/Application Support/ZoomPhone",
            f"{self.user_home}/Library/Application Support/ZoomClips",
            f"{self.user_home}/Library/Application Support/ZoomChat",
            f"{self.user_home}/Library/Application Support/ZoomPresence",
            f"{self.user_home}/Library/Caches/us.zoom.xos",
            f"{self.user_home}/Library/Caches/ZoomPhone",
            f"{self.user_home}/Library/Caches/ZoomChat",
            f"{self.user_home}/Library/Logs/zoom.us",
            f"{self.user_home}/Library/Logs/ZoomPhone",
            f"{self.user_home}/Library/Logs/ZoomChat",
            f"{self.user_home}/Library/Saved Application State/us.zoom.xos.savedState",
        ]

        for path in app_data_paths:
            self._remove_path(path, f"App data: {os.path.basename(path)}")

    def remove_preferences(self) -> None:
        """Remove preference files"""
        self.logger.info("⚙️ Removing preference files...")

        pref_files = [
            f"{self.user_home}/Library/Preferences/us.zoom.xos.plist",
            f"{self.user_home}/Library/Preferences/us.zoom.updater.plist",
            f"{self.user_home}/Library/Preferences/us.zoom.updater.config.plist",
            f"{self.user_home}/Library/Preferences/us.zoom.ZoomAutoUpdater.plist",
            f"{self.user_home}/Library/Preferences/us.zoom.ZoomClips.plist",
            f"{self.user_home}/Library/Preferences/ZoomChat.plist",
            f"{self.user_home}/Library/Preferences/ZoomPhone.plist",
            f"{self.user_home}/Library/Preferences/ZoomPresence.plist",
        ]

        for pref in pref_files:
            self._remove_path(pref, f"Preference: {os.path.basename(pref)}")

    def clean_system_caches(self) -> None:
        """Clean system caches and receipts with security validation"""
        self.logger.info("🧹 Cleaning system caches...")

        # Clean receipts using secure command execution
        self._run_command(
            ["find", "/private/var/db/receipts", "-name", "*zoom*", "-delete"],
            "Removing Zoom receipts",
            require_sudo=True,
            timeout=60,
        )

        # Clean temporary files more securely
        temp_dirs = ["/tmp", "/var/tmp", "/private/tmp", "/var/folders"]

        for temp_dir in temp_dirs:
            if os.path.exists(temp_dir):
                # Find zoom files in temp directory
                self._run_command(
                    ["find", temp_dir, "-name", "*zoom*", "-delete"],
                    f"Cleaning zoom files in {temp_dir}",
                    require_sudo=True,
                    timeout=60,
                )
                self.cleanup_stats["system_locations_cleaned"] += 1

    def reset_network_interfaces(self) -> None:
        """Reset network interfaces to change device fingerprint (ZoomFixer method)"""
        self.logger.info("🌐 Resetting network interfaces (ZoomFixer technique)...")

        # Get current Wi-Fi interface (usually en0 on Mac)
        wifi_interface = "en0"

        try:
            # Check if interface exists and is Wi-Fi
            success, output = self._run_command(
                ["networksetup", "-listallhardwareports"], "Listing network interfaces"
            )

            if success and "Wi-Fi" in output:
                # Find the Wi-Fi interface name
                lines = output.split("\n")
                for i, line in enumerate(lines):
                    if "Wi-Fi" in line and i + 1 < len(lines):
                        device_line = lines[i + 1]
                        if "Device:" in device_line:
                            wifi_interface = device_line.split("Device: ")[1].strip()
                            break

            self.logger.info(f"🔍 Detected Wi-Fi interface: {wifi_interface}")

            # Turn Wi-Fi off and on (ZoomFixer technique)
            self.logger.info(
                "📡 Cycling Wi-Fi interface to reset network fingerprint..."
            )

            # Turn Wi-Fi off
            success1, _ = self._run_command(
                ["networksetup", "-setairportpower", wifi_interface, "off"],
                f"Turning off Wi-Fi interface {wifi_interface}",
            )

            if not self.dry_run and success1:
                # Wait a moment for the interface to fully disconnect
                time.sleep(2)

                # Turn Wi-Fi back on
                success2, _ = self._run_command(
                    ["networksetup", "-setairportpower", wifi_interface, "on"],
                    f"Turning on Wi-Fi interface {wifi_interface}",
                )

                if success2:
                    self.logger.info("✅ Wi-Fi interface reset completed")
                    self.logger.info(
                        "💡 Note: You may need to reconnect to your Wi-Fi network"
                    )
                    self.cleanup_stats["network_interfaces_reset"] += 1
                    self.cleanup_stats["wifi_cycles_completed"] += 1
                else:
                    self.logger.warning("⚠️ Failed to turn Wi-Fi back on")
            elif success1:
                self.logger.info("✅ Wi-Fi interface cycle simulated")
                self.cleanup_stats["network_interfaces_reset"] += 1
                self.cleanup_stats["wifi_cycles_completed"] += 1

        except Exception as e:
            self.logger.error(f"Error resetting network interfaces: {e}")

    def randomize_hostname(self) -> None:
        """Randomize system hostname (ZoomFixer technique)"""
        self.logger.info("🏷️ Randomizing system hostname (ZoomFixer technique)...")

        try:
            # Generate new hostname with UUID (ZoomFixer pattern)
            import uuid

            random_id = str(uuid.uuid4()).split("-")[0]
            new_hostname = f"macbook-{random_id}"

            self.logger.info(f"🎲 Generated new hostname: {new_hostname}")

            # Set all hostname variants using scutil (ZoomFixer method)
            hostname_commands = [
                (
                    ["scutil", "--set", "HostName", new_hostname],
                    f"Setting HostName to {new_hostname}",
                ),
                (
                    ["scutil", "--set", "LocalHostName", new_hostname],
                    f"Setting LocalHostName to {new_hostname}",
                ),
                (
                    ["scutil", "--set", "ComputerName", new_hostname],
                    f"Setting ComputerName to {new_hostname}",
                ),
            ]

            all_success = True
            for cmd_args, desc in hostname_commands:
                success, _ = self._run_command(cmd_args, desc, require_sudo=True)
                if not success:
                    all_success = False

            if all_success:
                self.logger.info("✅ System hostname randomized successfully")
                self.cleanup_stats["hostname_reset_success"] = True
            else:
                self.logger.warning("⚠️ Some hostname changes may have failed")

        except Exception as e:
            self.logger.error(f"Error randomizing hostname: {e}")

    def spoof_mac_address(self) -> None:
        """Attempt MAC address spoofing (ZoomFixer technique)"""
        self.logger.info("🎭 Attempting MAC address spoofing (ZoomFixer technique)...")

        # Check if spoof-mac tool is available
        success, _ = self._run_command(
            ["which", "spoof-mac"], "Checking for spoof-mac tool"
        )

        if success:
            # Use spoof-mac to randomize MAC address on en0
            success, output = self._run_command(
                ["spoof-mac", "randomize", "en0"],
                "Spoofing MAC address on en0",
                require_sudo=True,
            )

            if success:
                self.logger.info("✅ MAC address spoofed successfully")
                self.cleanup_stats["mac_addresses_spoofed"] += 1
            else:
                self.logger.warning("⚠️ MAC address spoofing failed")
        else:
            self.logger.info("ℹ️ spoof-mac tool not found - skipping MAC spoofing")
            self.logger.info("💡 Install spoof-mac with: brew install spoof-mac")

    def flush_network_caches(self) -> None:
        """Flush DNS and network caches with security validation"""
        self.logger.info("🔄 Flushing DNS and network caches...")

        network_commands = [
            (["dscacheutil", "-flushcache"], "Flushing DNS cache"),
            (["killall", "-HUP", "mDNSResponder"], "Restarting mDNSResponder"),
            (["pfctl", "-F", "all"], "Flushing firewall state tables"),
        ]

        for cmd_args, desc in network_commands:
            self._run_command(cmd_args, desc, require_sudo=True)

        # Add ZoomFixer network reset techniques
        self.reset_network_interfaces()
        self.randomize_hostname()
        self.spoof_mac_address()

    def comprehensive_file_search(self) -> List[str]:
        """Perform comprehensive search for remaining Zoom files"""
        self.logger.info(
            "🔍 Performing comprehensive search for remaining Zoom files..."
        )

        remaining_files = []
        search_locations = [
            "/Library",
            "/System/Library",
            "/private/var",
            "/Applications",
        ]

        # Add user directories to search locations
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

        excluded_dirs = [
            "*/.Trash/*",
            "*/Library/Caches/*",
            "*/Application Support/MobileSync/*",
            "*/Time Machine Backups/*",
        ]

        for location in search_locations:
            if not os.path.exists(location):
                continue

            self.logger.info(f"🔎 Searching in {location}...")

            # Use a more robust find command that handles permission errors
            find_command = ["find", location, "-iname", "*zoom*"]

            # Add exclusions
            for excluded in excluded_dirs:
                find_command.extend(["-not", "-path", excluded])

            find_command.extend(["-type", "f", "2>/dev/null"])

            # Run without requiring sudo for better permission handling
            try:
                result = subprocess.run(
                    find_command,
                    capture_output=True,
                    text=True,
                    timeout=180,
                    shell=False,
                )

                # Log the command for dry run mode
                if self.dry_run:
                    cmd_str = " ".join(find_command)
                    self.logger.info(
                        f"DRY RUN: Searching for Zoom files in {location} | Command: {cmd_str}"
                    )

                if result.stdout.strip():
                    found_files = [
                        f.strip()
                        for f in result.stdout.strip().split("\n")
                        if f.strip()
                    ]
                    remaining_files.extend(found_files)
                    self.cleanup_stats["remaining_files_found"] += len(found_files)

                # Log permission errors as debug info, not warnings
                if result.stderr and "Operation not permitted" in result.stderr:
                    self.logger.debug(
                        f"Some directories in {location} require elevated permissions"
                    )

            except subprocess.TimeoutExpired:
                self.logger.warning(f"Search in {location} timed out")
            except Exception as e:
                self.logger.debug(f"Search error in {location}: {e}")

        return remaining_files

    def run_advanced_features(self) -> Dict[str, Any]:
        """Execute advanced fingerprint detection and modification features"""
        if not self.enable_advanced_features:
            self.logger.info("🔒 Advanced features disabled")
            return {"enabled": False}

        self.logger.info("🚀 Running advanced fingerprint features...")
        advanced_results = {}

        try:
            # 1. Comprehensive Keychain Scan
            self.logger.info("=" * 60)
            keychain_results = self.advanced_features.scan_keychain_comprehensive()
            advanced_results["keychain_scan"] = keychain_results
            self.cleanup_stats["keychain_comprehensive_scan"] = True
            self.cleanup_stats["advanced_features_executed"] += 1

            # 2. MDM Profile Detection
            self.logger.info("=" * 60)
            mdm_results = self.advanced_features.detect_mdm_profiles()
            advanced_results["mdm_detection"] = mdm_results
            self.cleanup_stats["mdm_profiles_detected"] = mdm_results["total_profiles"]
            self.cleanup_stats["advanced_features_executed"] += 1

            # 3. System UUID Detection
            self.logger.info("=" * 60)
            uuid_results = self.advanced_features.detect_system_uuids()
            advanced_results["uuid_detection"] = uuid_results
            self.cleanup_stats["system_identifiers_detected"] = uuid_results[
                "total_identifiers"
            ]
            self.cleanup_stats["advanced_features_executed"] += 1

            # 4. Hostname Reset (if enabled)
            if self.reset_hostname:
                self.logger.info("=" * 60)
                hostname_results = self.advanced_features.reset_hostname(
                    self.new_hostname
                )
                advanced_results["hostname_reset"] = hostname_results
                self.cleanup_stats["hostname_reset_success"] = hostname_results[
                    "success"
                ]
                self.cleanup_stats["advanced_features_executed"] += 1

            # 5. MAC Address Spoofing (if enabled)
            if self.enable_mac_spoofing:
                self.logger.info("=" * 60)
                mac_results = self.advanced_features.spoof_mac_addresses()
                advanced_results["mac_spoofing"] = mac_results
                if "interfaces_spoofed" in mac_results:
                    self.cleanup_stats["mac_addresses_spoofed"] = len(
                        mac_results["interfaces_spoofed"]
                    )
                self.cleanup_stats["advanced_features_executed"] += 1

            self.logger.info("=" * 60)
            self.logger.info("✅ Advanced features execution completed")

        except AdvancedFeaturesError as e:
            self.logger.error(f"Advanced features error: {e}")
            advanced_results["error"] = str(e)
            self.cleanup_stats["errors"] += 1
        except Exception as e:
            self.logger.error(f"Unexpected error in advanced features: {e}")
            advanced_results["error"] = str(e)
            self.cleanup_stats["errors"] += 1

        return advanced_results

    def show_hardware_info(self) -> None:
        """Display hardware identifier information using secure command execution"""
        self.logger.info("🆔 Hardware identifier status:")

        try:
            success, output = self._run_command(
                ["system_profiler", "SPHardwareDataType"],
                "Retrieving hardware information",
                timeout=15,
            )

            if success:
                for line in output.split("\n"):
                    if any(
                        keyword in line
                        for keyword in [
                            "Hardware UUID",
                            "Serial Number",
                            "Model Identifier",
                        ]
                    ):
                        self.logger.info(f"   📋 {line.strip()}")
            else:
                self.logger.warning("Could not retrieve hardware information")

        except Exception as e:
            self.logger.warning(f"Error retrieving hardware info: {e}")

    def perform_system_reboot(self) -> None:
        """Perform system reboot if requested"""
        if not self.system_reboot:
            return

        if self.dry_run:
            self.logger.info("DRY RUN: Would reboot system")
            return

        self.logger.info("🔄 Initiating system reboot...")
        self.logger.info("System will reboot in 10 seconds. Press Ctrl+C to cancel.")

        try:
            time.sleep(10)
            self._run_command(
                ["shutdown", "-r", "now"], "Rebooting system", require_sudo=True
            )
        except KeyboardInterrupt:
            self.logger.info("System reboot cancelled by user")

    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive cleanup report with security metrics"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "version": "2.2.0-vm-aware-system-wide",
            "dry_run": self.dry_run,
            "backup_enabled": self.enable_backup,
            "vm_aware": self.vm_aware,
            "system_reboot": self.system_reboot,
            "backup_location": self.backup_dir if self.enable_backup else None,
            "statistics": self.cleanup_stats,
            "log_file": self.log_file,
            "security_features": {
                "path_validation": True,
                "command_sanitization": True,
                "zoom_file_verification": True,
                "backup_functionality": self.enable_backup,
                "vm_awareness": self.vm_aware,
                "comprehensive_search": True,
            },
        }

        return report

    def export_dry_run_operations(self, output_file: Optional[str] = None) -> str:
        """Export dry-run operations to JSON file"""
        if not self.dry_run:
            raise ValueError("Can only export operations in dry-run mode")

        if not hasattr(self, "dry_run_operations"):
            self.dry_run_operations = []

        # Prepare export data
        export_data = {
            "metadata": {
                "version": "2.2.0",
                "timestamp": datetime.now().isoformat(),
                "dry_run": True,
                "total_operations": len(self.dry_run_operations),
            },
            "operations": self.dry_run_operations,
            "summary": {
                "process_operations": len(
                    [
                        op
                        for op in self.dry_run_operations
                        if any(
                            cmd in str(op["command"])
                            for cmd in ["pkill", "kill", "pgrep"]
                        )
                    ]
                ),
                "file_operations": len(
                    [
                        op
                        for op in self.dry_run_operations
                        if any(
                            cmd in str(op["command"])
                            for cmd in ["find", "rm", "delete"]
                        )
                    ]
                ),
                "security_operations": len(
                    [
                        op
                        for op in self.dry_run_operations
                        if "security" in str(op["command"])
                    ]
                ),
                "system_operations": len(
                    [
                        op
                        for op in self.dry_run_operations
                        if any(
                            cmd in str(op["command"])
                            for cmd in ["launchctl", "system_profiler", "ioreg"]
                        )
                    ]
                ),
            },
        }

        # Determine output file
        if output_file is None:
            output_file = os.path.expanduser("~/Documents/zoom_dry_run_operations.json")

        # Write JSON file
        try:
            with open(output_file, "w") as f:
                json.dump(export_data, f, indent=2, default=str)

            self.logger.info(f"📋 Dry-run operations exported to: {output_file}")
            return output_file

        except Exception as e:
            self.logger.error(f"Failed to export dry-run operations: {e}")
            raise

    def save_report(self, report: Dict[str, Any]) -> None:
        """Save cleanup report to JSON file with security validation"""
        try:
            report_file = self._validate_path(
                os.path.expanduser("~/Documents/zoom_cleanup_enhanced_report.json")
            )

            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(report_file), mode=0o755, exist_ok=True)

            with open(report_file, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2, ensure_ascii=False)

            # Set secure file permissions
            os.chmod(report_file, 0o600)

            self.logger.info(f"📊 Enhanced cleanup report saved to: {report_file}")

        except SecurityError as e:
            self.logger.error(f"Security validation failed for report file: {e}")
        except Exception as e:
            self.logger.error(f"Could not save report: {e}")

    def was_cancelled_by_user(self) -> bool:
        """Check if the operation was cancelled by user (Ctrl+C)"""
        return self.user_cancelled

    def run_deep_clean(self) -> bool:
        """Execute the complete enhanced deep clean process"""
        try:
            self.logger.info(
                "🔥 ZOOM DEEP CLEAN ENHANCED - VM-Aware & System-Wide v2.2.0 by PHLthy215"
            )
            self.logger.info("=" * 80)

            # Check sudo access for system operations
            if not self._check_sudo_access() and not self.dry_run:
                self.logger.warning(
                    "Sudo access not available - some system-level cleanup may fail"
                )

            # Execute enhanced cleanup steps
            self.stop_zoom_processes()
            self.remove_zoom_applications()  # NEW: Remove main Zoom apps from /Applications

            # Comprehensive authentication token cleanup (CRITICAL for login issues)
            self.logger.info(
                "🔐 Starting comprehensive authentication token cleanup..."
            )
            auth_cleaner = AuthTokenCleaner(verbose=self.verbose, dry_run=self.dry_run)
            auth_cleanup_results = auth_cleaner.clean_all_auth_tokens()

            self.remove_keychain_entries()
            self.remove_launch_agents()
            self.remove_system_daemon()
            self.remove_audio_driver()
            self.clean_webkit_storage()
            self.remove_group_containers()
            self.clean_application_data()
            self.remove_preferences()
            self.clean_system_caches()
            self.flush_network_caches()

            # Execute deep system cleanup (addresses "login works but can't join meetings" issue)
            self.logger.info("🔍 Starting deep system artifact cleanup...")
            deep_cleanup_results = (
                self.deep_system_cleaner.clean_deep_system_artifacts()
            )

            # Update cleanup stats with deep cleanup results
            for key, value in deep_cleanup_results.items():
                if key in self.cleanup_stats:
                    self.cleanup_stats[key] += value
                else:
                    self.cleanup_stats[key] = value

            # Run advanced fingerprint features
            advanced_results = self.run_advanced_features()

            # Verify deep system cleanup was successful
            deep_cleanup_verified = self.deep_system_cleaner.verify_deep_cleanup()
            if not deep_cleanup_verified:
                self.logger.warning(
                    "⚠️ Deep system cleanup verification failed - some artifacts may remain"
                )
            else:
                self.logger.info("✅ Deep system cleanup verification passed")

            # Perform comprehensive search for remaining files
            remaining_files = self.comprehensive_file_search()
            if remaining_files:
                self.logger.warning(
                    f"⚠️ Found {len(remaining_files)} remaining Zoom files:"
                )
                for file_path in remaining_files[:10]:  # Show first 10
                    self.logger.warning(f"   📄 {file_path}")
                if len(remaining_files) > 10:
                    self.logger.warning(
                        f"   ... and {len(remaining_files) - 10} more files"
                    )

            self.show_hardware_info()

            # Perform comprehensive device fingerprint verification
            self.logger.info(
                "🔍 Starting comprehensive device fingerprint verification..."
            )
            fingerprint_verifier = DeviceFingerprintVerifier(verbose=self.verbose)
            verification_report = fingerprint_verifier.verify_complete_cleanup()

            # Generate and save report
            report = self.generate_report()
            report["advanced_features_results"] = (
                advanced_results if "advanced_results" in locals() else {}
            )
            report["deep_system_cleanup"] = {
                "results": deep_cleanup_results,
                "verification_passed": deep_cleanup_verified,
                "detailed_report": self.deep_system_cleaner.generate_deep_cleanup_report(),
            }
            report["device_fingerprint_verification"] = verification_report
            report["authentication_cleanup"] = auth_cleanup_results
            self.save_report(report)

            # Final summary
            self.logger.info("=" * 80)
            self.logger.info(
                "🎉 ENHANCED DEEP CLEAN COMPLETE - With ZoomFixer Techniques!"
            )
            self.logger.info(f"📊 Statistics:")
            self.logger.info(
                f"   • Files removed: {self.cleanup_stats['files_removed']}"
            )
            self.logger.info(
                f"   • Directories removed: {self.cleanup_stats['directories_removed']}"
            )
            self.logger.info(
                f"   • Processes killed: {self.cleanup_stats['processes_killed']}"
            )
            self.logger.info(
                f"   • VM services stopped: {self.cleanup_stats['vm_services_stopped']}"
            )
            self.logger.info(
                f"   • Keychain entries removed: {self.cleanup_stats['keychain_entries_removed']}"
            )
            self.logger.info(
                f"   • System locations cleaned: {self.cleanup_stats['system_locations_cleaned']}"
            )
            self.logger.info(
                f"   • Files backed up: {self.cleanup_stats['files_backed_up']}"
            )
            self.logger.info(
                f"   • Remaining files found: {self.cleanup_stats['remaining_files_found']}"
            )

            # ZoomFixer-inspired features statistics
            self.logger.info("🎯 ZoomFixer-Inspired Features:")
            self.logger.info(
                f"   • Encrypted databases shredded: {self.cleanup_stats['encrypted_databases_shredded']}"
            )
            self.logger.info(
                f"   • Fingerprint files shredded: {self.cleanup_stats['fingerprint_files_shredded']}"
            )
            self.logger.info(
                f"   • Network interfaces reset: {self.cleanup_stats['network_interfaces_reset']}"
            )
            self.logger.info(
                f"   • Wi-Fi cycles completed: {self.cleanup_stats['wifi_cycles_completed']}"
            )
            self.logger.info(
                f"   • MAC addresses spoofed: {self.cleanup_stats['mac_addresses_spoofed']}"
            )
            self.logger.info(
                f"   • Hostname randomized: {'✅ YES' if self.cleanup_stats['hostname_reset_success'] else '❌ NO'}"
            )

            # Deep system cleanup statistics
            self.logger.info("🔍 Deep System Cleanup:")
            self.logger.info(
                f"   • IORegistry entries cleared: {deep_cleanup_results.get('ioreg_entries_cleared', 0)}"
            )
            self.logger.info(
                f"   • System temp files cleaned: {deep_cleanup_results.get('system_temp_cleaned', 0)}"
            )
            self.logger.info(
                f"   • Network configs reset: {deep_cleanup_results.get('network_configs_reset', 0)}"
            )
            self.logger.info(
                f"   • Audio/video configs reset: {deep_cleanup_results.get('audio_video_configs_reset', 0)}"
            )
            self.logger.info(
                f"   • System identifiers cleared: {deep_cleanup_results.get('system_identifiers_cleared', 0)}"
            )
            self.logger.info(
                f"   • Receipt files removed: {deep_cleanup_results.get('receipt_files_removed', 0)}"
            )
            self.logger.info(
                f"   • Deep caches cleared: {deep_cleanup_results.get('deep_cache_cleared', 0)}"
            )
            self.logger.info(
                f"   • Kernel extensions cleared: {deep_cleanup_results.get('kernel_extensions_cleared', 0)}"
            )

            # Authentication cleanup statistics
            self.logger.info("🔐 Authentication Token Cleanup:")
            auth_items_cleaned = len(auth_cleanup_results.get("cleaned_items", []))
            auth_errors = len(auth_cleanup_results.get("errors", []))
            auth_success = auth_cleanup_results.get("success", False)

            self.logger.info(
                f"   • Authentication tokens cleaned: {auth_items_cleaned}"
            )
            self.logger.info(f"   • Authentication cleanup errors: {auth_errors}")
            self.logger.info(
                f"   • Authentication cleanup success: {'✅ YES' if auth_success else '❌ NO'}"
            )

            if auth_success:
                self.logger.info("🎉 SUCCESS: All authentication tokens cleared!")
            else:
                self.logger.warning("⚠️ WARNING: Some authentication data may remain")

            # Device fingerprint verification statistics
            self.logger.info("🔍 Device Fingerprint Verification:")
            device_ready = verification_report.get("verification_summary", {}).get(
                "device_ready_for_zoom", False
            )
            items_cleaned = verification_report.get("verification_summary", {}).get(
                "total_items_cleaned", 0
            )
            items_remaining = verification_report.get("verification_summary", {}).get(
                "remaining_items_count", 0
            )

            self.logger.info(
                f"   • Device ready for Zoom: {'✅ YES' if device_ready else '❌ NO'}"
            )
            self.logger.info(f"   • Additional items cleaned: {items_cleaned}")
            self.logger.info(f"   • Items still remaining: {items_remaining}")

            if device_ready:
                self.logger.info("🎉 SUCCESS: Device will appear as NEW to Zoom!")
            else:
                self.logger.warning("⚠️ WARNING: Some device identifiers may remain")

            # Advanced features statistics
            if self.enable_advanced_features:
                self.logger.info(
                    f"   • Advanced features executed: {self.cleanup_stats['advanced_features_executed']}"
                )
                self.logger.info(
                    f"   • Keychain comprehensive scan: {self.cleanup_stats['keychain_comprehensive_scan']}"
                )
                self.logger.info(
                    f"   • MDM profiles detected: {self.cleanup_stats['mdm_profiles_detected']}"
                )
                self.logger.info(
                    f"   • System identifiers detected: {self.cleanup_stats['system_identifiers_detected']}"
                )
                if self.reset_hostname:
                    self.logger.info(
                        f"   • Hostname reset success: {self.cleanup_stats['hostname_reset_success']}"
                    )
                if self.enable_mac_spoofing:
                    self.logger.info(
                        f"   • MAC addresses spoofed: {self.cleanup_stats['mac_addresses_spoofed']}"
                    )

            self.logger.info(
                f"   • Security violations: {self.cleanup_stats['security_violations']}"
            )
            self.logger.info(f"   • Warnings: {self.cleanup_stats['warnings']}")
            self.logger.info(f"   • Errors: {self.cleanup_stats['errors']}")

            if not self.dry_run:
                self.logger.info("\n🔄 Recommended next steps:")
                if self.system_reboot:
                    self.logger.info("   1. System will reboot automatically")
                else:
                    self.logger.info("   1. Restart your computer manually")
                self.logger.info("   2. Download fresh Zoom installer")
                self.logger.info("   3. Install Zoom as if on a new device")

            # Perform system reboot if requested
            self.perform_system_reboot()

            # Return success only if no errors AND no security violations
            return (
                self.cleanup_stats["errors"] == 0
                and self.cleanup_stats["security_violations"] == 0
            )

        except KeyboardInterrupt:
            self.logger.warning("Operation cancelled by user")
            self.user_cancelled = True
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error during cleanup: {e}")
            return False

#!/usr/bin/env python3
"""
Enhanced Security Validation Module
Advanced security checks and validation for Zoom Deep Clean Enhanced

Created by: PHLthy215 (Enhanced by Amazon Q)
Version: 2.3.0 - Security Enhanced
"""

import os
import sys
import hashlib
import hmac
import secrets
import subprocess
import re
from typing import List, Dict, Tuple, Optional, Set
from pathlib import Path
import logging


class SecurityValidator:
    """Enhanced security validation for system operations"""

    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.session_token = secrets.token_hex(32)
        self.validated_paths: Set[str] = set()

        # Enhanced path validation patterns
        self.DANGEROUS_PATTERNS = [
            r"\.\./",  # Directory traversal
            r"/etc/",  # System config (unless specifically allowed)
            r"/usr/bin/",  # System binaries
            r"/System/",  # macOS system files
            r"[;&|`$]",  # Command injection chars
            r"rm\s+-rf\s+/",  # Dangerous rm commands
        ]

        # Allowed system paths for Zoom cleanup
        self.ALLOWED_SYSTEM_PATHS = {
            "/Library/LaunchAgents/",
            "/Library/LaunchDaemons/",
            "/Library/Application Support/",
            "/Library/Caches/",
            "/Library/Preferences/",
            "/var/db/receipts/",
            "/private/var/",
        }

    def validate_operation_context(self) -> bool:
        """Validate the security context for operations"""
        try:
            # Check if running with appropriate privileges
            if os.geteuid() == 0:
                self.logger.warning(
                    "Running as root - enhanced security checks enabled"
                )

            # Validate system integrity
            if not self._check_system_integrity():
                return False

            # Check for suspicious processes
            if not self._check_process_environment():
                return False

            return True

        except Exception as e:
            self.logger.error(f"Security context validation failed: {e}")
            return False

    def validate_path_operation(self, path: str, operation: str) -> bool:
        """Enhanced path validation with operation-specific checks"""
        try:
            # Basic path validation
            if not self._basic_path_validation(path):
                return False

            # Operation-specific validation
            if operation == "delete":
                return self._validate_delete_operation(path)
            elif operation == "read":
                return self._validate_read_operation(path)
            elif operation == "write":
                return self._validate_write_operation(path)

            return True

        except Exception as e:
            self.logger.error(f"Path validation failed for {path}: {e}")
            return False

    def _basic_path_validation(self, path: str) -> bool:
        """Basic path security validation"""
        # Check for dangerous patterns
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, path):
                self.logger.error(f"Dangerous pattern detected in path: {path}")
                return False

        # Validate path length
        if len(path) > 1024:
            self.logger.error(f"Path too long: {len(path)} characters")
            return False

        # Check if path is within allowed boundaries
        resolved_path = os.path.realpath(path)
        if not self._is_path_allowed(resolved_path):
            self.logger.error(f"Path not in allowed locations: {resolved_path}")
            return False

        return True

    def _is_path_allowed(self, path: str) -> bool:
        """Check if path is in allowed locations"""
        # User home directory is always allowed
        user_home = os.path.expanduser("~")
        if path.startswith(user_home):
            return True

        # Check allowed system paths
        for allowed_path in self.ALLOWED_SYSTEM_PATHS:
            if path.startswith(allowed_path):
                return True

        return False

    def _validate_delete_operation(self, path: str) -> bool:
        """Validate delete operations with extra security"""
        # Never allow deletion of critical system files
        critical_paths = [
            "/System/",
            "/usr/bin/",
            "/usr/sbin/",
            "/bin/",
            "/sbin/",
            "/etc/passwd",
            "/etc/hosts",
        ]

        for critical in critical_paths:
            if path.startswith(critical):
                self.logger.error(f"Attempted deletion of critical path: {path}")
                return False

        return True

    def _check_system_integrity(self) -> bool:
        """Check system integrity before operations"""
        try:
            # Check if SIP is enabled (recommended)
            result = subprocess.run(
                ["csrutil", "status"], capture_output=True, text=True
            )
            if result.returncode == 0:
                if "enabled" in result.stdout.lower():
                    self.logger.info("System Integrity Protection is enabled (good)")
                else:
                    self.logger.warning("System Integrity Protection is disabled")

            return True

        except Exception as e:
            self.logger.warning(f"Could not check system integrity: {e}")
            return True  # Don't fail if we can't check

    def _check_process_environment(self) -> bool:
        """Check for suspicious process environment"""
        try:
            # Check for debugging/analysis tools
            suspicious_processes = [
                "dtrace",
                "dtruss",
                "fs_usage",
                "lsof",
                "wireshark",
                "tcpdump",
                "nmap",
            ]

            result = subprocess.run(["ps", "aux"], capture_output=True, text=True)
            if result.returncode == 0:
                for proc in suspicious_processes:
                    if proc in result.stdout:
                        self.logger.warning(f"Suspicious process detected: {proc}")

            return True

        except Exception as e:
            self.logger.warning(f"Could not check process environment: {e}")
            return True

    def generate_operation_signature(self, operation: str, path: str) -> str:
        """Generate HMAC signature for operations"""
        message = f"{operation}:{path}:{self.session_token}"
        signature = hmac.new(
            self.session_token.encode(), message.encode(), hashlib.sha256
        ).hexdigest()
        return signature

    def verify_operation_signature(
        self, operation: str, path: str, signature: str
    ) -> bool:
        """Verify operation signature"""
        expected = self.generate_operation_signature(operation, path)
        return hmac.compare_digest(expected, signature)


class FileIntegrityChecker:
    """Check file integrity and detect Zoom-related files"""

    def __init__(self, logger: logging.Logger):
        self.logger = logger

        # Known Zoom file signatures
        self.ZOOM_SIGNATURES = [
            b"us.zoom.xos",
            b"zoom.us",
            b"ZoomPhone",
            b"ZoomClips",
            b"ZoomChat",
            b"com.zoom.",
            b"ZoomOpener",
            b"ZoomPresence",
        ]

    def verify_zoom_file(self, file_path: str) -> bool:
        """Verify if file is actually Zoom-related"""
        try:
            if not os.path.exists(file_path):
                return False

            # Check file size (avoid huge files)
            file_size = os.path.getsize(file_path)
            if file_size > 100 * 1024 * 1024:  # 100MB limit
                self.logger.warning(f"File too large for signature check: {file_path}")
                return self._check_path_indicators(file_path)

            # Read file and check for Zoom signatures
            with open(file_path, "rb") as f:
                content = f.read(8192)  # Read first 8KB

                for signature in self.ZOOM_SIGNATURES:
                    if signature in content:
                        self.logger.debug(f"Zoom signature found in {file_path}")
                        return True

            # Check path-based indicators
            return self._check_path_indicators(file_path)

        except Exception as e:
            self.logger.warning(f"Could not verify Zoom file {file_path}: {e}")
            return self._check_path_indicators(file_path)

    def _check_path_indicators(self, file_path: str) -> bool:
        """Check if path indicates Zoom-related file"""
        path_lower = file_path.lower()
        zoom_indicators = [
            "zoom",
            "zoomphone",
            "zoomchat",
            "zoomclips",
            "us.zoom",
            "com.zoom",
            "zoomopener",
        ]

        return any(indicator in path_lower for indicator in zoom_indicators)

    def calculate_file_hash(self, file_path: str) -> Optional[str]:
        """Calculate SHA-256 hash of file"""
        try:
            hash_sha256 = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            self.logger.warning(f"Could not calculate hash for {file_path}: {e}")
            return None

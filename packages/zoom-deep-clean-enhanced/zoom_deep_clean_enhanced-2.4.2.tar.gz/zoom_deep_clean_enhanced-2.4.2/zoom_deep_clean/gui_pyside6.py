#!/usr/bin/env python3
"""
Zoom Deep Clean Enhanced - Modern PySide6 GUI
Native macOS interface with async operations and performance optimizations

Created by: PHLthy215 (Enhanced with PySide6)
Version: 2.3.0 - PySide6 GUI
"""

import sys
import os
import asyncio
import json
import webbrowser
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from concurrent.futures import ThreadPoolExecutor
import threading

try:
    from PySide6.QtWidgets import (
        QApplication,
        QMainWindow,
        QWidget,
        QVBoxLayout,
        QHBoxLayout,
        QGridLayout,
        QLabel,
        QPushButton,
        QTextEdit,
        QProgressBar,
        QCheckBox,
        QGroupBox,
        QTabWidget,
        QScrollArea,
        QSplitter,
        QMenuBar,
        QMenu,
        QStatusBar,
        QMessageBox,
        QFileDialog,
        QDialog,
        QDialogButtonBox,
        QFrame,
        QSpacerItem,
        QSizePolicy,
    )
    from PySide6.QtCore import (
        Qt,
        QThread,
        QObject,
        Signal,
        QTimer,
        QSize,
        QRect,
        QPropertyAnimation,
        QEasingCurve,
        QParallelAnimationGroup,
    )
    from PySide6.QtGui import (
        QFont,
        QIcon,
        QPixmap,
        QPalette,
        QColor,
        QAction,
        QTextCursor,
        QTextCharFormat,
        QSyntaxHighlighter,
    )

    PYSIDE6_AVAILABLE = True
except ImportError:
    PYSIDE6_AVAILABLE = False
    print("PySide6 not available. Install with: pip install PySide6")
    sys.exit(1)

# Add the package to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from .cleaner_enhanced import ZoomDeepCleanerEnhanced
from .advanced_features import AdvancedFeatures


class LogHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for log output with color coding"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_formats()

    def setup_formats(self):
        """Setup text formats for different log levels"""
        self.formats = {}

        # Error format (red)
        error_format = QTextCharFormat()
        error_format.setForeground(QColor(220, 50, 47))  # Red
        error_format.setFontWeight(QFont.Bold)
        self.formats["ERROR"] = error_format

        # Warning format (orange)
        warning_format = QTextCharFormat()
        warning_format.setForeground(QColor(203, 75, 22))  # Orange
        self.formats["WARNING"] = warning_format

        # Info format (blue)
        info_format = QTextCharFormat()
        info_format.setForeground(QColor(38, 139, 210))  # Blue
        self.formats["INFO"] = info_format

        # Success format (green)
        success_format = QTextCharFormat()
        success_format.setForeground(QColor(133, 153, 0))  # Green
        self.formats["SUCCESS"] = success_format

        # Timestamp format (gray)
        timestamp_format = QTextCharFormat()
        timestamp_format.setForeground(QColor(147, 161, 161))  # Gray
        self.formats["TIMESTAMP"] = timestamp_format

    def highlightBlock(self, text):
        """Apply syntax highlighting to text block"""
        # Highlight timestamps
        if text.startswith("["):
            end_bracket = text.find("]")
            if end_bracket > 0:
                self.setFormat(0, end_bracket + 1, self.formats["TIMESTAMP"])

        # Highlight log levels
        for level, format_obj in self.formats.items():
            if level in ["ERROR", "WARNING", "INFO", "SUCCESS"]:
                if level in text:
                    start = text.find(level)
                    if start >= 0:
                        self.setFormat(start, len(level), format_obj)


class CleanupWorker(QObject):
    """Worker thread for cleanup operations with progress reporting"""

    # Signals
    progress_updated = Signal(int, str)  # progress, message
    log_message = Signal(str)
    cleanup_finished = Signal(bool, dict)  # success, results

    def __init__(self, cleaner_config: Dict[str, Any]):
        super().__init__()
        self.cleaner_config = cleaner_config
        self.cleaner = None
        self.is_cancelled = False

    def run_cleanup(self):
        """Execute cleanup operation with progress reporting"""
        try:
            # Extract force flag and performance monitoring flag
            force_cleanup = self.cleaner_config.pop("_force_cleanup", False)
            enable_performance_monitoring = self.cleaner_config.pop(
                "_enable_performance_monitoring", True
            )

            self.log_message.emit(
                f"DEBUG: Cleaner config after processing: {self.cleaner_config}"
            )
            self.log_message.emit(f"DEBUG: Force cleanup: {force_cleanup}")
            self.log_message.emit(
                f"DEBUG: Performance monitoring: {enable_performance_monitoring}"
            )

            # Initialize cleaner with valid config
            self.progress_updated.emit(5, "Creating cleaner instance...")
            self.cleaner = ZoomDeepCleanerEnhanced(**self.cleaner_config)

            # Connect to cleaner's progress signals if available
            self.progress_updated.emit(10, "Initializing cleanup...")
            self.log_message.emit("✅ Cleaner initialized successfully")

            # Handle force cleanup logic
            if not self.cleaner.dry_run and not force_cleanup:
                # This would normally be handled by the GUI confirmation dialog
                # but we'll let the GUI handle the confirmation
                pass

            # Run the cleanup
            self.progress_updated.emit(20, "Starting cleanup process...")
            self.log_message.emit("🔄 Running cleanup process...")

            success = self.cleaner.run_deep_clean()

            self.progress_updated.emit(90, "Generating report...")
            self.log_message.emit("📊 Generating cleanup report...")

            # Generate report
            report = self.cleaner.generate_report()

            self.progress_updated.emit(100, "Cleanup completed!")
            self.log_message.emit(f"✅ Cleanup completed with success: {success}")

            self.cleanup_finished.emit(success, report)

        except Exception as e:
            import traceback

            error_details = traceback.format_exc()
            self.log_message.emit(f"ERROR: Cleanup failed: {str(e)}")
            self.log_message.emit(f"ERROR: Full traceback:\n{error_details}")
            self.cleanup_finished.emit(False, {})

    def cancel_cleanup(self):
        """Cancel the cleanup operation"""
        self.is_cancelled = True
        if self.cleaner:
            self.cleaner.user_cancelled = True


class ModernZoomCleanerGUI(QMainWindow):
    """Modern PySide6 GUI for Zoom Deep Clean Enhanced"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Zoom Deep Clean Enhanced v2.3.0")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)

        # Initialize variables
        self.cleanup_worker = None
        self.cleanup_thread = None
        self.is_cleanup_running = False
        self.executor = ThreadPoolExecutor(max_workers=4)

        # Setup UI
        self.setup_ui()
        self.setup_menu_bar()
        self.setup_status_bar()
        self.apply_modern_styling()

        # Center window
        self.center_window()

    def setup_ui(self):
        """Setup the main user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # Header
        self.create_header(main_layout)

        # Main content area with splitter
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)

        # Left panel - Controls
        left_panel = self.create_control_panel()
        splitter.addWidget(left_panel)

        # Right panel - Output and progress
        right_panel = self.create_output_panel()
        splitter.addWidget(right_panel)

        # Set splitter proportions
        splitter.setSizes([400, 800])

        # Action buttons
        self.create_action_buttons(main_layout)

    def create_header(self, layout):
        """Create application header"""
        header_frame = QFrame()
        header_frame.setFrameStyle(QFrame.Box)
        header_frame.setStyleSheet(
            """
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f8f9fa, stop:1 #e9ecef);
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 10px;
            }
        """
        )

        header_layout = QHBoxLayout(header_frame)

        # Title and version
        title_label = QLabel("🧹 Zoom Deep Clean Enhanced")
        title_label.setFont(QFont("SF Pro Display", 24, QFont.Bold))
        title_label.setStyleSheet("color: #2c3e50; margin: 5px;")

        version_label = QLabel("v2.3.0 - PySide6 Edition")
        version_label.setFont(QFont("SF Pro Text", 12))
        version_label.setStyleSheet("color: #6c757d; margin: 5px;")

        header_layout.addWidget(title_label)
        header_layout.addWidget(version_label)
        header_layout.addStretch()

        # Status indicator
        self.status_indicator = QLabel("🟢 Ready")
        self.status_indicator.setFont(QFont("SF Pro Text", 14, QFont.Bold))
        self.status_indicator.setStyleSheet("color: #28a745; margin: 5px;")
        header_layout.addWidget(self.status_indicator)

        layout.addWidget(header_frame)

    def create_control_panel(self):
        """Create the left control panel"""
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        control_widget = QWidget()
        layout = QVBoxLayout(control_widget)
        layout.setSpacing(15)

        # Cleanup Options
        self.create_cleanup_options(layout)

        # Advanced Features
        self.create_advanced_options(layout)

        # VM Options
        self.create_vm_options(layout)

        # System Options
        self.create_system_options(layout)

        layout.addStretch()
        scroll_area.setWidget(control_widget)
        return scroll_area

    def create_cleanup_options(self, layout):
        """Create cleanup options group"""
        group = QGroupBox("🧹 Cleanup Options")
        group.setFont(QFont("SF Pro Text", 14, QFont.Bold))
        group_layout = QVBoxLayout(group)

        self.dry_run_cb = QCheckBox("Dry Run (Preview Only)")
        self.dry_run_cb.setChecked(True)
        self.dry_run_cb.setToolTip(
            "Preview what will be cleaned without making changes"
        )

        self.verbose_cb = QCheckBox("Verbose Output")
        self.verbose_cb.setChecked(True)
        self.verbose_cb.setToolTip("Show detailed information during cleanup")

        self.backup_cb = QCheckBox("Create Backups")
        self.backup_cb.setChecked(True)
        self.backup_cb.setToolTip("Create backups before removing files")

        self.force_cb = QCheckBox("Force Cleanup")
        self.force_cb.setToolTip("Force cleanup without confirmation prompts")

        group_layout.addWidget(self.dry_run_cb)
        group_layout.addWidget(self.verbose_cb)
        group_layout.addWidget(self.backup_cb)
        group_layout.addWidget(self.force_cb)

        layout.addWidget(group)

    def create_advanced_options(self, layout):
        """Create advanced options group"""
        group = QGroupBox("🔧 Advanced Features")
        group.setFont(QFont("SF Pro Text", 14, QFont.Bold))
        group_layout = QVBoxLayout(group)

        self.advanced_features_cb = QCheckBox("Enable Advanced Features")
        self.advanced_features_cb.setToolTip(
            "Enable MAC spoofing and fingerprint modification"
        )

        self.spoof_mac_cb = QCheckBox("Spoof MAC Address")
        self.spoof_mac_cb.setEnabled(False)
        self.spoof_mac_cb.setToolTip("Change MAC address for privacy")

        self.reset_hostname_cb = QCheckBox("Reset Hostname")
        self.reset_hostname_cb.setEnabled(False)
        self.reset_hostname_cb.setToolTip("Reset system hostname")

        # Connect advanced features checkbox
        self.advanced_features_cb.toggled.connect(self.toggle_advanced_features)

        group_layout.addWidget(self.advanced_features_cb)
        group_layout.addWidget(self.spoof_mac_cb)
        group_layout.addWidget(self.reset_hostname_cb)

        layout.addWidget(group)

    def create_vm_options(self, layout):
        """Create VM options group"""
        group = QGroupBox("🖥️ Virtual Machine Support")
        group.setFont(QFont("SF Pro Text", 14, QFont.Bold))
        group_layout = QVBoxLayout(group)

        self.vm_aware_cb = QCheckBox("VM-Aware Cleanup")
        self.vm_aware_cb.setChecked(True)
        self.vm_aware_cb.setToolTip("Detect and handle virtual machines during cleanup")

        self.stop_vms_cb = QCheckBox("Stop VMs During Cleanup")
        self.stop_vms_cb.setChecked(True)
        self.stop_vms_cb.setToolTip("Automatically stop VMs before cleanup")

        group_layout.addWidget(self.vm_aware_cb)
        group_layout.addWidget(self.stop_vms_cb)

        layout.addWidget(group)

    def create_system_options(self, layout):
        """Create system options group"""
        group = QGroupBox("⚙️ System Options")
        group.setFont(QFont("SF Pro Text", 14, QFont.Bold))
        group_layout = QVBoxLayout(group)

        self.system_reboot_cb = QCheckBox("Reboot After Cleanup")
        self.system_reboot_cb.setToolTip("Automatically reboot system after cleanup")

        self.performance_monitoring_cb = QCheckBox("Performance Monitoring")
        self.performance_monitoring_cb.setChecked(True)
        self.performance_monitoring_cb.setToolTip("Monitor performance during cleanup")

        group_layout.addWidget(self.system_reboot_cb)
        group_layout.addWidget(self.performance_monitoring_cb)

        layout.addWidget(group)

    def create_output_panel(self):
        """Create the right output panel"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Progress section
        progress_group = QGroupBox("📊 Progress")
        progress_group.setFont(QFont("SF Pro Text", 14, QFont.Bold))
        progress_layout = QVBoxLayout(progress_group)

        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setStyleSheet(
            """
            QProgressBar {
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                text-align: center;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3498db, stop:1 #2980b9);
                border-radius: 6px;
            }
        """
        )

        self.progress_label = QLabel("Ready to start cleanup...")
        self.progress_label.setFont(QFont("SF Pro Text", 12))
        self.progress_label.setStyleSheet("color: #6c757d; margin: 5px;")

        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.progress_label)

        # Output section
        output_group = QGroupBox("📝 Output Log")
        output_group.setFont(QFont("SF Pro Text", 14, QFont.Bold))
        output_layout = QVBoxLayout(output_group)

        self.output_text = QTextEdit()
        self.output_text.setFont(QFont("SF Mono", 11))
        self.output_text.setReadOnly(True)
        self.output_text.setStyleSheet(
            """
            QTextEdit {
                background-color: #2b2b2b;
                color: #f8f8f2;
                border: 1px solid #555;
                border-radius: 6px;
                padding: 10px;
            }
        """
        )

        # Add syntax highlighter
        self.highlighter = LogHighlighter(self.output_text.document())

        output_layout.addWidget(self.output_text)

        layout.addWidget(progress_group)
        layout.addWidget(output_group)

        return widget

    def create_action_buttons(self, layout):
        """Create action buttons"""
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        # Start cleanup button
        self.start_button = QPushButton("🚀 Start Cleanup")
        self.start_button.setFont(QFont("SF Pro Text", 14, QFont.Bold))
        self.start_button.setMinimumHeight(45)
        self.start_button.setStyleSheet(
            """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #27ae60, stop:1 #229954);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2ecc71, stop:1 #27ae60);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #229954, stop:1 #1e8449);
            }
            QPushButton:disabled {
                background: #bdc3c7;
                color: #7f8c8d;
            }
        """
        )
        self.start_button.clicked.connect(self.start_cleanup)

        # Cancel button
        self.cancel_button = QPushButton("⏹️ Cancel")
        self.cancel_button.setFont(QFont("SF Pro Text", 14, QFont.Bold))
        self.cancel_button.setMinimumHeight(45)
        self.cancel_button.setEnabled(False)
        self.cancel_button.setStyleSheet(
            """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #e74c3c, stop:1 #c0392b);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ec7063, stop:1 #e74c3c);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #c0392b, stop:1 #a93226);
            }
            QPushButton:disabled {
                background: #bdc3c7;
                color: #7f8c8d;
            }
        """
        )
        self.cancel_button.clicked.connect(self.cancel_cleanup)

        # Clear output button
        clear_button = QPushButton("🗑️ Clear Output")
        clear_button.setFont(QFont("SF Pro Text", 12))
        clear_button.setMinimumHeight(35)
        clear_button.clicked.connect(self.clear_output)

        # Save report button
        save_button = QPushButton("💾 Save Report")
        save_button.setFont(QFont("SF Pro Text", 12))
        save_button.setMinimumHeight(35)
        save_button.clicked.connect(self.save_report)

        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.cancel_button)
        button_layout.addStretch()
        button_layout.addWidget(clear_button)
        button_layout.addWidget(save_button)

        layout.addLayout(button_layout)

    def setup_menu_bar(self):
        """Setup application menu bar"""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")

        save_config_action = QAction("Save Configuration", self)
        save_config_action.setShortcut("Cmd+S")
        save_config_action.triggered.connect(self.save_configuration)
        file_menu.addAction(save_config_action)

        load_config_action = QAction("Load Configuration", self)
        load_config_action.setShortcut("Cmd+O")
        load_config_action.triggered.connect(self.load_configuration)
        file_menu.addAction(load_config_action)

        file_menu.addSeparator()

        export_log_action = QAction("Export Log", self)
        export_log_action.triggered.connect(self.export_log)
        file_menu.addAction(export_log_action)

        file_menu.addSeparator()

        quit_action = QAction("Quit", self)
        quit_action.setShortcut("Cmd+Q")
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        # Tools menu
        tools_menu = menubar.addMenu("Tools")

        hardware_info_action = QAction("Show Hardware Info", self)
        hardware_info_action.triggered.connect(self.show_hardware_info)
        tools_menu.addAction(hardware_info_action)

        system_info_action = QAction("System Information", self)
        system_info_action.triggered.connect(self.show_system_info)
        tools_menu.addAction(system_info_action)

        # Help menu
        help_menu = menubar.addMenu("Help")

        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

        help_action = QAction("Help", self)
        help_action.setShortcut("F1")
        help_action.triggered.connect(self.show_help)
        help_menu.addAction(help_action)

    def setup_status_bar(self):
        """Setup status bar"""
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Ready")

        # Add permanent widgets to status bar
        self.memory_label = QLabel("Memory: 0 MB")
        self.cpu_label = QLabel("CPU: 0%")

        self.status_bar.addPermanentWidget(self.memory_label)
        self.status_bar.addPermanentWidget(self.cpu_label)

        # Timer for updating system stats
        self.stats_timer = QTimer()
        self.stats_timer.timeout.connect(self.update_system_stats)
        self.stats_timer.start(2000)  # Update every 2 seconds

    def apply_modern_styling(self):
        """Apply modern macOS-style theming"""
        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #f8f9fa;
            }
            
            QGroupBox {
                font-weight: bold;
                border: 2px solid #dee2e6;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: white;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                color: #495057;
                background-color: white;
            }
            
            QCheckBox {
                font-size: 13px;
                color: #495057;
                spacing: 8px;
                margin: 4px;
            }
            
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 3px;
                border: 2px solid #6c757d;
                background-color: white;
            }
            
            QCheckBox::indicator:checked {
                background-color: #007bff;
                border-color: #007bff;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iOSIgdmlld0JveD0iMCAwIDEyIDkiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIGQ9Ik0xMC42IDEuNEw0LjIgNy44TDEuNCA1IiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPgo8L3N2Zz4K);
            }
            
            QCheckBox::indicator:hover {
                border-color: #007bff;
            }
            
            QPushButton {
                font-size: 13px;
                font-weight: 500;
                border: 1px solid #dee2e6;
                border-radius: 6px;
                padding: 8px 16px;
                background-color: white;
                color: #495057;
            }
            
            QPushButton:hover {
                background-color: #f8f9fa;
                border-color: #adb5bd;
            }
            
            QPushButton:pressed {
                background-color: #e9ecef;
            }
            
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            
            QScrollBar:vertical {
                background-color: #f8f9fa;
                width: 12px;
                border-radius: 6px;
            }
            
            QScrollBar::handle:vertical {
                background-color: #adb5bd;
                border-radius: 6px;
                min-height: 20px;
            }
            
            QScrollBar::handle:vertical:hover {
                background-color: #6c757d;
            }
        """
        )

    def center_window(self):
        """Center the window on screen"""
        screen = QApplication.primaryScreen().geometry()
        window = self.geometry()
        x = (screen.width() - window.width()) // 2
        y = (screen.height() - window.height()) // 2
        self.move(x, y)

    def toggle_advanced_features(self, enabled):
        """Toggle advanced features checkboxes"""
        self.spoof_mac_cb.setEnabled(enabled)
        self.reset_hostname_cb.setEnabled(enabled)

    def update_system_stats(self):
        """Update system statistics in status bar"""
        try:
            import psutil

            memory = psutil.virtual_memory()
            cpu = psutil.cpu_percent()

            self.memory_label.setText(f"Memory: {memory.percent:.1f}%")
            self.cpu_label.setText(f"CPU: {cpu:.1f}%")
        except ImportError:
            pass

    def append_log(self, message):
        """Append message to log output with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"

        self.output_text.append(formatted_message)

        # Auto-scroll to bottom
        cursor = self.output_text.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.output_text.setTextCursor(cursor)

    def clear_output(self):
        """Clear the output text area"""
        self.output_text.clear()
        self.append_log("Output cleared")

    def get_cleaner_config(self):
        """Get cleaner configuration from UI"""
        return {
            "dry_run": self.dry_run_cb.isChecked(),
            "verbose": self.verbose_cb.isChecked(),
            "enable_backup": self.backup_cb.isChecked(),
            "enable_advanced_features": self.advanced_features_cb.isChecked(),
            "vm_aware": self.vm_aware_cb.isChecked(),
            "system_reboot": self.system_reboot_cb.isChecked(),
            # Store force separately for use in cleanup logic
            "_force_cleanup": self.force_cb.isChecked(),
            "_enable_performance_monitoring": self.performance_monitoring_cb.isChecked(),
        }

    def start_cleanup(self):
        """Start the cleanup process"""
        if self.is_cleanup_running:
            return

        # Validate configuration
        config = self.get_cleaner_config()

        # Handle force confirmation
        force_cleanup = config.get("_force_cleanup", False)
        is_dry_run = config.get("dry_run", True)

        if not is_dry_run and not force_cleanup:
            reply = QMessageBox.question(
                self,
                "Confirm Cleanup",
                "This will permanently remove Zoom files from your system. Continue?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if reply != QMessageBox.Yes:
                return

        # Update UI state
        self.is_cleanup_running = True
        self.start_button.setEnabled(False)
        self.cancel_button.setEnabled(True)
        self.status_indicator.setText("🟡 Running...")
        self.status_indicator.setStyleSheet("color: #ffc107; margin: 5px;")
        self.progress_bar.setValue(0)
        self.progress_label.setText("Starting cleanup...")

        # Clear previous output
        self.output_text.clear()
        self.append_log("🚀 Starting Zoom Deep Clean Enhanced...")
        self.append_log(f"Configuration: {config}")

        # Create and start worker thread
        self.cleanup_thread = QThread()
        self.cleanup_worker = CleanupWorker(config)
        self.cleanup_worker.moveToThread(self.cleanup_thread)

        # Connect signals
        self.cleanup_worker.progress_updated.connect(self.update_progress)
        self.cleanup_worker.log_message.connect(self.append_log)
        self.cleanup_worker.cleanup_finished.connect(self.cleanup_finished)

        self.cleanup_thread.started.connect(self.cleanup_worker.run_cleanup)
        self.cleanup_thread.start()

    def cancel_cleanup(self):
        """Cancel the running cleanup"""
        if not self.is_cleanup_running:
            return

        reply = QMessageBox.question(
            self,
            "Cancel Cleanup",
            "Are you sure you want to cancel the cleanup?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            self.append_log("🛑 Cancelling cleanup...")
            if self.cleanup_worker:
                self.cleanup_worker.cancel_cleanup()

    def update_progress(self, value, message):
        """Update progress bar and message"""
        self.progress_bar.setValue(value)
        self.progress_label.setText(message)
        self.status_bar.showMessage(message)

    def cleanup_finished(self, success, results):
        """Handle cleanup completion"""
        self.is_cleanup_running = False
        self.start_button.setEnabled(True)
        self.cancel_button.setEnabled(False)

        if success:
            self.status_indicator.setText("🟢 Completed")
            self.status_indicator.setStyleSheet("color: #28a745; margin: 5px;")
            self.progress_bar.setValue(100)
            self.progress_label.setText("Cleanup completed successfully!")
            self.append_log("✅ Cleanup completed successfully!")

            # Show results summary
            if results:
                self.show_results_summary(results)
        else:
            self.status_indicator.setText("🔴 Failed")
            self.status_indicator.setStyleSheet("color: #dc3545; margin: 5px;")
            self.progress_label.setText("Cleanup failed!")
            self.append_log("❌ Cleanup failed!")

        # Clean up thread
        if self.cleanup_thread:
            self.cleanup_thread.quit()
            self.cleanup_thread.wait()
            self.cleanup_thread = None
            self.cleanup_worker = None

    def show_results_summary(self, results):
        """Show cleanup results summary"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Cleanup Results")
        dialog.setMinimumSize(600, 400)

        layout = QVBoxLayout(dialog)

        # Results text
        results_text = QTextEdit()
        results_text.setReadOnly(True)
        results_text.setPlainText(json.dumps(results, indent=2))
        results_text.setFont(QFont("SF Mono", 11))

        layout.addWidget(QLabel("Cleanup Results:"))
        layout.addWidget(results_text)

        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(dialog.accept)
        layout.addWidget(button_box)

        dialog.exec()

    def save_configuration(self):
        """Save current configuration to file"""
        config = self.get_cleaner_config()

        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save Configuration",
            "zoom_cleanup_config.json",
            "JSON Files (*.json)",
        )

        if filename:
            try:
                with open(filename, "w") as f:
                    json.dump(config, f, indent=2)
                self.append_log(f"Configuration saved to {filename}")
            except Exception as e:
                QMessageBox.critical(
                    self, "Error", f"Failed to save configuration: {e}"
                )

    def load_configuration(self):
        """Load configuration from file"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Load Configuration", "", "JSON Files (*.json)"
        )

        if filename:
            try:
                with open(filename, "r") as f:
                    config = json.load(f)

                # Apply configuration to UI
                self.dry_run_cb.setChecked(config.get("dry_run", True))
                self.verbose_cb.setChecked(config.get("verbose", True))
                self.backup_cb.setChecked(config.get("enable_backup", True))
                self.force_cb.setChecked(config.get("force", False))
                self.advanced_features_cb.setChecked(
                    config.get("enable_advanced_features", False)
                )
                self.vm_aware_cb.setChecked(config.get("vm_aware", True))
                self.system_reboot_cb.setChecked(config.get("system_reboot", False))
                self.performance_monitoring_cb.setChecked(
                    config.get("enable_performance_monitoring", True)
                )

                self.append_log(f"Configuration loaded from {filename}")
            except Exception as e:
                QMessageBox.critical(
                    self, "Error", f"Failed to load configuration: {e}"
                )

    def export_log(self):
        """Export log to file"""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export Log",
            f"zoom_cleanup_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            "Text Files (*.txt)",
        )

        if filename:
            try:
                with open(filename, "w") as f:
                    f.write(self.output_text.toPlainText())
                self.append_log(f"Log exported to {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export log: {e}")

    def save_report(self):
        """Save cleanup report"""
        # This would be implemented to save the last cleanup report
        QMessageBox.information(
            self, "Info", "Report saving will be implemented with cleanup results"
        )

    def show_hardware_info(self):
        """Show hardware information dialog"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Hardware Information")
        dialog.setMinimumSize(500, 400)

        layout = QVBoxLayout(dialog)

        info_text = QTextEdit()
        info_text.setReadOnly(True)
        info_text.setFont(QFont("SF Mono", 11))

        # Get hardware info (simplified version)
        try:
            import subprocess

            result = subprocess.run(
                ["system_profiler", "SPHardwareDataType"],
                capture_output=True,
                text=True,
            )
            info_text.setPlainText(result.stdout)
        except Exception as e:
            info_text.setPlainText(f"Error getting hardware info: {e}")

        layout.addWidget(info_text)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(dialog.accept)
        layout.addWidget(button_box)

        dialog.exec()

    def show_system_info(self):
        """Show system information dialog"""
        dialog = QDialog(self)
        dialog.setWindowTitle("System Information")
        dialog.setMinimumSize(500, 400)

        layout = QVBoxLayout(dialog)

        info_text = QTextEdit()
        info_text.setReadOnly(True)
        info_text.setFont(QFont("SF Mono", 11))

        # Get system info
        try:
            import platform
            import psutil

            info = f"""System Information:
OS: {platform.system()} {platform.release()}
Architecture: {platform.machine()}
Processor: {platform.processor()}
Python: {platform.python_version()}

Memory: {psutil.virtual_memory().total // (1024**3)} GB
CPU Cores: {psutil.cpu_count()}
"""
            info_text.setPlainText(info)
        except Exception as e:
            info_text.setPlainText(f"Error getting system info: {e}")

        layout.addWidget(info_text)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(dialog.accept)
        layout.addWidget(button_box)

        dialog.exec()

    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About Zoom Deep Clean Enhanced",
            """<h2>Zoom Deep Clean Enhanced v2.3.0</h2>
                         <p><b>PySide6 Edition</b></p>
                         <p>Complete Zoom removal tool for macOS with VM awareness and device fingerprint elimination.</p>
                         <p>Created by: PHLthy215</p>
                         <p>Enhanced with modern PySide6 interface</p>
                         <p><a href="https://github.com/PHLthy215/zoom-deep-clean-enhanced">GitHub Repository</a></p>
                         """,
        )

    def show_help(self):
        """Show help dialog"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Help")
        dialog.setMinimumSize(700, 500)

        layout = QVBoxLayout(dialog)

        help_text = QTextEdit()
        help_text.setReadOnly(True)
        help_text.setHtml(
            """
        <h2>Zoom Deep Clean Enhanced - Help</h2>
        
        <h3>🧹 Cleanup Options</h3>
        <ul>
            <li><b>Dry Run:</b> Preview what will be cleaned without making changes</li>
            <li><b>Verbose Output:</b> Show detailed information during cleanup</li>
            <li><b>Create Backups:</b> Create backups before removing files</li>
            <li><b>Force Cleanup:</b> Force cleanup without confirmation prompts</li>
        </ul>
        
        <h3>🔧 Advanced Features</h3>
        <ul>
            <li><b>Enable Advanced Features:</b> Enable MAC spoofing and fingerprint modification</li>
            <li><b>Spoof MAC Address:</b> Change MAC address for privacy</li>
            <li><b>Reset Hostname:</b> Reset system hostname</li>
        </ul>
        
        <h3>🖥️ Virtual Machine Support</h3>
        <ul>
            <li><b>VM-Aware Cleanup:</b> Detect and handle virtual machines during cleanup</li>
            <li><b>Stop VMs During Cleanup:</b> Automatically stop VMs before cleanup</li>
        </ul>
        
        <h3>⚙️ System Options</h3>
        <ul>
            <li><b>Reboot After Cleanup:</b> Automatically reboot system after cleanup</li>
            <li><b>Performance Monitoring:</b> Monitor performance during cleanup</li>
        </ul>
        
        <h3>🚀 Getting Started</h3>
        <ol>
            <li>Configure your cleanup options</li>
            <li>Enable "Dry Run" for a safe preview</li>
            <li>Click "Start Cleanup" to begin</li>
            <li>Review the output log for details</li>
        </ol>
        
        <p><b>⚠️ Important:</b> Always run a dry run first to preview changes!</p>
        """
        )

        layout.addWidget(help_text)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(dialog.accept)
        layout.addWidget(button_box)

        dialog.exec()

    def closeEvent(self, event):
        """Handle application close event"""
        if self.is_cleanup_running:
            reply = QMessageBox.question(
                self,
                "Cleanup Running",
                "Cleanup is currently running. Are you sure you want to quit?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )

            if reply != QMessageBox.Yes:
                event.ignore()
                return

            # Cancel cleanup
            if self.cleanup_worker:
                self.cleanup_worker.cancel_cleanup()

            if self.cleanup_thread:
                self.cleanup_thread.quit()
                self.cleanup_thread.wait(3000)  # Wait up to 3 seconds

        # Clean up resources
        self.executor.shutdown(wait=False)
        event.accept()


def main():
    """Main entry point for PySide6 GUI"""
    if not PYSIDE6_AVAILABLE:
        print("PySide6 is required for this GUI. Install with: pip install PySide6")
        return 1

    app = QApplication(sys.argv)
    app.setApplicationName("Zoom Deep Clean Enhanced")
    app.setApplicationVersion("2.3.0")
    app.setOrganizationName("PHLthy215")

    # Set application icon if available
    try:
        app.setWindowIcon(QIcon("icon.png"))
    except:
        pass

    # Apply macOS-specific styling
    if sys.platform == "darwin":
        app.setAttribute(Qt.AA_DontShowIconsInMenus, True)

    window = ModernZoomCleanerGUI()
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())

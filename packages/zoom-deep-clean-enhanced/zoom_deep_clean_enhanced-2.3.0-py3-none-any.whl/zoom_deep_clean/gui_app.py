#!/usr/bin/env python3
"""
Zoom Deep Clean Enhanced - GUI Application
User-friendly interface for advanced Zoom cleanup

Created by: PHLthy215
Enhanced Version: 2.2.0 - GUI Application
"""

import sys
import os
import threading
import json
import webbrowser
from datetime import datetime
from pathlib import Path

try:
    import tkinter as tk
    from tkinter import ttk, messagebox, filedialog, scrolledtext
    from tkinter.font import Font
except ImportError:
    print("Error: tkinter not available. Please install tkinter.")
    sys.exit(1)

# Add the package to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from .cleaner_enhanced import ZoomDeepCleanerEnhanced
from .advanced_features import AdvancedFeatures


class ZoomCleanerGUI:
    """User-friendly GUI for Zoom Deep Clean Enhanced"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Zoom Deep Clean Enhanced v2.2.0 - by PHLthy215")
        self.root.geometry("1000x800")
        self.root.minsize(900, 700)

        # Fix screen tearing and improve performance
        self.root.tk.call("tk", "scaling", 1.0)

        # Configure style
        self.setup_styles()

        # Variables
        self.setup_variables()

        # Create GUI
        self.create_widgets()

        # Center window
        self.center_window()

        # Bind close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Bind keyboard shortcuts
        self.setup_keyboard_shortcuts()

        # Status
        self.is_running = False
        self.cleaner = None

        # Performance optimization
        self.update_pending = False

    def setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts"""
        # Bind keyboard shortcuts
        self.root.bind("<Command-a>", lambda e: self.select_all())
        self.root.bind("<Control-a>", lambda e: self.select_all())  # For non-Mac
        self.root.bind("<Command-c>", lambda e: self.copy_selection())
        self.root.bind("<Control-c>", lambda e: self.copy_selection())  # For non-Mac
        self.root.bind("<Command-Shift-k>", lambda e: self.clear_output())
        self.root.bind(
            "<Control-Shift-k>", lambda e: self.clear_output()
        )  # For non-Mac

        # Focus management
        self.root.bind("<Tab>", self.focus_next_widget)
        self.root.bind("<Shift-Tab>", self.focus_prev_widget)

    def focus_next_widget(self, event):
        """Move focus to next widget"""
        event.widget.tk_focusNext().focus()
        return "break"

    def focus_prev_widget(self, event):
        """Move focus to previous widget"""
        event.widget.tk_focusPrev().focus()
        return "break"

    def setup_styles(self):
        """Setup GUI styles and colors"""
        # Configure ttk styles
        style = ttk.Style()

        # Try to use a modern theme
        try:
            style.theme_use("aqua")  # macOS native theme
        except Exception:
            try:
                style.theme_use("clam")  # Cross-platform modern theme
            except Exception:
                pass  # Use default theme

        # Custom colors
        self.colors = {
            "primary": "#007AFF",  # Blue
            "success": "#34C759",  # Green
            "warning": "#FF9500",  # Orange
            "danger": "#FF3B30",  # Red
            "secondary": "#8E8E93",  # Gray
            "background": "#F2F2F7",  # Light gray
            "surface": "#FFFFFF",  # White
        }

        # Configure custom styles
        style.configure("Title.TLabel", font=("SF Pro Display", 18, "bold"))
        style.configure("Subtitle.TLabel", font=("SF Pro Display", 12))
        style.configure("Primary.TButton", font=("SF Pro Display", 11, "bold"))
        style.configure("Success.TButton", font=("SF Pro Display", 11))
        style.configure("Warning.TButton", font=("SF Pro Display", 11))

    def setup_variables(self):
        """Setup tkinter variables"""
        # Basic options
        self.dry_run_var = tk.BooleanVar(value=True)
        self.verbose_var = tk.BooleanVar(value=True)
        self.backup_var = tk.BooleanVar(value=True)
        self.vm_aware_var = tk.BooleanVar(value=True)
        self.system_reboot_var = tk.BooleanVar(value=False)

        # Advanced features
        self.advanced_features_var = tk.BooleanVar(value=True)
        self.reset_hostname_var = tk.BooleanVar(value=False)
        self.mac_spoofing_var = tk.BooleanVar(value=False)
        self.new_hostname_var = tk.StringVar(value="")

        # Log file
        self.log_file_var = tk.StringVar(
            value=os.path.expanduser("~/Documents/zoom_deep_clean_enhanced.log")
        )

    def create_widgets(self):
        """Create all GUI widgets"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # Header
        self.create_header(main_frame)

        # Options sections
        self.create_basic_options(main_frame)
        self.create_advanced_options(main_frame)
        self.create_log_options(main_frame)

        # Action buttons
        self.create_action_buttons(main_frame)

        # Progress and output
        self.create_progress_section(main_frame)

        # Status bar
        self.create_status_bar(main_frame)

    def create_header(self, parent):
        """Create header section"""
        header_frame = ttk.Frame(parent)
        header_frame.grid(
            row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20)
        )
        header_frame.columnconfigure(1, weight=1)

        # Icon/Logo (using emoji for now)
        icon_label = ttk.Label(header_frame, text="🔥", font=("SF Pro Display", 32))
        icon_label.grid(row=0, column=0, padx=(0, 15))

        # Title and description
        title_frame = ttk.Frame(header_frame)
        title_frame.grid(row=0, column=1, sticky=(tk.W, tk.E))

        title_label = ttk.Label(
            title_frame, text="Zoom Deep Clean Enhanced", style="Title.TLabel"
        )
        title_label.grid(row=0, column=0, sticky=tk.W)

        subtitle_label = ttk.Label(
            title_frame,
            text="VM-Aware & System-Wide Device Fingerprint Removal",
            style="Subtitle.TLabel",
        )
        subtitle_label.grid(row=1, column=0, sticky=tk.W)

        version_label = ttk.Label(
            title_frame,
            text="v2.2.0 by PHLthy215",
            font=("SF Pro Display", 10),
            foreground=self.colors["secondary"],
        )
        version_label.grid(row=2, column=0, sticky=tk.W)

    def create_basic_options(self, parent):
        """Create basic options section"""
        # Basic Options Frame
        basic_frame = ttk.LabelFrame(parent, text="Basic Options", padding="15")
        basic_frame.grid(
            row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15)
        )
        basic_frame.columnconfigure(1, weight=1)

        row = 0

        # Dry Run
        ttk.Checkbutton(
            basic_frame,
            text="Preview Mode (Dry Run)",
            variable=self.dry_run_var,
            command=self.on_dry_run_changed,
        ).grid(row=row, column=0, sticky=tk.W, pady=2)
        ttk.Label(
            basic_frame,
            text="Preview operations without making changes",
            font=("SF Pro Display", 10),
            foreground=self.colors["secondary"],
        ).grid(row=row, column=1, sticky=tk.W, padx=(10, 0))
        row += 1

        # Verbose
        ttk.Checkbutton(
            basic_frame, text="Detailed Logging", variable=self.verbose_var
        ).grid(row=row, column=0, sticky=tk.W, pady=2)
        ttk.Label(
            basic_frame,
            text="Show detailed progress information",
            font=("SF Pro Display", 10),
            foreground=self.colors["secondary"],
        ).grid(row=row, column=1, sticky=tk.W, padx=(10, 0))
        row += 1

        # Backup
        ttk.Checkbutton(
            basic_frame, text="Create Backups", variable=self.backup_var
        ).grid(row=row, column=0, sticky=tk.W, pady=2)
        ttk.Label(
            basic_frame,
            text="Backup files before removal (recommended)",
            font=("SF Pro Display", 10),
            foreground=self.colors["secondary"],
        ).grid(row=row, column=1, sticky=tk.W, padx=(10, 0))
        row += 1

        # VM Aware
        ttk.Checkbutton(
            basic_frame, text="VM-Aware Cleanup", variable=self.vm_aware_var
        ).grid(row=row, column=0, sticky=tk.W, pady=2)
        ttk.Label(
            basic_frame,
            text="Stop VM services and clean VM-specific processes",
            font=("SF Pro Display", 10),
            foreground=self.colors["secondary"],
        ).grid(row=row, column=1, sticky=tk.W, padx=(10, 0))
        row += 1

        # System Reboot
        ttk.Checkbutton(
            basic_frame,
            text="Auto Reboot After Cleanup",
            variable=self.system_reboot_var,
        ).grid(row=row, column=0, sticky=tk.W, pady=2)
        ttk.Label(
            basic_frame,
            text="Automatically restart system when cleanup completes",
            font=("SF Pro Display", 10),
            foreground=self.colors["secondary"],
        ).grid(row=row, column=1, sticky=tk.W, padx=(10, 0))

    def create_advanced_options(self, parent):
        """Create advanced options section"""
        # Advanced Options Frame
        advanced_frame = ttk.LabelFrame(
            parent, text="Advanced Fingerprint Features", padding="15"
        )
        advanced_frame.grid(
            row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15)
        )
        advanced_frame.columnconfigure(1, weight=1)

        row = 0

        # Enable Advanced Features
        ttk.Checkbutton(
            advanced_frame,
            text="Enable Advanced Features",
            variable=self.advanced_features_var,
            command=self.on_advanced_features_changed,
        ).grid(row=row, column=0, sticky=tk.W, pady=2)
        ttk.Label(
            advanced_frame,
            text="Keychain scan, MDM detection, UUID identification",
            font=("SF Pro Display", 10),
            foreground=self.colors["secondary"],
        ).grid(row=row, column=1, sticky=tk.W, padx=(10, 0))
        row += 1

        # Hostname Reset
        self.hostname_check = ttk.Checkbutton(
            advanced_frame,
            text="Reset System Hostname",
            variable=self.reset_hostname_var,
            command=self.on_hostname_changed,
        )
        self.hostname_check.grid(row=row, column=0, sticky=tk.W, pady=2)

        hostname_frame = ttk.Frame(advanced_frame)
        hostname_frame.grid(row=row, column=1, sticky=(tk.W, tk.E), padx=(10, 0))
        hostname_frame.columnconfigure(1, weight=1)

        ttk.Label(
            hostname_frame, text="Custom name:", font=("SF Pro Display", 10)
        ).grid(row=0, column=0, sticky=tk.W)
        self.hostname_entry = ttk.Entry(
            hostname_frame, textvariable=self.new_hostname_var, width=20
        )
        self.hostname_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 0))
        row += 1

        # MAC Spoofing
        self.mac_check = ttk.Checkbutton(
            advanced_frame,
            text="MAC Address Spoofing (VM Only)",
            variable=self.mac_spoofing_var,
        )
        self.mac_check.grid(row=row, column=0, sticky=tk.W, pady=2)

        mac_warning = ttk.Label(
            advanced_frame,
            text="⚠️ Use with caution - may affect network connectivity",
            font=("SF Pro Display", 10),
            foreground=self.colors["warning"],
        )
        mac_warning.grid(row=row, column=1, sticky=tk.W, padx=(10, 0))

        # Initially disable advanced options if not enabled
        self.on_advanced_features_changed()

    def create_log_options(self, parent):
        """Create log file options"""
        log_frame = ttk.LabelFrame(parent, text="Log File", padding="15")
        log_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        log_frame.columnconfigure(1, weight=1)

        ttk.Label(log_frame, text="Log file location:").grid(
            row=0, column=0, sticky=tk.W, pady=2
        )

        log_entry_frame = ttk.Frame(log_frame)
        log_entry_frame.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0))
        log_entry_frame.columnconfigure(0, weight=1)

        log_entry = ttk.Entry(log_entry_frame, textvariable=self.log_file_var)
        log_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))

        ttk.Button(
            log_entry_frame, text="Browse...", command=self.browse_log_file
        ).grid(row=0, column=1)

    def create_action_buttons(self, parent):
        """Create action buttons"""
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=4, column=0, columnspan=2, pady=(0, 15))

        # Preview button
        self.preview_btn = ttk.Button(
            button_frame,
            text="🔍 Preview Cleanup",
            command=self.preview_cleanup,
            style="Primary.TButton",
        )
        self.preview_btn.grid(row=0, column=0, padx=(0, 10))

        # Run cleanup button
        self.run_btn = ttk.Button(
            button_frame,
            text="🔥 Run Cleanup",
            command=self.run_cleanup,
            style="Success.TButton",
        )
        self.run_btn.grid(row=0, column=1, padx=(0, 10))

        # Stop button
        self.stop_btn = ttk.Button(
            button_frame,
            text="⏹ Stop",
            command=self.stop_cleanup,
            style="Warning.TButton",
            state="disabled",
        )
        self.stop_btn.grid(row=0, column=2, padx=(0, 10))

        # View logs button
        self.logs_btn = ttk.Button(
            button_frame, text="📋 View Logs", command=self.view_logs
        )
        self.logs_btn.grid(row=0, column=3, padx=(0, 10))

        # Help button
        self.help_btn = ttk.Button(button_frame, text="❓ Help", command=self.show_help)
        self.help_btn.grid(row=0, column=4)

    def create_progress_section(self, parent):
        """Create progress and output section with improved scrolling"""
        progress_frame = ttk.LabelFrame(parent, text="Progress & Output", padding="15")
        progress_frame.grid(
            row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15)
        )
        progress_frame.columnconfigure(0, weight=1)
        progress_frame.rowconfigure(1, weight=1)

        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            progress_frame, variable=self.progress_var, mode="determinate", length=400
        )
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        # Create frame for output with better scrolling
        output_frame = ttk.Frame(progress_frame)
        output_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)

        # Output text area with improved scrolling
        self.output_text = tk.Text(
            output_frame,
            height=20,
            width=100,
            font=("Monaco", 10),
            wrap=tk.WORD,
            bg="#FFFFFF",
            fg="#000000",
            relief="sunken",
            bd=1,
        )

        # Vertical scrollbar
        v_scrollbar = ttk.Scrollbar(
            output_frame, orient=tk.VERTICAL, command=self.output_text.yview
        )
        self.output_text.configure(yscrollcommand=v_scrollbar.set)

        # Horizontal scrollbar
        h_scrollbar = ttk.Scrollbar(
            output_frame, orient=tk.HORIZONTAL, command=self.output_text.xview
        )
        self.output_text.configure(xscrollcommand=h_scrollbar.set)

        # Grid the text widget and scrollbars
        self.output_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))

        # Configure text tags for colored output
        self.output_text.tag_configure("info", foreground=self.colors["primary"])
        self.output_text.tag_configure("success", foreground=self.colors["success"])
        self.output_text.tag_configure("warning", foreground=self.colors["warning"])
        self.output_text.tag_configure("error", foreground=self.colors["danger"])
        self.output_text.tag_configure(
            "timestamp", foreground=self.colors["secondary"], font=("Monaco", 9)
        )

        # Bind mouse wheel scrolling
        self.output_text.bind("<MouseWheel>", self._on_mousewheel)
        self.output_text.bind("<Button-4>", self._on_mousewheel)
        self.output_text.bind("<Button-5>", self._on_mousewheel)

        # Auto-scroll to bottom when new content is added
        self.auto_scroll = True

        # Add context menu for copy/select all
        self.create_context_menu()

    def create_status_bar(self, parent):
        """Create status bar"""
        status_frame = ttk.Frame(parent)
        status_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E))
        status_frame.columnconfigure(1, weight=1)

        self.status_label = ttk.Label(
            status_frame, text="Ready", font=("SF Pro Display", 10)
        )
        self.status_label.grid(row=0, column=0, sticky=tk.W)

        # Statistics labels
        self.stats_label = ttk.Label(
            status_frame,
            text="",
            font=("SF Pro Display", 10),
            foreground=self.colors["secondary"],
        )
        self.stats_label.grid(row=0, column=1, sticky=tk.E)

    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def on_dry_run_changed(self):
        """Handle dry run checkbox change"""
        if self.dry_run_var.get():
            self.run_btn.configure(text="🔍 Preview Cleanup")
        else:
            self.run_btn.configure(text="🔥 Run Cleanup")

    def on_advanced_features_changed(self):
        """Handle advanced features checkbox change"""
        state = "normal" if self.advanced_features_var.get() else "disabled"
        self.hostname_check.configure(state=state)
        self.mac_check.configure(state=state)
        self.on_hostname_changed()

    def on_hostname_changed(self):
        """Handle hostname checkbox change"""
        if self.advanced_features_var.get() and self.reset_hostname_var.get():
            self.hostname_entry.configure(state="normal")
        else:
            self.hostname_entry.configure(state="disabled")

    def browse_log_file(self):
        """Browse for log file location"""
        filename = filedialog.asksaveasfilename(
            title="Select Log File Location",
            defaultextension=".log",
            filetypes=[("Log files", "*.log"), ("All files", "*.*")],
            initialfile="zoom_deep_clean_enhanced.log",
        )
        if filename:
            self.log_file_var.set(filename)

    def create_context_menu(self):
        """Create context menu for output text area"""
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Copy", command=self.copy_selection)
        self.context_menu.add_command(label="Select All", command=self.select_all)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Clear Output", command=self.clear_output)
        self.context_menu.add_separator()
        self.context_menu.add_checkbutton(
            label="Auto-scroll",
            variable=tk.BooleanVar(value=True),
            command=self.toggle_auto_scroll,
        )

        # Bind right-click to show context menu
        self.output_text.bind("<Button-2>", self.show_context_menu)  # macOS right-click
        self.output_text.bind(
            "<Control-Button-1>", self.show_context_menu
        )  # macOS ctrl-click

    def show_context_menu(self, event):
        """Show context menu at cursor position"""
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def copy_selection(self):
        """Copy selected text to clipboard"""
        try:
            selected_text = self.output_text.selection_get()
            self.root.clipboard_clear()
            self.root.clipboard_append(selected_text)
        except tk.TclError:
            pass  # No selection

    def select_all(self):
        """Select all text in output area"""
        self.output_text.tag_add(tk.SEL, "1.0", tk.END)
        self.output_text.mark_set(tk.INSERT, "1.0")
        self.output_text.see(tk.INSERT)

    def toggle_auto_scroll(self):
        """Toggle auto-scroll feature"""
        self.auto_scroll = not self.auto_scroll

    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling"""
        # Disable auto-scroll when user manually scrolls
        if event.delta:
            self.auto_scroll = False
            self.output_text.yview_scroll(int(-1 * (event.delta / 120)), "units")
        return "break"

    def log_message(self, message, level="info"):
        """Add message to output text area with improved performance"""
        if self.update_pending:
            return

        timestamp = datetime.now().strftime("%H:%M:%S")

        # Insert timestamp with special formatting
        self.output_text.insert(tk.END, f"[{timestamp}] ", "timestamp")

        # Insert message with appropriate color
        self.output_text.insert(tk.END, f"{message}\n", level)

        # Auto-scroll to bottom if enabled
        if self.auto_scroll:
            self.output_text.see(tk.END)

        # Limit text buffer to prevent memory issues
        self._limit_text_buffer()

        # Schedule GUI update to prevent screen tearing
        self._schedule_update()

    def _limit_text_buffer(self):
        """Limit text buffer to prevent memory issues"""
        lines = self.output_text.get("1.0", tk.END).count("\n")
        if lines > 1000:  # Keep last 1000 lines
            # Delete first 200 lines
            self.output_text.delete("1.0", "200.0")

    def _schedule_update(self):
        """Schedule GUI update to prevent screen tearing"""
        if not self.update_pending:
            self.update_pending = True
            self.root.after_idle(self._perform_update)

    def _perform_update(self):
        """Perform the actual GUI update"""
        self.update_pending = False
        try:
            self.root.update_idletasks()
        except tk.TclError:
            pass  # Window might be destroyed

    def update_status(self, message, stats=None):
        """Update status bar with improved performance"""
        self.status_label.configure(text=message)
        if stats:
            stats_text = f"Files: {stats.get('files_removed', 0)} | Processes: {stats.get('processes_killed', 0)} | Advanced: {stats.get('advanced_features_executed', 0)}"
            self.stats_label.configure(text=stats_text)
        self._schedule_update()

    def update_progress(self, value):
        """Update progress bar with improved performance"""
        self.progress_var.set(value)
        self._schedule_update()

    def clear_output(self):
        """Clear output text area"""
        self.output_text.delete(1.0, tk.END)
        self.auto_scroll = True  # Re-enable auto-scroll when clearing

    def preview_cleanup(self):
        """Run cleanup in preview mode"""
        if self.is_running:
            return

        # Force dry run for preview
        original_dry_run = self.dry_run_var.get()
        self.dry_run_var.set(True)

        self.run_cleanup_internal()

        # Restore original dry run setting
        self.dry_run_var.set(original_dry_run)

    def run_cleanup(self):
        """Run the cleanup process"""
        if self.is_running:
            return

        # Confirm if not in dry run mode
        if not self.dry_run_var.get():
            result = messagebox.askyesno(
                "Confirm Cleanup",
                "⚠️ This will permanently remove Zoom files and modify system settings.\n\n"
                "Are you sure you want to continue?\n\n"
                "Advanced features enabled:\n"
                f"• Keychain scan: {self.advanced_features_var.get()}\n"
                f"• Hostname reset: {self.reset_hostname_var.get()}\n"
                f"• MAC spoofing: {self.mac_spoofing_var.get()}\n"
                f"• VM-aware cleanup: {self.vm_aware_var.get()}\n"
                f"• System reboot: {self.system_reboot_var.get()}",
                icon="warning",
            )
            if not result:
                return

        self.run_cleanup_internal()

    def run_cleanup_internal(self):
        """Internal method to run cleanup in thread"""
        self.is_running = True
        self.update_buttons_state()
        self.clear_output()
        self.update_progress(0)

        # Start cleanup in separate thread
        cleanup_thread = threading.Thread(target=self.cleanup_worker, daemon=True)
        cleanup_thread.start()

    def cleanup_worker(self):
        """Worker thread for cleanup process"""
        try:
            self.log_message("🔥 Starting Zoom Deep Clean Enhanced...", "info")
            self.update_status("Initializing cleanup...")
            self.update_progress(10)

            # Validate hostname if specified
            hostname = (
                self.new_hostname_var.get().strip()
                if self.reset_hostname_var.get()
                else None
            )
            if hostname and not self.validate_hostname(hostname):
                self.log_message(f"❌ Invalid hostname: {hostname}", "error")
                return

            # Create cleaner instance
            self.cleaner = ZoomDeepCleanerEnhanced(
                log_file=self.log_file_var.get(),
                verbose=self.verbose_var.get(),
                dry_run=self.dry_run_var.get(),
                enable_backup=self.backup_var.get(),
                vm_aware=self.vm_aware_var.get(),
                system_reboot=self.system_reboot_var.get(),
                enable_advanced_features=self.advanced_features_var.get(),
                enable_mac_spoofing=self.mac_spoofing_var.get(),
                reset_hostname=self.reset_hostname_var.get(),
                new_hostname=hostname,
            )

            self.log_message("✅ Cleaner initialized successfully", "success")
            self.update_progress(20)

            # Setup custom logging handler
            self.setup_gui_logging()

            # Run cleanup with progress updates
            self.run_cleanup_with_progress()

        except Exception as e:
            self.log_message(f"💥 Unexpected error: {str(e)}", "error")
            self.update_status("Error occurred")
        finally:
            self.is_running = False
            self.root.after(0, self.update_buttons_state)

    def setup_gui_logging(self):
        """Setup logging to capture cleaner output"""
        import logging

        class GUILogHandler(logging.Handler):
            def __init__(self, gui):
                super().__init__()
                self.gui = gui

            def emit(self, record):
                try:
                    msg = self.format(record)
                    level = "info"
                    if record.levelno >= logging.ERROR:
                        level = "error"
                    elif record.levelno >= logging.WARNING:
                        level = "warning"
                    elif "✅" in msg or "SUCCESS" in msg:
                        level = "success"

                    # Schedule GUI update in main thread
                    self.gui.root.after(0, lambda: self.gui.log_message(msg, level))
                except:
                    pass

        # Add GUI handler to cleaner's logger
        gui_handler = GUILogHandler(self)
        gui_handler.setFormatter(logging.Formatter("%(message)s"))
        self.cleaner.logger.addHandler(gui_handler)

    def run_cleanup_with_progress(self):
        """Run cleanup with progress updates"""
        try:
            self.update_status("Stopping processes...")
            self.update_progress(30)

            # Run the actual cleanup
            success = self.cleaner.run_deep_clean()

            self.update_progress(100)

            # Show results
            stats = self.cleaner.cleanup_stats
            self.update_status("Cleanup completed", stats)

            if success:
                self.log_message("🎉 Cleanup completed successfully!", "success")
                if not self.dry_run_var.get():
                    self.show_completion_dialog(stats)
            else:
                self.log_message("⚠️ Cleanup completed with warnings", "warning")
                self.show_results_dialog(stats, success=False)

        except Exception as e:
            self.log_message(f"❌ Cleanup failed: {str(e)}", "error")
            self.update_status("Cleanup failed")

    def validate_hostname(self, hostname):
        """Validate hostname format"""
        if not hostname:
            return True

        # Basic hostname validation
        if len(hostname) > 63:
            return False

        import re

        pattern = r"^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?$"
        return bool(re.match(pattern, hostname))

    def stop_cleanup(self):
        """Stop the cleanup process"""
        if self.is_running and self.cleaner:
            self.log_message("🛑 Stopping cleanup...", "warning")
            self.is_running = False
            self.update_status("Stopping...")
            # Note: Actual process stopping would need to be implemented in the cleaner

    def update_buttons_state(self):
        """Update button states based on running status"""
        if self.is_running:
            self.preview_btn.configure(state="disabled")
            self.run_btn.configure(state="disabled")
            self.stop_btn.configure(state="normal")
        else:
            self.preview_btn.configure(state="normal")
            self.run_btn.configure(state="normal")
            self.stop_btn.configure(state="disabled")

    def view_logs(self):
        """Open log file in default editor"""
        log_file = self.log_file_var.get()
        if os.path.exists(log_file):
            try:
                os.system(f'open "{log_file}"')
            except:
                messagebox.showinfo("Log File", f"Log file location:\n{log_file}")
        else:
            messagebox.showwarning("Log File", "Log file not found. Run cleanup first.")

    def show_help(self):
        """Show help dialog with improved scrolling and resizing"""
        help_text = """
🔥 Zoom Deep Clean Enhanced - Help

BASIC OPTIONS:
• Preview Mode: Shows what would be removed without making changes
• Detailed Logging: Provides verbose output for troubleshooting
• Create Backups: Backs up files before removal (recommended)
• VM-Aware Cleanup: Stops VM services and cleans VM-specific processes
• Auto Reboot: Automatically restarts system after cleanup

ADVANCED FEATURES:
• Keychain Scan: Comprehensive scan for Zoom-related keychain entries
• MDM Detection: Detects corporate device management profiles
• UUID Detection: Identifies system hardware identifiers
• Hostname Reset: Changes system hostname to break fingerprinting
• MAC Spoofing: Changes network interface MAC addresses (VM only)

OUTPUT AREA FEATURES:
• Right-click for context menu (Copy, Select All, Clear)
• Mouse wheel scrolling
• Auto-scroll toggle
• Color-coded messages:
  - Blue: Information
  - Green: Success
  - Yellow: Warning
  - Red: Error

KEYBOARD SHORTCUTS:
• Cmd+A: Select all text
• Cmd+C: Copy selected text
• Cmd+Shift+K: Clear output

SAFETY NOTES:
⚠️ Always run Preview Mode first to see what will be changed
⚠️ MAC spoofing may affect network connectivity
⚠️ Hostname reset will change your computer's network identity
⚠️ System reboot will restart your computer automatically

SUPPORT:
For issues or questions, check the log file for detailed information.
Right-click in the output area for copy/paste options.
        """

        help_window = tk.Toplevel(self.root)
        help_window.title("Help - Zoom Deep Clean Enhanced")
        help_window.geometry("700x600")
        help_window.minsize(600, 500)
        help_window.transient(self.root)
        help_window.grab_set()

        # Create main frame
        main_frame = ttk.Frame(help_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)

        # Create text widget with scrollbars
        text_frame = ttk.Frame(main_frame)
        text_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)

        help_text_widget = tk.Text(
            text_frame,
            wrap=tk.WORD,
            font=("SF Pro Display", 11),
            bg="#FFFFFF",
            fg="#000000",
            relief="sunken",
            bd=1,
        )

        # Vertical scrollbar
        v_scrollbar = ttk.Scrollbar(
            text_frame, orient=tk.VERTICAL, command=help_text_widget.yview
        )
        help_text_widget.configure(yscrollcommand=v_scrollbar.set)

        # Grid the text widget and scrollbar
        help_text_widget.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # Insert help text
        help_text_widget.insert(tk.END, help_text)
        help_text_widget.configure(state="disabled")

        # Add close button
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, pady=(10, 0))

        close_button = ttk.Button(
            button_frame, text="Close", command=help_window.destroy
        )
        close_button.pack()

        # Bind mouse wheel scrolling
        def on_mousewheel(event):
            help_text_widget.yview_scroll(int(-1 * (event.delta / 120)), "units")
            return "break"

        help_text_widget.bind("<MouseWheel>", on_mousewheel)
        help_text_widget.bind("<Button-4>", on_mousewheel)
        help_text_widget.bind("<Button-5>", on_mousewheel)

        # Center help window
        help_window.update_idletasks()
        x = (
            self.root.winfo_x()
            + (self.root.winfo_width() // 2)
            - (help_window.winfo_width() // 2)
        )
        y = (
            self.root.winfo_y()
            + (self.root.winfo_height() // 2)
            - (help_window.winfo_height() // 2)
        )
        help_window.geometry(f"+{x}+{y}")

        # Focus on the help window
        help_text_widget.focus_set()

    def show_completion_dialog(self, stats):
        """Show completion dialog with results"""
        if self.dry_run_var.get():
            title = "Preview Complete"
            message = "🔍 Preview completed successfully!\n\n"
        else:
            title = "Cleanup Complete"
            message = "🎉 Cleanup completed successfully!\n\n"

        message += f"Statistics:\n"
        message += f"• Files removed: {stats.get('files_removed', 0)}\n"
        message += f"• Directories removed: {stats.get('directories_removed', 0)}\n"
        message += f"• Processes killed: {stats.get('processes_killed', 0)}\n"
        message += f"• VM services stopped: {stats.get('vm_services_stopped', 0)}\n"
        message += (
            f"• Keychain entries removed: {stats.get('keychain_entries_removed', 0)}\n"
        )

        if self.advanced_features_var.get():
            message += f"\nAdvanced Features:\n"
            message += (
                f"• Features executed: {stats.get('advanced_features_executed', 0)}\n"
            )
            message += f"• System identifiers detected: {stats.get('system_identifiers_detected', 0)}\n"
            message += (
                f"• MDM profiles detected: {stats.get('mdm_profiles_detected', 0)}\n"
            )

        if not self.dry_run_var.get():
            message += f"\n📋 Next Steps:\n"
            if self.system_reboot_var.get():
                message += "• System will reboot automatically\n"
            else:
                message += "• Restart your computer manually\n"
            message += "• Download fresh Zoom installer\n"
            message += "• Install Zoom as new device\n"

        messagebox.showinfo(title, message)

    def show_results_dialog(self, stats, success=True):
        """Show results dialog"""
        if success:
            messagebox.showinfo(
                "Results",
                f"Operation completed with some warnings.\n\nCheck the log file for details.",
            )
        else:
            messagebox.showerror(
                "Results",
                f"Operation completed with errors.\n\nCheck the log file for details.",
            )

    def on_closing(self):
        """Handle window closing"""
        if self.is_running:
            result = messagebox.askyesno(
                "Confirm Exit",
                "Cleanup is still running. Are you sure you want to exit?",
            )
            if not result:
                return

        self.root.destroy()

    def run(self):
        """Start the GUI application"""
        self.root.mainloop()


def main():
    """Main entry point for GUI application"""
    try:
        app = ZoomCleanerGUI()
        app.run()
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
    except Exception as e:
        print(f"Error starting GUI application: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

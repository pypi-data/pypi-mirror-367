#!/usr/bin/env python3
"""
Zoom Deep Clean Enhanced - Simple Stable GUI
A more stable version that should work on all macOS versions

Created by: PHLthy215
Enhanced Version: 2.2.0 - Simple Stable GUI
"""

import sys
import os
import threading
import time
from datetime import datetime

try:
    import tkinter as tk
    from tkinter import ttk, messagebox, filedialog
    from tkinter.font import Font
except ImportError:
    print("Error: tkinter not available. Please install tkinter.")
    sys.exit(1)

# Add the package to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from .cleaner_enhanced import ZoomDeepCleanerEnhanced


class SimpleZoomCleanerGUI:
    """Simple, stable GUI for Zoom Deep Clean Enhanced"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Zoom Deep Clean Enhanced v2.2.0")
        self.root.geometry("800x600")
        self.root.minsize(700, 500)

        # Simple styling
        self.setup_variables()
        self.create_simple_widgets()
        self.center_window()

        # Bind close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Status
        self.is_running = False
        self.cleaner = None

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

    def create_simple_widgets(self):
        """Create simple, stable GUI widgets"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Header
        header_label = ttk.Label(
            main_frame, text="🔥 Zoom Deep Clean Enhanced", font=("Arial", 16, "bold")
        )
        header_label.pack(pady=(0, 10))

        subtitle_label = ttk.Label(
            main_frame, text="VM-Aware & System-Wide Device Fingerprint Removal"
        )
        subtitle_label.pack(pady=(0, 20))

        # Options frame
        options_frame = ttk.LabelFrame(main_frame, text="Options", padding="10")
        options_frame.pack(fill=tk.X, pady=(0, 10))

        # Basic options
        ttk.Checkbutton(
            options_frame, text="Preview Mode (Safe)", variable=self.dry_run_var
        ).pack(anchor=tk.W)
        ttk.Checkbutton(
            options_frame, text="Detailed Logging", variable=self.verbose_var
        ).pack(anchor=tk.W)
        ttk.Checkbutton(
            options_frame, text="Create Backups", variable=self.backup_var
        ).pack(anchor=tk.W)
        ttk.Checkbutton(
            options_frame, text="VM-Aware Cleanup", variable=self.vm_aware_var
        ).pack(anchor=tk.W)
        ttk.Checkbutton(
            options_frame,
            text="Auto Reboot After Cleanup",
            variable=self.system_reboot_var,
        ).pack(anchor=tk.W)

        # Advanced options
        advanced_frame = ttk.LabelFrame(
            main_frame, text="Advanced Features", padding="10"
        )
        advanced_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Checkbutton(
            advanced_frame,
            text="Enable Advanced Features",
            variable=self.advanced_features_var,
        ).pack(anchor=tk.W)
        ttk.Checkbutton(
            advanced_frame,
            text="Reset System Hostname",
            variable=self.reset_hostname_var,
        ).pack(anchor=tk.W)

        hostname_frame = ttk.Frame(advanced_frame)
        hostname_frame.pack(fill=tk.X, pady=(5, 0))
        ttk.Label(hostname_frame, text="Custom hostname:").pack(side=tk.LEFT)
        ttk.Entry(hostname_frame, textvariable=self.new_hostname_var, width=20).pack(
            side=tk.LEFT, padx=(5, 0)
        )

        ttk.Checkbutton(
            advanced_frame,
            text="MAC Address Spoofing (VM Only - Use with Caution)",
            variable=self.mac_spoofing_var,
        ).pack(anchor=tk.W)

        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)

        self.preview_btn = ttk.Button(
            button_frame, text="🔍 Preview Cleanup", command=self.preview_cleanup
        )
        self.preview_btn.pack(side=tk.LEFT, padx=(0, 5))

        self.run_btn = ttk.Button(
            button_frame, text="🔥 Run Cleanup", command=self.run_cleanup
        )
        self.run_btn.pack(side=tk.LEFT, padx=(0, 5))

        self.stop_btn = ttk.Button(
            button_frame, text="⏹ Stop", command=self.stop_cleanup, state="disabled"
        )
        self.stop_btn.pack(side=tk.LEFT, padx=(0, 5))

        self.help_btn = ttk.Button(button_frame, text="❓ Help", command=self.show_help)
        self.help_btn.pack(side=tk.LEFT)

        # Progress frame
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding="10")
        progress_frame.pack(fill=tk.BOTH, expand=True)

        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            progress_frame, variable=self.progress_var, mode="determinate"
        )
        self.progress_bar.pack(fill=tk.X, pady=(0, 10))

        # Output text
        self.output_text = tk.Text(
            progress_frame, height=15, width=80, wrap=tk.WORD, font=("Monaco", 10)
        )
        scrollbar = ttk.Scrollbar(
            progress_frame, orient=tk.VERTICAL, command=self.output_text.yview
        )
        self.output_text.configure(yscrollcommand=scrollbar.set)

        self.output_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Status bar
        self.status_label = ttk.Label(main_frame, text="Ready")
        self.status_label.pack(pady=(10, 0))

    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def log_message(self, message, level="info"):
        """Add message to output text area"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"

        self.output_text.insert(tk.END, formatted_message)
        self.output_text.see(tk.END)
        self.root.update()

    def update_status(self, message):
        """Update status bar"""
        self.status_label.configure(text=message)
        self.root.update()

    def update_progress(self, value):
        """Update progress bar"""
        self.progress_var.set(value)
        self.root.update()

    def clear_output(self):
        """Clear output text area"""
        self.output_text.delete(1.0, tk.END)

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
                "Are you sure you want to continue?",
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
            self.log_message("🔥 Starting Zoom Deep Clean Enhanced...")
            self.update_status("Initializing cleanup...")
            self.update_progress(10)

            # Validate hostname if specified
            hostname = (
                self.new_hostname_var.get().strip()
                if self.reset_hostname_var.get()
                else None
            )

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

            self.log_message("✅ Cleaner initialized successfully")
            self.update_progress(20)

            # Setup simple logging handler
            self.setup_simple_logging()

            # Run cleanup with progress updates
            self.update_status("Running cleanup...")
            self.update_progress(50)

            success = self.cleaner.run_deep_clean()

            self.update_progress(100)

            # Show results
            if success:
                self.log_message("🎉 Cleanup completed successfully!")
                self.update_status("Cleanup completed successfully")
            else:
                self.log_message("⚠️ Cleanup completed with warnings")
                self.update_status("Cleanup completed with warnings")

            # Show stats
            stats = self.cleaner.cleanup_stats
            self.log_message(f"📊 Files removed: {stats.get('files_removed', 0)}")
            self.log_message(f"📊 Processes killed: {stats.get('processes_killed', 0)}")
            self.log_message(
                f"📊 Advanced features executed: {stats.get('advanced_features_executed', 0)}"
            )

        except Exception as e:
            self.log_message(f"💥 Error: {str(e)}")
            self.update_status("Error occurred")
        finally:
            self.is_running = False
            self.root.after(0, self.update_buttons_state)

    def setup_simple_logging(self):
        """Setup simple logging to capture cleaner output"""
        import logging

        class SimpleGUILogHandler(logging.Handler):
            def __init__(self, gui):
                super().__init__()
                self.gui = gui

            def emit(self, record):
                try:
                    msg = self.format(record)
                    # Schedule GUI update in main thread
                    self.gui.root.after(0, lambda: self.gui.log_message(msg))
                except:
                    pass

        # Add GUI handler to cleaner's logger
        gui_handler = SimpleGUILogHandler(self)
        gui_handler.setFormatter(logging.Formatter("%(message)s"))
        if hasattr(self.cleaner, "logger"):
            self.cleaner.logger.addHandler(gui_handler)

    def stop_cleanup(self):
        """Stop the cleanup process"""
        if self.is_running:
            self.log_message("🛑 Stopping cleanup...")
            self.is_running = False
            self.update_status("Stopping...")

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

    def show_help(self):
        """Show simple help dialog"""
        help_text = """
🔥 Zoom Deep Clean Enhanced - Help

BASIC OPTIONS:
• Preview Mode: Shows what would be removed without making changes
• Detailed Logging: Provides verbose output for troubleshooting
• Create Backups: Backs up files before removal (recommended)
• VM-Aware Cleanup: Stops VM services and cleans VM-specific processes
• Auto Reboot: Automatically restarts system after cleanup

ADVANCED FEATURES:
• Enable Advanced Features: Enables fingerprint removal features
• Reset System Hostname: Changes system hostname
• MAC Spoofing: Changes network MAC addresses (VM only, use with caution)

SAFETY NOTES:
⚠️ Always run Preview Mode first
⚠️ MAC spoofing may affect network connectivity
⚠️ Hostname reset will change your computer's network identity

HOW TO USE:
1. Keep "Preview Mode" checked for safety
2. Configure your options
3. Click "Preview Cleanup" to see what would be changed
4. Uncheck "Preview Mode" when ready
5. Click "Run Cleanup" to execute
        """

        messagebox.showinfo("Help", help_text)

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
        # Add welcome message
        self.log_message("🎨 Welcome to Zoom Deep Clean Enhanced!")
        self.log_message("✨ Simple, stable GUI version")
        self.log_message("🔍 Always start with Preview Mode for safety")

        self.root.mainloop()


def main():
    """Main entry point for simple GUI application"""
    try:
        app = SimpleZoomCleanerGUI()
        app.run()
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
    except Exception as e:
        print(f"Error starting GUI application: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

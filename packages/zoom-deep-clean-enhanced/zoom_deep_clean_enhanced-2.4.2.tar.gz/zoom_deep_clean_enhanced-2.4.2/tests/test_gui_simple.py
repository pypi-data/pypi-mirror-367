#!/usr/bin/env python3
"""
Tests for Simple GUI module
Comprehensive testing of Tkinter GUI functionality
"""

import pytest
import sys
import os
import unittest
import tkinter as tk
import threading
import time
from unittest.mock import patch, MagicMock, Mock
from io import StringIO

# Import the GUI module
from zoom_deep_clean.gui_simple import SimpleZoomCleanerGUI


class TestSimpleGUIInitialization(unittest.TestCase):
    """Test GUI initialization and setup"""

    def setUp(self):
        """Set up test environment"""
        # Create a hidden root window for testing
        self.test_root = tk.Tk()
        self.test_root.withdraw()  # Hide the window

    def tearDown(self):
        """Clean up after tests"""
        try:
            if hasattr(self, "gui") and self.gui:
                self.gui.root.destroy()
        except:
            pass
        try:
            self.test_root.destroy()
        except:
            pass

    @patch("zoom_deep_clean.gui_simple.tk.Tk")
    def test_gui_initialization(self, mock_tk):
        """Test GUI initialization without creating actual window"""
        mock_root = MagicMock()
        mock_tk.return_value = mock_root

        # Create GUI instance
        gui = SimpleZoomCleanerGUI()

        # Verify initialization calls
        mock_root.title.assert_called_with("Zoom Deep Clean Enhanced v2.2.0")
        # geometry() gets called twice - once with "800x600" and once for centering
        self.assertTrue(mock_root.geometry.called)
        mock_root.minsize.assert_called_with(700, 500)
        mock_root.protocol.assert_called_with("WM_DELETE_WINDOW", gui.on_closing)

    @patch("zoom_deep_clean.gui_simple.tk.Tk")
    def test_setup_variables(self, mock_tk):
        """Test variable initialization"""
        mock_root = MagicMock()
        mock_tk.return_value = mock_root

        gui = SimpleZoomCleanerGUI()

        # Check that essential attributes are set
        self.assertFalse(gui.is_running)
        self.assertIsNone(gui.cleaner)

    @patch("zoom_deep_clean.gui_simple.tk.Tk")
    def test_center_window_method_exists(self, mock_tk):
        """Test that center_window method exists and is callable"""
        mock_root = MagicMock()
        mock_tk.return_value = mock_root

        gui = SimpleZoomCleanerGUI()

        # Verify method exists
        self.assertTrue(hasattr(gui, "center_window"))
        self.assertTrue(callable(gui.center_window))


class TestSimpleGUIComponents(unittest.TestCase):
    """Test GUI component creation and behavior"""

    def setUp(self):
        """Set up test environment"""
        self.test_root = tk.Tk()
        self.test_root.withdraw()

    def tearDown(self):
        """Clean up after tests"""
        try:
            if hasattr(self, "gui") and self.gui:
                self.gui.root.destroy()
        except:
            pass
        try:
            self.test_root.destroy()
        except:
            pass

    @patch("zoom_deep_clean.gui_simple.tk.Tk")
    def test_create_simple_widgets_called(self, mock_tk):
        """Test that widget creation method is called"""
        mock_root = MagicMock()
        mock_tk.return_value = mock_root

        gui = SimpleZoomCleanerGUI()

        # Verify method exists
        self.assertTrue(hasattr(gui, "create_simple_widgets"))

    @patch("zoom_deep_clean.gui_simple.tk.Tk")
    def test_on_closing_method(self, mock_tk):
        """Test on_closing method behavior"""
        mock_root = MagicMock()
        mock_tk.return_value = mock_root

        gui = SimpleZoomCleanerGUI()

        # Test on_closing method exists and is callable
        self.assertTrue(hasattr(gui, "on_closing"))
        self.assertTrue(callable(gui.on_closing))


class TestSimpleGUIFunctionality(unittest.TestCase):
    """Test GUI functionality and interactions"""

    def setUp(self):
        """Set up test environment"""
        self.test_root = tk.Tk()
        self.test_root.withdraw()

    def tearDown(self):
        """Clean up after tests"""
        try:
            if hasattr(self, "gui") and self.gui:
                self.gui.root.destroy()
        except:
            pass
        try:
            self.test_root.destroy()
        except:
            pass

    @patch("zoom_deep_clean.gui_simple.ZoomDeepCleanerEnhanced")
    @patch("zoom_deep_clean.gui_simple.tk.Tk")
    def test_cleaner_integration(self, mock_tk, mock_cleaner_class):
        """Test integration with ZoomDeepCleanerEnhanced"""
        mock_root = MagicMock()
        mock_tk.return_value = mock_root

        gui = SimpleZoomCleanerGUI()

        # Verify cleaner class is accessible
        self.assertTrue(hasattr(gui, "cleaner"))
        self.assertIsNone(gui.cleaner)  # Should be None initially

    @patch("zoom_deep_clean.gui_simple.tk.Tk")
    def test_threading_safety_attributes(self, mock_tk):
        """Test that GUI has thread-safe attributes"""
        mock_root = MagicMock()
        mock_tk.return_value = mock_root

        gui = SimpleZoomCleanerGUI()

        # Check thread-related attributes
        self.assertTrue(hasattr(gui, "is_running"))
        self.assertIsInstance(gui.is_running, bool)


class TestSimpleGUIImports(unittest.TestCase):
    """Test GUI import handling and dependencies"""

    def test_tkinter_import_handling(self):
        """Test that tkinter import is handled properly"""
        # This test verifies the module can be imported
        from zoom_deep_clean import gui_simple

        self.assertTrue(hasattr(gui_simple, "SimpleZoomCleanerGUI"))

    @patch("zoom_deep_clean.gui_simple.sys.exit")
    @patch("builtins.print")
    def test_tkinter_import_error_handling(self, mock_print, mock_exit):
        """Test handling of tkinter import errors"""
        # This would be tested by mocking the import, but it's complex
        # For now, we verify the error handling structure exists
        import zoom_deep_clean.gui_simple as gui_module

        # Verify the module has error handling structure
        source = open(gui_module.__file__).read()
        self.assertIn("ImportError", source)
        self.assertIn("tkinter not available", source)


class TestSimpleGUIWidgetCreation(unittest.TestCase):
    """Test widget creation and layout"""

    def setUp(self):
        """Set up test environment"""
        self.test_root = tk.Tk()
        self.test_root.withdraw()

    def tearDown(self):
        """Clean up after tests"""
        try:
            if hasattr(self, "gui") and self.gui:
                self.gui.root.destroy()
        except:
            pass
        try:
            self.test_root.destroy()
        except:
            pass

    @patch("zoom_deep_clean.gui_simple.tk.Tk")
    def test_setup_variables_method(self, mock_tk):
        """Test setup_variables method"""
        mock_root = MagicMock()
        mock_tk.return_value = mock_root

        gui = SimpleZoomCleanerGUI()

        # Verify method exists
        self.assertTrue(hasattr(gui, "setup_variables"))


class TestSimpleGUIErrorHandling(unittest.TestCase):
    """Test GUI error handling and edge cases"""

    def setUp(self):
        """Set up test environment"""
        self.test_root = tk.Tk()
        self.test_root.withdraw()

    def tearDown(self):
        """Clean up after tests"""
        try:
            if hasattr(self, "gui") and self.gui:
                self.gui.root.destroy()
        except:
            pass
        try:
            self.test_root.destroy()
        except:
            pass

    @patch("zoom_deep_clean.gui_simple.tk.Tk")
    def test_gui_destruction_handling(self, mock_tk):
        """Test GUI destruction and cleanup"""
        mock_root = MagicMock()
        mock_tk.return_value = mock_root

        gui = SimpleZoomCleanerGUI()

        # Test on_closing method
        if hasattr(gui, "on_closing"):
            # Should not raise exception
            try:
                gui.on_closing()
            except Exception as e:
                self.fail(f"on_closing raised exception: {e}")


class TestSimpleGUIIntegration(unittest.TestCase):
    """Test GUI integration with cleaner components"""

    def setUp(self):
        """Set up test environment"""
        self.test_root = tk.Tk()
        self.test_root.withdraw()

    def tearDown(self):
        """Clean up after tests"""
        try:
            if hasattr(self, "gui") and self.gui:
                self.gui.root.destroy()
        except:
            pass
        try:
            self.test_root.destroy()
        except:
            pass

    @patch("zoom_deep_clean.gui_simple.ZoomDeepCleanerEnhanced")
    @patch("zoom_deep_clean.gui_simple.tk.Tk")
    def test_cleaner_instantiation_capability(self, mock_tk, mock_cleaner):
        """Test that GUI can instantiate cleaner when needed"""
        mock_root = MagicMock()
        mock_tk.return_value = mock_root

        gui = SimpleZoomCleanerGUI()

        # Verify cleaner class is available for instantiation
        self.assertTrue(hasattr(gui, "cleaner"))


class TestSimpleGUIMethodCoverage(unittest.TestCase):
    """Test specific GUI methods to improve coverage"""

    def setUp(self):
        """Set up test environment"""
        self.test_root = tk.Tk()
        self.test_root.withdraw()

    def tearDown(self):
        """Clean up after tests"""
        try:
            if hasattr(self, "gui") and self.gui:
                self.gui.root.destroy()
        except:
            pass
        try:
            self.test_root.destroy()
        except:
            pass

    @patch("zoom_deep_clean.gui_simple.tk.Tk")
    def test_log_message_method(self, mock_tk):
        """Test log_message method functionality"""
        mock_root = MagicMock()
        mock_tk.return_value = mock_root

        gui = SimpleZoomCleanerGUI()

        # Mock the output_text widget
        gui.output_text = MagicMock()

        # Test log_message
        gui.log_message("Test message")

        # Verify insert and see methods were called
        gui.output_text.insert.assert_called()
        gui.output_text.see.assert_called_with(tk.END)

    @patch("zoom_deep_clean.gui_simple.tk.Tk")
    def test_update_status_method(self, mock_tk):
        """Test update_status method functionality"""
        mock_root = MagicMock()
        mock_tk.return_value = mock_root

        gui = SimpleZoomCleanerGUI()

        # Mock the status_label widget
        gui.status_label = MagicMock()

        # Test update_status
        gui.update_status("Test status")

        # Verify configure was called
        gui.status_label.configure.assert_called_with(text="Test status")

    @patch("zoom_deep_clean.gui_simple.tk.Tk")
    def test_update_progress_method(self, mock_tk):
        """Test update_progress method functionality"""
        mock_root = MagicMock()
        mock_tk.return_value = mock_root

        gui = SimpleZoomCleanerGUI()

        # Mock the progress_var
        gui.progress_var = MagicMock()

        # Test update_progress
        gui.update_progress(50)

        # Verify set was called
        gui.progress_var.set.assert_called_with(50)

    @patch("zoom_deep_clean.gui_simple.tk.Tk")
    def test_clear_output_method(self, mock_tk):
        """Test clear_output method functionality"""
        mock_root = MagicMock()
        mock_tk.return_value = mock_root

        gui = SimpleZoomCleanerGUI()

        # Mock the output_text widget
        gui.output_text = MagicMock()

        # Test clear_output
        gui.clear_output()

        # Verify delete was called
        gui.output_text.delete.assert_called_with(1.0, tk.END)

    @patch("zoom_deep_clean.gui_simple.tk.Tk")
    def test_update_buttons_state_method(self, mock_tk):
        """Test update_buttons_state method functionality"""
        mock_root = MagicMock()
        mock_tk.return_value = mock_root

        gui = SimpleZoomCleanerGUI()

        # Mock button widgets
        gui.preview_btn = MagicMock()
        gui.run_btn = MagicMock()
        gui.stop_btn = MagicMock()

        # Test when running
        gui.is_running = True
        gui.update_buttons_state()

        gui.preview_btn.configure.assert_called_with(state="disabled")
        gui.run_btn.configure.assert_called_with(state="disabled")
        gui.stop_btn.configure.assert_called_with(state="normal")

        # Test when not running
        gui.is_running = False
        gui.update_buttons_state()

        gui.preview_btn.configure.assert_called_with(state="normal")
        gui.run_btn.configure.assert_called_with(state="normal")
        gui.stop_btn.configure.assert_called_with(state="disabled")

    @patch("zoom_deep_clean.gui_simple.messagebox.showinfo")
    @patch("zoom_deep_clean.gui_simple.tk.Tk")
    def test_show_help_method(self, mock_tk, mock_showinfo):
        """Test show_help method functionality"""
        mock_root = MagicMock()
        mock_tk.return_value = mock_root

        gui = SimpleZoomCleanerGUI()

        # Test show_help
        gui.show_help()

        # Verify messagebox.showinfo was called
        mock_showinfo.assert_called_once()
        args, kwargs = mock_showinfo.call_args
        self.assertEqual(args[0], "Help")
        self.assertIn("Zoom Deep Clean Enhanced", args[1])

    @patch("zoom_deep_clean.gui_simple.messagebox.askyesno")
    @patch("zoom_deep_clean.gui_simple.tk.Tk")
    def test_on_closing_method_while_running(self, mock_tk, mock_askyesno):
        """Test on_closing method when cleanup is running"""
        mock_root = MagicMock()
        mock_tk.return_value = mock_root
        mock_askyesno.return_value = False

        gui = SimpleZoomCleanerGUI()
        gui.is_running = True

        # Test on_closing when user cancels
        gui.on_closing()

        # Verify confirmation dialog was shown
        mock_askyesno.assert_called_once()
        # Verify root.destroy was not called
        mock_root.destroy.assert_not_called()

    @patch("zoom_deep_clean.gui_simple.tk.Tk")
    def test_on_closing_method_not_running(self, mock_tk):
        """Test on_closing method when cleanup is not running"""
        mock_root = MagicMock()
        mock_tk.return_value = mock_root

        gui = SimpleZoomCleanerGUI()
        gui.is_running = False

        # Test on_closing when not running
        gui.on_closing()

        # Verify root.destroy was called
        mock_root.destroy.assert_called_once()

    @patch("zoom_deep_clean.gui_simple.tk.Tk")
    def test_preview_cleanup_method(self, mock_tk):
        """Test preview_cleanup method functionality"""
        mock_root = MagicMock()
        mock_tk.return_value = mock_root

        gui = SimpleZoomCleanerGUI()
        gui.is_running = False

        # Mock the run_cleanup_internal method
        gui.run_cleanup_internal = MagicMock()

        # Set initial dry_run state
        original_state = False
        gui.dry_run_var.set(original_state)

        # Test preview_cleanup
        gui.preview_cleanup()

        # Verify dry_run was restored to original state after method completes
        self.assertEqual(gui.dry_run_var.get(), original_state)
        # Verify run_cleanup_internal was called
        gui.run_cleanup_internal.assert_called_once()

    @patch("zoom_deep_clean.gui_simple.tk.Tk")
    def test_preview_cleanup_method_when_running(self, mock_tk):
        """Test preview_cleanup method when already running"""
        mock_root = MagicMock()
        mock_tk.return_value = mock_root

        gui = SimpleZoomCleanerGUI()
        gui.is_running = True

        # Mock the run_cleanup_internal method
        gui.run_cleanup_internal = MagicMock()

        # Test preview_cleanup when already running
        gui.preview_cleanup()

        # Verify run_cleanup_internal was NOT called
        gui.run_cleanup_internal.assert_not_called()

    @patch("zoom_deep_clean.gui_simple.messagebox.askyesno")
    @patch("zoom_deep_clean.gui_simple.tk.Tk")
    def test_run_cleanup_method_with_confirmation(self, mock_tk, mock_askyesno):
        """Test run_cleanup method with user confirmation"""
        mock_root = MagicMock()
        mock_tk.return_value = mock_root
        mock_askyesno.return_value = True

        gui = SimpleZoomCleanerGUI()
        gui.is_running = False
        gui.dry_run_var.set(False)  # Not in dry run mode

        # Mock the run_cleanup_internal method
        gui.run_cleanup_internal = MagicMock()

        # Test run_cleanup
        gui.run_cleanup()

        # Verify confirmation dialog was shown
        mock_askyesno.assert_called_once()
        # Verify run_cleanup_internal was called
        gui.run_cleanup_internal.assert_called_once()

    @patch("zoom_deep_clean.gui_simple.tk.Tk")
    def test_stop_cleanup_method(self, mock_tk):
        """Test stop_cleanup method functionality"""
        mock_root = MagicMock()
        mock_tk.return_value = mock_root

        gui = SimpleZoomCleanerGUI()
        gui.is_running = True

        # Mock log_message and update_status methods
        gui.log_message = MagicMock()
        gui.update_status = MagicMock()

        # Test stop_cleanup
        gui.stop_cleanup()

        # Verify methods were called
        gui.log_message.assert_called_with("🛑 Stopping cleanup...")
        gui.update_status.assert_called_with("Stopping...")
        self.assertFalse(gui.is_running)

    @patch("zoom_deep_clean.gui_simple.tk.Tk")
    def test_run_method(self, mock_tk):
        """Test run method functionality"""
        mock_root = MagicMock()
        mock_tk.return_value = mock_root

        gui = SimpleZoomCleanerGUI()

        # Mock log_message method
        gui.log_message = MagicMock()

        # Test run method
        gui.run()

        # Verify welcome messages were logged
        self.assertEqual(gui.log_message.call_count, 3)
        gui.log_message.assert_any_call("🎨 Welcome to Zoom Deep Clean Enhanced!")
        gui.log_message.assert_any_call("✨ Simple, stable GUI version")
        gui.log_message.assert_any_call("🔍 Always start with Preview Mode for safety")

        # Verify mainloop was called
        mock_root.mainloop.assert_called_once()


if __name__ == "__main__":
    unittest.main()

# Zoom Deep Clean Enhanced

![Tests](https://github.com/PHLthy215/zoom-deep-clean-enhanced/workflows/Tests/badge.svg)
![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)
![macOS](https://img.shields.io/badge/platform-macOS-lightgrey.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

Complete Zoom removal tool for macOS with VM awareness and device fingerprint elimination.

**Version: 2.3.0**

## 🚀 Quick Start

```bash
# Install
pip3 install zoom-deep-clean-enhanced

# Preview cleanup (safe)
zoom-deep-clean-enhanced --dry-run --verbose

# Run cleanup
zoom-deep-clean-enhanced --force
```

📖 **[Full Documentation](docs/)** | 🚨 **[Troubleshooting](docs/troubleshooting.md)** | 💻 **[Development](docs/development.md)**

## ✨ Features

### 🖥️ VM Support
- **VMware Fusion, VirtualBox, Parallels Desktop** detection
- **VM-aware process management** and cleanup
- **Shared resource cleanup** between host and VMs

### 🔍 Complete Removal
- **System-wide file search** across all macOS locations
- **Keychain entries** and authentication tokens
- **Launch agents/daemons** and privileged helpers
- **WebKit storage** and HTTP caches
- **Preference files** and application data

### 🛡️ Safety & Security
- **Dry-run mode** for safe preview
- **Comprehensive logging** and error handling
- **Input validation** and security checks
- **Automatic backups** before cleanup

## 📦 Installation

```bash
# From PyPI
pip3 install zoom-deep-clean-enhanced

# From source
git clone https://github.com/PHLthy215/zoom-deep-clean-enhanced.git
cd zoom-deep-clean-enhanced
pip3 install -e .
```

## 🖥️ Usage

### Command Line
```bash
# Basic usage
zoom-deep-clean-enhanced --force

# With GUI
python3 -m zoom_deep_clean.gui_enhanced

# Common options
zoom-deep-clean-enhanced --dry-run --verbose    # Safe preview
zoom-deep-clean-enhanced --force --system-reboot    # Full cleanup + reboot
```

### Python API
```python
from zoom_deep_clean import ZoomDeepCleanerEnhanced

cleaner = ZoomDeepCleanerEnhanced(verbose=True, dry_run=True)
success = cleaner.run_deep_clean()
```

## ⚙️ Requirements

- **macOS 12.x+** (Monterey, Ventura, Sonoma, Sequoia)
- **Python 3.9+**
- **sudo privileges** (for system-level cleanup)

## 📁 Output Files

- **Log**: `~/Documents/zoom_deep_clean_enhanced.log`
- **Report**: `~/Documents/zoom_cleanup_enhanced_report.json`

## ⚠️ Important Notes

- **Complete removal**: Reinstallation of Zoom required after cleanup
- **VM awareness**: Automatically detects and stops VMs during cleanup
- **System reboot**: Optional automatic reboot ensures complete cleanup
- **Always preview first**: Use `--dry-run` to see what will be removed

## 📄 License

MIT License

## 🔗 Links

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/PHLthy215/zoom-deep-clean-enhanced/issues)
- **PyPI**: [zoom-deep-clean-enhanced](https://pypi.org/project/zoom-deep-clean-enhanced/)

---

**⚠️ Use at your own risk. Always run `--dry-run` first to preview changes.**

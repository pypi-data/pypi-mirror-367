# Qt Lottie

[![PyPI version](https://badge.fury.io/py/qt-lottie.svg)](https://badge.fury.io/py/qt-lottie)
[![Python versions](https://img.shields.io/pypi/pyversions/qt-lottie.svg)](https://pypi.org/project/qt-lottie/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Cross-platform Python library providing Lottie animation support for Qt applications, compatible with both PySide6 and PyQt6.

## Features

- **QML Component**: Feature-rich `LottieAnimation` component for QML applications
- **Python API**: Programmatic control of animations from Python
- **Cross-binding compatibility**: Works with both PySide6 and PyQt6
- **Performance optimized**: Uses RLottie backend with Qt-style caching
- **Zero-configuration**: Simple pip installation

## Installation

```bash
# Auto-detect Qt binding
pip install qt-lottie

# With specific Qt binding
pip install qt-lottie[pyside6]
pip install qt-lottie[pyqt6]
```

## Quick Start

### QML Usage

```qml
import QtQuick 2.15
import QtQuick.Window 2.15
import QtLottie 1.0

Window {
    width: 640
    height: 480
    visible: true
    
    LottieAnimation {
        anchors.centerIn: parent
        width: 200
        height: 200
        source: "path/to/animation.json"
        autoPlay: true
        loops: -1  // Infinite loops
        
        onFinished: console.log("Animation finished")
    }
}
```

### Python Usage

```python
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtQml import QQmlApplicationEngine
import qtlottie

# Initialize QML types
qtlottie.init_qml()

app = QApplication(sys.argv)
engine = QQmlApplicationEngine()

# Load QML that uses LottieAnimation
engine.load("main.qml")

sys.exit(app.exec())
```

## API Reference

### LottieAnimation Properties

#### Source & Loading
- `source: url` - Animation file path/URL
- `status: int` - Loading status (Null, Loading, Ready, Error)
- `asynchronous: bool` - Async loading (default: true)
- `cacheMode: int` - CacheNone, CacheLoop, CacheAll (default: CacheNone)

#### Playback Control
- `playing: bool` - Play state (default: false)
- `autoPlay: bool` - Auto-start (default: false)
- `playbackRate: real` - Speed multiplier (default: 1.0)
- `loops: int` - Loop count (-1 = infinite)
- `direction: int` - Forward, Reverse, Alternate

#### Timing & Position
- `position: real` - Current time in seconds
- `duration: real` - Total duration (read-only)
- `progress: real` - Progress 0.0-1.0 (read-only)
- `currentFrame: int` - Current frame (read-only)

#### Visual Properties
- `tintColor: color` - Color overlay
- `fillMode: int` - Stretch, PreserveAspectFit, PreserveAspectCrop
- `smooth: bool` - Antialiasing (default: true)

### Methods

- `play()` - Start animation
- `pause()` - Pause animation
- `stop()` - Stop and reset animation
- `toggle()` - Toggle play/pause
- `seek(position)` - Seek to time position
- `seekToFrame(frame)` - Seek to frame number
- `seekToMarker(name)` - Seek to named marker

### Signals

- `started()` - Animation started
- `stopped()` - Animation stopped
- `finished()` - Animation finished
- `positionChanged(real)` - Position changed
- `frameChanged(int)` - Frame changed
- `markerReached(string)` - Marker reached
- `error(string)` - Error occurred

## Performance

The library is designed for optimal performance with Qt-style size-based frame caching.

### Cache Modes

- `CacheNone`: Render frames on demand (default, lowest memory)
- `CacheLoop`: Cache one complete animation loop
- `CacheAll`: Cache entire animation (best performance for small animations)

## Requirements

- Python 3.8+
- PySide6 or PyQt6  
- rlottie-python
- Pillow (for image processing)

## License

MIT License - see LICENSE file for details.

## Development

### Setup
```bash
# Clone repository
git clone https://gitlab.com/acemetrics-oss/qt-lottie.git
cd qt-lottie

# Install in development mode
pip install -e ".[dev,pyside6,pyqt6]"
```

### Building
```bash
# Build package
python -m build

# Install from wheel
pip install dist/*.whl

# Test basic functionality
python -c "import qtlottie; print('✓ Import successful')"
```

### Testing
```bash
# Test examples
cd examples/pyside6
python main.py

cd ../pyqt6  
python main.py
```

## Contributing

Contributions welcome! Please see our [GitLab repository](https://gitlab.com/acemetrics-oss/qt-lottie) for guidelines.

## Links

- **PyPI**: https://pypi.org/project/qt-lottie/
- **Source Code**: https://gitlab.com/acemetrics-oss/qt-lottie
- **Issues**: https://gitlab.com/acemetrics-oss/qt-lottie/-/issues
- **Examples**: See examples/ directory in the repository

## Support

- **Issues**: Report bugs and request features on [GitLab Issues](https://gitlab.com/acemetrics-oss/qt-lottie/-/issues)
- **Documentation**: Full API reference available in the repository
- **Examples**: Working examples for both PySide6 and PyQt6 included
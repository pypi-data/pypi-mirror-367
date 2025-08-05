"""Qt binding compatibility layer

Auto-detects Qt binding (PySide6 or PyQt6) and provides unified API.

Supported Qt versions:
- PySide6 (recommended)
- PyQt6 (alternative)

Note: This library requires Qt6. PyQt5 is not supported.
"""

import sys
from typing import Any, Optional

# Detect Qt binding
QT_BINDING: Optional[str] = None
QtCore = None
QtGui = None
QtQml = None
QtQuick = None

# Try PySide6 first
try:
    from PySide6 import QtCore, QtGui, QtQml, QtQuick
    QT_BINDING = 'PySide6'
except ImportError:
    try:
        from PyQt6 import QtCore, QtGui, QtQml, QtQuick
        QT_BINDING = 'PyQt6'
    except ImportError:
        raise ImportError(
            "Neither PySide6 nor PyQt6 found. Please install one of them:\n"
            "  pip install PySide6\n"
            "  pip install PyQt6"
        )

# Unified Signal API


def signal(*args: Any) -> Any:
    """Create a signal compatible with both PySide6 and PyQt6"""
    if QT_BINDING == 'PySide6':
        return QtCore.Signal(*args)
    else:  # PyQt6
        return QtCore.pyqtSignal(*args)

# Unified Property API


def property_(type_: Any, fget: Any = None, fset: Any = None, freset: Any = None,
              fdel: Any = None, doc: str = "", notify: Any = None) -> Any:
    """Create a property compatible with both PySide6 and PyQt6

    FIXED: PyQt6 now properly supports notify signals for QML binding

    Args:
        type_: Property type (int, float, bool, str, QUrl, QColor, etc.)
        fget: Getter function
        fset: Setter function (optional)
        freset: Reset function (optional)
        fdel: Delete function (optional)
        doc: Documentation string
        notify: Notify signal for property changes (CRITICAL for QML binding)

    Returns:
        Property object compatible with the detected Qt binding

    Note:
        The notify parameter is ESSENTIAL for QML property binding.
        Without it, PyQt6 will show "non-bindable properties" warnings.
    """
    if QT_BINDING == 'PySide6':
        if notify is not None:
            return QtCore.Property(type_, fget, fset, freset, fdel, doc, notify=notify)
        else:
            return QtCore.Property(type_, fget, fset, freset, fdel, doc)
    else:  # PyQt6
        # FIXED: PyQt6 DOES support notify parameter in pyqtProperty
        # This eliminates the "non-bindable properties" warnings in QML
        if notify is not None:
            return QtCore.pyqtProperty(type_, fget, fset, freset, fdel, doc, notify=notify)
        else:
            # Without notify, properties will be non-bindable in QML
            return QtCore.pyqtProperty(type_, fget, fset, freset, fdel, doc)

# Unified Slot API


def slot(*args: Any) -> Any:
    """Create a slot compatible with both PySide6 and PyQt6"""
    if QT_BINDING == 'PySide6':
        return QtCore.Slot(*args)
    else:  # PyQt6
        return QtCore.pyqtSlot(*args)


# Common Qt classes with unified access
QObject = QtCore.QObject
QTimer = QtCore.QTimer
QUrl = QtCore.QUrl
QSize = QtCore.QSize
QSizeF = QtCore.QSizeF
QPointF = QtCore.QPointF
QRectF = QtCore.QRectF
QThread = QtCore.QThread
QMutex = QtCore.QMutex
QMutexLocker = QtCore.QMutexLocker

QImage = QtGui.QImage
QPixmap = QtGui.QPixmap
QColor = QtGui.QColor
QPainter = QtGui.QPainter

# QImage format constants for performance optimization
QImage_Format_RGBA8888 = QImage.Format.Format_RGBA8888
QImage_Format_RGBA8888_Premultiplied = QImage.Format.Format_RGBA8888_Premultiplied
QImage_Format_ARGB32 = QImage.Format.Format_ARGB32
QImage_Format_ARGB32_Premultiplied = QImage.Format.Format_ARGB32_Premultiplied

QQmlEngine = QtQml.QQmlEngine
qmlRegisterType = QtQml.qmlRegisterType

QQuickItem = QtQuick.QQuickItem
QQuickPaintedItem = QtQuick.QQuickPaintedItem

# Enums


class Status:
    """Animation loading status"""
    Null = 0
    Loading = 1
    Ready = 2
    Error = 3


class CacheMode:
    """Frame caching modes"""
    CacheNone = 0
    CacheLoop = 1
    CacheAll = 2


class Direction:
    """Animation direction"""
    Forward = 0
    Reverse = 1
    Alternate = 2


class FillMode:
    """Image fill modes"""
    Stretch = 0
    PreserveAspectFit = 1
    PreserveAspectCrop = 2


class AnimationState:
    """Animation playback state"""
    STOPPED = 0
    PLAYING = 1
    PAUSED = 2
    FINISHED = 3


def get_qt_version() -> str:
    """Get Qt version string"""
    return QtCore.qVersion()


def get_binding_info() -> dict:
    """Get information about the Qt binding in use"""
    return {
        'binding': QT_BINDING,
        'qt_version': get_qt_version(),
        'python_version': sys.version,
    }

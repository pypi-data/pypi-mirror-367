"""QML registration and Python API

Registers QML components and provides Python API initialization.
"""

from ..compat import qmlRegisterType, QT_BINDING
from ..core.animation import LottieAnimation

# QML module information
QML_MODULE_NAME = "QtLottie"
QML_MODULE_VERSION_MAJOR = 1
QML_MODULE_VERSION_MINOR = 0

_qml_initialized = False

def init_qml() -> bool:
    """Initialize QML module registration
    
    Returns:
        True if initialization was successful
    """
    global _qml_initialized
    
    if _qml_initialized:
        return True
    
    try:
        # Register the LottieAnimation component
        result = qmlRegisterType(
            LottieAnimation,
            QML_MODULE_NAME,
            QML_MODULE_VERSION_MAJOR,
            QML_MODULE_VERSION_MINOR,
            "LottieAnimation"
        )
        
        if result != -1:
            _qml_initialized = True
            return True
        else:
            return False
            
    except Exception:
        return False

def register_qml_types() -> bool:
    """Register all QML types (alias for init_qml)
    
    Returns:
        True if registration was successful
    """
    return init_qml()

def get_qml_import_statement() -> str:
    """Get the QML import statement for this module
    
    Returns:
        QML import statement string
    """
    return f"import {QML_MODULE_NAME} {QML_MODULE_VERSION_MAJOR}.{QML_MODULE_VERSION_MINOR}"

def is_qml_initialized() -> bool:
    """Check if QML types are initialized
    
    Returns:
        True if QML types are registered
    """
    return _qml_initialized

def get_module_info() -> dict:
    """Get module information
    
    Returns:
        Dictionary with module information
    """
    return {
        'module_name': QML_MODULE_NAME,
        'version_major': QML_MODULE_VERSION_MAJOR,
        'version_minor': QML_MODULE_VERSION_MINOR,
        'qt_binding': QT_BINDING,
        'initialized': _qml_initialized
    }
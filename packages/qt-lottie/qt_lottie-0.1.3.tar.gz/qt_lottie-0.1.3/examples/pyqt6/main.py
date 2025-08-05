#!/usr/bin/env python3
"""Simple Qt Lottie Example - PyQt6"""

import sys
from pathlib import Path

# Add parent directory to path for qtlottie module
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtQml import QQmlApplicationEngine
from PyQt6.QtCore import QUrl

def main():
    # Import and initialize qt-lottie
    import qtlottie
    
    # Create application
    app = QApplication(sys.argv)
    
    # Initialize qt-lottie QML types
    qtlottie.init_qml()
    
    # Create QML engine and load QML file
    engine = QQmlApplicationEngine()
    qml_file = Path(__file__).parent / "main.qml"
    engine.load(QUrl.fromLocalFile(str(qml_file)))
    
    # Run the application
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
"""Qt Lottie Animation Library

Cross-platform Python library providing Lottie animation support for Qt applications,
compatible with both PySide6 and PyQt6.
"""


__author__ = "Qt Lottie Contributors"

from .core.animation import LottieAnimation
from .qml.register import init_qml

__all__ = ["LottieAnimation", "init_qml"]

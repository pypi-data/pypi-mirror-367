
import os
from typing import Optional, Tuple, Any, List, Dict
from ..compat import (
    QImage, QSize,
    QImage_Format_RGBA8888, QImage_Format_RGBA8888_Premultiplied,
    QImage_Format_ARGB32, QImage_Format_ARGB32_Premultiplied
)

try:
    import rlottie_python as rlottie
    RLOTTIE_AVAILABLE = True
except ImportError:
    try:
        import rlottie
        RLOTTIE_AVAILABLE = True
    except ImportError:
        RLOTTIE_AVAILABLE = False
        rlottie = None


class RLottieError(Exception):
    pass


class RLottieWrapper:

    def __init__(self):
        if not RLOTTIE_AVAILABLE:
            raise RLottieError(
                "rlottie-python not found. Install with: pip install rlottie-python"
            )

        self.animation: Optional[Any] = None
        self._width = 0
        self._height = 0
        self._total_frames = 0
        self._frame_rate = 30.0
        self._duration = 0.0
        self._surface: Optional[Any] = None
        self._last_render_size = (0, 0)

        # Rendering quality settings
        self._use_direct_rendering = False  # Disable direct rendering until color format is fixed
        self._use_async_rendering = False  # Enable async rendering for performance

        try:
            rlottie.lottie_configure_model_cache_size(50)  # Cache up to 50 models
        except (AttributeError, Exception):
            pass

    def load_from_file(self, file_path: str) -> bool:
        if not os.path.exists(file_path):
            return False

        try:
            self.animation = rlottie.LottieAnimation.from_file(file_path)
            if not self.animation:
                return False

            self._total_frames = self.animation.lottie_animation_get_totalframe()
            self._frame_rate = self.animation.lottie_animation_get_framerate()
            self._duration = self.animation.lottie_animation_get_duration()

            width, height = self.animation.lottie_animation_get_size()
            self._width = int(width)
            self._height = int(height)

            return True

        except Exception:
            return False

    def load_from_data(self, json_data: str, resource_path: str = "") -> bool:
        try:
            self.animation = rlottie.LottieAnimation.from_data(json_data)
            if not self.animation:
                return False

            self._total_frames = self.animation.lottie_animation_get_totalframe()
            self._frame_rate = self.animation.lottie_animation_get_framerate()
            self._duration = self.animation.lottie_animation_get_duration()

            width, height = self.animation.lottie_animation_get_size()
            self._width = int(width)
            self._height = int(height)

            return True

        except Exception:
            return False

    def set_size(self, width: int, height: int) -> None:
        new_size = (max(1, width), max(1, height))
        if new_size != self._last_render_size:
            self._width, self._height = new_size
            self._last_render_size = new_size

    def render_frame(self, frame_number: int) -> Optional[QImage]:
        if not self.animation:
            return None

        if frame_number < 0 or frame_number >= self._total_frames:
            return None

        try:
            # Choose rendering method based on preferences
            if self._use_direct_rendering:
                return self._render_frame_direct(frame_number)
            else:
                # Fallback to PIL method
                pil_image = self.animation.render_pillow_frame(
                    frame_num=frame_number,
                    width=self._width,
                    height=self._height
                )
                return self._pil_to_qimage(pil_image)
        except Exception:
            # Fallback to PIL method if direct rendering fails
            try:
                pil_image = self.animation.render_pillow_frame(
                    frame_num=frame_number,
                    width=self._width,
                    height=self._height
                )
                return self._pil_to_qimage(pil_image)
            except Exception:
                return None

    def _render_frame_direct(self, frame_number: int) -> Optional[QImage]:
        """Render frame using direct buffer method for better quality"""
        if not self.animation:
            return None

        try:
            # Calculate buffer parameters
            bytes_per_pixel = 4  # RGBA
            bytes_per_line = self._width * bytes_per_pixel
            buffer_size = self._height * bytes_per_line

            # Render directly to buffer
            buffer = self.animation.lottie_animation_render(
                frame_num=frame_number,
                buffer_size=buffer_size,
                width=self._width,
                height=self._height,
                bytes_per_line=bytes_per_line
            )

            if buffer and len(buffer) >= buffer_size:
                # Try different approaches to handle color format
                return self._buffer_to_qimage(buffer, bytes_per_line)

        except Exception:
            pass

        return None

    def _buffer_to_qimage(self, buffer, bytes_per_line: int) -> Optional[QImage]:
        """Convert buffer to QImage with proper color handling"""
        try:
            # RLottie outputs BGRA format, we need to convert to ARGB for Qt
            width = self._width
            height = self._height

            # Fast approach: Use numpy if available for bulk conversion
            try:
                import numpy as np

                # Convert buffer to numpy array
                if isinstance(buffer, (bytes, bytearray)):
                    buffer_array = np.frombuffer(buffer, dtype=np.uint8)
                else:
                    buffer_array = np.array(buffer, dtype=np.uint8)

                # Reshape to (height, width, 4) for BGRA
                image_array = buffer_array.reshape((height, width, 4))

                # Convert BGRA to RGBA by swapping R and B channels
                rgba_array = image_array.copy()
                rgba_array[:, :, 0] = image_array[:, :, 2]  # R = B
                rgba_array[:, :, 2] = image_array[:, :, 0]  # B = R
                # G and A stay the same

                # Create QImage from RGBA data
                qimage = QImage(rgba_array.data, width, height,
                                bytes_per_line, QImage_Format_RGBA8888)
                return qimage.copy()  # Copy to ensure data persistence

            except ImportError:
                # Fallback: Manual conversion (slower but works without numpy)
                pass

            # Fallback method: Convert using QImage constructor with format swapping
            # Create QImage directly from buffer but treat as BGRA
            # This is experimental - different Qt versions handle this differently

            # Try creating with ARGB32 format and manual conversion
            import array

            # Convert buffer to array for easier manipulation
            if isinstance(buffer, (bytes, bytearray)):
                src_data = array.array('B', buffer)
            else:
                src_data = buffer

            # Create output array for ARGB32 format
            argb_data = array.array('B', [0] * (width * height * 4))

            # Convert BGRA to ARGB efficiently
            for i in range(0, len(src_data), 4):
                if i + 3 < len(src_data):
                    # Source: BGRA
                    b = src_data[i + 0]
                    g = src_data[i + 1]
                    r = src_data[i + 2]
                    a = src_data[i + 3]

                    # Target: ARGB (big-endian) or BGRA (little-endian)
                    # On little-endian systems, ARGB32 is stored as BGRA in memory
                    argb_data[i + 0] = b  # Blue
                    argb_data[i + 1] = g  # Green
                    argb_data[i + 2] = r  # Red
                    argb_data[i + 3] = a  # Alpha

            # Create QImage from converted data
            qimage = QImage(argb_data.tobytes(), width, height,
                            bytes_per_line, QImage_Format_ARGB32)
            return qimage.copy()

        except Exception:
            # Silently fall back to None - caller will handle fallback to PIL
            return None

    def debug_buffer_format(self, frame_number: int = 0) -> Dict[str, Any]:
        """Debug method to analyze RLottie's buffer format"""
        if not self.animation or frame_number >= self._total_frames:
            return {}

        try:
            bytes_per_pixel = 4
            bytes_per_line = self._width * bytes_per_pixel
            buffer_size = self._height * bytes_per_line

            buffer = self.animation.lottie_animation_render(
                frame_num=frame_number,
                buffer_size=buffer_size,
                width=self._width,
                height=self._height,
                bytes_per_line=bytes_per_line
            )

            if buffer and len(buffer) >= 16:  # At least 4 pixels
                return {
                    'buffer_size': len(buffer),
                    'expected_size': buffer_size,
                    'width': self._width,
                    'height': self._height,
                    'bytes_per_line': bytes_per_line,
                    'first_16_bytes': list(buffer[:16]),
                    'sample_pixel_interpretations': {
                        'as_rgba': [buffer[0], buffer[1], buffer[2], buffer[3]],
                        'as_bgra': [buffer[2], buffer[1], buffer[0], buffer[3]],
                        'as_argb': [buffer[3], buffer[0], buffer[1], buffer[2]],
                        'as_abgr': [buffer[3], buffer[2], buffer[1], buffer[0]]
                    }
                }
        except Exception as e:
            return {'error': str(e)}

        return {}

    def render_frame_async(self, frame_number: int) -> None:
        """Start async rendering of a frame"""
        if not self.animation:
            return

        if frame_number < 0 or frame_number >= self._total_frames:
            return

        try:
            # Calculate buffer parameters
            bytes_per_pixel = 4  # RGBA
            bytes_per_line = self._width * bytes_per_pixel
            buffer_size = self._height * bytes_per_line

            # Start async rendering
            self.animation.lottie_animation_render_async(
                frame_num=frame_number,
                buffer_size=buffer_size,
                width=self._width,
                height=self._height,
                bytes_per_line=bytes_per_line
            )
        except Exception:
            pass

    def get_async_frame(self) -> Optional[QImage]:
        """Get the result of async rendering"""
        if not self.animation:
            return None

        try:
            # Calculate buffer parameters
            bytes_per_pixel = 4  # RGBA
            bytes_per_line = self._width * bytes_per_pixel
            buffer_size = self._height * bytes_per_line

            # Get the rendered buffer
            buffer = self.animation.lottie_animation_render_flush()

            if buffer and len(buffer) >= buffer_size:
                # Use the same buffer conversion logic
                return self._buffer_to_qimage(buffer, bytes_per_line)

        except Exception:
            pass

        return None

    def render_frames_batch(self, frame_numbers: List[int]) -> Dict[int, Optional[QImage]]:
        results = {}

        for frame_num in frame_numbers:
            results[frame_num] = self.render_frame(frame_num)

        return results

    def render_frame_at_pos(self, position: float) -> Optional[QImage]:
        if self._duration <= 0:
            return None

        frame = int(position * self._frame_rate)
        frame = max(0, min(frame, self._total_frames - 1))

        return self.render_frame(frame)

    def set_direct_rendering(self, enabled: bool) -> None:
        """Enable/disable direct buffer rendering for better quality"""
        self._use_direct_rendering = enabled

    def get_direct_rendering(self) -> bool:
        """Get current direct rendering setting"""
        return self._use_direct_rendering

    def set_async_rendering(self, enabled: bool) -> None:
        """Enable/disable async rendering for performance"""
        self._use_async_rendering = enabled

    def get_async_rendering(self) -> bool:
        """Get current async rendering setting"""
        return self._use_async_rendering

    def _pil_to_qimage(self, pil_image) -> QImage:
        if not pil_image:
            return QImage()

        # Fast path: Direct PIL to QImage conversion without numpy
        try:
            if hasattr(pil_image, 'tobytes'):
                # Ensure RGBA format for consistent handling
                if pil_image.mode != 'RGBA':
                    pil_image = pil_image.convert('RGBA')

                raw_data = pil_image.tobytes()
                width, height = pil_image.size
                bytes_per_line = width * 4

                # Use non-premultiplied format for better compatibility with PIL
                qimage = QImage(raw_data, width, height, bytes_per_line, QImage_Format_RGBA8888)
                return qimage.copy()  # Copy to ensure data persistence
        except Exception:
            pass

        # Fallback: numpy path (if available) - faster than PNG
        try:
            import numpy as np
            if hasattr(pil_image, 'mode') and pil_image.mode == 'RGBA':
                np_array = np.array(pil_image)
                height, width, channels = np_array.shape
                bytes_per_line = channels * width

                qimage = QImage(np_array.data, width, height,
                                bytes_per_line, QImage_Format_RGBA8888)
                return qimage.copy()
        except (ImportError, AttributeError, Exception):
            pass

        # Final fallback: PNG method (slowest but most compatible)
        import io
        bytes_io = io.BytesIO()
        pil_image.save(bytes_io, format='PNG')
        image_bytes = bytes_io.getvalue()

        image = QImage()
        image.loadFromData(image_bytes)
        return image

    @property
    def total_frames(self) -> int:
        return self._total_frames

    @property
    def frame_rate(self) -> float:
        return self._frame_rate

    @property
    def duration(self) -> float:
        return self._duration

    @property
    def size(self) -> Tuple[int, int]:
        return (self._width, self._height)

    @property
    def is_loaded(self) -> bool:
        return self.animation is not None


def is_rlottie_available() -> bool:
    return RLOTTIE_AVAILABLE


def get_rlottie_version() -> str:
    if not RLOTTIE_AVAILABLE:
        return "Not available"
    try:
        return getattr(rlottie, '__version__', 'Unknown')
    except:
        return "Unknown"

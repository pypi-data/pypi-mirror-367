
import os
from typing import Optional, Tuple, Any, List, Dict
from ..compat import QImage, QSize

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
            pil_image = self.animation.render_pillow_frame(
                frame_num=frame_number, 
                width=self._width, 
                height=self._height
            )
            return self._pil_to_qimage(pil_image)
        except Exception:
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
    
    def _pil_to_qimage(self, pil_image) -> QImage:
        if not pil_image:
            return QImage()
        
        try:
            import numpy as np
            if hasattr(pil_image, 'mode') and pil_image.mode == 'RGBA':
                np_array = np.array(pil_image)
                height, width, channels = np_array.shape
                bytes_per_line = channels * width
                
                from ..compat import QImage_Format_RGBA8888
                qimage = QImage(np_array.data, width, height, bytes_per_line, QImage_Format_RGBA8888)
                return qimage.copy()
        except (ImportError, AttributeError, Exception):
            pass
        
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
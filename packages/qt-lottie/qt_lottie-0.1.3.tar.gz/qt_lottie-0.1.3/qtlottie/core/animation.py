
import os
from typing import Optional, List, Dict, Any, Tuple
from ..compat import (
    QQuickPaintedItem, QObject, QUrl, QColor, QRectF, QPainter, QSize,
    signal, property_, slot,
    Status, CacheMode, Direction, FillMode
)
from ..rlottie.wrapper import RLottieWrapper, RLottieError
from .controller import AnimationController
from .cache import AnimationFrameCache


class LottieAnimation(QQuickPaintedItem):
    """QML component for Lottie animation playback"""

    # Signals
    started = signal()
    stopped = signal()
    finished = signal()
    position_changed = signal(float)
    frame_changed = signal(int)
    marker_reached = signal(str)
    error = signal(str)

    # Property notification signals
    status_changed = signal()
    cache_mode_changed = signal()
    source_changed = signal()
    playing_changed = signal()
    current_frame_changed = signal()
    progress_changed = signal()
    duration_changed = signal()
    position_changed_notify = signal()
    fill_mode_changed = signal()
    auto_play_changed = signal()
    playback_rate_changed = signal()
    loops_changed = signal()
    direction_changed = signal()
    tint_color_changed = signal()
    asynchronous_changed = signal()
    max_render_size_changed = signal()
    enable_render_scaling_changed = signal()
    direct_rendering_changed = signal()

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)

        try:
            self._rlottie = RLottieWrapper()
        except RLottieError as e:
            print(f"Warning: RLottie not available: {e}")
            self._rlottie = None

        self._controller = AnimationController(self)
        self._cache = AnimationFrameCache()

        self._source = QUrl()
        self._status = Status.Null
        self._asynchronous = True
        self._cache_mode = CacheMode.CacheLoop  # Enable caching by default for better performance

        # Performance optimization settings
        self._max_render_size = 1024  # Reasonable default for good quality/performance balance
        self._enable_render_scaling = True  # Enable adaptive rendering by default
        self._direct_rendering = True  # Direct rendering now works with proper BGRA->RGBA conversion

        self._tint_color = QColor()
        self._fill_mode = FillMode.PreserveAspectFit
        self._smooth = True

        self._visible_layers: List[str] = []
        self._layer_opacities: Dict[str, float] = {}

        self._last_item_size = QSize(0, 0)
        self._target_rect_cache: Optional[QRectF] = None
        self._source_rect_cache: Optional[Any] = None

        self._base_image_cache: Dict[Tuple[int, int, int], Any] = {}

        self._last_render_size = QSize(0, 0)

        self._controller.started.connect(self.started)
        self._controller.stopped.connect(self.stopped)
        self._controller.finished.connect(self.finished)
        self._controller.position_changed.connect(self.position_changed)
        self._controller.position_changed.connect(self.position_changed_notify)
        self._controller.frame_changed.connect(self.frame_changed)
        self._controller.frame_changed.connect(self.current_frame_changed)
        self._controller.frame_changed.connect(self.progress_changed)
        self._controller.marker_reached.connect(self.marker_reached)
        self._controller.error.connect(self.error)

        self._controller.set_frame_callback(self._on_frame_changed)

        self._property_update_timer = None

        self.setAntialiasing(True)
        self.setRenderTarget(QQuickPaintedItem.RenderTarget.FramebufferObject)

        self.widthChanged.connect(self._on_size_changed)
        self.heightChanged.connect(self._on_size_changed)

    def paint(self, painter: QPainter) -> None:
        if not self._rlottie or not self._rlottie.is_loaded:
            return

        current_frame = self._controller.current_frame

        image = self._cache.get_frame(current_frame)

        if image is None:
            image = self._render_current_frame()
            if image is None:
                return

            self._cache.cache_frame(current_frame, image)

        current_size = self.size()
        if (self._target_rect_cache is None or
            self._source_rect_cache is None or
                current_size != self._last_item_size):

            self._source_rect_cache = image.rect()
            self._target_rect_cache = self._calculate_target_rect(self._source_rect_cache)
            self._last_item_size = current_size

        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, self._smooth)

        if self._tint_color.isValid() and self._tint_color.alpha() > 0:
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Multiply)
            painter.fillRect(self._target_rect_cache, self._tint_color)
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)

        painter.drawImage(self._target_rect_cache, image, self._source_rect_cache)

    def _render_current_frame(self) -> Optional[Any]:
        if not self._rlottie or not self._rlottie.is_loaded:
            return None

        item_size = self.size()
        if item_size.width() <= 0 or item_size.height() <= 0:
            return None

        current_frame = self._controller.current_frame

        # Performance optimization: limit render size for large widgets
        if self._enable_render_scaling:
            max_dimension = max(item_size.width(), item_size.height())
            if max_dimension > self._max_render_size:
                # Calculate scale to fit within max_render_size
                scale = self._max_render_size / max_dimension
                render_width = int(item_size.width() * scale)
                render_height = int(item_size.height() * scale)
                # Ensure minimum size for quality
                render_width = max(render_width, 100)
                render_height = max(render_height, 100)
            else:
                render_width = int(item_size.width())
                render_height = int(item_size.height())
        else:
            render_width = int(item_size.width())
            render_height = int(item_size.height())

        render_size = QSize(render_width, render_height)

        cache_key = (current_frame, render_width, render_height)
        if cache_key in self._base_image_cache:
            return self._base_image_cache[cache_key]

        if render_size != self._last_render_size:
            self._rlottie.set_size(render_width, render_height)
            self._last_render_size = render_size

        image = self._rlottie.render_frame(current_frame)
        if image:
            self._base_image_cache[cache_key] = image

            # Limit base image cache size based on image resolution
            # More aggressive caching for better performance
            pixels_per_frame = render_width * render_height
            memory_per_frame = pixels_per_frame * 4  # 4 bytes per pixel (RGBA)
            max_cache_memory = 100 * 1024 * 1024  # 100MB max cache
            max_cache_items = max(5, min(50, max_cache_memory // memory_per_frame))

            if len(self._base_image_cache) > max_cache_items:
                # Remove oldest items, keep most recent
                keys_to_remove = list(self._base_image_cache.keys())[:-max_cache_items//2]
                for key in keys_to_remove:
                    del self._base_image_cache[key]

        return image

    def _calculate_target_rect(self, source_rect: Any) -> QRectF:
        item_rect = QRectF(0, 0, self.width(), self.height())

        if self._fill_mode == FillMode.Stretch:
            return item_rect

        source_size = source_rect.size()
        target_size = item_rect.size()

        if source_size.width() <= 0 or source_size.height() <= 0:
            return item_rect

        scale_x = target_size.width() / source_size.width()
        scale_y = target_size.height() / source_size.height()

        if self._fill_mode == FillMode.PreserveAspectFit:
            scale = min(scale_x, scale_y)
        else:  # PreserveAspectCrop
            scale = max(scale_x, scale_y)

        scaled_width = source_size.width() * scale
        scaled_height = source_size.height() * scale

        x = (target_size.width() - scaled_width) / 2
        y = (target_size.height() - scaled_height) / 2

        return QRectF(x, y, scaled_width, scaled_height)

    def _start_property_timer(self) -> None:
        if self._property_update_timer is None:
            try:
                from ..compat import QTimer
                self._property_update_timer = QTimer(self)
                self._property_update_timer.timeout.connect(self._emit_property_updates)
                self._property_update_timer.start(100)  # Update every 100ms
            except Exception as e:
                print(f"Warning: Could not create property update timer: {e}")

    def _emit_property_updates(self) -> None:
        if self._controller:
            if self._controller.playing:
                self.playing_changed.emit()
                self.position_changed_notify.emit()
                self.current_frame_changed.emit()
                self.progress_changed.emit()

    def _on_frame_changed(self, frame_num: int) -> None:
        self.update()

        if self._cache.cache_mode != CacheMode.CacheNone:
            frames_to_prerender = self._cache.get_prerender_frames(
                frame_num,
                self._controller.playback_rate >= 0
            )

            if frames_to_prerender:
                frames_needed = [f for f in frames_to_prerender[:3] if not self._cache.has_frame(f)]
                if frames_needed:
                    from ..compat import QTimer
                    QTimer.singleShot(0, lambda: self._prerender_frames_batch(frames_needed))

    def _prerender_frame(self, frame_num: int) -> None:
        if self._rlottie and not self._cache.has_frame(frame_num):
            item_size = self.size()
            render_width = int(item_size.width())
            render_height = int(item_size.height())
            cache_key = (frame_num, render_width, render_height)

            if cache_key not in self._base_image_cache:
                current_size = QSize(render_width, render_height)
                if current_size != self._last_render_size:
                    self._rlottie.set_size(render_width, render_height)
                    self._last_render_size = current_size

                image = self._rlottie.render_frame(frame_num)
                if image:
                    self._base_image_cache[cache_key] = image
                    self._cache.cache_frame(frame_num, image)

    def _prerender_frames_batch(self, frame_numbers: List[int]) -> None:
        if not self._rlottie:
            return

        for frame_num in frame_numbers[:3]:
            self._prerender_frame(frame_num)

    def _on_size_changed(self) -> None:
        self._target_rect_cache = None
        self._source_rect_cache = None

        current_size = self.size()
        if (self._last_item_size.width() > 0 and self._last_item_size.height() > 0):
            width_change = abs(current_size.width() - self._last_item_size.width()
                               ) / self._last_item_size.width()
            height_change = abs(current_size.height() -
                                self._last_item_size.height()) / self._last_item_size.height()

            # More conservative cache clearing - only clear if significant size change
            # or if render scaling would change the actual render resolution
            should_clear_cache = False

            if width_change > 0.3 or height_change > 0.3:  # More conservative threshold
                should_clear_cache = True
            elif self._enable_render_scaling:
                # Check if the render resolution would actually change
                old_max = max(self._last_item_size.width(), self._last_item_size.height())
                new_max = max(current_size.width(), current_size.height())

                old_scale = min(1.0, self._max_render_size / old_max) if old_max > 0 else 1.0
                new_scale = min(1.0, self._max_render_size / new_max) if new_max > 0 else 1.0

                old_render_size = (int(self._last_item_size.width() * old_scale),
                                   int(self._last_item_size.height() * old_scale))
                new_render_size = (int(current_size.width() * new_scale),
                                   int(current_size.height() * new_scale))

                # Only clear if render size actually changes significantly
                if abs(old_render_size[0] - new_render_size[0]) > 50 or \
                   abs(old_render_size[1] - new_render_size[1]) > 50:
                    should_clear_cache = True

            if should_clear_cache:
                self._cache.clear_cache()
                self._base_image_cache.clear()
                self._last_render_size = QSize(0, 0)

    def _load_animation(self, source_path: str) -> None:
        if not os.path.exists(source_path):
            self._status = Status.Error
            self.error.emit(f"File not found: {source_path}")
            return

        try:
            if not self._rlottie:
                self._status = Status.Error
                self.status_changed.emit()
                self.error.emit("RLottie not available - install rlottie-python")
                return

            if self._rlottie.load_from_file(source_path):
                # Configure rendering quality
                if hasattr(self._rlottie, 'set_direct_rendering'):
                    self._rlottie.set_direct_rendering(self._direct_rendering)

                self._controller.set_animation_properties(
                    self._rlottie.total_frames,
                    self._rlottie.frame_rate,
                    self._rlottie.duration
                )

                self._cache.set_animation_properties(
                    self._rlottie.total_frames,
                    hash(source_path)
                )
                self._cache.set_cache_mode(self._cache_mode)

                self._status = Status.Ready
                self.status_changed.emit()

                self.duration_changed.emit()
                self.current_frame_changed.emit()
                self.progress_changed.emit()
                self.position_changed_notify.emit()

                if self._controller.auto_play:
                    self.play()

            else:
                self._status = Status.Error
                self.status_changed.emit()
                self.error.emit("Failed to load animation")

        except RLottieError as e:
            self._status = Status.Error
            self.status_changed.emit()
            self.error.emit(str(e))
        except Exception as e:
            self._status = Status.Error
            self.status_changed.emit()
            self.error.emit(f"Unexpected error: {str(e)}")

    # Public methods (slots)
    @slot()
    def play(self) -> None:
        """Start animation playback"""
        self._start_property_timer()  # Start property updates when animation plays
        self._controller.play()

    @slot()
    def pause(self) -> None:
        """Pause animation playback"""
        self._controller.pause()
        self.playing_changed.emit()

    @slot()
    def stop(self) -> None:
        """Stop animation playback"""
        self._controller.stop()
        self.playing_changed.emit()

    @slot()
    def toggle(self) -> None:
        """Toggle between play and pause"""
        self._controller.toggle()

    @slot(float)
    def seek(self, position: float) -> None:
        """Seek to time position"""
        self._cache.optimize_for_seek(int(position * self._controller.frame_rate))
        self._controller.seek(position)

    @slot(int)
    def seek_to_frame(self, frame: int) -> None:
        """Seek to frame number"""
        self._cache.optimize_for_seek(frame)
        self._controller.seek_to_frame(frame)

    @slot(str)
    def seek_to_marker(self, marker_name: str) -> None:
        """Seek to named marker"""
        self._controller.seek_to_marker(marker_name)

    @slot(str)
    def show_layer(self, layer_name: str) -> None:
        """Show a specific layer"""
        if layer_name not in self._visible_layers:
            self._visible_layers.append(layer_name)
            self._cache.clear_cache()
            self.update()

    @slot(str)
    def hide_layer(self, layer_name: str) -> None:
        """Hide a specific layer"""
        if layer_name in self._visible_layers:
            self._visible_layers.remove(layer_name)
            self._cache.clear_cache()
            self.update()

    @slot(str, float)
    def set_layer_opacity(self, layer_name: str, opacity: float) -> None:
        """Set layer opacity"""
        opacity = max(0.0, min(1.0, opacity))
        self._layer_opacities[layer_name] = opacity
        self._cache.clear_cache()
        self.update()

    def get_source(self) -> QUrl:
        return self._source

    def set_source(self, source) -> None:
        # Convert various source formats to QUrl
        if isinstance(source, str):
            if source.startswith("file://"):
                qurl_source = QUrl(source)
            else:
                # Treat as local file path
                qurl_source = QUrl.fromLocalFile(source)
        elif hasattr(source, 'toString'):  # QUrl-like object
            qurl_source = source
        else:
            # Fallback - try to convert to string then to QUrl
            qurl_source = QUrl.fromLocalFile(str(source))

        if qurl_source != self._source:
            self._source = qurl_source
            self._status = Status.Loading
            self.source_changed.emit()
            self.status_changed.emit()

            if qurl_source.isLocalFile():
                self._load_animation(qurl_source.toLocalFile())
            elif qurl_source.toString():
                # Handle URL loading (could be implemented later)
                self._status = Status.Error
                self.status_changed.emit()
                self.error.emit("URL loading not yet implemented")

    source = property_(QUrl, get_source, set_source, notify=source_changed)

    # Status
    def get_status(self) -> int:
        return self._status

    status = property_(int, get_status, notify=status_changed)

    # Playing
    def get_playing(self) -> bool:
        return self._controller.playing

    def set_playing(self, playing: bool) -> None:
        if playing != self._controller.playing:
            self._controller.playing = playing
            self.playing_changed.emit()

    playing = property_(bool, get_playing, set_playing, notify=playing_changed)

    # Auto Play
    def get_auto_play(self) -> bool:
        return self._controller.auto_play

    def set_auto_play(self, auto_play: bool) -> None:
        if auto_play != self._controller.auto_play:
            self._controller.auto_play = auto_play
            self.auto_play_changed.emit()

    autoPlay = property_(bool, get_auto_play, set_auto_play, notify=auto_play_changed)

    # Playback Rate
    def get_playback_rate(self) -> float:
        return self._controller.playback_rate

    def set_playback_rate(self, rate: float) -> None:
        if rate != self._controller.playback_rate:
            self._controller.playback_rate = rate
            self.playback_rate_changed.emit()

    playbackRate = property_(float, get_playback_rate, set_playback_rate,
                             notify=playback_rate_changed)

    # Loops
    def get_loops(self) -> int:
        return self._controller.loops

    def set_loops(self, loops: int) -> None:
        if loops != self._controller.loops:
            self._controller.loops = loops
            self.loops_changed.emit()

    loops = property_(int, get_loops, set_loops, notify=loops_changed)

    # Direction
    def get_direction(self) -> int:
        return self._controller.direction

    def set_direction(self, direction: int) -> None:
        if direction != self._controller.direction:
            self._controller.direction = direction
            self.direction_changed.emit()

    direction = property_(int, get_direction, set_direction, notify=direction_changed)

    # Position
    def get_position(self) -> float:
        return self._controller.position

    position = property_(float, get_position, notify=position_changed_notify)

    # Duration
    def get_duration(self) -> float:
        return self._controller.duration

    duration = property_(float, get_duration, notify=duration_changed)

    # Progress
    def get_progress(self) -> float:
        return self._controller.progress

    progress = property_(float, get_progress, notify=progress_changed)

    # Current Frame
    def get_current_frame(self) -> int:
        return self._controller.current_frame

    currentFrame = property_(int, get_current_frame, notify=current_frame_changed)

    # Cache Mode - define with explicit Qt Property for PySide6 compatibility
    def get_cache_mode(self) -> int:
        return self._cache_mode

    def set_cache_mode(self, mode: int) -> None:
        """Set cache mode with proper validation"""
        try:
            if mode != self._cache_mode:
                self._cache_mode = mode
                if hasattr(self._cache, 'set_cache_mode'):
                    self._cache.set_cache_mode(mode)
                self.cache_mode_changed.emit()
        except Exception as e:
            print(f"Error in set_cache_mode: {e}")
            # Continue with a safe fallback
            self._cache_mode = 0

    # Create property with explicit function binding to ensure proper resolution
    cacheMode = property_(int, get_cache_mode, set_cache_mode, notify=cache_mode_changed)

    # Tint Color
    def get_tint_color(self) -> QColor:
        return self._tint_color

    def set_tint_color(self, color: QColor) -> None:
        if color != self._tint_color:
            self._tint_color = color
            self.tint_color_changed.emit()
            self.update()

    tintColor = property_(QColor, get_tint_color, set_tint_color, notify=tint_color_changed)

    # Fill Mode
    def get_fill_mode(self) -> int:
        return self._fill_mode

    def set_fill_mode(self, mode: int) -> None:
        """Set fill mode with proper validation"""
        try:
            if mode != self._fill_mode:
                self._fill_mode = mode
                self.fill_mode_changed.emit()
                self.update()
        except Exception as e:
            print(f"Error in set_fill_mode: {e}")
            # Continue with a safe fallback
            self._fill_mode = 0

    # Create property with explicit function binding to ensure proper resolution
    fillMode = property_(int, get_fill_mode, set_fill_mode, notify=fill_mode_changed)

    # Smooth
    def get_smooth(self) -> bool:
        return self._smooth

    def set_smooth(self, smooth: bool) -> None:
        if smooth != self._smooth:
            self._smooth = smooth
            self.update()

    smooth = property_(bool, get_smooth, set_smooth)

    # Asynchronous
    def get_asynchronous(self) -> bool:
        return self._asynchronous

    def set_asynchronous(self, async_: bool) -> None:
        if async_ != self._asynchronous:
            self._asynchronous = async_
            self.asynchronous_changed.emit()

    asynchronous = property_(bool, get_asynchronous, set_asynchronous, notify=asynchronous_changed)

    # Performance optimization properties
    def get_max_render_size(self) -> int:
        return self._max_render_size

    def set_max_render_size(self, size: int) -> None:
        if size != self._max_render_size and size > 0:
            self._max_render_size = size
            # Clear cache to apply new render size
            self._cache.clear_cache()
            self._base_image_cache.clear()
            self._last_render_size = QSize(0, 0)
            self.max_render_size_changed.emit()
            self.update()

    maxRenderSize = property_(int, get_max_render_size, set_max_render_size,
                              notify=max_render_size_changed)

    def get_enable_render_scaling(self) -> bool:
        return self._enable_render_scaling

    def set_enable_render_scaling(self, enabled: bool) -> None:
        if enabled != self._enable_render_scaling:
            self._enable_render_scaling = enabled
            # Clear cache when changing render scaling mode
            self._cache.clear_cache()
            self._base_image_cache.clear()
            self._last_render_size = QSize(0, 0)
            self.enable_render_scaling_changed.emit()
            self.update()

    enableRenderScaling = property_(bool, get_enable_render_scaling,
                                    set_enable_render_scaling, notify=enable_render_scaling_changed)

    def get_direct_rendering(self) -> bool:
        return self._direct_rendering

    def set_direct_rendering(self, enabled: bool) -> None:
        if enabled != self._direct_rendering:
            self._direct_rendering = enabled
            # Apply to rlottie if available
            if hasattr(self._rlottie, 'set_direct_rendering'):
                self._rlottie.set_direct_rendering(enabled)
            self.direct_rendering_changed.emit()

    directRendering = property_(bool, get_direct_rendering,
                                set_direct_rendering, notify=direct_rendering_changed)

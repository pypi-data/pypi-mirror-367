
from typing import Optional, Callable
from ..compat import (
    QObject, QTimer, signal, slot, 
    AnimationState, Direction
)

class AnimationController(QObject):
    
    started = signal()
    stopped = signal()
    finished = signal()
    paused = signal()
    resumed = signal()
    position_changed = signal(float)  # position in seconds
    frame_changed = signal(int)       # current frame number
    marker_reached = signal(str)      # marker name
    error = signal(str)               # error message
    
    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        
        # Animation properties
        self._state = AnimationState.STOPPED
        self._position = 0.0
        self._duration = 0.0
        self._current_frame = 0
        self._total_frames = 0
        self._frame_rate = 30.0
        
        # Playback properties
        self._playing = False
        self._auto_play = False
        self._playback_rate = 1.0
        self._loops = 1
        self._current_loop = 0
        self._direction = Direction.Forward
        self._reverse_playback = False
        
        # Timer for frame updates
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_frame)
        
        # Frame update callback
        self._frame_callback: Optional[Callable[[int], None]] = None
        
        # Markers (name -> position in seconds)
        self._markers = {}
    
    def set_animation_properties(self, total_frames: int, frame_rate: float, duration: float) -> None:
        """Set animation properties from loaded animation
        
        Args:
            total_frames: Total number of frames
            frame_rate: Frames per second
            duration: Duration in seconds
        """
        self._total_frames = max(1, total_frames)
        self._frame_rate = max(1.0, frame_rate)
        self._duration = max(0.0, duration)
        
        # Reset position to start
        self.seek(0.0)
    
    def set_frame_callback(self, callback: Callable[[int], None]) -> None:
        """Set callback for frame updates
        
        Args:
            callback: Function to call with current frame number
        """
        self._frame_callback = callback
    
    @slot()
    def play(self) -> None:
        """Start or resume animation playback"""
        if self._state == AnimationState.FINISHED and self._loops != -1:
            # Restart from beginning if finished
            self.seek(0.0)
            self._current_loop = 0
        
        self._playing = True
        self._state = AnimationState.PLAYING
        
        # Calculate timer interval based on frame rate and playback rate
        interval = max(1, int(1000.0 / (self._frame_rate * abs(self._playback_rate))))
        self._timer.start(interval)
        
        self.started.emit()
    
    @slot()
    def pause(self) -> None:
        """Pause animation playback"""
        if self._state == AnimationState.PLAYING:
            self._timer.stop()
            self._state = AnimationState.PAUSED
            self._playing = False
            self.paused.emit()
    
    @slot()
    def stop(self) -> None:
        """Stop animation and reset to beginning"""
        self._timer.stop()
        self._state = AnimationState.STOPPED
        self._playing = False
        self._current_loop = 0
        self.seek(0.0)
        self.stopped.emit()
    
    @slot()
    def toggle(self) -> None:
        """Toggle between play and pause"""
        if self._playing:
            self.pause()
        else:
            self.play()
    
    @slot(float)
    def seek(self, position: float) -> None:
        """Seek to specific time position
        
        Args:
            position: Position in seconds
        """
        position = max(0.0, min(position, self._duration))
        
        if abs(position - self._position) < 1e-6:
            return
            
        self._position = position
        
        # Calculate frame number
        if self._duration > 0:
            frame = int(position * self._frame_rate)
            frame = max(0, min(frame, self._total_frames - 1))
            
            if frame != self._current_frame:
                self._current_frame = frame
                self.frame_changed.emit(frame)
                
                # Trigger frame callback
                if self._frame_callback:
                    self._frame_callback(frame)
        
        self.position_changed.emit(position)
        
        # Check for markers
        self._check_markers()
    
    @slot(int)
    def seek_to_frame(self, frame: int) -> None:
        """Seek to specific frame number
        
        Args:
            frame: Frame number (0-based)
        """
        frame = max(0, min(frame, self._total_frames - 1))
        position = frame / self._frame_rate if self._frame_rate > 0 else 0.0
        self.seek(position)
    
    @slot(str)
    def seek_to_marker(self, marker_name: str) -> None:
        """Seek to named marker
        
        Args:
            marker_name: Name of the marker
        """
        if marker_name in self._markers:
            self.seek(self._markers[marker_name])
    
    @slot()
    def _update_frame(self) -> None:
        """Update animation frame (called by timer)"""
        if not self._playing or self._duration <= 0:
            return
        
        # Calculate time step based on playback rate
        time_step = (1.0 / self._frame_rate) * self._playback_rate
        
        # Determine playback direction
        forward = (self._direction == Direction.Forward or 
                  (self._direction == Direction.Alternate and not self._reverse_playback))
        
        if self._playback_rate < 0:
            forward = not forward
        
        # Update position
        if forward:
            new_position = self._position + abs(time_step)
        else:
            new_position = self._position - abs(time_step)
        
        # Handle loop boundaries
        if new_position >= self._duration:
            self._handle_end_reached()
        elif new_position < 0:
            self._handle_start_reached()
        else:
            self.seek(new_position)
    
    def _handle_end_reached(self) -> None:
        """Handle reaching end of animation"""
        if self._loops == -1:  # Infinite loops
            self._handle_loop()
        elif self._current_loop < self._loops - 1:
            self._current_loop += 1
            self._handle_loop()
        else:
            # Animation finished
            self.seek(self._duration)
            self._timer.stop()
            self._state = AnimationState.FINISHED
            self._playing = False
            self.finished.emit()
    
    def _handle_start_reached(self) -> None:
        """Handle reaching start of animation (reverse playback)"""
        if self._loops == -1:  # Infinite loops
            self._handle_loop()
        elif self._current_loop < self._loops - 1:
            self._current_loop += 1
            self._handle_loop()
        else:
            # Animation finished
            self.seek(0.0)
            self._timer.stop()
            self._state = AnimationState.FINISHED
            self._playing = False
            self.finished.emit()
    
    def _handle_loop(self) -> None:
        """Handle loop behavior"""
        if self._direction == Direction.Alternate:
            # Ping-pong: reverse direction
            self._reverse_playback = not self._reverse_playback
            # Stay at current boundary
        else:
            # Normal loop: jump to opposite end
            if self._playback_rate >= 0:
                self.seek(0.0)
            else:
                self.seek(self._duration)
    
    def _check_markers(self) -> None:
        """Check if current position matches any markers"""
        for name, marker_pos in self._markers.items():
            if abs(self._position - marker_pos) < 1e-3:  # 1ms tolerance
                self.marker_reached.emit(name)
    
    def add_marker(self, name: str, position: float) -> None:
        """Add a named marker at specific position
        
        Args:
            name: Marker name
            position: Position in seconds
        """
        self._markers[name] = max(0.0, min(position, self._duration))
    
    def remove_marker(self, name: str) -> None:
        """Remove a named marker
        
        Args:
            name: Marker name to remove
        """
        self._markers.pop(name, None)
    
    def clear_markers(self) -> None:
        """Clear all markers"""
        self._markers.clear()
    
    # Properties
    @property
    def state(self) -> int:
        return self._state
    
    @property
    def playing(self) -> bool:
        return self._playing
    
    @playing.setter
    def playing(self, value: bool) -> None:
        if value and not self._playing:
            self.play()
        elif not value and self._playing:
            self.pause()
    
    @property
    def auto_play(self) -> bool:
        return self._auto_play
    
    @auto_play.setter
    def auto_play(self, value: bool) -> None:
        self._auto_play = value
    
    @property
    def playback_rate(self) -> float:
        return self._playback_rate
    
    @playback_rate.setter
    def playback_rate(self, value: float) -> None:
        self._playback_rate = value
        if self._playing:
            # Update timer interval
            interval = max(1, int(1000.0 / (self._frame_rate * abs(value))))
            self._timer.setInterval(interval)
    
    @property
    def loops(self) -> int:
        return self._loops
    
    @loops.setter
    def loops(self, value: int) -> None:
        self._loops = max(-1, value)
    
    @property
    def direction(self) -> int:
        return self._direction
    
    @direction.setter
    def direction(self, value: int) -> None:
        self._direction = value
        self._reverse_playback = False  # Reset ping-pong state
    
    @property
    def position(self) -> float:
        return self._position
    
    @property
    def duration(self) -> float:
        return self._duration
    
    @property
    def progress(self) -> float:
        """Animation progress from 0.0 to 1.0"""
        return self._position / self._duration if self._duration > 0 else 0.0
    
    @property
    def current_frame(self) -> int:
        return self._current_frame
    
    @property
    def total_frames(self) -> int:
        return self._total_frames
    
    @property
    def frame_rate(self) -> float:
        return self._frame_rate
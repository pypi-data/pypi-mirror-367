
from typing import Dict, Optional, List, Tuple
from collections import OrderedDict
from ..compat import QImage, QSize, CacheMode

class FrameCache:
    
    def __init__(self, max_size_mb: int = 50):
        """Initialize frame cache
        
        Args:
            max_size_mb: Maximum cache size in megabytes
        """
        self.max_size = max_size_mb * 1024 * 1024  # Convert to bytes
        self.current_size = 0
        self.frames: OrderedDict[int, QImage] = OrderedDict()
        self.frame_sizes: Dict[int, int] = {}
        
        self.hit_count = 0
        self.miss_count = 0
    
    def cache_frame(self, frame_num: int, image: QImage) -> bool:
        """Cache a frame image
        
        Args:
            frame_num: Frame number
            image: QImage to cache
            
        Returns:
            True if cached successfully, False if image too large
        """
        if image.isNull():
            return False
            
        image_size = self._calculate_image_size(image)
        
        # Check if image is too large for cache
        if image_size > self.max_size:
            return False
        
        # Remove existing frame if present
        if frame_num in self.frames:
            self._remove_frame(frame_num)
        
        # Make space for new frame
        while (self.current_size + image_size > self.max_size and self.frames):
            # Remove oldest frame (LRU eviction)
            oldest_frame = next(iter(self.frames))
            self._remove_frame(oldest_frame)
        
        # Add new frame
        self.frames[frame_num] = image.copy()  # Make a copy to avoid external modifications
        self.frame_sizes[frame_num] = image_size
        self.current_size += image_size
        
        return True
    
    def get_frame(self, frame_num: int) -> Optional[QImage]:
        """Get cached frame
        
        Args:
            frame_num: Frame number to retrieve
            
        Returns:
            Cached QImage or None if not found
        """
        if frame_num in self.frames:
            # Move to end (most recently used)
            image = self.frames.pop(frame_num)
            self.frames[frame_num] = image
            self.hit_count += 1
            return image
        
        self.miss_count += 1
        return None
    
    def has_frame(self, frame_num: int) -> bool:
        """Check if frame is cached
        
        Args:
            frame_num: Frame number to check
            
        Returns:
            True if frame is cached
        """
        return frame_num in self.frames
    
    def remove_frame(self, frame_num: int) -> bool:
        """Remove specific frame from cache
        
        Args:
            frame_num: Frame number to remove
            
        Returns:
            True if frame was removed
        """
        return self._remove_frame(frame_num)
    
    def _remove_frame(self, frame_num: int) -> bool:
        """Internal method to remove frame"""
        if frame_num in self.frames:
            self.frames.pop(frame_num)
            size = self.frame_sizes.pop(frame_num)
            self.current_size -= size
            return True
        return False
    
    def clear(self) -> None:
        """Clear all cached frames"""
        self.frames.clear()
        self.frame_sizes.clear()
        self.current_size = 0
        self.hit_count = 0
        self.miss_count = 0
    
    def get_cached_range(self) -> Tuple[int, int]:
        """Get range of cached frames
        
        Returns:
            Tuple of (min_frame, max_frame) or (-1, -1) if empty
        """
        if not self.frames:
            return (-1, -1)
        
        frame_nums = list(self.frames.keys())
        return (min(frame_nums), max(frame_nums))
    
    def get_cached_frames(self) -> List[int]:
        """Get list of cached frame numbers
        
        Returns:
            List of cached frame numbers
        """
        return list(self.frames.keys())
    
    def set_max_size(self, max_size_mb: int) -> None:
        """Set maximum cache size
        
        Args:
            max_size_mb: Maximum size in megabytes
        """
        self.max_size = max_size_mb * 1024 * 1024
        
        # Evict frames if over new limit
        while self.current_size > self.max_size and self.frames:
            oldest_frame = next(iter(self.frames))
            self._remove_frame(oldest_frame)
    
    def _calculate_image_size(self, image: QImage) -> int:
        """Calculate memory size of QImage
        
        Args:
            image: QImage to calculate size for
            
        Returns:
            Size in bytes
        """
        return image.sizeInBytes()
    
    @property
    def cache_hit_rate(self) -> float:
        """Get cache hit rate as percentage"""
        total = self.hit_count + self.miss_count
        return (self.hit_count / total * 100.0) if total > 0 else 0.0
    
    @property
    def memory_usage_mb(self) -> float:
        """Get current memory usage in MB"""
        return self.current_size / (1024 * 1024)
    
    @property
    def frame_count(self) -> int:
        """Get number of cached frames"""
        return len(self.frames)

class AnimationFrameCache:
    
    def __init__(self, max_size_mb: int = 50):
        """Initialize animation frame cache
        
        Args:
            max_size_mb: Maximum cache size in megabytes
        """
        self._cache = FrameCache(max_size_mb)
        self._mode = CacheMode.CacheNone
        self._total_frames = 0
        self._animation_id = 0
        
        # Pre-rendering state
        self._prerender_enabled = False
        self._prerender_ahead = 5  # Frames to render ahead
        self._prerender_behind = 2  # Frames to keep behind
    
    def set_cache_mode(self, mode: int) -> None:
        """Set caching mode
        
        Args:
            mode: CacheMode value
        """
        if mode != self._mode:
            self._mode = mode
            
            if mode == CacheMode.CacheNone:
                self._cache.clear()
            # Other modes will populate cache as needed
    
    def set_animation_properties(self, total_frames: int, animation_id: int = 0) -> None:
        """Set animation properties for cache management
        
        Args:
            total_frames: Total frames in animation
            animation_id: Unique ID for animation (for cache invalidation)
        """
        if animation_id != self._animation_id:
            self._cache.clear()
            self._animation_id = animation_id
        
        self._total_frames = total_frames
    
    def should_cache_frame(self, frame_num: int) -> bool:
        """Check if frame should be cached based on mode
        
        Args:
            frame_num: Frame number
            
        Returns:
            True if frame should be cached
        """
        if self._mode == CacheMode.CacheNone:
            return False
        elif self._mode == CacheMode.CacheAll:
            return True
        elif self._mode == CacheMode.CacheLoop:
            # Cache one complete loop
            return frame_num < self._total_frames
        
        return False
    
    def cache_frame(self, frame_num: int, image: QImage) -> bool:
        """Cache frame if appropriate
        
        Args:
            frame_num: Frame number
            image: Frame image
            
        Returns:
            True if cached
        """
        if not self.should_cache_frame(frame_num):
            return False
        
        return self._cache.cache_frame(frame_num, image)
    
    def get_frame(self, frame_num: int) -> Optional[QImage]:
        """Get frame from cache
        
        Args:
            frame_num: Frame number
            
        Returns:
            Cached frame or None
        """
        return self._cache.get_frame(frame_num)
    
    def has_frame(self, frame_num: int) -> bool:
        """Check if frame is cached
        
        Args:
            frame_num: Frame number
            
        Returns:
            True if cached
        """
        return self._cache.has_frame(frame_num)
    
    def clear_cache(self) -> None:
        """Clear all cached frames"""
        self._cache.clear()
    
    def setup_prerendering(self, enabled: bool, ahead: int = 5, behind: int = 2) -> None:
        """Setup frame pre-rendering
        
        Args:
            enabled: Enable pre-rendering
            ahead: Frames to render ahead
            behind: Frames to keep behind
        """
        self._prerender_enabled = enabled
        self._prerender_ahead = ahead
        self._prerender_behind = behind
    
    def get_prerender_frames(self, current_frame: int, forward: bool = True) -> List[int]:
        """Get frames that should be pre-rendered
        
        Args:
            current_frame: Current frame number
            forward: Playback direction
            
        Returns:
            List of frame numbers to pre-render
        """
        if not self._prerender_enabled or self._mode == CacheMode.CacheNone:
            return []
        
        frames_to_render = []
        
        # Frames ahead of current position
        for i in range(1, self._prerender_ahead + 1):
            if forward:
                frame = (current_frame + i) % self._total_frames
            else:
                frame = (current_frame - i) % self._total_frames
            
            if not self.has_frame(frame):
                frames_to_render.append(frame)
        
        # Remove old frames behind current position
        behind_threshold = self._prerender_behind
        frames_to_remove = []
        
        for frame_num in self._cache.get_cached_frames():
            if forward:
                distance = (current_frame - frame_num) % self._total_frames
            else:
                distance = (frame_num - current_frame) % self._total_frames
            
            if distance > behind_threshold:
                frames_to_remove.append(frame_num)
        
        # Remove old frames
        for frame_num in frames_to_remove:
            self._cache.remove_frame(frame_num)
        
        return frames_to_render
    
    def optimize_for_seek(self, target_frame: int, threshold: int = 10) -> None:
        """Optimize cache for seek operations
        
        Args:
            target_frame: Target frame after seek
            threshold: Frame distance threshold for cache clearing
        """
        if self._mode == CacheMode.CacheNone:
            return
        
        # If seeking far from cached range, clear cache
        min_frame, max_frame = self._cache.get_cached_range()
        
        if min_frame >= 0:  # Cache not empty
            distance_from_range = min(
                abs(target_frame - min_frame),
                abs(target_frame - max_frame)
            )
            
            if distance_from_range > threshold:
                self._cache.clear()
    
    @property
    def cache_mode(self) -> int:
        return self._mode
    
    @property
    def cache_statistics(self) -> Dict[str, float]:
        """Get cache performance statistics"""
        return {
            'hit_rate': self._cache.cache_hit_rate,
            'memory_usage_mb': self._cache.memory_usage_mb,
            'frame_count': self._cache.frame_count,
            'max_size_mb': self._cache.max_size / (1024 * 1024)
        }
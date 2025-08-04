"""Animation utility functions and math helpers

Provides utility functions for animation calculations and transformations.
"""

import math
from typing import Tuple, List

def clamp(value: float, min_val: float, max_val: float) -> float:
    """Clamp value between min and max
    
    Args:
        value: Value to clamp
        min_val: Minimum value
        max_val: Maximum value
        
    Returns:
        Clamped value
    """
    return max(min_val, min(value, max_val))

def lerp(start: float, end: float, t: float) -> float:
    """Linear interpolation between two values
    
    Args:
        start: Start value
        end: End value
        t: Interpolation factor (0.0 to 1.0)
        
    Returns:
        Interpolated value
    """
    return start + (end - start) * clamp(t, 0.0, 1.0)

def smooth_step(t: float) -> float:
    """Smooth step function for easing
    
    Args:
        t: Input value (0.0 to 1.0)
        
    Returns:
        Smoothed value
    """
    t = clamp(t, 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)

def smoother_step(t: float) -> float:
    """Smoother step function for better easing
    
    Args:
        t: Input value (0.0 to 1.0)
        
    Returns:
        Smoothed value
    """
    t = clamp(t, 0.0, 1.0)
    return t * t * t * (t * (t * 6.0 - 15.0) + 10.0)

def ease_in_quad(t: float) -> float:
    """Quadratic ease-in function
    
    Args:
        t: Input value (0.0 to 1.0)
        
    Returns:
        Eased value
    """
    return t * t

def ease_out_quad(t: float) -> float:
    """Quadratic ease-out function
    
    Args:
        t: Input value (0.0 to 1.0)
        
    Returns:
        Eased value
    """
    return 1.0 - (1.0 - t) * (1.0 - t)

def ease_in_out_quad(t: float) -> float:
    """Quadratic ease-in-out function
    
    Args:
        t: Input value (0.0 to 1.0)
        
    Returns:
        Eased value
    """
    if t < 0.5:
        return 2.0 * t * t
    else:
        return 1.0 - 2.0 * (1.0 - t) * (1.0 - t)

def ease_in_cubic(t: float) -> float:
    """Cubic ease-in function
    
    Args:
        t: Input value (0.0 to 1.0)
        
    Returns:
        Eased value
    """
    return t * t * t

def ease_out_cubic(t: float) -> float:
    """Cubic ease-out function
    
    Args:
        t: Input value (0.0 to 1.0)
        
    Returns:
        Eased value
    """
    return 1.0 - (1.0 - t) ** 3

def ease_in_out_cubic(t: float) -> float:
    """Cubic ease-in-out function
    
    Args:
        t: Input value (0.0 to 1.0)
        
    Returns:
        Eased value
    """
    if t < 0.5:
        return 4.0 * t * t * t
    else:
        return 1.0 - 4.0 * (1.0 - t) ** 3

def calculate_aspect_ratio(width: int, height: int) -> float:
    """Calculate aspect ratio from dimensions
    
    Args:
        width: Width in pixels
        height: Height in pixels
        
    Returns:
        Aspect ratio (width/height)
    """
    return width / height if height > 0 else 1.0

def fit_dimensions(source_width: int, source_height: int, 
                  target_width: int, target_height: int,
                  preserve_aspect: bool = True, 
                  crop: bool = False) -> Tuple[int, int]:
    """Calculate fitted dimensions
    
    Args:
        source_width: Source width
        source_height: Source height
        target_width: Target width
        target_height: Target height
        preserve_aspect: Whether to preserve aspect ratio
        crop: Whether to crop (fill) instead of fit
        
    Returns:
        Tuple of (fitted_width, fitted_height)
    """
    if not preserve_aspect:
        return (target_width, target_height)
    
    if source_width <= 0 or source_height <= 0:
        return (target_width, target_height)
    
    source_aspect = source_width / source_height
    target_aspect = target_width / target_height
    
    if crop:
        # Fill/crop: use larger scale factor
        if source_aspect > target_aspect:
            # Source is wider, fit to height
            scale = target_height / source_height
        else:
            # Source is taller, fit to width
            scale = target_width / source_width
    else:
        # Fit: use smaller scale factor
        if source_aspect > target_aspect:
            # Source is wider, fit to width
            scale = target_width / source_width
        else:
            # Source is taller, fit to height
            scale = target_height / source_height
    
    fitted_width = int(source_width * scale)
    fitted_height = int(source_height * scale)
    
    return (fitted_width, fitted_height)

def calculate_center_offset(container_width: int, container_height: int,
                          content_width: int, content_height: int) -> Tuple[int, int]:
    """Calculate offset to center content in container
    
    Args:
        container_width: Container width
        container_height: Container height
        content_width: Content width
        content_height: Content height
        
    Returns:
        Tuple of (x_offset, y_offset)
    """
    x_offset = (container_width - content_width) // 2
    y_offset = (container_height - content_height) // 2
    
    return (x_offset, y_offset)

def normalize_angle(angle: float) -> float:
    """Normalize angle to 0-360 degrees
    
    Args:
        angle: Angle in degrees
        
    Returns:
        Normalized angle (0-360)
    """
    angle = angle % 360
    return angle if angle >= 0 else angle + 360

def degrees_to_radians(degrees: float) -> float:
    """Convert degrees to radians
    
    Args:
        degrees: Angle in degrees
        
    Returns:
        Angle in radians
    """
    return degrees * math.pi / 180.0

def radians_to_degrees(radians: float) -> float:
    """Convert radians to degrees
    
    Args:
        radians: Angle in radians
        
    Returns:
        Angle in degrees
    """
    return radians * 180.0 / math.pi

def calculate_bezier_point(t: float, p0: Tuple[float, float], 
                          p1: Tuple[float, float], p2: Tuple[float, float], 
                          p3: Tuple[float, float]) -> Tuple[float, float]:
    """Calculate point on cubic Bezier curve
    
    Args:
        t: Parameter (0.0 to 1.0)
        p0: Start point
        p1: First control point
        p2: Second control point
        p3: End point
        
    Returns:
        Point on curve (x, y)
    """
    u = 1.0 - t
    tt = t * t
    uu = u * u
    uuu = uu * u
    ttt = tt * t
    
    x = uuu * p0[0] + 3 * uu * t * p1[0] + 3 * u * tt * p2[0] + ttt * p3[0]
    y = uuu * p0[1] + 3 * uu * t * p1[1] + 3 * u * tt * p2[1] + ttt * p3[1]
    
    return (x, y)

def frame_to_time(frame: int, frame_rate: float) -> float:
    """Convert frame number to time in seconds
    
    Args:
        frame: Frame number (0-based)
        frame_rate: Frames per second
        
    Returns:
        Time in seconds
    """
    return frame / frame_rate if frame_rate > 0 else 0.0

def time_to_frame(time: float, frame_rate: float) -> int:
    """Convert time to frame number
    
    Args:
        time: Time in seconds
        frame_rate: Frames per second
        
    Returns:
        Frame number (0-based)
    """
    return int(time * frame_rate) if frame_rate > 0 else 0

def calculate_fps_from_duration(total_frames: int, duration: float) -> float:
    """Calculate frame rate from total frames and duration
    
    Args:
        total_frames: Total number of frames
        duration: Duration in seconds
        
    Returns:
        Frame rate (fps)
    """
    return total_frames / duration if duration > 0 else 30.0

def is_power_of_two(n: int) -> bool:
    """Check if number is power of two
    
    Args:
        n: Number to check
        
    Returns:
        True if power of two
    """
    return n > 0 and (n & (n - 1)) == 0

def next_power_of_two(n: int) -> int:
    """Get next power of two greater than or equal to n
    
    Args:
        n: Input number
        
    Returns:
        Next power of two
    """
    if n <= 0:
        return 1
    
    if is_power_of_two(n):
        return n
    
    power = 1
    while power < n:
        power *= 2
    
    return power

def color_blend(color1: Tuple[int, int, int, int], 
               color2: Tuple[int, int, int, int], 
               factor: float) -> Tuple[int, int, int, int]:
    """Blend two RGBA colors
    
    Args:
        color1: First color (r, g, b, a)
        color2: Second color (r, g, b, a)
        factor: Blend factor (0.0 = color1, 1.0 = color2)
        
    Returns:
        Blended color (r, g, b, a)
    """
    factor = clamp(factor, 0.0, 1.0)
    
    r = int(lerp(color1[0], color2[0], factor))
    g = int(lerp(color1[1], color2[1], factor))
    b = int(lerp(color1[2], color2[2], factor))
    a = int(lerp(color1[3], color2[3], factor))
    
    return (
        clamp(r, 0, 255),
        clamp(g, 0, 255),
        clamp(b, 0, 255),
        clamp(a, 0, 255)
    )
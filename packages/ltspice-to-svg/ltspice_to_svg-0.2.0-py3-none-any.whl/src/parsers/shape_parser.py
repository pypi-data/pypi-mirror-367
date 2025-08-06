"""
Common shape parsing functions for LTspice schematics and symbols.
"""
from typing import Dict, List, Tuple, Optional
import math

# List of shape types that can be parsed by this module
SUPPORTED_SHAPES = ['LINE', 'CIRCLE', 'RECTANGLE', 'ARC']

def parse_shape(line: str) -> Optional[Dict]:
    """
    Parse a shape line by detecting its type and calling the appropriate parser.
    
    Args:
        line: The line to parse
        
    Returns:
        Parsed shape data or None if parsing fails
    """
    parts = line.split()
    if not parts:
        return None
        
    shape_type = parts[0]
    if shape_type not in SUPPORTED_SHAPES:
        return None
    
    # Map shape types to their parser functions
    parser_map = {
        'LINE': parse_line,
        'CIRCLE': parse_circle,
        'RECTANGLE': parse_rectangle,
        'ARC': parse_arc
    }
    
    return parser_map[shape_type](line)

def get_line_style(style_code: int, is_symbol: bool = False) -> str:
    """Convert LTspice line style code to SVG dash array.
    0: solid
    1: dash
    2: dot
    3: dash dot
    4: dash dot dot
    
    For dots, we use a small length to make them round.
    For dashes, we use a length of 4 times the stroke width.
    The gap between elements is 2 times the stroke width.
    
    Args:
        style_code: The style code from LTspice (0-4)
        is_symbol: Whether this style is for a symbol shape (default: False)
    """
    # For dots, use a small value relative to stroke width
    dot_size = "0.001"  # This will be multiplied by stroke width
    gap_size = "2"    # This will be multiplied by stroke width
    dash_size = "4"   # This will be multiplied by stroke width
    
    # These values will be multiplied by stroke-width in SVG
    style_map = {
        0: None,  # solid
        1: f"{dash_size},{gap_size}",  # dash
        2: f"{dot_size},{gap_size}",  # dot
        3: f"{dash_size},{gap_size},{dot_size},{gap_size}",  # dash dot
        4: f"{dash_size},{gap_size},{dot_size},{gap_size},{dot_size},{gap_size}"  # dash dot dot
    }
    return style_map.get(style_code)

def parse_line(line: str, is_symbol: bool = False) -> Dict:
    """Parse a LINE entry and extract coordinates.
    Format: LINE Normal x1 y1 x2 y2 [style]
    """
    parts = line.split()
    if len(parts) >= 6 and parts[1] == 'Normal':  # LINE + Normal + 4 coordinates
        try:
            # Convert coordinates to integers
            x1, y1, x2, y2 = map(int, parts[2:6])
            line_data = {
                'x1': x1,
                'y1': y1,
                'x2': x2,
                'y2': y2
            }
            # Add line style if present
            if len(parts) > 6:
                try:
                    style_code = int(parts[6])
                    line_style = get_line_style(style_code, is_symbol)
                    if line_style is not None:
                        line_data['style'] = line_style
                except ValueError:
                    pass
            return line_data
        except ValueError:
            pass
    return None

def parse_circle(line: str, is_symbol: bool = False) -> Dict:
    """Parse a CIRCLE entry and extract coordinates.
    Format: CIRCLE Normal x1 y1 x2 y2 [style]
    """
    parts = line.split()
    if len(parts) >= 6 and parts[1] == 'Normal':  # CIRCLE + Normal + 4 coordinates
        try:
            # Convert coordinates to integers
            x1, y1, x2, y2 = map(int, parts[2:6])
            circle_data = {
                'x1': x1,
                'y1': y1,
                'x2': x2,
                'y2': y2
            }
            # Add line style if present
            if len(parts) > 6:
                try:
                    style_code = int(parts[6])
                    line_style = get_line_style(style_code, is_symbol)
                    if line_style is not None:
                        circle_data['style'] = line_style
                except ValueError:
                    pass
            return circle_data
        except ValueError:
            pass
    return None

def parse_rectangle(line: str, is_symbol: bool = False) -> Dict:
    """Parse a RECTANGLE entry and extract coordinates.
    Format: RECTANGLE Normal x1 y1 x2 y2 [style]
    """
    parts = line.split()
    if len(parts) >= 6 and parts[1] == 'Normal':  # RECTANGLE + Normal + 4 coordinates
        try:
            # Convert coordinates to integers
            x1, y1, x2, y2 = map(int, parts[2:6])
            rect_data = {
                'x1': x1,
                'y1': y1,
                'x2': x2,
                'y2': y2
            }
            # Add line style if present
            if len(parts) > 6:
                try:
                    style_code = int(parts[6])
                    line_style = get_line_style(style_code, is_symbol)
                    if line_style is not None:
                        rect_data['style'] = line_style
                except ValueError:
                    pass
            return rect_data
        except ValueError:
            pass
    return None

def parse_arc(line: str, is_symbol: bool = False) -> Dict:
    """Parse an ARC entry and extract coordinates.
    Format: ARC Normal x1 y1 x2 y2 x3 y3 x4 y4 [style]
    where:
    - (x1,y1) and (x2,y2) define the bounding box of the circle/ellipse
    - (x3,y3) defines the end point of the arc
    - (x4,y4) defines the start point of the arc
    """
    parts = line.split()
    if len(parts) >= 10 and parts[1] == 'Normal':  # ARC + Normal + 8 coordinates
        try:
            # Convert coordinates to integers
            x1, y1, x2, y2, x3, y3, x4, y4 = map(int, parts[2:10])
            
            # Calculate center of the bounding box
            center_x = (x1 + x2) / 2
            center_y = (y1 + y2) / 2
            
            # Calculate start and end angles (swap x3,y3 and x4,y4)
            start_angle = math.atan2(y4 - center_y, x4 - center_x)
            end_angle = math.atan2(y3 - center_y, x3 - center_x)
            
            # Convert angles to degrees
            start_angle = math.degrees(start_angle)
            end_angle = math.degrees(end_angle)
            
            # Ensure angles are in [0, 360) range
            start_angle = (start_angle + 360) % 360
            end_angle = (end_angle + 360) % 360
            
            arc_data = {
                'x1': x1,
                'y1': y1,
                'x2': x2,
                'y2': y2,
                'start_angle': start_angle,
                'end_angle': end_angle
            }
            # Add line style if present
            if len(parts) > 10:
                try:
                    style_code = int(parts[10])
                    line_style = get_line_style(style_code, is_symbol)
                    if line_style is not None:
                        arc_data['style'] = line_style
                except ValueError:
                    pass
            return arc_data
        except ValueError:
            pass
    return None 
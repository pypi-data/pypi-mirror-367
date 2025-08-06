from yta_constants.enum import YTAEnum as Enum


class GreenscreenType(Enum):
    """
    The type of greenscreen we are handling.
    """
    
    VIDEO = 'video'
    """
    Video that includes at least one greenscreen
    in at least one of its frames.
    """
    IMAGE = 'image'

GREENSCREEN_RGB_COLOR = (0, 249, 12)
"""
The RGB color we use to generate greenscreens.
"""
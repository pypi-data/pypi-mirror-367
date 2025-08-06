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
from yta_validation.parameter import ParameterValidator
from moviepy import VideoClip

import numpy as np


# TODO: I think I don't use this method
# so please, remove it if possible
def is_video_transparent(
    video: VideoClip
) -> bool:
    """
    Checks if the first frame of the mask of the
    given 'video' has, at least, one transparent
    pixel.

    The video must include a mask.
    """
    ParameterValidator.validate_mandatory_instance_of('video', video, VideoClip)
    
    # We need to find, by now, at least one transparent pixel
    # TODO: I would need to check all frames to be sure of this above
    # TODO: The mask can have partial transparency, which 
    # is a value greater than 0, so what do we consider
    # 'transparent' here (?)
    return (
        np.any(video.mask.get_frame(t = 0) == 1)
        if video.mask is not None else
        False
    )
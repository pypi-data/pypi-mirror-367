from yta_validation.parameter import ParameterValidator
from moviepy import VideoClip
from typing import Union


def subclip_video(
    video: VideoClip,
    start_time: float,
    end_time: float
) -> tuple[Union[VideoClip, None], VideoClip, Union[VideoClip, None]]:
    """
    Subclip the provided 'video' into 3 different subclips,
    according to the provided 'start_time' and 'end_time',
    and return them as a tuple of those 3 clips. First and
    third clip could be None.

    The first clip will be None when 'start_time' is 0, and 
    the third one when the 'end_time' is equal to the given
    'video' duration.
    """
    ParameterValidator.validate_mandatory_instance_of('video', video, VideoClip)
    ParameterValidator.validate_mandatory_positive_number('start_time', start_time, do_include_zero = True)
    ParameterValidator.validate_mandatory_positive_number('end_time', end_time, do_include_zero = False)

    left = (
        None
        if (
            start_time == 0 or
            start_time == None
        ) else
        video.with_subclip(0, start_time)
    )
    center = video.with_subclip(start_time, end_time)
    right = (
        None
        if (
            end_time is None or
            end_time >= video.duration
        ) else
        video.with_subclip(start_time = end_time)
    )

    return left, center, right




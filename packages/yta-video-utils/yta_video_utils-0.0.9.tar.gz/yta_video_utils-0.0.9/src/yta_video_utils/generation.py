from yta_image_base.parser import ImageParser
from yta_validation import PythonValidator
from yta_validation.parameter import ParameterValidator
from moviepy import ImageClip


def image_to_video(
    image: str,
    duration: float = 1.0,
    fps: float = 60.0
) -> ImageClip:
    """
    Create an ImageClip of 'duration' seconds with the
    given 'image'.
    """
    ParameterValidator.validate_mandatory_string('image', image, do_accept_empty = False)
    ParameterValidator.validate_mandatory_positive_number('duration', duration, do_include_zero = False)
    ParameterValidator.validate_mandatory_positive_number('fps', fps, do_include_zero = False)

    return (
        ImageClip(ImageParser.to_numpy(image), duration = duration).with_fps(fps)
        if not PythonValidator.is_instance_of(image, ImageClip) else
        image
    )
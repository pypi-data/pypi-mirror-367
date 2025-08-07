from yta_video_editor.video.attribute import VideoWrappedAttributeSingleValue, VideoWrappedAttributeProgressionValue, VideoWrappedAttributeGraphicValue
from yta_validation.parameter import ParameterValidator
from typing import Union


class VideoWrappedAttributeModifier:
    """
    Class to be used to modify a video attribute,
    generating as many values as frames the video
    has, so can frame can be modified individually.

    This instance can be instantiated only with
    one of the next types:
    - VideoWrappedAttributeSingleValue
    - VideoWrappedAttributeProgression
    - VideoWrappedAttributeGraphic
    """

    def __init__(
        self,
        modifier: Union[VideoWrappedAttributeSingleValue, VideoWrappedAttributeProgressionValue, VideoWrappedAttributeGraphicValue]
    ):
        ParameterValidator.validate_mandatory_instance_of('modifier', modifier, [VideoWrappedAttributeSingleValue, VideoWrappedAttributeProgressionValue, VideoWrappedAttributeGraphicValue])
        
        self.modifier = modifier

    def get_values(
        self,
        number_of_frames: float
    ):
        """
        Obtain an array of 'number_of_frames' values that
        will modify the attribute this instance is
        designed for.
        """
        return self.modifier.get_values(number_of_frames)
    
    def validate_values(
        self,
        number_of_frames: float,
        limit: tuple[float, float]
    ):
        """
        Validate that any of those 'values' is between the
        limit range. The 'n' parameter must be the number of
        frames in the video, and 'limit' a tuple of the lower
        and upper limit.

        This method must be called when a SubClipAttributeModifier
        instance is set in a SubClip because we know the number
        of frames and the limit for that specific attribute (it
        is being added to that attribute modifier) in that 
        moment.
        """
        if any(
            (
                value < limit[0] or
                value > limit[1]
            )
            for value in self.get_values(number_of_frames)
        ):
            raise Exception(f'One of the generated "values" is out of the limit [{limit[0]}, {limit[1]}]')

    def copy(
        self
    ):
        """
        Get a copy of the instance.
        """
        return VideoWrappedAttributeModifier(self.modifier.copy())
    
__all__ = [
    'VideoWrappedAttributeModifier'
]
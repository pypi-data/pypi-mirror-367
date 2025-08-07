from yta_video_editor.settings import VIDEO_MIN_POSITION, VIDEO_MAX_POSITION
from yta_video_moviepy.t import T, get_number_of_frames
from yta_validation.parameter import ParameterValidator
from yta_random import Random
from abc import ABC, abstractmethod

import math


class PositionOffsetChange(ABC):
    """
    Class that represent a variation of the video
    position respect to the main (absolute)
    position the video has. This offset should
    be added to the absolute position.

    This is for the kind of effects that modify
    the relative position of the video. For 
    example, making the video bounce or move in
    circles. It is relative to its current 
    position and not about an absolute position
    in the scene.
    """

    @property
    def number_of_frames(
        self
    ) -> int:
        """
        The number of frames affected by this
        change (which is the number of offsets
        we will have).
        """
        return get_number_of_frames(self.duration, self.fps)

    @property
    @abstractmethod
    def offsets(
        self
    ) -> list[tuple[int, int]]:
        """
        The list of offsets calculated for all the
        video frames.
        """
        pass

    def __init__(
        self,
        video_duration: float,
        video_fps: float,
    ):
        self.duration = video_duration
        """
        The duration of the video, to be able to
        calculate the values for the different frame
        time moments.
        """
        self.fps = video_fps
        """
        The frames per second of the video, to be 
        able to calculate the values for the different
        frame time moments.
        """

    def get_offset(
        self,
        t: float
    ) -> tuple[int, int]:
        """
        Get the relative offset for the provided 't'
        frame time moment. This offset must be added
        to the current video position.
        """
        return self.offsets[T.frame_time_to_frame_index(t, self.fps)]

# These classes below are custom made and
# must be in other module to avoid mixing
# the imports maybe
class PositionOffsetDefault(PositionOffsetChange):
    """
    The default value. This has to be used when
    we don't want to apply changes.
    """

    @property
    def offsets(
        self
    ) -> list[tuple[int, int]]:
        """
        The list of offsets calculated for all the
        video frames.
        """
        if not hasattr(self, '_offsets'):
            self._offsets = [(0, 0)] * self.number_of_frames

        return self._offsets
    
class PositionOffsetStatic(PositionOffsetChange):
    """
    Just a normal and static offset, the same for
    each frame.

    This is similar to the move effect we can 
    apply in any video editor.
    """

    @property
    def offsets(
        self
    ) -> list[tuple[int, int]]:
        """
        The list of offsets calculated for all the
        video frames.
        """
        if not hasattr(self, '_offsets'):
            self._offsets = [(self.x_variation, self.y_variation)] * self.number_of_frames

        return self._offsets
    
    def __init__(
        self,
        video_duration: float,
        video_fps: float,
        x_variation: int,
        y_variation: int
    ):
        self.duration = video_duration
        """
        The duration of the video, to be able to
        calculate the values for the different frame
        time moments.
        """
        self.fps = video_fps
        """
        The frames per second of the video, to be 
        able to calculate the values for the different
        frame time moments.
        """
        # This doesn't make sense at all, because
        # if the absolute position is near the
        # limits, this will make the video go far
        # away from them... 
        ParameterValidator.validate_mandatory_number_between('x_variation', x_variation, VIDEO_MIN_POSITION[0], VIDEO_MAX_POSITION[0])
        ParameterValidator.validate_mandatory_number_between('y_variation', y_variation, VIDEO_MIN_POSITION[1], VIDEO_MAX_POSITION[1])

        self.x_variation = x_variation
        """
        The x movement variation we want to apply.
        """
        self.y_variation = y_variation
        """
        The y movement variation we want to apply
        """

class PositionOffsetShake(PositionOffsetChange):
    """
    Shake the video in the current position.
    """

    @property
    def offsets(
        self
    ) -> list[tuple[int, int]]:
        """
        The list of offsets calculated for all the
        video frames.
        """
        if not hasattr(self, '_offsets'):
            
            frequency = 25

            self._offsets = [
                (
                    math.sin(2 * math.pi * frequency * T.frame_index_to_frame_time(i, self.fps) + Random.float_between(-0.5, 0.5)) * self.intensity * Random.float_between(0.7, 1.0),
                    math.cos(2 * math.pi * frequency * T.frame_index_to_frame_time(i, self.fps) + Random.float_between(-0.5, 0.5)) * self.intensity * Random.float_between(0.7, 1.0)
                )
                for i in range(self.number_of_frames)
            ]

        return self._offsets

    def __init__(
        self,
        video_duration: float,
        video_fps: float,
        intensity: int = 4,
    ):
        super().__init__(video_duration, video_fps)

        # TODO: Validate intensity
        self.intensity = intensity
        """
        The intensity of the shake.

        TODO: Explain this better.
        """
        
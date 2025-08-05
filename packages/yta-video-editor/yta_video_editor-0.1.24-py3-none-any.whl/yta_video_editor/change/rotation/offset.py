from yta_video_moviepy.t import T, get_number_of_frames
from yta_random import Random
from abc import ABC, abstractmethod


class RotationOffsetChange(ABC):
    """
    Class that represent a variation of the video
    rotation respect to the main (absolute)
    rotation the video has. This offset should
    be added to the absolute rotation.

    This is for the kind of effects that modify
    the relative rotation of the video. For 
    example, making the video move like if it
    was a boat, while other rotation is happening.
    It is relative to its current rotation and not
    about an absolute rotation in the scene.
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
    ) -> list[int]:
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
    ) -> int:
        """
        Get the relative offset for the provided 't'
        frame time moment. This offset must be added
        to the current video rotation.
        """
        return self.offsets[T.frame_time_to_frame_index(t, self.fps)]

# These classes below are custom made and
# must be in other module to avoid mixing
# the imports maybe
class RotationOffsetDefault(RotationOffsetChange):
    """
    The default value. This has to be used when
    we don't want to apply changes.
    """

    @property
    def offsets(
        self
    ) -> list[int]:
        """
        The list of offsets calculated for all the
        video frames.
        """
        if not hasattr(self, '_offsets'):
            self._offsets = [0] * self.number_of_frames

        return self._offsets

class RotationOffsetFlipRandomly(RotationOffsetChange):
    """
    Flips the video horizontally but randomly.
    """

    @property
    def offsets(
        self
    ) -> list[int]:
        """
        The list of offsets calculated for all the
        video frames.
        """
        if not hasattr(self, '_offsets'):
            self._offsets = [
                (
                    180
                    if Random.chance(1 / 10) else
                    0
                )
                for _ in range(self.number_of_frames)
            ]

        return self._offsets

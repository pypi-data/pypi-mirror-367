from yta_video_moviepy.t import T, get_number_of_frames
from yta_general_utils.math.progression import Progression
from abc import ABC, abstractmethod


class ResizeOffsetChange(ABC):
    """
    Class that represent a variation of the video
    resize factor respect to the main (absolute)
    resize factor the video has. This offset
    should be added to the absolute resize factor.

    This is for the kind of effects that modify
    the relative size of the video. For example,
    making the video zoom in in an specific 
    position. It is relative to its current size
    and not about an absolute resize factor in the 
    scene.
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
        frame time moment. This offset must be
        multiplying the current video resize factor.
        """
        return self.offsets[T.frame_time_to_frame_index(t, self.fps)]

# These classes below are custom made and
# must be in other module to avoid mixing
# the imports maybe
class ResizeOffsetDefault(ResizeOffsetChange):
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
            self._offsets = [0.0] * self.number_of_frames

        return self._offsets

class ResizeOffsetZoomIn(ResizeOffsetChange):
    """
    Apply a zoom in (0.8 to 1.0) to the video.
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
            self._offsets = Progression(0.8, 1.0, self.number_of_frames).values

        return self._offsets
        
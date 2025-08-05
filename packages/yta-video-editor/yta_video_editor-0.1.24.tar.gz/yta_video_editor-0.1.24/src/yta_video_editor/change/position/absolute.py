from yta_video_moviepy.t import T, get_number_of_frames
from yta_constants.multimedia import DEFAULT_SCENE_WIDTH, DEFAULT_SCENE_HEIGHT
from yta_general_utils.math.progression import Progression
from abc import ABC, abstractmethod


class PositionAbsoluteChange(ABC):
    """
    Class that represent a variation of the video
    position by absolute values. This position
    should be used directly to position the video.
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
    def positions(
        self
    ) -> list[tuple[int, int]]:
        """
        The list of positions calculated for all the
        video frames. These positions are the place
        in which the center of the video must be
        placed.
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

    def get_position(
        self,
        t: float
    ) -> tuple[int, int]:
        """
        Get the absolute position for the provided 't'
        frame time moment. This position must replace
        the current video position.
        """
        return self.positions[T.frame_time_to_frame_index(t, self.fps)]

# These classes below are custom made and
# must be in other module to avoid mixing
# the imports maybe
class PositionAbsoluteDefault(PositionAbsoluteChange):
    """
    The default value. This has to be used when
    we don't want to apply changes.
    """

    @property
    def positions(
        self
    ) -> list[tuple[int, int]]:
        """
        The list of positions calculated for all the
        video frames. These positions are the place
        in which the center of the video must be
        placed.
        """
        if not hasattr(self, '_positions'):
            self._positions = [(DEFAULT_SCENE_WIDTH / 2, DEFAULT_SCENE_HEIGHT / 2)] * self.number_of_frames

        return self._positions

class PositionAbsoluteFromAtoB(PositionAbsoluteChange):
    """
    Move the video from A to B.
    """

    @property
    def positions(
        self
    ) -> list[tuple[int, int]]:
        """
        The list of positions calculated for all the
        video frames. These positions are the place
        in which the center of the video must be
        placed.
        """
        if not hasattr(self, '_positions'):
            # By now its just linear movement
            x_values = Progression(self.origin[0], self.destination[0], self.number_of_frames).values
            y_values = Progression(self.origin[1], self.destination[1], self.number_of_frames).values

            self._positions = list(zip(x_values, y_values))

        return self._positions

    def __init__(
        self,
        video_duration: float,
        video_fps: float,
        origin: tuple[int, int],
        destination: tuple[int, int],
    ):
        super().__init__(video_duration, video_fps)

        # TODO: Validate positions
        self.origin = origin
        self.destination = destination
        
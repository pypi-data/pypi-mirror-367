from yta_video_moviepy.t import T, get_number_of_frames
from yta_general_utils.math.progression import Progression
from yta_validation.parameter import ParameterValidator
from abc import ABC, abstractmethod


class RotationAbsoluteChange(ABC):
    """
    Class that represent a variation of the video
    rotation by absolute values. This rotation
    should be used directly to the video.
    """

    @property
    def number_of_frames(
        self
    ) -> int:
        """
        The number of frames affected by this
        change (which is the number of rotation
        values we will have).
        """
        return get_number_of_frames(self.duration, self.fps)

    @property
    @abstractmethod
    def rotations(
        self
    ) -> list[int]:
        """
        The list of rotations calculated for all the
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

    def get_rotation(
        self,
        t: float
    ) -> int:
        """
        Get the absolute rotation for the provided 't'
        frame time moment. This rotation must replace
        the current video rotation.
        """
        return self.rotations[T.frame_time_to_frame_index(t, self.fps)]

# These classes below are custom made and
# must be in other module to avoid mixing
# the imports maybe
class RotationAbsoluteDefault(RotationAbsoluteChange):
    """
    The default value. This has to be used when
    we don't want to apply changes.
    """

    @property
    def rotations(
        self
    ) -> list[int]:
        """
        The list of rotations calculated for all the
        video frames.
        """
        if not hasattr(self, '_rotations'):
            self._rotations = [0] * self.number_of_frames

        return self._rotations
    
class RotationAbsoluteStatic(RotationAbsoluteChange):
    """
    Just a normal and static rotation, the same for
    each frame.

    This is similar to the rotation effect we can 
    apply in any video editor.
    """

    @property
    def rotations(
        self
    ) -> list[int]:
        """
        The list of rotations calculated for all the
        video frames.
        """
        if not hasattr(self, '_rotations'):
            self._rotations = [self.rotation_factor] * self.number_of_frames

        return self._rotations
    
    def __init__(
        self,
        video_duration: float,
        video_fps: float,
        rotation_factor: float
    ):
        """
        The 'rotation_factor' parameter should be a number
        between 0 and 360, that can be negative.
        """
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
        ParameterValidator.validate_mandatory_number('rotation_factor', rotation_factor, do_include_zero = True)

        self.rotation_factor = int(rotation_factor % 360)
        """
        The rotation we want to apply, as a value
        between 0 and 359, both inclusive, and also
        accepted as negative numbers.
        """

class RotationAbsoluteSpinXTimes(RotationAbsoluteChange):
    """
    Spin the video X times.
    """

    @property
    def rotations(
        self
    ) -> list[int]:
        """
        The list of rotations calculated for all the
        video frames.
        """
        if not hasattr(self, '_rotations'):
            self._rotations = Progression(0, 360 * self.times, self.number_of_frames).values

        return self._rotations

    def __init__(
        self,
        video_duration: float,
        video_fps: float,
        times: int = 1
    ):
        ParameterValidator.validate_mandatory_positive_int('times', times, do_include_zero = False)

        super().__init__(video_duration, video_fps)

        self.times = times
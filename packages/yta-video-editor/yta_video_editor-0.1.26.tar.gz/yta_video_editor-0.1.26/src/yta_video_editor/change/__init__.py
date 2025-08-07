"""
Module to include all the specific
modifications we can do in a video about
its core moviepy attributes.
"""
from yta_video_editor.change.transform import _Transform, TransformChange
from yta_video_editor.change.position import PositionChange
from yta_video_editor.change.rotation import RotationChange
from yta_video_editor.change.resize import ResizeChange
from yta_video_editor.change.position.absolute import PositionAbsoluteChange
from yta_video_editor.change.position.offset import PositionOffsetChange
from yta_video_editor.change.resize.absolute import ResizeAbsoluteChange
from yta_video_editor.change.resize.offset import ResizeOffsetChange
from yta_video_editor.change.rotation.absolute import RotationAbsoluteChange
from yta_video_editor.change.rotation.offset import RotationOffsetChange
from yta_video_editor.utils import put_video_over_black_background, get_rotated_image_size
from yta_video_moviepy.t import T
from yta_validation.parameter import ParameterValidator
from yta_validation import PythonValidator
from moviepy import VideoClip
from typing import Union
from abc import ABC, abstractmethod


class _SetChange:
    """
    Base class to be inherited by the other
    classes that set the position, rotation
    and resize change.
    """

    def __init__(
        self
    ):
        self.values: _SetChangeValues = None
        """
        The values that represent each factor to be
        applied for each change and video time frame
        moment. Each array index is one video frame
        index.
        """

    def get_value(
        self,
        t: float,
        fps: float
    ) -> tuple[int, int]:
        """
        Get the position value for the given 't'
        according to the 'fps' of the video.
        """
        return self.values.get_value(t, fps)

    def apply_to_video(
        self,
        video: VideoClip
    ) -> VideoClip:
        """
        Get the 'video' with the position applied
        over a black background scene to be able to
        position it.
        """
        return self.values.apply_to_video(video)

class _SetChangeValues(ABC):
    """
    Abstract class to be inherited by all the
    values class that are related to position,
    rotation and resizing of a video.
    """

    def __init__(
        self,
        values: list[any]
    ):
        self.values = values
        """
        The change values that must be applied for
        each video time frame moment t. Each array
        index is one video frame index.
        """

    def get_value(
        self,
        t: float,
        fps: float
    ) -> tuple[int, int]:
        """
        Get the value for the given 't'
        according to the 'fps' of the video.
        """
        return self.values[T.frame_time_to_frame_index(t, fps)]

    @abstractmethod
    def apply_to_video(
        self,
        video: VideoClip
    ) -> VideoClip:
        """
        Get the 'video' with the change applied 
        according to all the values.
        """
        pass

class _SetRotationValues(_SetChangeValues):
    """
    Class representing all the position values
    that we need to use to position the center
    of the video where we want, on each frame
    of it.
    """

    def __init__(
        self,
        values: list[int]
    ):
        # TODO: Validate 'values' (?)
        self.values = values
        """
        The rotation values that represent how much
        do we need to rotate the video for each time
        frame moment t. Each array index is one video
        frame index.
        """

    def apply_to_video(
        self,
        video: VideoClip
    ) -> VideoClip:
        """
        Get the 'video' but rotated.
        """
        return video.rotated(
            angle = lambda t: self.get_value(t, video.fps),
            expand = True
        )

class _SetRotation(_SetChange):
    """
    Class to make easy the way we apply a rotation
    to the video and to encapsulate the code we
    need to do it.
    """

    def __init__(
        self,
        rotation: RotationChange,
        ts: list[float]
    ):
        ParameterValidator.validate_mandatory_instance_of('rotation', rotation, RotationChange)
        # TODO: Validate 'ts' (?)

        self.values = _SetRotationValues([
            rotation.get_rotation(t)
            for t in ts
        ])
        """
        The rotation values that represent how much
        do we need to rotate the video for each time
        frame moment t. Each array index is one video
        frame index.
        """

class _SetPositionValues(_SetChangeValues):
    """
    Class representing all the position values
    that we need to use to position the center
    of the video where we want, on each frame
    of it.
    """

    def __init__(
        self,
        values: list[tuple[int, int]]
    ):
        # TODO: Validate 'values' (?)
        self.values = values
        """
        The position values that represent were the
        center of the video must be placed for each
        time frame moment t. Each array index is one
        video frame index.
        """

    def apply_to_video(
        self,
        video: VideoClip
    ) -> VideoClip:
        """
        Get the 'video' with the position applied
        over a black background scene to be able to
        position it.
        """
        return put_video_over_black_background(
            video = video,
            position = lambda t: self.get_value(t, video.fps)
        )

class _SetPosition(_SetChange):
    """
    Class to make easy the way we apply a position
    to the video and to encapsulate the code we
    need to do it.
    """

    def __init__(
        self,
        position: PositionChange,
        ts: list[float]
    ):
        ParameterValidator.validate_mandatory_instance_of('position', position, PositionChange)
        # TODO: Validate 'ts' (?)

        self.values = _SetPositionValues([
            position.get_position(t)
            for t in ts
        ])
        """
        The position values that represent were the
        center of the video must be placed for each
        time frame moment t. Each array index is one
        video frame index.
        """

class _SetResizeValues(_SetChangeValues):
    """
    Class representing all the resize values
    that we need to use to resize the video,
    on each frame of it.
    """

    def __init__(
        self,
        values: list[tuple[int, int]]
    ):
        # TODO: Validate 'values' (?)
        self.values = values
        """
        The resize factor that must be applied for
        each video frame time moment t of the video.
        Each array index is one video frame index.
        """

    def apply_to_video(
        self,
        video: VideoClip
    ) -> VideoClip:
        """
        Get the 'video' but resized.
        """
        return video.resized(lambda t: self.get_value(t, video.fps))

class _SetResize(_SetChange):
    """
    Class to make easy the way we apply a resize
    factor to the video and to encapsulate the
    code we need to do it.
    """

    def __init__(
        self,
        resize: ResizeChange,
        ts: list[float]
    ):
        ParameterValidator.validate_mandatory_instance_of('resize', resize, ResizeChange)
        # TODO: Validate 'ts' (?)

        self.values = _SetResizeValues([
            resize.get_resize(t)
            for t in ts
        ])
        """
        The resize factor that must be applied for
        each video frame time moment t of the video.
        Each array index is one video frame index.
        """

class Changes:
    """
    All the changes a video must suffer.
    """

    @property
    def positions(
        self
    ) -> list[tuple[int, int]]:
        """
        The raw position values, as tuples of (x, y) in
        which the center of the video must be placed.

        These positions, as they represent where the 
        center of the video should be, can be used as
        they come in this attribute.
        """
        return self._positions.values
    
    @property
    def rotations(
        self
    ) -> list[int]:
        """
        The raw rotation factors, as float values, that
        we must apply to each video frame to obtain the
        expected rotation effect.

        These positions represent the final value that
        we must apply.

        (!) Rotating the video modifies each frame size,
        so the dimensions to calculate the upper left
        corner (to position it properly) have to be
        recalculated according to the resize factor that
        has been generated when rotating it.
        """
        return self._rotations.values
    
    @property
    def resizes(
        self
    ) -> list[int]:
        """
        The raw resize factors, as float values, that
        must be applied to resize the video.

        These values represent the final value that 
        must be applied.

        (!) Resizing the video means that we need to
        recalculate the upper left corner (to position
        it properly) according to this resize factor.
        """
        return self._resizes.values

    def __init__(
        self
    ):
        super().__init__()

        # TODO: What about the position? Are we sure
        # that the Default is the one we want (?)
        self._position_change: PositionChange = PositionChange()
        self._rotation_change: RotationChange = RotationChange()
        self._resize_change: ResizeChange = ResizeChange()
        self._transform_change: TransformChange = TransformChange()

        self._positions: Union[_SetPositionValues, None] = None
        """
        The positions in which the center of the video
        must be placed on each frame time moment.
        """
        self._rotations: Union[_SetRotationValues, None] = None
        """
        The rotation factors we need to apply to the
        video on each frame time moment.
        """
        self._resizes: Union[_SetResizeValues, None] = None
        """
        The resize factors we need to apply to the video
        on each frame time moment.
        """
        self.has_changes: bool = False
        """
        Internal flag to determine if it has changes to
        apply or not.
        """

    def add(
        self,
        # TODO: What do we accept (?)
        change: Union[PositionAbsoluteChange, PositionOffsetChange, ResizeAbsoluteChange, ResizeOffsetChange, RotationAbsoluteChange, RotationOffsetChange, _Transform]
    ) -> 'Changes':
        """
        Add the given 'change' to the corresponding
        change section (position, rotation or 
        resizing). The absolute changes will replace
        the previous ones (if existing), and the
        offset changes will be just appended.

        This method returns the Changes instance
        itself to be able to chain more changes.
        """
        ParameterValidator.validate_mandatory_subclass_of('change', change, [PositionAbsoluteChange, PositionOffsetChange, ResizeAbsoluteChange, ResizeOffsetChange, RotationAbsoluteChange, RotationOffsetChange, _Transform])

        if PythonValidator.is_subclass_of(change, [PositionAbsoluteChange, PositionOffsetChange]):
            self._position_change.add(change)
        elif PythonValidator.is_subclass_of(change, [ResizeAbsoluteChange, ResizeOffsetChange]):
            self._resize_change.add(change)
        elif PythonValidator.is_subclass_of(change, [RotationAbsoluteChange, RotationOffsetChange]):
            self._rotation_change.add(change)
        elif PythonValidator.is_subclass_of(change, _Transform):
            self._transform_change.add(change)

        self.has_changes = True

        return self

    def _precalculate(
        self,
        video: VideoClip
        # TODO: Maybe better 'duration' and 'fps' so
        # I can store them and recalculate only if 
        # needed...
    ) -> None:
        """
        Precalculate all the values we need to apply
        the changes on the video, but applying not.
        """
        ts = T.get_frame_time_moments(video.duration, video.fps)

        if self._position_change:
            self._positions = _SetPosition(
                position = self._position_change,
                ts = ts
            ).values

        if self._rotation_change:
            self._rotations = _SetRotation(
                rotation = self._rotation_change,
                ts = ts
            ).values

        if self._resize_change:
            self._resizes = _SetResize(
                resize = self._resize_change,
                ts = ts
            ).values

        # We don't need to precalculate the transform
        # as it is applied directly on the frame
        # modifying (transforming) it

    def apply(
        self,
        video: VideoClip,
        apply_to: Union[any, None] = None,
        do_keep_duration: bool = True
    ) -> VideoClip:
        """
        Apply all the changes to the given 'video'.
        """
        self._precalculate(video)

        # First, we need to apply all the changes
        # that are related to transforming the 
        # frame: color temperature, brightness, etc.
        video = self._transform_change.apply(video, apply_to, do_keep_duration)

        resizes = self.resizes
        rotations = self.rotations
        positions = self.positions

        # 1. We obtain the video size frame by frame
        # after resize
        video_sizes = [
            (int(video.w * resizes[i]), int(video.h * resizes[i]))
            for i in range(len(self.resizes))
        ]

        # 2. Then, the video is rotated so the video
        # size is also changed due to the rotation, so
        # we recalculate teh video size according to
        # that rotation
        for i in range(len(self.rotations)):
            video_sizes[i] = get_rotated_image_size(video_sizes[i], int(rotations[i]))[0]

        # 3. Now that we know the new video size for
        # each frame, resized and rotated, lets 
        # calculate the positions in which we need to
        # place the upper left corner of the video
        positions = [
            (
                self.positions[i][0] - video_sizes[i][0] / 2,
                self.positions[i][1] - video_sizes[i][1] / 2
            )
            for i in range(len(self.positions))
        ]

        video = video.resized(lambda t: resizes[T.frame_time_to_frame_index(t, video.fps)])
        video = video.rotated(lambda t: rotations[T.frame_time_to_frame_index(t, video.fps)], expand = True)
        # We need a black background to be able
        # to position it
        video = put_video_over_black_background(
            video = video,
            position = lambda t: positions[T.frame_time_to_frame_index(t, video.fps)]
        )

        return video

"""
Basically, the '_SetPosition' class is the
class to calculate the position values 
according to the 'PositionChange' we provide,
and the '_SetPositionValues' is the class
that holds all those calculated values, is
able to apply to a video but also allows us
to modify the values if we need (because there
is other related change that modifies it).
"""

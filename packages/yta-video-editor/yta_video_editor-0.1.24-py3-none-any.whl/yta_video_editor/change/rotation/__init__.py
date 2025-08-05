"""
TODO: This module is not working properly. We
are not able to correctly set the rotation of
a video because it modifies each frame size 
and it is difficult to manage it.
"""
from yta_video_editor.settings import DEFAULT_ROTATION_VALUE
from yta_video_editor.change.rotation.absolute import RotationAbsoluteChange
from yta_video_editor.change.rotation.offset import RotationOffsetChange
from yta_validation.parameter import ParameterValidator
from yta_validation import PythonValidator
from typing import Union


class RotationChange:
    """
    Class to handle a video rotation change by
    managing the RotationAbsoluteChange and all
    the different RotationOffsetChange provided.
    """

    def __init__(
        self,
        rotation_absolute: Union[RotationAbsoluteChange, None] = None,
        rotation_offsets: list[RotationOffsetChange] = []
    ):
        ParameterValidator.validate_subclass_of('rotation_absolute', rotation_absolute, RotationAbsoluteChange)
        ParameterValidator.validate_list_of_subclasses_of('rotation_offsets', rotation_offsets, RotationOffsetChange)

        self.rotation_absolute = rotation_absolute
        """
        The absolute rotation that must be applied to
        the video.
        """
        self.rotation_offsets = rotation_offsets
        """
        The offset value of the rotation that must be
        added to the absolute position of the video.
        """

    def add(
        self,
        change: Union[RotationAbsoluteChange, RotationOffsetChange]
    ):
        """
        Adds an absolute or offset change to this
        instance.

        - If an absolute change is added, it will replace
        the previous absolute change if existing.
        - If an offset change is added, it will be appended
        to the offset changes list.
        """
        ParameterValidator.validate_mandatory_subclass_of('change', change, [RotationAbsoluteChange, RotationOffsetChange])

        if PythonValidator.is_subclass_of(change, RotationAbsoluteChange):
            self.rotation_absolute = change
        else:
            self.rotation_offsets.append(change)

    def get_rotation(
        self,
        t: float
    ) -> int:
        """
        Get the final rotation that must be applied
        to the video according to the absolute and
        offset rotations provided.

        This rotation must be applied to the video.
        """
        rotation = (
            self.rotation_absolute.get_rotation(t)
            if self.rotation_absolute is not None else
            DEFAULT_ROTATION_VALUE
        )

        for rotation_offset in self.rotation_offsets:
            rotation += rotation_offset.get_offset(t)

        return rotation
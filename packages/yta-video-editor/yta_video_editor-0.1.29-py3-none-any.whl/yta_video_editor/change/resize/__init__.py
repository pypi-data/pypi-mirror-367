from yta_video_editor.settings import DEFAULT_RESIZE_VALUE
from yta_video_editor.change.resize.absolute import ResizeAbsoluteChange
from yta_video_editor.change.resize.offset import ResizeOffsetChange
from yta_validation.parameter import ParameterValidator
from yta_validation import PythonValidator
from typing import Union


class ResizeChange:
    """
    Class to handle a video resize change by
    managing the ResizeAbsoluteChange and all
    the different ResizeOffsetChange provided.
    """

    def __init__(
        self,
        resize_absolute: Union[ResizeAbsoluteChange, None] = None,
        resize_offsets: list[ResizeOffsetChange] = []
    ):
        ParameterValidator.validate_subclass_of('resize_absolute', resize_absolute, ResizeAbsoluteChange)
        ParameterValidator.validate_list_of_subclasses_of('resize_offsets', resize_offsets, ResizeOffsetChange)

        self.resize_absolute = resize_absolute
        """
        The absolute resize that must be applied to
        the video.
        """
        self.resize_offsets = resize_offsets
        """
        The relative offsets that must be added to the
        absolute resize of the video.
        """

    def add(
        self,
        change: Union[ResizeAbsoluteChange, ResizeOffsetChange]
    ):
        """
        Adds an absolute or offset change to this
        instance.

        - If an absolute change is added, it will replace
        the previous absolute change if existing.
        - If an offset change is added, it will be appended
        to the offset changes list.
        """
        ParameterValidator.validate_mandatory_subclass_of('change', change, [ResizeAbsoluteChange, ResizeOffsetChange])

        if PythonValidator.is_subclass_of(change, ResizeAbsoluteChange):
            self.resize_absolute = change
        else:
            self.resize_offsets.append(change)

    def get_resize(
        self,
        t: float
    ) -> float:
        """
        Get the final resize factor that must be
        applied according to the absolute resize
        factor and relative offsets provided.

        This resize factor must be used to resize
        the video.
        """
        resize = (
            self.resize_absolute.get_resize(t)
            if self.resize_absolute is not None else
            # TODO: Maybe '("center", "center")' (?)
            DEFAULT_RESIZE_VALUE
        )

        for resize_offset in self.resize_offsets:
            resize *= resize_offset.get_offset(t)

        return resize
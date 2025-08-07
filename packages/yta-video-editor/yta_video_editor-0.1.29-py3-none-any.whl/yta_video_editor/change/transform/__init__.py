from yta_video_editor.parameter import MakeFrameParameterSingleValue, MakeFrameParameter
from yta_video_moviepy.t import T, get_number_of_frames
from yta_validation.parameter import ParameterValidator
from yta_validation import PythonValidator
from moviepy import VideoClip
from typing import Union
from abc import ABC, abstractmethod


class _Transform(ABC):
    """
    Abstract class to be inherited by all the
    classes that are able to transform a video
    frame by frame.

    The parameters will be provided when 
    instantiated, being instances of our
    MakeFrameParameter class, and the transform
    values to be applied will be calculated 
    when needed.

    Each will have its own limit, that can be
    None, and all the code that will transform
    each video frame.
    """

    @property
    def limit(
        self
    ) -> Union[tuple[float, float], None]:
        """
        The limit in between all the values to apply
        when transforming have to fit.
        """
        return None

    @abstractmethod
    def transform(
        self,
        frame: 'np.ndarray',
        value: any
    ) -> 'np.ndarray':
        """
        Transform the given 'frame' with the 'value'
        provided and return the image transformed as
        a numpy array.
        """
        pass

    def apply(
        self,
        video: VideoClip,
        apply_to: Union[any, None] = None,
        do_keep_duration: bool = True
    ) -> VideoClip:
        """
        Use the provided 'transform_values' to modify 
        each frame of the given 'video' by applying 
        the also provided 'transform_function', that
        must be a function like this:

        - `transform_function(frame, value, **kwargs)`

        The 'frame' is the video frame as a numpy array
        that we will send, for each frame of the video.
        The 'value' is the specific modifier we will use
        to modify that frame, which is the value 
        obtained from the 'transform_values' that 
        corresponds to the frame we are transforming in
        the moment.

        If you need to send more than one factor, use
        array elements inside and extract them in your
        transform function.
        """
        values = self.factor.get_values(get_number_of_frames(video.duration, video.fps))

        return video.transform(
            func = lambda get_frame, t: self.transform(get_frame(t), values[T.frame_time_to_frame_index(t, video.fps)]),
            apply_to = apply_to,
            keep_duration = do_keep_duration
        )

    def __init__(
        self,
        factor: Union[MakeFrameParameter, float]
    ):
        if (
            not PythonValidator.is_number(factor) and
            not PythonValidator.is_subclass_of(factor, MakeFrameParameter)
        ):
            # TODO: Improve this text
            raise Exception('The "factor" provided is invalid.')
        
        factor = (
            MakeFrameParameterSingleValue(factor)
            if PythonValidator.is_number(factor) else
            factor
        )

        # Validate that the factor is valid according to
        # the limit of this class
        if self.limit is not None:
            if PythonValidator.is_instance_of(factor, 'MakeFrameParameterSingleValue'):
                ParameterValidator.validate_mandatory_number_between('factor.value', factor._value, self.limit[0], self.limit[1])
            elif PythonValidator.is_instance_of(factor, 'MakeFrameParameterValues'):
                for value in factor._values:
                    ParameterValidator.validate_mandatory_number_between('factor.value', value, self.limit[0], self.limit[1])
            elif PythonValidator.is_instance_of(factor, 'MakeFrameParameterProgression'):
                ParameterValidator.validate_mandatory_number_between('factor.initial_value', factor.initial_value, self.limit[0], self.limit[1])
                ParameterValidator.validate_mandatory_number_between('factor.final_value', factor.final_value, self.limit[0], self.limit[1])
            elif PythonValidator.is_instance_of(factor, 'MakeFrameParameterGraphic'):
                # TODO: Wtf do I do to check?
                pass

        self.factor = factor
        """
        The MakeFrameParameter that is able to calculate
        the values we need to apply as modification
        factors to each frame of the video.
        """

class TransformChange:
    """
    Class to handle the changes related to
    transform each video frame.
    """

    def __init__(
        self,
        change: Union[_Transform, None] = None,
    ):
        ParameterValidator.validate_subclass_of('change', change, _Transform)

        self.transform_changes = (
            [change]
            if change is not None else
            []
        )
        """
        The list of transform changes we want to
        apply in the video, one after the other.
        """

    def add(
        self,
        change: Union[_Transform]
    ):
        """
        Adds a transform change to this instance.
        """
        ParameterValidator.validate_mandatory_subclass_of('change', change, _Transform)

        # TODO: Validate something (?)
        self.transform_changes.append(change)

    def apply(
        self,
        video: VideoClip,
        apply_to: Union[any, None] = None,
        do_keep_duration: bool = True
    ) -> 'np.ndarray':
        """
        Get the video modified with all the transform
        changes that have been set in this instance
        to be applied.

        The changes will be applied in the order they
        were added (FIFO).

        This video must replace the original one.
        """
        for transform_change in self.transform_changes:
            video = transform_change.apply(video, apply_to, do_keep_duration)

        return video
        


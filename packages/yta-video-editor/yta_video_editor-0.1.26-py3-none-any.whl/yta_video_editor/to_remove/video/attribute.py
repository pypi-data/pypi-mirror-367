"""
The video has attributes or properties that can be
modified for each of the video frames. The values
of those frames are calculated by a modifier, that
is able to use 3 different types of values.
"""
from yta_validation.parameter import ParameterValidator
from yta_general_utils.math.progression import Progression
from yta_general_utils.math.rate_functions.rate_function_argument import RateFunctionArgument
from yta_general_utils.math.graphic.graphic import Graphic
from abc import ABC, abstractmethod


class VideoWrappedAttributeValue(ABC):
    @abstractmethod
    def get_values(
        self,
        number_of_frames: int
    ) -> list[any]:
        """
        Get the list of values for all the 'number_of_frames'
        frames of the video.
        """
        pass

    @abstractmethod
    def copy(
        self
    ) -> 'VideoWrappedAttributeValue':
        """
        Get a copy of the instance.
        """
        pass

class VideoWrappedAttributeSingleValue(VideoWrappedAttributeValue):
    """
    Class to include a single value for an attribute
    of a video, that must be applied in all the 
    video frames.

    This class can be used only for a video attribute
    modifier.
    """

    @property
    def value(
        self
    ) -> any:
        """
        The value of the attribute.
        """
        return self._value

    def __init__(
        self,
        value: any
    ):
        self._value = value

    def get_values(
        self,
        number_of_frames: int
    ) -> list[any]:
        """
        Get the list of values for all the 'number_of_frames'
        frames of the video.
        """
        ParameterValidator.validate_mandatory_positive_int('number_of_frames', number_of_frames)

        return [self.value] * number_of_frames
    
    def copy(
        self
    ) -> 'VideoWrappedAttributeSingleValue':
        """
        Get a copy of the instance.
        """
        return VideoWrappedAttributeSingleValue(self.value)


class VideoWrappedAttributeProgressionValue(VideoWrappedAttributeValue):
    """
    Class to represent the set of values that a video
    attribute must have for each of the frames the
    video includes. This means that we can make a video
    go from 0 contrast to 10 constrast increasing it
    smoothly (for example: 0, 2, 4, 6, 8 and 10) and
    not only abruptly (from 0 in one frame to 10 in the
    next one).
    
    This class can be used only for a video attribute
    modifier.
    """

    @property
    def is_single_value(
        self
    ) -> bool:
        """
        Check if the set of values is actually a single value
        because the initial and final value are the same.
        """
        return self.initial_value == self.final_value

    def __init__(
        self,
        initial_value: float,
        final_value: float,
        # TODO: Careful with this type
        rate_function: RateFunctionArgument = RateFunctionArgument.default()
    ):
        ParameterValidator.validate_mandatory_float('initial_value', initial_value)
        ParameterValidator.validate_mandatory_float('final_value', final_value)
        ParameterValidator.validate_mandatory_instance_of('rate_function', rate_function, RateFunctionArgument)

        # TODO: Maybe validate something? I don't know the
        # limits because each setting is different, but by
        # now I'm verifying the 'initial_value' and the
        # 'final_value' when using them on a VideoWrapped
        self.initial_value: float = initial_value
        """
        The initial value of the progression.
        """
        self.final_value: float = final_value
        """
        The final value of the progression.
        """
        self.rate_function = rate_function
        """
        The rate function to apply to the progression.
        """
        self._values: list[float] = None
        """
        The list of values calculated in a previous method call
        to avoid recalculating them. The amount of elements is
        the number of frames used in the previous calculation.
        """

    def get_values(
        self,
        number_of_frames: int
    ) -> list[any]:
        """
        Get the list of values for all the 'number_of_frames'
        frames of the video by using the 'rate_function' with
        the provided 'initial_value' and 'final_value' when
        instantiating this attribute set of values instance.

        The values will be calculated only when needed. If a
        previous set has been calculated and the parameter
        'number_of_frames' is the same, they won't be 
        recalculated but returned inmediately.
        """
        ParameterValidator.validate_mandatory_positive_int('number_of_frames', number_of_frames)

        # Maybe we have to be careful with the limits that
        # our Progression class is able to handle
        self._values = (
            [self.initial_value] * number_of_frames
            if self.is_single_value else
            # Recalculate values only if needed
            Progression(self.initial_value, self.final_value, number_of_frames, self.rate_function).values
            if (
                self._values is None or
                len(self._values) != number_of_frames
            ) else
            self._values
        )

        return self._values

    def copy(
        self
    ) -> 'VideoWrappedAttributeProgressionValue':
        """
        Get a copy of the instance.
        """
        return VideoWrappedAttributeProgressionValue(
            initial_value = self.initial_value,
            final_value = self.final_value,
            rate_function = self.rate_function
        )
    
class VideoWrappedAttributeGraphicValue(VideoWrappedAttributeValue):
    """
    Class to represent the set of values that a video
    attribute must have for each of the frames the
    video includes. This means that we can make a video
    change the parameters as we want by generating a
    graphic that modifies the sequence of values for
    each of all the video frames.

    This class can be used only for a video attribute
    modifier.
    """

    def __init__(
        self,
        graphic: 'Graphic'
    ):
        ParameterValidator.validate_mandatory_instance_of('graphic', graphic, 'Graphic')

        self._graphic: Graphic = graphic

    def get_values(
        self,
        number_of_frames: int
    ) -> list[any]:
        """
        Get the list of values for all the 'number_of_frames'
        frames of the video.
        """
        ParameterValidator.validate_mandatory_positive_int('number_of_frames', number_of_frames)

        return [
            self._graphic.get_xy_from_normalized_d(d)[1]
            for d in Progression(0, 1, number_of_frames).values
        ]
    
    def copy(
        self
    ) -> 'VideoWrappedAttributeGraphicValue':
        """
        Get a copy of the instance.
        """
        return VideoWrappedAttributeGraphicValue(
            graphic = self._graphic
        )
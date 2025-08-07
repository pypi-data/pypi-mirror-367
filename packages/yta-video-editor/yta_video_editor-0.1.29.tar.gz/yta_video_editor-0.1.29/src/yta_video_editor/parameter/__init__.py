"""
Module to contain all the different parameters
we can handle when working with a 'make_frame'
function related to moviepy.

- MakeFrameParameterSingleValue: A single value
(same for all the frames)
- MakeFrameParameterValues: An array of
'number_of_frames' precalculated values.
- MakeFrameParameterProgression: A dynamic
Progression with an easing function
- MakeFrameParameterGraphic: A custom Graphic
function

The ability of caching the values is because
we can calculate them and access to only one,
but later to another one, etc. So we don't
want to be calculated again (progression and
graphic).
"""
from yta_validation.parameter import ParameterValidator
from yta_general_utils.math.progression import Progression
from yta_general_utils.math.rate_functions.rate_function_argument import RateFunctionArgument
from yta_general_utils.math.graphic.graphic import Graphic
from abc import ABC, abstractmethod
from typing import Union


class MakeFrameParameter(ABC):
    """
    Abstract class to identify the different options
    (classes) we have to pass as a 'make_frame' 
    function parameter to build moviepy effects.
    """
    
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
    ) -> 'MakeFrameParameter':
        """
        Get a copy of the instance.
        """
        pass

class MakeFrameParameterSingleValue(MakeFrameParameter):
    """
    Class to provide a single value for a 'make_frame'
    function, that must be applied in all the video
    frames.

    You can do this `MakeFrameParameterSingleValue(3)`
    and the parameter will be used to calculate the
    values to be used when needed, based on the video
    number of frames (the video in which the parameter
    will be applied).
    """

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

        return [self._value] * number_of_frames
    
    def copy(
        self
    ) -> 'MakeFrameParameterSingleValue':
        """
        Get a copy of the instance.
        """
        return MakeFrameParameterSingleValue(self._value)
    
class MakeFrameParameterValues(MakeFrameParameter):
    """
    Class to represent a sequence of values that
    will be applied for each frame of the video.
    The amount of values must be the amount of
    frames or this will give an error.

    You can do this `MakeFrameParameterValues([3, 4, 7])`
    and the parameter will be used as it is when
    needed, based on the video number of frames
    (the video in which the parameter will be
    applied).

    (!) This is the most special, as the number
    of values that you provide must be equal to
    the number of frames in the video.
    """

    def __init__(
        self,
        values: list[Union[float, int]]
    ):
        ParameterValidator.validate_mandatory_list_of_numbers('values', values)

        self._values: list[Union[float, int]] = values

    def get_values(
        self,
        number_of_frames: int
    ) -> list[any]:
        """
        Get the list of values for all the 'number_of_frames'
        frames of the video.

        This method will raise an Exception if the amount of
        values provided is not the same as the 
        'number_of_frames'.
        """
        ParameterValidator.validate_mandatory_positive_int('number_of_frames', number_of_frames)

        if number_of_frames != len(self._values):
            raise Exception('The amount of "values" provided must be the same as the number of frames of the video.')
        
        return self._values
    
    def copy(
        self
    ) -> 'MakeFrameParameterValues':
        """
        Get a copy of the instance.
        """
        return MakeFrameParameterValues(
            values = self._values
        )

class MakeFrameParameterProgression(MakeFrameParameter):
    """
    Class to provide a progression that must be used
    to calculate the value for each of the video
    frames we are applying this to.

    This means that we can make a video go from 0
    contrast to 10 constrast increasing it smoothly
    (for example: 0, 2, 4, 6, 8 and 10) and not only
    abruptly (from 0 in one frame to 10 in the next
    one).
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
        ParameterValidator.validate_mandatory_number('initial_value', initial_value)
        ParameterValidator.validate_mandatory_number('final_value', final_value)
        ParameterValidator.validate_mandatory_instance_of('rate_function', rate_function, RateFunctionArgument)

        self.initial_value: float = float(initial_value)
        """
        The initial value of the progression.
        """
        self.final_value: float = float(final_value)
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
        # We have some problems when trying to apply rate
        # functions with the same initial and final value
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
    ) -> 'MakeFrameParameterProgression':
        """
        Get a copy of the instance.
        """
        return MakeFrameParameterProgression(
            initial_value = self.initial_value,
            final_value = self.final_value,
            rate_function = self.rate_function
        )
    
class MakeFrameParameterGraphic(MakeFrameParameter):
    """
    Class to generate a sequence of values to be 
    used for each frame of the video in which we
    are applying this.

    We create a custom Graphic function, that can
    be as we want, and the values are calculated
    to be applied.
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
    ) -> 'MakeFrameParameterGraphic':
        """
        Get a copy of the instance.
        """
        return MakeFrameParameterGraphic(
            graphic = self._graphic
        )

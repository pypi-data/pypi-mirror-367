"""
Module to wrap the functionality related to
basic video edition.
"""
from yta_video_editor.change.transform.color import ColorTemperatureTransform, ColorHueTransform, ColorBrightnessTransform, ColorContrastTransform, ColorSharpnessTransform, ColorWhiteBalanceTransform
from yta_video_editor.change import Changes
from yta_video_editor.change.resize.absolute import ResizeAbsoluteStatic
from yta_video_editor.change.rotation.absolute import RotationAbsoluteStatic
from yta_video_editor.change.position.offset import PositionOffsetStatic
from yta_video_editor.utils import put_video_over_black_background
from yta_validation.parameter import ParameterValidator
from moviepy import VideoClip
from typing import Union
from yta_video_editor.settings import ZOOM_LIMIT, VIDEO_MIN_POSITION, VIDEO_MAX_POSITION


class _Color:
    """
    Class to handle the color variations of a
    video when inside a VideoEditor instance.
    """

    def __init__(
        self,
        editor: 'VideoEditor'
    ):
        self.editor: VideoEditor = editor
        """
        The VideoEditor instance this _Color instance
        belongs to.
        """

    def temperature(
        self,
        factor: Union[int, list[int]] = 0
    ) -> 'VideoEditor':
        """
        Modify the video color temperature.
        
        Each time you call this method the video
        is modified, so calling it again will
        modified the modified version of it.

        Limits of the 'factor' attribute:
        - `[-50, 50]`
        """
        # TODO: Why are we accepting 'list[int]' (?)
        # TODO: Maybe accept single values or any
        # MakeFrameParameter instance as we accept in
        # the ColorXXXTransform instances...
        #self.editor._video = ColorTemperatureTransform(factor).apply(self.editor._video)
        self.editor._changes.add(ColorTemperatureTransform(factor))

        return self.editor
    
    def hue(
        self,
        factor: int = 0
    ) -> 'VideoEditor':
        """
        Modify the video color hue.
        
        Each time you call this method the video
        is modified, so calling it again will
        modified the modified version of it.

        Limits of the 'factor' attribute:
        - `[-50, 50]`
        """
        #self.editor._video = ColorHueTransform(factor).apply(self.editor._video)
        self.editor._changes.add(ColorHueTransform(factor))

        return self.editor
    
    def brightness(
        self,
        factor: int = 0
    ) -> 'VideoEditor':
        """
        Modify the video color brightness.
        
        Each time you call this method the video
        is modified, so calling it again will
        modified the modified version of it.

        Limits of the 'factor' attribute:
        - `[-100, 100]`
        """
        #self.editor._video = ColorBrightnessTransform(factor).apply(self.editor._video)
        self.editor._changes.add(ColorBrightnessTransform(factor))

        return self.editor
    
    def contrast(
        self,
        factor: int = 0
    ) -> 'VideoEditor':
        """
        Modify the video color contrast.
        
        Each time you call this method the video
        is modified, so calling it again will
        modified the modified version of it.

        Limits of the 'factor' attribute:
        - `[-100, 100]`
        """
        #self.editor._video = ColorContrastTransform(factor).apply(self.editor._video)
        self.editor._changes.add(ColorContrastTransform(factor))

        return self.editor

    def sharpness(
        self,
        factor: int = 0
    ) -> 'VideoEditor':
        """
        Modify the video color sharpness.
        
        Each time you call this method the video
        is modified, so calling it again will
        modified the modified version of it.

        Limits of the 'factor' attribute:
        - `[-100, 100]`
        """
        #self.editor._video = ColorSharpnessTransform(factor).apply(self.editor._video)
        self.editor._changes.add(ColorSharpnessTransform(factor))

        return self.editor

    def white_balance(
        self,
        factor: int = 0
    ) -> 'VideoEditor':
        """
        Modify the video color white balance.
        
        Each time you call this method the video
        is modified, so calling it again will
        modified the modified version of it.

        Limits of the 'factor' attribute:
        - `[-100, 100]`
        """
        #self.editor._video = ColorWhiteBalanceTransform(factor).apply(self.editor._video)
        self.editor._changes.add(ColorWhiteBalanceTransform(factor))

        return self.editor
    
# TODO: This single editor is used in the
# image library as a simple editor that is
# called from the image class instance...
# so maybe this should be very simple. It
# is also in the 'yta_image_base' library 
# and not in a different one
class VideoEditor:
    """
    Class to simplify and encapsulate all the
    functionality related to video edition.

    This VideoEditor works editing the video
    that has been providing when instantiating
    this class. All the changes you make will
    be chained.

    # TODO: I read that an interesting thing 
    is to store the operations you want to do
    in a list, and to perform all of them when
    needed. You can also revert the steps in
    that way. How can we do that? Also, if we
    want to apply zoom and then apply zoom
    again, that shouldn't be possible. We can
    add one zoom attribute that is the one we
    will apply, but not zoom x zoom.
    """

    @property
    def video(
        self
    ) -> VideoClip:
        """
        The moviepy video we are editing, with
        all the changes applied.
        """
        return self._video
    
    @property
    def copy(
        self
    ) -> VideoClip:
        """
        A copy of the video we are editing, with
        all the changes applied.
        """
        return self.video.copy()

    @property
    def color(
        self
    ):
        """
        The properties related to color we can change.
        """
        return self._color

    def __init__(
        self,
        video: VideoClip
    ):
        ParameterValidator.validate_mandatory_instance_of('video', video, VideoClip)

        self._original_video = video
        """
        The original video as it was loaded with
        no changes on it.
        """
        self._video = self._original_video.copy()
        """
        The moviepy video we are editing, with
        all the changes applied.
        """
        self._color: _Color = _Color(self)
        """
        The properties related to color we can change.
        """
        self._changes = Changes()
        """
        The internal changes to apply on the video.
        """

    def zoom(
        self,
        factor: int = 100
    ) -> 'VideoEditor':
        """
        Apply zoom on the video. A factor of 1 means x0.01 zoom,
        which is a zoom out. A factor of 200 means x2.00 zoom,
        which is a zoom in.
        """
        ParameterValidator.validate_mandatory_number_between('factor', factor, ZOOM_LIMIT[0], ZOOM_LIMIT[1])

        #self._video = Changes().add(ResizeAbsoluteStatic(self.video.duration, self.video.fps, factor)).apply(self.video)
        self._changes.add(ResizeAbsoluteStatic(self.video.duration, self.video.fps, factor))

        return self
    
    def move(
        self,
        x_variation: int = 0,
        y_variation: int = 0
    ) -> 'VideoEditor':
        """
        Apply a movement in the video, which means that it
        will be not centered if 'x_variation' and/or
        'y_variation' are different from zero.

        TODO: I don't like the 'move' method name
        """
        ParameterValidator.validate_mandatory_number_between('x_variation', x_variation, VIDEO_MIN_POSITION[0], VIDEO_MAX_POSITION[0])
        ParameterValidator.validate_mandatory_number_between('y_variation', y_variation, VIDEO_MIN_POSITION[1], VIDEO_MAX_POSITION[1])

        #self._video = Changes().add(PositionOffsetStatic(self.video.duration, self.video.fps, x_variation, y_variation)).apply(self.video)
        self._changes.add(PositionOffsetStatic(self.video.duration, self.video.fps, x_variation, y_variation))

        return self
    
    def rotate(
        self,
        factor: int = 0
    ) -> 'VideoEditor':
        """
        Apply a rotation in the video. A positive rotation
        will rotate it clockwise, and a negative one,
        anti-clockwise. A factor of 90 means rotating it 90
        degrees to the right (clockwise).
        """
        # We accept any factor and then we adapt it
        ParameterValidator.validate_mandatory_number('factor', factor)
        #ParameterValidator.validate_mandatory_number_between('factor', factor, ROTATION_LIMIT[0], ROTATION_LIMIT[1])

        #self._video = Changes().add(RotationAbsoluteStatic(self.video.duration, self.video.fps, int(factor % 360))).apply(self.video)
        self._changes.add(RotationAbsoluteStatic(self.video.duration, self.video.fps, int(factor % 360)))

        return self
    
    # TODO: Maybe these ones below could be with
    # the dynamic attribute format (single value,
    # array, etc.)
    def set_color_temperature(
        self,
        factor: int = 0
    ) -> 'VideoEditor':
        """
        Set the color temperature of the video.

        Limits of the 'factor' attribute:
        - `[-50, 50]`

        This is a shortcut of:
        - `VideoEditor(video).color.temperature(factor)`.
        """
        return self.color.temperature(factor)

    def set_color_hue(
        self,
        factor: int = 0
    ) -> 'VideoEditor':
        """
        Set the color hue of the video.

        Limits of the 'factor' attribute:
        - `[-50, 50]`

        This is a shortcut of:
        - `VideoEditor(video).color.hue(factor)`.
        """
        return self.color.hue(factor)
    
    def set_color_brightness(
        self,
        factor: int = 0
    ) -> 'VideoEditor':
        """
        Set the color brightness of the image.

        Limits of the 'factor' attribute:
        - `[-100, 100]`

        This is a shortcut of:
        - `VideoEditor(video).color.brightness(factor)`.
        """
        return self.color.brightness(factor)

    def set_color_contrast(
        self,
        factor: int = 0
    ) -> 'VideoEditor':
        """
        Set the color contrast of the video.

        Limits of the 'factor' attribute:
        - `[-100, 100]`

        This is a shortcut of:
        - `VideoEditor(video).color.contrast(factor)`.
        """
        return self.color.contrast(factor)

    def set_color_sharpness(
        self,
        factor: int = 0
    ) -> 'VideoEditor':
        """
        Set the color sharpness of the video.

        Limits of the 'factor' attribute:
        - `[-100, 100]`

        This is a shortcut of:
        - `VideoEditor(video).color.sharpness(factor)`.
        """
        return self.color.sharpness(factor)

    def set_color_white_balance(
        self,
        factor: int = 0
    ) -> 'VideoEditor':
        """
        Set the color white_balance of the video.

        Limits of the 'factor' attribute:
        - `[-100, 100]`

        This is a shortcut of:
        - `VideoEditor(video).color.white_balance(factor)`.
        """
        return self.color.white_balance(factor)
    
    # TODO: All inside this method has to be refactored
    # and moved, but I managed to make it work!
    def process_test(
        self,
        filename: str,
        do_quick: bool = True
    ) -> str:
        # TODO: Test processing the movements, rotation, etc
        # by different effects.

        # Subclip to test quick
        self._video = (
            self.video.with_subclip(0, 0.5)
            if do_quick else
            self.video
        )

        # Precalculate the 'ts' for all the changes
        from yta_video_editor.change import Changes
        from yta_video_editor.change.position.absolute import PositionAbsoluteFromAtoB
        from yta_video_editor.change.rotation.absolute import RotationAbsoluteSpinXTimes
        from yta_video_editor.change.resize.absolute import ResizeAbsoluteTest
        from yta_video_editor.parameter import MakeFrameParameterProgression

        changes = Changes()
        changes.add(PositionAbsoluteFromAtoB(self.video.duration, self.video.fps, (-100, -100), (1920 / 2, 1080 / 2)))
        changes.add(RotationAbsoluteSpinXTimes(self.video.duration, self.video.fps, 2))
        changes.add(ResizeAbsoluteTest(self.video.duration, self.video.fps))
        changes.add(ColorBrightnessTransform(MakeFrameParameterProgression(-50, 50)))
        changes.add(ColorTemperatureTransform(MakeFrameParameterProgression(-50, 50)))

        self._video = changes.apply(self.video)

        # TODO: Check this:
        # If I set the position but I don't use a 
        # black background, the position is set but
        # the scene doesn't change because there is
        # only one single video, so I think using
        # this black background should be just the
        # last step for the final compound sum of
        # video layers just in case, but not here
        self.save_as(filename)

        return filename
    
    def _apply_changes(
        self
    ):
        if self._changes.has_changes:
            self._video = self._changes.apply(self.video)
            # We empty it because we already applied those
            # changes and don't want them applied again
            # TODO: We need to check if this is a good
            # strategy or not
            self._changes = Changes()

    def save_as(
        self,
        filename: str
    ) -> str:
        """
        Save the video with all the modifications to
        the provided 'filename'.
        """
        ParameterValidator.validate_mandatory_string('filename', filename, do_accept_empty = False)

        # We apply the changes we have to
        self._apply_changes()

        self.video.write_videofile(filename)

        return filename


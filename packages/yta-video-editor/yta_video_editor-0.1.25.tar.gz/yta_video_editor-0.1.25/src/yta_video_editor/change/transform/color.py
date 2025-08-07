from yta_video_editor.settings import COLOR_TEMPERATURE_LIMIT, COLOR_HUE_LIMIT, BRIGHTNESS_LIMIT, CONTRAST_LIMIT, SHARPNESS_LIMIT, WHITE_BALANCE_LIMIT
from yta_video_editor.change.transform import _Transform
from yta_image_base.editor import ImageEditor


class ColorTemperatureTransform(_Transform):
    """
    Transform the color temperature of each frame
    of a video.

    Accepted parameters between:
    - `[-50, 50]`
    """

    @property
    def limit(
        self
    ) -> tuple[float, float]:
        """
        The limit in between all the values to apply
        when transforming have to fit.
        """
        return COLOR_TEMPERATURE_LIMIT

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
        return ImageEditor(frame).color.temperature(value).image
    
class ColorHueTransform(_Transform):
    """
    Transform the color hue of each frame of a
    video.

    Accepted parameters between:
    - `[-50, 50]`
    """

    @property
    def limit(
        self
    ) -> tuple[float, float]:
        """
        The limit in between all the values to apply
        when transforming have to fit.
        """
        return COLOR_HUE_LIMIT

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
        return ImageEditor(frame).color.hue(value).image
    
class ColorBrightnessTransform(_Transform):
    """
    Transform the color brightness of each frame
    of a video.

    Accepted parameters between:
    - `[-100, 100]`
    """

    @property
    def limit(
        self
    ) -> tuple[float, float]:
        """
        The limit in between all the values to apply
        when transforming have to fit.
        """
        return BRIGHTNESS_LIMIT

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
        return ImageEditor(frame).color.brightness(value).image
    
class ColorContrastTransform(_Transform):
    """
    Transform the color contrast of each frame
    of a video. 

    Accepted parameters between:
    - `[-100, 100]`
    """

    @property
    def limit(
        self
    ) -> tuple[float, float]:
        """
        The limit in between all the values to apply
        when transforming have to fit.
        """
        return CONTRAST_LIMIT

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
        return ImageEditor(frame).color.contrast(value).image
    
class ColorSharpnessTransform(_Transform):
    """
    Transform the color sharpness of each
    frame of a video.
    
    Accepted parameters between:
    - `[-100, 100]`
    """

    @property
    def limit(
        self
    ) -> tuple[float, float]:
        """
        The limit in between all the values to apply
        when transforming have to fit.
        """
        return SHARPNESS_LIMIT

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
        return ImageEditor(frame).color.sharpness(value).image
    
class ColorWhiteBalanceTransform(_Transform):
    """
    Transform the color white balance of
    each frame of a video. 

    Accepted parameters between:
    - `[-100, 100]`
    """

    @property
    def limit(
        self
    ) -> tuple[float, float]:
        """
        The limit in between all the values to apply
        when transforming have to fit.
        """
        return WHITE_BALANCE_LIMIT

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
        return ImageEditor(frame).color.white_balance(value).image
from yta_constants.video import VideoCombinatorAudioMode
from yta_video_moviepy.generator import MoviepyNormalClipGenerator
from yta_video_utils.combination import VideoAudioCombinator
from moviepy import VideoClip, CompositeVideoClip


def _overlay_video(
    background_video: VideoClip,
    video: VideoClip,
    position: tuple = ('center', 'center'),
    audio_mode: VideoCombinatorAudioMode = VideoCombinatorAudioMode.BOTH_CLIPS_AUDIO
):
    """
    Overlay the provided 'video' on top of the also given
    'background_video'.
    """
    return CompositeVideoClip([
        background_video,
        video.with_position(position)
    ]).with_audio(VideoAudioCombinator(audio_mode).process_audio(background_video, video))

def put_video_over_black_background(
    video: VideoClip,
    position: tuple = ('center', 'center'),
    audio_mode: VideoCombinatorAudioMode = VideoCombinatorAudioMode.BOTH_CLIPS_AUDIO
) -> VideoClip:
    """
    Put the 'video' provided over a black background.

    We apply a black background to ensure the video size
    is the expected one and we dont have problems with
    movement.
    """
    black_background = MoviepyNormalClipGenerator.get_static_default_color_background(
        duration = video.duration,
        fps = video.fps
    )

    return _overlay_video(
        background_video = black_background,
        video = video,
        position = position,
        audio_mode = audio_mode
    )

# As the rotation changes the frame size, we need
# to recalculate the resize factors
def get_rotated_image_size(
    size: tuple[int, int],
    angle: int
):
    """
    Get the size of an image of the given 'size' when it
    is rotated the also given 'angle'.

    This method is based on the moviepy Rotate effect to
    pre-calculate the frame rotation new size so we are
    able to apply that resize factor to the other 
    attributes.

    This method returns the new size and also the width
    size change factor and the height size change factor.
    """
    from PIL import Image

    new_size = Image.new('RGB', size, (0, 0, 0)).rotate(
        angle,
        expand = True,
        resample = Image.Resampling.BILINEAR
    ).size

    width_factor = new_size[0] / size[0]
    height_factor = new_size[1] / size[1]

    return new_size, width_factor, height_factor


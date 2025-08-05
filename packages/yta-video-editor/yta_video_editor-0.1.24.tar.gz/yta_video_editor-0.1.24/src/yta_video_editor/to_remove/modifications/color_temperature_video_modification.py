"""
TODO: This has been commented because I don't
know if it will be definitive or not...
"""
# from yta_video_editor.modifications.video_modification import VideoModification
# # TODO: VideEditor will not be here in
# # 'yta_video_base' library
# from yta_video_base.video_editor import VideoEditor
# from moviepy.Clip import Clip


# class ColorTemperatureVideoModification(VideoModification):
#     """
#     A modification that changes the video
#     color temperature.
#     """

#     factor: int = None
    
#     def __init__(
#         self,
#         start_time: float,
#         end_time: float,
#         layer: int,
#         factor: int = 45
#     ):
#         super().__init__(start_time, end_time, layer)
        
#         # TODO: Validate that 'factor' is actually between
#         # the limits
#         self.factor = factor

#     def _modificate(
#         self,
#         video: Clip
#     ) -> Clip:
#         # TODO: What do I do with the VideoEditor (?)
#         return VideoEditor(video).change_color_temperature(self.factor)
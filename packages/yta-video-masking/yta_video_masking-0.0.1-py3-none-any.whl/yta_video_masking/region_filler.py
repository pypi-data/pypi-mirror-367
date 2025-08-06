from yta_video_utils.duration import set_video_duration
from yta_video_utils.resize import resize_video
from yta_constants.video import ExtendVideoMode, EnshortVideoMode
from yta_image_base.parser import ImageParser
from yta_validation.parameter import ParameterValidator
from yta_validation import PythonValidator
from yta_positioning.region import Region
from moviepy import ImageClip, CompositeVideoClip, VideoClip


# TODO: It would be interesting that the ImageGreenscreen,
# VideoGreenscreen, ImageAlphascreen and VideoAlphascreen
# inherit from this one instead of having an instance and
# using it, but I decided to start like this because of
# the inheritance problems I've experienced in the past 
# that delayed me too much.
class RegionFiller:
    """
    Class created to encapsulate the way we handle regions with
    transparency in moviepy clips and to add other multimedia
    elements behind those regions to be seen through a new 
    CompositedVideoClip.

    This class is intended to be used by the Alphascreen and
    Greenscreen classes that are generating this kind of videos
    with alpha or green regions on the source files.
    """

    @property
    def number_of_regions(
        self
    ) -> int:
        """
        The number of regions we have.
        """
        return len(self.regions)

    def __init__(
        self,
        regions: list[Region],
        masked_clip: VideoClip
    ):
        self.regions: list[Region] = regions
        """
        The regions existing in the masked_clip
        """
        self.masked_clip: VideoClip = masked_clip
        """
        The masked clip we want to use to put some multimedia
        elements behind it with the transparency applied to
        let them be seen through the existing regions. This
        videoclip must have a mask with some transparency to
        allow putting elements behind that are seeing through
        that alpha channel.
        """

    def images_to_image(
        self,
        images: list[any]
    ) -> 'np.ndarray':
        """
        Insert the provided 'images' in the first frame of the
        masked clip, and return the whole new image as a numpy
        array.
        
        This method need to have as many 'images' as the number
        of regions we have to fill. If one single image is
        provided as 'images' parameter, it will be repeated as
        many times as regions we have.
        """
        images = (
            [images] * self.regions
            if not PythonValidator.is_list(images) else
            images
        )

        self._validate_enough_elements_for_regions(images)
        
        # TODO: This is not returning RGBA only RGB. You can use
        # the 'rgba' method from VideoFrameExtractor
        return self.images_to_video(images, duration = 1 / 60).get_frame(t = 0)
    
    def images_to_video(
        self,
        images: list[any],
        duration: float
    ) -> CompositeVideoClip:
        """
        Insert the provided 'images' in the masked clip, and
        return the new video with the 'images' inside the 
        regions of the video, being seen through the alpha
        channel.
        
        This method need to have as many 'images' as the number
        of regions we have to fill. If one single image is
        provided as 'images' parameter, it will be repeated as
        many times as regions we have.
        """
        images = (
            [images] * self.regions
            if not PythonValidator.is_list(images) else
            images
        )

        self._validate_enough_elements_for_regions(images)

        ParameterValidator.validate_mandatory_positive_number('duration', duration, do_include_zero = False)

        # TODO: Use the 'transparent' parameter (?)
        videos = [
            ImageClip(ImageParser.to_numpy(image), duration = duration).with_fps(60)
            for image in images
        ]

        return self.videos_to_video(videos)

    def videos_to_video(
        self,
        videos: list[VideoClip]
    ) -> CompositeVideoClip:
        """
        Insert the provided 'videos' in the masked clip, and
        return the new video with the 'videos' inside the 
        regions of the video, being seen through the alpha
        channel.
        
        This method need to have as many 'videos' as the number
        of regions we have to fill. If one single video is
        provided as 'videos' parameter, it will be repeated as
        many times as regions we have.

        This method is pretend to be used by the Alphascreen or
        Greenscreen classes to simplify the process and code.
        """
        videos = (
            [videos] * self.regions
            if not PythonValidator.is_list(videos) else
            videos
        )

        ParameterValidator.validate_list_of_these_instances('videos', videos, VideoClip)

        self._validate_enough_elements_for_regions(videos)

        longest_duration = max(videos, key = lambda video: video.duration).duration

        # Place the video inside the region
        for index, video in enumerate(videos):
            videos[index] = place_video_inside_region(video, self.regions[index])

        # TODO: What if video is not as longer as 'longest_duration' (?)
        masked_clip = self.masked_clip.with_duration(longest_duration)

        return self._build_composite_clip(videos, masked_clip)


    def _validate_enough_elements_for_regions(
        self,
        elements
    ):
        """
        Raises an exception if the provided amount of 'elements' is 
        greater or less than the amount of alpha regions.
        """
        if len(elements) != len(self.regions):
            raise Exception(f'There are more or less elements provided ({str(len(elements))}) than available masked regions ({str(len(self.regions))}).')

    def _build_composite_clip(
        self,
        videos: list[VideoClip],
        masked_clip: VideoClip
    ) -> CompositeVideoClip:
        """
        Builds the CompositeVideoClip that includes the provided 'videos'
        and the also provided 'alpha_clip' to build the desired video with
        alpha regions filled with the videos.
        """
        # TODO: Please private method
        # As this is for internal use I consider that 'videos' and
        # 'alpha_clip' are valid ones and ready to be used at this point

        # TODO: Provided videos can be shorther than the alphascreen
        # or the alphascreen can be shorter than the videos, so we
        # need an strategy to follow. By now I'm forcing all the 
        # videos to fit the alphascreen duration by shortening or
        # enlarging them.
        for index, _ in enumerate(videos):
            videos[index] = set_video_duration(videos[index], masked_clip.duration, ExtendVideoMode.FREEZE_LAST_FRAME, EnshortVideoMode.CROP)

        composite_clip = CompositeVideoClip([
            *videos,
            masked_clip
        ], size = masked_clip.size)

        return (
            composite_clip.with_fps(60)
            if not composite_clip.fps else
            composite_clip
        )

def place_video_inside_region(
    video: VideoClip,
    region: Region
):
    """
    Resize and place the provided 'video' in the
    position that fits the given 'region'.
    """
    #video = VideoParser.to_moviepy(video)

    # Resize
    video = resize_video(video, region.size_to_fit)
    # Position
    x = region.center[0] - video.w / 2
    y = region.center[1] - video.h / 2

    # TODO: What about upper limits (out of bottom left bounds) (?)
    x = (
        0
        if x < 0 else
        x
    )
    y = (
        0
        if y < 0 else
        y
    )

    return video.with_position((x, y))
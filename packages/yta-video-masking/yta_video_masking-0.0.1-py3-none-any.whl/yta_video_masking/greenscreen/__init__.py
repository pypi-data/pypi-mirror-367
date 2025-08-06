from yta_video_masking.region_filler import RegionFiller
from yta_image_masking.greenscreen.utils import get_greenscreen_areas_from_image, Image
from yta_constants.masking import GreenscreenType
from yta_validation.parameter import ParameterValidator
from moviepy.video.fx import MaskColor
from moviepy import ImageClip, VideoClip, CompositeVideoClip, VideoFileClip
from typing import Union


class GreenscreenToFill:
    """
    Class to implement a greenscreen image or
    video, that includes green regions, to insert
    images or videos in those regions.
    """

    @property
    def is_image(
        self
    ) -> bool:
        """
        Flag to indicate if it is an image greenscreen.
        """
        return self.type == GreenscreenType.IMAGE
    
    @property
    def number_of_regions(
        self
    ) -> int:
        """
        Get the number of autodetected regions.
        """
        return len(self.greenscreen_areas)

    def __init__(
        self,
        image_or_video: Union[str, 'np.ndarray', Image.Image, VideoClip],
        # Maybe this can be optional
        #greenscreen: Union[GreenscreenDetails, str],
        type: GreenscreenType = GreenscreenType.IMAGE
    ):
        # TODO: Maybe autodetect if video or image (?)
        type = GreenscreenType.to_enum(type)

        ParameterValidator.validate_mandatory_instance_of('image_or_video', image_or_video, [str, 'np.ndarray', Image.Image, VideoClip])

        image = (
            image_or_video.get_frame(t = 0)
            if type == GreenscreenType.VIDEO else
            image_or_video
        )

        # TODO: Check because we have the
        # 'ImageRegionFinder.find_green_regions' method
        self.greenscreen_areas = get_greenscreen_areas_from_image(image)
        """
        The information about the greenscreen areas.
        """
        self.type = type
        """
        The type of the greenscreen.
        """

        # I consider the same greenscreen rgb color for all areas
        # Duration will be set at the end
        greenscreen_clip = (
            ImageClip(image, duration = 1 / 60)
            if type == GreenscreenType.IMAGE else
            VideoFileClip(image)
        ).with_effects([
            MaskColor(
                color = self.greenscreen_areas[0].rgb_color,
                threshold = 100,
                stiffness = 5
            )
        ])
        # This above will transform the green pixels in
        # transparent alpha pixels as a mask
        
        regions = [
            gsa.region
            for gsa in self.greenscreen_areas
        ]

        self.region_filler = RegionFiller(regions, greenscreen_clip)
        """
        Instance to easily fill the regions with the images
        or videos we want.
        """

    def images_to_image(
        self,
        images: Union[any, list[any]]
    ) -> 'np.ndarray':
        """
        Put the provided 'images' in the greenscreen areas
        that this instance has and return the new image.
        """
        # TODO: This is not returning RGBA only RGB
        return self.region_filler.images_to_image(images)
    
    def images_to_video(
        self,
        images: Union[any, list[any]],
        duration: float
    ) -> CompositeVideoClip:
        """
        Put the provided 'images' in the greenscreen areas
        that this instance has, and return it as a new video
        with the given 'duration'.
        """
        return self.region_filler.images_to_video(images, duration)

    def videos_to_video(
        self,
        videos: Union[VideoClip, list[VideoClip]]
    ) -> CompositeVideoClip:
        """
        Put the provided 'videos' in the greenscreen areas
        that this instance has, and return it as a new video.
        """
        return self.region_filler.videos_to_video(videos)
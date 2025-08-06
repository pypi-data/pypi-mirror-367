from yta_video_masking.region_filler import RegionFiller
from yta_constants.masking import AlphascreenType
from yta_image_base.region.finder import ImageRegionFinder
from yta_video_moviepy.frame.extractor import MoviepyVideoFrameExtractor
from yta_validation.parameter import ParameterValidator
from moviepy import ImageClip, VideoClip, CompositeVideoClip
from typing import Union


class AlphascreenToFill:
    """
    Class to implement an alphascreen image or
    video, that includes alpha regions, to insert
    images or videos in those regions.
    """

    @property
    def is_image(
        self
    ) -> bool:
        """
        Flag to indicate if it is an image alphascreen.
        """
        return self.type == AlphascreenType.IMAGE
    
    @property
    def number_of_regions(
        self
    ) -> int:
        """
        Get the number of autodetected regions.
        """
        return len(self.regions)
    
    def __init__(
        self,
        image_or_video: Union[str, 'np.ndarray', 'Image.Image', VideoClip],
        type: AlphascreenType = AlphascreenType.IMAGE
    ):
        """
        If a video provided, it must include the mask
        to be able to detect the transparency to put
        the images or videos inside.
        """
        type = AlphascreenType.to_enum(type)

        ParameterValidator.validate_mandatory_instance_of('image_or_video', image_or_video, [str, 'ndarray', 'Image', VideoClip])
        ParameterValidator.validate_mandatory_numpy_array()
        
        self.regions = ImageRegionFinder.find_transparent_regions(
            image = (
                MoviepyVideoFrameExtractor.get_frame_as_rgba_by_t(image_or_video, 0)
                if type == AlphascreenType.VIDEO else
                image_or_video
            )
        )
        """
        The information about the alpha regions that
        exist in the provided image or in the first
        frame of the video.
        """
        self.type = type
        """
        The type of the alphascreen.
        """

        if self.number_of_regions == 0:
            raise Exception(f'No alpha regions found in the provided video or image provided.')
        
        # TODO: What about regions that are just one pixel or too short (?)

        # Duration will be processed and updated in the last step
        alpha_clip = (
            ImageClip(image_or_video, duration = 1 / 60, transparent = True)
            if type == AlphascreenType.IMAGE else
            # TODO: This video must have a mask
            image_or_video
        )
        self.region_filler = RegionFiller(self.regions, alpha_clip)
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
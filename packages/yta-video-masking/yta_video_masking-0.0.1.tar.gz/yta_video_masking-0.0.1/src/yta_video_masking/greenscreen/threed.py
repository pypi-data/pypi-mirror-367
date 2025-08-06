"""
TODO: This module is experimental... Be careful.

This is a class to keep the code that allows me to
insert an image into another image that contains
a greenscreen region but that is not rectangular,
so we need to make some transformations to fit the
expected region and position.

TODO: Please, this is not fine at all and need 
review, work and love
"""
from yta_image_base.converter import ImageConverter
from yta_image_masking.greenscreen.threed import insert_image_into_3d_greenscreen
from moviepy.Clip import Clip
from moviepy import ImageClip, concatenate_videoclips


def insert_video_into_3d_greenscreen(greenscreen_filename: str, video: Clip, output_filename: str):
    """
    Inserts the provided 'video' into the also provided 3d 
    greenscreen in the file 'greenscreen_filename'. This 
    method will write the file as 'output_filename' if this
    is provided, and will return the new video anyways.
    """
    # We create each image by inserting each frame and then 
    # concatenate all of them to make a new video
    imageclips = [
        ImageClip(insert_image_into_3d_greenscreen(greenscreen_filename, ImageConverter.numpy_image_to_opencv(frame), 'a.png'), duration = 1 / video.fps).with_fps(video.fps) 
        for frame in video.iter_frames()
    ]

    video = concatenate_videoclips(imageclips)

    if (output_filename):
        video.write_videofile(output_filename)

    return video
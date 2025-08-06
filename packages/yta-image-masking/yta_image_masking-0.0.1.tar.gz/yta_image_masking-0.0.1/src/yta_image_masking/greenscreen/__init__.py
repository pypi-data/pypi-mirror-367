# TODO: Remove this when new greenscreen system has been
# completely implemented and this file doesn't make sense
from yta_image_masking.greenscreen.utils import generate_greenscreen
from yta_constants.multimedia import DEFAULT_SCENE_SIZE
from yta_temp import Temp
from yta_colors.converter import ColorConverter
from PIL import Image, ImageDraw, ImageFont
from random import choice as random_choice
from moviepy import VideoFileClip, ImageClip, CompositeVideoClip
from moviepy.video.fx import MaskColor

import os


# TODO: This has to be refactored to be dynamically built
# and to obtain the files from Google Drive, that must be
# also registered in somewhere to include details like the
# size, the number of green screens and their positions, 
# etc.
#
# We will need to refactor it again to handle different
# texts (not only one) and more elements that could be
# applied while whe develop the app an this greenscreen
# functionality.
class GreenScreenImage:
    """
    Green screen of custom size that is
    placed over a background image of
    1920x1080. It can include a text that
    is placed in the bottom side of the
    green screen.
    """

    __GREEN_SCREEN_RGB_COLOR = (0, 249, 12)
    # TODO: Move this to .env
    __FONTS_PATH = 'C:/USERS/DANIA/APPDATA/LOCAL/MICROSOFT/WINDOWS/FONTS/'

    def __init__(
        self,
        width = 1344,
        height = 756
    ):
        # TODO: What is this size for (?)
        if width <= 0 or width > DEFAULT_SCENE_SIZE[0] or height <= 0 or height > DEFAULT_SCENE_SIZE[1]:
            # TODO: Handle this exception
            print('Green screen size error, setting to default (1344x756).')
            width = 1344
            height = 756

        self.width = width
        self.height = height

    def save(
        self,
        output_filename: str
    ):
        # We use a random 1920x1080 background image
        # We insert the green_screen in the base_image
        base = Image.open(self.background_filename)
        green_screen = generate_greenscreen(self.width, self.height)

        # Dynamically get x,y start to put the green screen in the base image center
        base.paste(green_screen, (self.x, self.y))

        PADDING = 15

        base.save(output_filename, quality = 100)
    
    def insert_video(self, video_filename, output_filename):
        tmp_filename = Temp.get_wip_filename('tmp_gs.png')
        self.save(tmp_filename)

        clip = VideoFileClip(video_filename)
        green_screen_clip = ImageClip(tmp_filename, duration = clip.duration).with_effects([MaskColor(color = self.rgb_color, threshold = 100, stiffness = 5)])

        width = self.drx - self.ulx
        clip = clip.resized(width = width).with_position((self.ulx, self.uly))

        final_clip = CompositeVideoClip([clip, green_screen_clip], size = green_screen_clip.size)

        final_clip.write_videofile(output_filename, fps = clip.fps)

    def insert_image(self, image_filename, output_filename):
        # I do the trick with moviepy that is working for videos...
        tmp_filename = Temp.get_wip_filename('tmp_gs.png')
        self.save(tmp_filename)

        width = self.drx - self.ulx

        clip = ImageClip(image_filename, duration = 1 / 60).resized(width = width).with_position((self.ulx, self.uly))
        green_screen_clip = ImageClip(tmp_filename, duration = clip.duration).with_effects([MaskColor(color = self.rgb_color, threshold = 100, stiffness = 5)])

        final_clip = CompositeVideoClip([clip, green_screen_clip], size = green_screen_clip.size)
        final_clip.save_frame(output_filename, t = 0)

        # https://medium.com/@gowtham180502/how-can-we-replace-the-green-screen-background-using-python-4947f1575b1f
        """
        # https://www.geeksforgeeks.org/replace-green-screen-using-opencv-python/
        # TODO: Please, implement with this below, but by now (above)
        image = cv2.imread(self.__filename) 
        frame = cv2.imread(output_filename)
    
        width = self.drx - self.ulx
        height = self.dry - self.uly
        frame = resize_image(resize_image, width, height)

        u_green = np.array([104, 153, 70]) 
        l_green = np.array([30, 30, 0]) 
    
        mask = cv2.inRange(frame, l_green, u_green) 
        res = cv2.bitwise_and(frame, frame, mask = mask) 
    
        f = frame - res 
        f = np.where(f == 0, image, f) 
    
        cv2.imshow("video", frame) 
        cv2.imshow("mask", f) 
        """
    

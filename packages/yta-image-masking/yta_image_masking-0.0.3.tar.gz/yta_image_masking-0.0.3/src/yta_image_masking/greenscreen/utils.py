from yta_image_masking.greenscreen.dataclasses import GreenscreenAreaDetails
from yta_constants.masking import GREENSCREEN_RGB_COLOR
from yta_colors.converter import ColorConverter
from yta_image_base.converter import ImageConverter
from yta_image_base.color.picker import ColorPicker
from yta_image_base.parser import ImageParser
from yta_image_base.region.finder import ImageRegionFinder
from PIL import Image, ImageDraw
from typing import Union


def generate_greenscreen_rectangle(
    size: tuple[int, int]
) -> Image.Image:
    """
    Create a greenscreen rectangle of the provided
    'size' with also a black rectangle surrounding
    it, as a border.
    """
    shape = [(10, 10), (size[0] - 10, size[1] - 10)] 
    
    img = Image.new('RGB', size) 
    draw = ImageDraw.Draw(img)   
    r, g, b = GREENSCREEN_RGB_COLOR
    draw.rectangle(shape, fill = ColorConverter.rgb_to_hex(r, g, b) , outline = 'black')

    return img

def get_greenscreen_areas_from_image(
    image: Union[str, 'np.ndarray', Image.Image]
) -> list[GreenscreenAreaDetails]:
    """
    Detect the different areas that are greenscreen
    areas within the provided 'image'. A greenscreen
    area is a very noticeable and rectangle-shaped
    green region.
    """
    image = ImageParser.to_pillow(image)
    
    green_rgb_color, similar_greens = ColorPicker.get_most_common_green_rgb_color_and_similars(image)
    regions = ImageRegionFinder.find_green_regions(ImageConverter.pil_image_to_numpy(image))

    return [
        GreenscreenAreaDetails(
            rgb_color = green_rgb_color,
            similar_greens = similar_greens,
            upper_left_pixel = region.top_left,
            lower_right_pixel = region.bottom_right,
        ) for region in regions
    ]
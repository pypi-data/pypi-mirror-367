from yta_image_masking.greenscreen.dataclasses import GreenscreenAreaDetails, GreenscreenDetails
from yta_constants.masking import GreenscreenType, GREENSCREEN_RGB_COLOR
from yta_colors.converter import ColorConverter
from yta_image_base.converter import ImageConverter
from yta_image_base.color.picker import ColorPicker
from yta_image_base.parser import ImageParser
from yta_image_base.region.finder import ImageRegionFinder
from yta_google_drive_downloader.resource import Resource
from yta_validation.parameter import ParameterValidator
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
    image: Union[str, any]
) -> list[GreenscreenAreaDetails]:
    """
    Detect the different areas that are greenscreen
    areas within the provided 'image'. A greenscreen
    area is a very noticeable and rectangle-shaped
    green region.
    """
    # Sometimes it comes from a moviepy clip turned into np
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

def get_greenscreen_details_from_image(
    greenscreen_filename_or_google_drive_url: str,
) -> GreenscreenDetails:
    """
    Get the greenscreen area and details of the
    given parameter automatically.
    """
    # TODO: The resource must be an image...
    ParameterValidator.validate_mandatory_string('greenscreen_filename_or_google_drive_url', greenscreen_filename_or_google_drive_url, do_accept_empty = False)
    
    resource = Resource(greenscreen_filename_or_google_drive_url)

    # We will need the resource filename or google drive url and
    # the image to extract the data from
    greenscreen_area_details = get_greenscreen_areas_from_image(resource.file)

    if len(greenscreen_area_details) == 0:
        raise Exception('No greenscreen detected automatically in "' + greenscreen_filename_or_google_drive_url + '". Aborting.')

    return GreenscreenDetails(
        greenscreen_areas = greenscreen_area_details,
        filename_or_google_drive_url = greenscreen_filename_or_google_drive_url,
        type = GreenscreenType.IMAGE
    )
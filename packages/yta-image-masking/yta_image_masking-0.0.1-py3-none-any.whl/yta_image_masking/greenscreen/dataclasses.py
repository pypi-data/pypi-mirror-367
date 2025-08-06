from yta_constants.masking import GreenscreenType
from yta_positioning.region import Region
from yta_positioning.coordinate import Coordinate
from yta_validation.parameter import ParameterValidator
from typing import Union
from dataclasses import dataclass


@dataclass
class GreenscreenAreaDetails:
    """
    The information about one area within a greenscreen
    image, including the green color, the other similar
    greens, and the region.
    """
    region: Region = None
    upper_left_pixel: Coordinate = None
    lower_right_pixel: Coordinate = None
    frames = None

    def __init__(
        self,
        rgb_color: tuple[int, int, int] = (0, 0, 255),
        similar_greens = [],
        upper_left_pixel: Coordinate = Coordinate((0, 0)),
        lower_right_pixel: Coordinate = Coordinate((0, 0)),
        frames: Union[tuple[int, int], None] = None
    ):
        # TODO: Implement checkings please
        self.rgb_color: tuple[int, int, int] = rgb_color
        """
        The RGB color that is the green color in the
        greenscreen.
        """
        self.similar_greens: list[tuple[int, int, int]] = similar_greens
        """
        The other green colors that are similar to the
        main green color.
        """
        self.upper_left_pixel: Coordinate = upper_left_pixel
        """
        The pixel position in which the upper left
        corner of the greenscreen area is.
        """
        self.lower_right_pixel: Coordinate = lower_right_pixel
        """
        The pixel position in which the lower right
        corner of the greenscreen area is.
        """
        self.region: Region = Region(
            self.upper_left_pixel.x,
            self.upper_left_pixel.y,
            self.lower_right_pixel.x,
            self.lower_right_pixel.y
        )
        """
        The region in which the area was found, as
        a rectangle including the bigger limits found.
        """
        self.frames = frames
        """
        The frames in which it is being shown, as
        (start, end).

        TODO: This is not useful like this...
        """

@dataclass
class GreenscreenDetails:
    """
    The information about a greenscreen, that can
    be an image or a video. The areas that are in
    the resource, etc.
    """
    greenscreen_areas = []
    filename_or_google_drive_url = None
    type = None

    @property
    def filename(
        self
    ) -> str:
        from yta_google_drive_downloader.resource import Resource
        # TODO: By now I want to simplify it, recover this
        # way of handling Google Drive resources in the
        # future...
        # TODO: Change this behaviour and be more strict
        # and make more fields if needed, please
        output_filename = (
            'greenscreen.png'
            if self.type == GreenscreenType.IMAGE else
            'greenscreen.mp4'
        )

        resource = Resource(
            filename_or_google_drive_url = self.filename_or_google_drive_url,
            output_filename = output_filename
        )

        return resource.file

    def __init__(
        self,
        greenscreen_areas: list[GreenscreenAreaDetails] = [],
        filename_or_google_drive_url: str = None,
        type: GreenscreenType = GreenscreenType.IMAGE
    ):
        # TODO: Implement checkings please
        ParameterValidator.validate_mandatory_list_of_these_instances('greenscreen_areas', greenscreen_areas, GreenscreenAreaDetails)
        type = GreenscreenType.to_enum(type)

        self.greenscreen_areas: list[GreenscreenAreaDetails] = greenscreen_areas
        self.filename_or_google_drive_url: str = filename_or_google_drive_url
        self.type: GreenscreenType = type
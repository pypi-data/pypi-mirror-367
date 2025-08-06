from yta_positioning.region import Region
from yta_positioning.coordinate import Coordinate
from typing import Union
from dataclasses import dataclass


@dataclass
class GreenscreenAreaDetails:
    """
    The information about one area within a greenscreen
    image, including the green color, the other similar
    greens, and the region.
    """

    def __init__(
        self,
        rgb_color: tuple[int, int, int] = (0, 0, 255),
        similar_greens: list[tuple[int, int, int]] = [],
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
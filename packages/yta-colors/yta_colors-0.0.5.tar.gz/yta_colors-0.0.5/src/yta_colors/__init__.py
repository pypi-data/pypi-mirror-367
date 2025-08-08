from yta_colors.converter import ColorConverter
from yta_colors.utils import parse_color
from yta_validation import PythonValidator
from yta_validation.parameter import ParameterValidator
from typing import Union
from dataclasses import dataclass


class Color:
    """
    Class that represents a color, stored as RGBA, makes
    easy the way we interact with color and provide them as
    parameters and simplify the color conversion. The color
    is stored as a not-normalized color, but values can be
    normalized through the methods that allow it (those 
    including the 'normalized' bool parameter).

    Any attribute has to be initialized with a value between
    0 and 255. Alpha as 255 means full opaque.

    TODO: Please confirm alpha 255 is opaque.
    """

    def __init__(
        self,
        red: int,
        green: int,
        blue: int,
        alpha: int = 255
    ):
        ParameterValidator.validate_mandatory_number_between('red', red, 0, 255)
        ParameterValidator.validate_mandatory_number_between('green', green, 0, 255)
        ParameterValidator.validate_mandatory_number_between('blue', blue, 0, 255)
        ParameterValidator.validate_mandatory_number_between('alpha', alpha, 0, 255)

        self.r: int = red
        """
        Red color, from 0 to 255, where 0 is no value and 255
        is everything.
        """
        self.g: int = green
        """
        Green color, from 0 to 255, where 0 is no value and 255
        is everything.
        """
        self.b: int = blue
        """
        Blue color, from 0 to 255, where 0 is no value and 255
        is everything.
        """
        self.a: int = alpha
        """
        Alpha (transparency), from 0 to 255, where 0 is no
        value and 255 is everything.
        """

    @property
    def rgb_not_normalized(
        self
    ):
        """
        Get the color as a tuple of the 3 RGB values that
        are, in order: red, green, blue. These values are
        not normalized, so each value is in the interval
        [0, 255].
        """
        return self.r, self.g, self.b
    
    @property
    def rgb_normalized(
        self
    ):
        """
        Get the color as a tuple of the 3 RGB values that
        are, in order: red, green, blue. These values are
        normalized, so each value is in the interval [0, 1].
        """
        return self.r / 255.0, self.g / 255.0, self.b / 255.0
    
    @property
    def rgba_not_normalized(
        self
    ):
        """
        Get the color as a tuple of the 3 RGB values and
        a 4th value representing the transparency, that
        are, in order: red, green, blue, alpha. These
        values are not normalized, so each value is in
        the interval [0, 255].
        """
        return self.r, self.g, self.b, self.a

    @property
    def rgba_normalized(
        self
    ):
        """
        Get the color as a tuple of the 3 RGB values and
        a 4th value representing the transparency, that
        are, in order: red, green, blue, alpha. These
        values are normalized, so each value is in the
        interval [0, 1].
        """
        return self.r / 255.0, self.g / 255.0, self.b / 255.0, self.a / 255.0
    
    @property
    def rgb_array_not_normalized(
        self
    ):
        """
        Get the color as an array of the 3 RGB values that
        are, in order: red, green, blue. These values are
        not normalized, so each value is in the interval
        [0, 255].
        """
        return [*self.rgba_not_normalized]
    
    @property
    def rgb_array_normalized(
        self
    ):
        """
        Get the color as an array of the 3 RGB values that
        are, in order: red, green, blue. These values are
        normalized, so each value is in the interval [0, 1].
        """
        return [*self.rgba_normalized]
    
    @property
    def rgba_array_not_normalized(
        self
    ):
        """
        Get the color as an array of the 3 RGB values and
        a 4th value representing the transparency, that
        are, in order: red, green, blue, alpha. These
        values are not normalized, so each value is in
        the interval [0, 255].
        """
        return [*self.rgba_not_normalized]
    
    @property
    def rgba_array_normalized(
        self
    ):
        """
        Get the color as an array of the 3 RGB values and
        a 4th value representing the transparency, that
        are, in order: red, green, blue, alpha. These
        values are normalized, so each value is in the
        interval [0, 1].
        """
        return [*self.rgba_normalized]
    
    @property
    def hex_with_alpha(
        self
    ):
        """
        Get the color as a string representing it in
        hexadecimal value. The result will be #RRGGBBAA
        because it includes the alpha value in the last
        position.
        """
        return ColorConverter.rgba_to_hex(self.rgba_not_normalized, True)

    @property
    def hex_without_alpha(
        self
    ):
        """
        Get the color as a string representing it in
        hexadecimal value. The result will be #RRGGBB
        because it doesn't include the alpha value.
        """
        return ColorConverter.rgba_to_hex(self.rgba_not_normalized, False)
    
    @property
    def hsl(
        self
    ):
        """
        Get the color as an HSL color.
        """
        return ColorConverter.rgba_to_hsl(self.rgba_not_normalized)
    
    @property
    def cymk(
        self
    ):
        """
        Get the color as an CYMK color.
        """
        return ColorConverter.rgba_to_cymk(self.rgba_not_normalized)

    @property
    def hsv(
        self
    ):
        """
        Get the color as a HSV color.
        """
        return ColorConverter.rgba_to_hsv(self.rgba_not_normalized)

    # Directly related to libraries below
    # TODO: Add more, not only for OpenCV
    @property
    def for_opencv(
        self
    ) -> tuple[int, int, int]:
        """
        Get the color in a BGR format, which is the 
        format that the OpenCV library handles.
        """
        return (self.b, self.g, self.r)
    
    # TODO: Use the cv2 library to make other changes
    @staticmethod
    def parse(
        color: Union[list, tuple, str, 'ColorString', 'Color']
    ):
        """
        Parse the provided 'color' parameter and return the
        color as r,g,b,a values or raises an Exception if it
        is not a valid and parseable color.

        This method accepts string colors (if names are
        registered in our system), hexadecimal colors (than
        can also include alpha value), RGB array or tuples
        (that can be normalized, with float values between
        0.0 and 1.0, or not normalized, with int values
        between 0 and 255), or RGBA array or tuples, similar
        to RGB but including a 4h alpha value.
        """
        # TODO: Work on this method to accept other arguments as
        # I've been working on the 'parse_hexadecimal_color' 
        # method which is in the 'utils.py' file.
        if PythonValidator.is_instance_of(color, Color):
            return color

        color = parse_color(color)

        if color is None:
            raise Exception(f'The provided "color" parameter is not parseable.')
        
        return Color(*color)


@dataclass
class Colors:
    """
    Class to hold color constants to simplify
    the way we use them. These colors are built
    with RGB values so they don't include any
    transparency.

    If you need a black color for your OpenCV
    library, just do this:
    - `Colors.BLACK.for_opencv`
    """

    BLACK = Color(0, 0, 0)
    WHITE = Color(255, 255, 255)
    BLUE = Color(0, 0, 255)
    GREEN = Color(0, 255, 0)
    RED = Color(255, 0, 0)
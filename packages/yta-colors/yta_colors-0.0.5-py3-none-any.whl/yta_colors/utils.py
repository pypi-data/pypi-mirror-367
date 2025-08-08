from yta_constants.color import ColorString
from yta_constants.regex import ColorRegularExpression
from yta_validation import PythonValidator
from colorsys import rgb_to_hsv as _rgb_to_hsv, hsv_to_rgb as _hsv_to_rgb
from typing import Union


def is_hexadecimal_color(
    color: str
) -> bool:
    """
    Check that the 'color' parameter is an hexadecimal
    color.
    """
    return ColorRegularExpression.HEX.parse(color)

def is_string_color(
    color: str
) -> bool:
    """
    Check that the 'color' parameter is an string 
    color accepted by our system, whose value is an
    hexadecimal value.
    """
    return ColorString.is_valid(color)

def is_array_or_tuple_without_alpha_normalized(
    color: str
):
    """
    Check that the 'color' parameter is an array or a
    tuple of 3 elements that are float values between
    0 and 1 (normalized value).
    """
    return (
        is_array_or_tuple_without_alpha and
        all(
            PythonValidator.is_instance_of(c, float) and
            0 <= c <= 1
            for c in color
        )
    )

def is_array_or_tuple_with_alpha_normalized(
    color: str
):
    """
    Check that the 'color' parameter is an array or a
    tuple of 4 elements that are float values between
    0 and 1 (normalized value).
    """
    return (
        is_array_or_tuple_with_alpha and
        all(
            PythonValidator.is_instance_of(c, float) and 
            0 <= c <= 1
            for c in color
        )
    )

def is_array_or_tuple_without_alpha(
    color: str
):
    """
    Check that the 'color' parameter is an array or a
    tuple of 3 elements that are int values between 0
    and 255.
    """
    return (
        PythonValidator.is_instance_of(color, [tuple, list]) and
        len(color) == 3 and
        all(
            PythonValidator.is_instance_of(c, int) and
            0 <= c <= 255
            for c in color
        )
    )

def is_array_or_tuple_with_alpha(
    color: Union[list, tuple]
) -> bool:
    """
    Check that the 'color' parameter is an array or a
    tuple of 4 elements that are int values between 0
    and 255.
    """
    return (
        PythonValidator.is_instance_of(color, [tuple, list]) and
        len(color) == 4 and
        all(
            PythonValidator.is_instance_of(c, int) and
            0 <= c <= 255
            for c in color
        )
    )

def parse_rgb_color(
    color: str
) -> list:
    """
    Parse the provided 'color' as RGB and returns it as
    r,g,b values.
    """
    if is_array_or_tuple_without_alpha_normalized(color):
        return color[0] * 255, color[1] * 255, color[2] * 255
    elif is_array_or_tuple_without_alpha(color):
        return color[0], color[1], color[2]
    else:
        raise Exception(f'The provided "color" parameter is not an RGB color.')

def parse_rgba_color(
    color: str
) -> list:
    """
    Parse the provided 'color' as RGBA and returns it as
    r,g,b,a values.
    """
    if is_array_or_tuple_with_alpha_normalized(color):
        return color[0] * 255, color[1] * 255, color[2] * 255, color[3] * 255
    elif is_array_or_tuple_with_alpha(color):
        return color[0], color[1], color[2], color[3]
    else:
        raise Exception(f'The provided "color" parameter is not an RGBA color.')
    
def parse_color(
    color: Union[str, list, tuple]
) -> Union[list, None]:
    """
    Tries to parse the provided 'color' and returns it
    as an RGBA if parseable, or None if not.
    """
    # As string color
    string_color = None
    try:
        string_color = ColorString.to_enum(color)
    except:
        pass

    color_array = None
    if string_color is not None:
        color_array = hex_to_rgba(string_color.value)
    # A hexadecimal string
    elif PythonValidator.is_string(color) and is_hexadecimal_color(color):
        color_array = hex_to_rgba(color)
    else:
        # RGBA color
        try:
            color_array = parse_rgba_color(color)
        except:
            pass

        # RGB color
        try:
            color_array = *parse_rgb_color(color), 0
        except:
            pass

    # TODO: What about HSL, CYMK, etc. (?)

    return color_array
    
# These methods below are just actioners, they don't
# check anything as they will be used by a class that
# validates everything before using these methods.
def hex_to_rgba(
    hex_color: str
) -> list:
    """
    Return a tuple containing the color in RGBA order.
    """
    # Hex can start with '0x', '0X' or '#'
    hex = hex_color.lstrip('#').lstrip('0x').lstrip('0X')
    if len(hex) == 8:
        # hex with alpha
        r, g, b, a = (int(hex[i:i+2], 16) for i in (0, 2, 4, 6))
    elif len(hex) == 6:
        # hex without alpha
        r, g, b, a = *(int(hex[i:i+2], 16) for i in (0, 2, 4)), 0
    
    return r, g, b, a

def hex_to_rgb(
    hex_color: str
) -> list:
    """
    Return a tuple containing the color in RGB order.
    """
    r, g, b, _ = hex_to_rgba(hex_color)

    return r, g, b

def rgb_to_hex(
    rgb_color: list,
    do_include_alpha: bool = False
) -> list:
    """
    Return a tuple containing the color in RGB or RGBA
    order (according to the given 'do_include_alpha'
    parameter value).
    """
    r, g, b = parse_rgb_color(rgb_color)

    return rgba_to_hex([r, g, b, 255], do_include_alpha)

def rgba_to_hex(
    rgba_color: list,
    do_include_alpha: bool = False
) -> list:
    """
    Return a tuple containing the color in HEX mode
    (including the alpha value if the given
    'do_include_alpha' parameter is True).
    """
    r, g, b, a = parse_rgba_color(rgba_color)

    return (
        "#{:02x}{:02x}{:02x}{:02x}".format(r, g, b, a)
        if do_include_alpha else
        "#{:02x}{:02x}{:02x}".format(r, g, b)
    )

def rgba_to_hsl(
    rgba_color: list
) -> list:
    r, g, b, _ = parse_rgba_color(rgba_color)

    return rgb_to_hsl([r, g, b])

def rgb_to_hsl(
    rgb_color: list
) -> list:
    r, g, b = parse_rgb_color(rgb_color)

    # Values normalization
    r /= 255.0
    g /= 255.0
    b /= 255.0
    
    # Max and minimum values for RGB
    cmax = max(r, g, b)
    cmin = min(r, g, b)
    delta = cmax - cmin

    # Tone (H)
    h = (
        0 # No difference => undefined (gray) tone
        if delta == 0 else
        (60 * ((g - b) / delta) + 360) % 360
        if cmax == r else
        (60 * ((b - r) / delta) + 120) % 360
        if cmax == g else
        (60 * ((r - g) / delta) + 240) % 360 # cmax == b
    )
    
    # Luminosity (L)
    l = (cmax + cmin) / 2
    
    # Saturation (S)
    s = (
        0 # No difference => saturation is 0
        if delta == 0 else
        delta / (1 - abs(2 * l - 1)) if l != 0 and l != 1 else delta / (2 - (cmax + cmin))
    )

    # TODO: I saw in some online solutions that they offer
    # the results without decimal figures
    return round(h, 2), round(s * 100, 2), round(l * 100, 2)

# TODO: Add 'hsl_to_rgb'
# TODO: Add 'hsl_to_rgba'

def rgb_to_cymk(
    rgb_color: list
) -> list:
    r, g, b = parse_rgb_color(rgb_color)

    r, g, b = r / 255.0, g / 255.0, b / 255.0

    k = 1 - max(r, g, b)

    if k == 1:
        c = m = y = 0
    else:
        c = (1 - r - k) / (1 - k)
        m = (1 - g - k) / (1 - k)
        y = (1 - b - k) / (1 - k)

    # TODO: I saw in some online solutions that they offer
    # the results without decimal figures
    return round(c * 100, 2), round(m * 100, 2), round(y * 100, 2), round(k * 100, 2)

def rgb_to_hsv(
    rgb_color
) -> list:
    r, g, b = parse_rgb_color(rgb_color)

    # TODO: Assume this is not normalized
    return _rgb_to_hsv(r, g, b)

def rgba_to_hsv(
    rgba_color
) -> list:
    r, g, b, _ = parse_rgba_color(rgba_color)
    
    # TODO: Assume this is not normalized
    return _rgb_to_hsv(r, g, b)

def hsv_to_rgb(
    h,
    s,
    v
):
    # TODO: Assume this is not normalized
    return _hsv_to_rgb(h, s, v)

def hsv_to_rgba(
    h,
    s,
    v
):
    # TODO: Assume this is not normalized
    return *hsv_to_rgb(h, s, v), 255



# TODO: We need to accept colors in different formats
# 1. string representing the color ('red', 'blue')
# 2. string representing hexa color ('#334455', '0x334455', '0X334455')
# 3. array, list or tuple containing 3 or 4 colors, each color can be only 1 number/letter (f means ff)
def parse_hexadecimal_color(
    color: Union[str, list, tuple]
) -> Union[list, None]:
    """
    Parse a hexadecimal color. It returns None if unparseable
    or an array containing [r, g, b, a].

    This method accepts a string color (such as 'black' or
    'white'), an hexadecimal value (such as '#ffffff' or
    '0x000000') and an array containing the RGB(A) values.

    TODO: Please, refactor this code.
    """
    if (
        not is_array_or_tuple_with_alpha(color) and
        not is_array_or_tuple_without_alpha(color) and
        not PythonValidator.is_string(color)
    ):
        # TODO: Raise an Exception or return None here?
        return None
    
    alpha = None
    if is_array_or_tuple_with_alpha(color):
        color = ''.join(f"{c:02X}" for c in color)
        alpha = color[-2:]
        color = color[:-2]
        #return color
    if is_array_or_tuple_without_alpha(color):
        color = f'{"".join(f"{c:02X}" for c in color)}'
        #return color.append(0)

    color = color.lower()

    # 1. Parse a string color name and turn into its hexadecimal value
    tmp_color = ColorString.from_color_string(color)
    if tmp_color is not None:
        color = tmp_color.value
        #return tmp_color.as_hex_array.append(0)

    from yta_constants.regex import ColorRegularExpression

    try:
        # Transform the string to its hexadecimal value '#xxxxxx'
        color = f'#{ColorString.to_enum(color.replace("#", "").replace("0x", "")).value}'
    except:
        pass

    if not ColorRegularExpression.HEXADECIMAL.is_valid(color):
        # TODO: Raise an Exception or return None here?
        return None
    
    # It is a valid hexadecimal string
    if (
        ColorRegularExpression.HEXADECIMAL_3_CHARACTERS_NO_ALPHA.is_valid(color) or
        ColorRegularExpression.HEXADECIMAL_4_CHARACTERS_ALPHA.is_valid(color)
    ):
        # We duplicate it to make it have 6 or 8 characters
        # duplicating not the '#' or '0x' flag.
        color = (
            f'#{"".join(c * 2 for c in color[1:])}'
            if color.startswith('#') else
            f'0x{"".join(c * 2 for c in color[2:])}'
            if color.startswith('0x') else
            ''.join(c * 2 for c in color)
        )

    if ColorRegularExpression.HEXADECIMAL_8_CHARACTERS_ALPHA.is_valid(color):
        #alpha = int(color[-2:], 16)
        alpha = color[-2:]
        color = color[:-2]

    alpha = (
        alpha.lower()
        if PythonValidator.is_string(alpha) else
        alpha
    )

    # String is like '#ffffff' or '0xffffff' here
    return [
        color[-6:-4],
        color[-4:-2],
        color[-2:],
        alpha
    ]



# TODO: This class has to be different, having '#FFFFFF' is not a good choice
from yta_constants.enum import YTAEnum as Enum
class ColorString(Enum):
    """
    The hexadecimal string that corresponds to the color.
    """
    
    BLACK = 'ffffff'
    WHITE = '000000'

    @property
    def as_color_string(
        self
    ) -> str:
        return self.name.lower()

    @property
    def as_hex_str(
        self
    ) -> str:
        """
        Get the color as a string in the '#ffffff' format.
        """
        return f'#{self.value.lower()}'
    
    @property
    def as_hex_0x_str(
        self
    ) -> str:
        """
        Get the color as a string in the '0xffffff' format.
        """
        return f'0x{self.value.lower()}'
    
    @property
    def as_hex_array(
        self
    ) -> list:
        """
        Get the color as an array in the [red, green, blue] format
        """
        return [
            self.value[-6:-4],
            self.value[-4:-2],
            self.value[-2:]
        ]
    
    @property
    def as_hex_int_array(
        self
    ) -> list:
        """
        Get the color as an array in the [red, green, blue] format
        but with integer values.
        """
        return [
            int(self.value[-6:-4], 16),
            int(self.value[-4:-2], 16),
            int(self.value[-2:], 16)
        ]
    
    @staticmethod
    def from_color_string(
        color: str
    ) -> Union[ColorString, None]:
        """
        Parse the provided 'color' string as an Enum instance or
        get None if not.
        """
        try:
            return ColorString[color.upper()]
        except KeyError:
            return None
            # TODO: Maybe better an Exception?
            raise Exception('The given "color" is not valid.')

        
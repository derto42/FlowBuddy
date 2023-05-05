import colorsys
import re


def lighten_color(hex_value: str, amount: int = 0.5) -> str:
    # Convert hex value to RGB tuple
    r, g, b = tuple(int(hex_value[i:i + 2], 16) for i in (0, 2, 4))
    # Convert RGB to HLS
    h, l, s = colorsys.rgb_to_hls(r / 255.0, g / 255.0, b / 255.0)
    # Increase lightness value
    l = min(1.0, l + amount)
    # Convert HLS back to RGB
    r, g, b = tuple(round(i * 255) for i in colorsys.hls_to_rgb(h, l, s))

    # Return the hex value
    return "#{:02x}{:02x}{:02x}".format(r, g, b)


def darken_color(hex_value: str, amount: int = 0.5) -> str:
    # Convert hex value to RGB tuple
    r, g, b = tuple(int(hex_value[i:i + 2], 16) for i in (0, 2, 4))
    # Convert RGB to HLS
    h, l, s = colorsys.rgb_to_hls(r / 255.0, g / 255.0, b / 255.0)
    # Increase lightness value
    l = max(0.0, l - amount)
    # Convert HLS back to RGB
    r, g, b = tuple(round(i * 255) for i in colorsys.hls_to_rgb(h, l, s))

    # Return the hex value
    return "#{:02x}{:02x}{:02x}".format(r, g, b)


def replace_color(style: str, color: str, amount: int = 0.5) -> str:
    pattern = r"background-color:\s*([^\s;}]+)"
    match = re.search(pattern, style)
    property_name = match[1]
    new_color = "#000000"
    if color == "light":
        new_color = lighten_color(match[2], amount)
    elif color == "dark":
        new_color = darken_color(match[2], amount)
    elif color.startswith("#") and len(color) == 7:
        new_color = color
    return str(re.sub(pattern, f"{property_name}{new_color}", style))

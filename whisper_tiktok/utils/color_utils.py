import re


def validate_hex_color(color: str) -> bool:
    """Validate if the input string is a valid hex color."""
    pattern = r"^#?([0-9A-Fa-f]{3}|[0-9A-Fa-f]{6})$"
    return bool(re.match(pattern, color))


def rgb_to_bgr(rgb: str) -> str:
    """Convert RGB hex to BGR hex."""
    # Validate input length
    if len(rgb) != 6 and len(rgb) != 7:
        raise ValueError("RGB hex must be 6 or 7 characters long (including #).")

    # Validate hex characters
    match = validate_hex_color(rgb)

    if not match:
        raise ValueError("Invalid RGB hex format.")

    if rgb.startswith("#"):
        rgb = rgb[1:]
    r, g, b = rgb[0:2], rgb[2:4], rgb[4:6]
    return b + g + r


def compute_contrast_color(rgb: str) -> str:
    """Return a contrasting RGB hex (no #) for readability.

    Uses relative luminance: if the color is light, return dark (#202020); if dark, return light (#F5F5F5).
    """
    if rgb.startswith("#"):
        rgb = rgb[1:]
    if len(rgb) != 6:
        raise ValueError("RGB hex must be 6 characters long")

    r = int(rgb[0:2], 16)
    g = int(rgb[2:4], 16)
    b = int(rgb[4:6], 16)

    # Relative luminance (approx)
    luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b

    # Threshold near mid; choose soft light or dark
    return "202020" if luminance > 180 else "F5F5F5"


if __name__ == "__main__":
    # Example usage
    rgb_color = "#1A2B3C"
    bgr_color = rgb_to_bgr(rgb_color)
    print(f"RGB: {rgb_color} -> BGR: #{bgr_color}")

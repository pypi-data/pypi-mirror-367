from .config import presets, unicodes, valid_colors, valid_styles

def build_tag(color = None, bg = None, styles = None):
    tags = []

    if styles:
        for style in styles:
            if style.lower() in valid_styles:
                tags.append(style.lower())
            else:
                RichPrint.warn(f"Invalid style: {style}")

    if color:
        if color.lower() in valid_colors:
            tags.append(color.lower())
        else:
            RichPrint.warn(f"Invalid color: {color}")

    if bg:
        if bg.lower() in valid_colors:
            tags.append(f"on {bg.lower()}")
        else:
            RichPrint.warn(f"Invalid background color: {bg}")

    return " ".join(tags)


def apply_tag(text, tag):
    return f"[{tag}]{text}[/{tag}]" if tag else text

def is_valid_color(c):
    return c.lower() in valid_colors

def is_valid_style(s):
    return s.lower() in valid_styles

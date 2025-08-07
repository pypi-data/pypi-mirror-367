from rich import print as rprint
from .utils import build_tag, apply_tag
from .config import presets, unicodes

class RichPrint:
    
    def __init__(self):
        self._color = None
        self._bg = None
        self._styles = []
        self._preset = None

    def color(self, color):
        self._color = color
        return self

    def bg(self, bg):
        self._bg = bg
        return self

    def style(self, *styles):
        self._styles.extend(styles)
        return self

    def preset(self, name):
        self._preset = name
        return self

    def show(self, message):
        if self._preset:
            config = presets.get(self._preset)
            if config:
                self._color = config.get("color", self._color)
                self._bg = config.get("bg", self._bg)
                self._styles = config.get("styles", self._styles)
            else:
                rprint("[bold red]Warning:[/] Unknown preset")

        tag_str = build_tag(self._color, self._bg, self._styles)

        if tag_str:
            rprint(f"[{tag_str}]{message}[/{tag_str}]")
        else:
            rprint(message)

        self._color = None
        self._bg = None
        self._styles = []
        self._preset = None

        return self

    @classmethod
    def success(cls, message):
        return cls().preset("success").show(message)

    @classmethod
    def error(cls, message):
        return cls().preset("error").show(message)

    @classmethod
    def info(cls, message):
        return cls().preset("info").show(message)

    @classmethod
    def warn(cls, message):
        return cls().preset("warning").show(message)

def print_status(message, ongoing = True):
    arrow = unicodes[1] if ongoing else unicodes[0]
    color = "cyan" if ongoing else "green"
    RichPrint().color(color).style("bold").show(f"{arrow} {message}")

def box(title, color = None, bg = None, styles = None):
    tag_str = build_tag(color, bg, styles)
    line = "═" * 60
    top = f"[{tag_str}]╔{line}╗[/{tag_str}]" if tag_str else f"╔{line}╗"
    mid = f"[{tag_str}]║ {title.center(58)} ║[/{tag_str}]" if tag_str else f"║ {title.center(58)} ║"
    bot = f"[{tag_str}]╚{line}╝[/{tag_str}]" if tag_str else f"╚{line}╝"
    RichPrint().show(top)
    RichPrint().show(mid)
    RichPrint().show(bot)

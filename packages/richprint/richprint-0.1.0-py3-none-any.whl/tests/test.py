from richprint.core import RichPrint, print_status, box
from richprint.utils import build_tag
from rich import print as show

# ========== RichPrint tests ==========

RichPrint().color("cyan").show("Just a cyan line")
RichPrint().bg("magenta").show("Only background magenta")
RichPrint().style("italic", "underline").show("Only italic and underline")
RichPrint().color("bright_red").bg("bright_black").show("Bright red on black")
RichPrint().color("green").style("bold", "reverse").show("Green bold reversed")
RichPrint().bg("yellow").style("dim", "italic").show("Dim italic on yellow")
RichPrint().color("blue").bg("bright_white").style("bold", "underline").show("All 3 params")
RichPrint().preset("success").show("Success preset only")
RichPrint().preset("warning").color("magenta").style("italic").show("Preset override test")
RichPrint().preset("invalid").show("This will warn about unknown preset")

# ========== print_status tests ==========

print_status("Downloading files", ongoing = True)
print_status("Training complete", ongoing = False)

# ========== box tests ==========

show(box("PLAIN BOX"))
show(box("COLORED BOX", color = "cyan"))
show(box("BOX WITH BG", color = "red", bg = "bright_white"))
show(box("BOX WITH STYLE", color = "green", styles = ["bold", "italic"]))
show(box("FULL CUSTOM BOX", color = "blue", bg = "bright_yellow", styles = ["underline", "reverse"]))

RichPrint.success("Success message test")

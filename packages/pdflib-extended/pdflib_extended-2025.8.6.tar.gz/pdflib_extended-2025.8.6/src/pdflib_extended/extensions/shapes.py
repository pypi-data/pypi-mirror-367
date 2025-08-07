from ..core.pdflib_base import PDFlibBase
from .classes import Box


def rectangle(p: PDFlibBase, box: Box, c: float, m: float, y: float, k: float) -> int:
    page_height: float = p.get_option("pageheight", "") / 72

    # Adjust box to be drawn correctly
    offset_x: float = box.urx - box.llx
    offset_y: float = (page_height - box.ury) - (page_height - box.lly)
    box = Box(box.llx, page_height - box.lly, offset_x, offset_y).as_pt()

    # Save graphics option to avoid stepping on any current ones then place box
    p.save()
    p.set_graphics_option(f"fillcolor={{cmyk {c} {m} {y} {k}}}")

    p.rect(box.llx, box.lly, box.urx, box.ury)
    p.fill()

    p.restore()

    return 0

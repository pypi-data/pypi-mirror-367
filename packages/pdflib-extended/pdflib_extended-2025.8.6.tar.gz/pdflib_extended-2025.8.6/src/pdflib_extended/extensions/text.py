from ..core.pdflib_base import PDFlibBase
from .classes import Box
from ..exceptions import InvalidTextflowHandle


def text_box(
    p: PDFlibBase,
    text: str,
    box: Box,
    font_name: str,
    font_size: int,
    tf_optlist: str,
    fit_optlist: str,
) -> str:
    page_height: float = p.get_option("pageheight", "") / 72

    # Adjust box coordinates to accurately place on page
    box = Box(box.llx, page_height - box.lly, box.urx, page_height - box.ury).as_pt()

    # Create textflow object
    tf: int = p.create_textflow(
        text,
        f"fontname={{{font_name}}} fontsize={font_size} "
        f"encoding=unicode embedding {tf_optlist}",
    )
    if tf < 0:
        raise InvalidTextflowHandle(p.get_errmsg())

    # Place object onto page
    p_result: str = p.fit_textflow(
        tf,
        box.llx,
        box.lly,
        box.urx,
        box.ury,
        f"verticalalign=bottom linespreadlimit=120% {fit_optlist}",
    )

    p.delete_textflow(tf)

    return p_result

from io import BytesIO
from typing import Union, Optional

import qrcode
from PIL import Image
from pylibdmtx.pylibdmtx import encode, Encoded

from .classes import Point, Box
from .text import text_box
from ..core.pdflib_base import PDFlibBase


def datamatrix(p: PDFlibBase, data: str, point: Point, scale: float) -> int:
    """
    Creates a datamatrix.

    :param p:
    :param data:
    :param point:
    :param scale:
    :return: int
    """
    data_bytes: bytes = data.encode("utf-8")
    encoded_data: Encoded = encode(data_bytes)

    # Save encoded data and convert to a memory buffer to be
    # read into the pvf system
    image = Image.frombytes(
        "RGB", (encoded_data.width, encoded_data.height), encoded_data.pixels
    )

    buffer = BytesIO()
    image.save(buffer, format="PNG")

    pvf_path = f"/pvf/{data}"
    if not int(p.info_pvf(pvf_path, "exists")):
        p.create_pvf(pvf_path, buffer.getvalue(), "")

    # Adjust Point object coordinates to be placed accurately
    image_border: float = 0.14
    border_offset: float = image_border * scale

    page_height: float = p.get_option("pageheight", "") / 72

    point = Point(
        point.x - border_offset, page_height - border_offset - point.y
    ).as_pt()

    # Load image from memory and place on page
    p_image: int = p.load_image("png", pvf_path, "")
    if p_image < 0:
        return p_image

    p.fit_image(p_image, point.x, point.y, f"scale={scale}")
    p.close_image(p_image)

    return 0


def code_128(p: PDFlibBase, data: str, box: Box, font_size: int = 24) -> int:
    """
    Reference: https://www.barcodefaq.com/1d/code-128/
    Requires Google Font 'Libre Barcode 128':
        https://fonts.google.com/specimen/Libre+Barcode+128
    Function created using character set B.

    :param p:
    :param data:
    :param box:
    :param font_size:
    :return: int
    """
    total = 0
    start_b = 104

    for idx, c in enumerate(data):
        weight = idx + 1
        c_value = ord(c) - 32
        total += c_value * weight

    total += start_b
    check_digit = total % 103
    check_digit_ascii = check_digit + 32

    if check_digit == 0:
        check_digit_ascii = 194
    elif check_digit > 95:
        check_digit_ascii = check_digit + 100

    checksum_c = chr(check_digit_ascii)
    encoded_data = rf"Ì{data}{checksum_c}Î"

    p_result: Union[str, int] = text_box(
        p,
        encoded_data,
        box,
        "LibreBarcode128-Regular",
        font_size,
        "begoptlistchar=« endoptlistchar=» features=calt",
        "",
    )

    if p_result != "_stop":
        # TODO: raise a box not big enough error, or not all data placed
        return -1

    return 0


def omr(p: PDFlibBase, eoc: bool, inserts: Optional[list[bool]] = None) -> int:
    """
    Draws Optical Recognition Marks in the top left of page
    for inserter machines.

    :param p: pdflib object reference
    :param eoc: end of collation for current piece
    :param inserts: list of booleans that control additional marks
    :return: int
    """
    if inserts is None:
        inserts = []

    line_length = 0.400 * 72
    line_height = 0.125 * 72

    # Get location of where to draw marks on page
    page_height: float = p.get_option("pageheight", "") / 72
    point = Point(0.050, page_height - 0.625).as_pt()

    def draw_line() -> None:
        nonlocal point
        p.moveto(point.x, point.y)
        p.lineto(point.x + line_length, point.y)
        point.y -= line_height

    # Draw initial line, this is always present
    draw_line()

    # Draw end of collation mark if flag is present
    if eoc:
        draw_line()
    else:
        point.y -= line_height  # Still need to shift y if it is not present

    # Draw all insert marks provided
    for insert in inserts:
        if insert:
            draw_line()
        else:
            point.y += line_height  # Shift the y if it is not present

    p.stroke()

    return 0


def qr_code(
    p: PDFlibBase,
    data: str,
    point: Point,
    size: int,
    box_size: int,
    border: int,
) -> int:
    qr = qrcode.main.QRCode(
        version=size,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=box_size,
        border=border,
    )

    qr.add_data(data)
    qr.make()

    image = qr.make_image(fill_color="black", back_color="white")

    # Save encoded data and convert to a memory buffer to be
    # read into the pvf system
    buffer = BytesIO()
    image.save(buffer, kind="PNG")

    pvf_path = f"/pvf/{data}"
    if not int(p.info_pvf(pvf_path, "exists")):
        p.create_pvf(pvf_path, buffer.getvalue(), "")

    page_height: float = p.get_option("pageheight", "") / 72

    point = Point(point.x, page_height - point.y).as_pt()

    # Load image from memory and place on page
    p_image: int = p.load_image("png", pvf_path, "")
    if p_image < 0:
        return p_image

    p.fit_image(p_image, point.x, point.y, "")
    p.close_image(p_image)

    return 0

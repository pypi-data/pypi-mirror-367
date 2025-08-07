from pathlib import Path
from typing import ContextManager, Union, Optional

from .core.pdflib_base import PDFlibBase
from .extensions.barcodes import omr, code_128, datamatrix, qr_code
from .extensions.classes import Point, Box
from .extensions.contexts import Document, NewDocument, Image
from .extensions.shapes import rectangle
from .extensions.text import text_box


BASE_DIR = Path(__file__).resolve().parent


class PDFlib(PDFlibBase):
    def __init__(
        self,
        license_key: Optional[str] = None,
        version: int = 10,
    ):
        super().__init__(version=version)

        if license_key:
            self.set_option(f"license={license_key}")

    def start_document(
        self, file_path: Union[str, Path], optlist: Optional[str] = ""
    ) -> ContextManager[NewDocument]:
        return NewDocument(self, file_path, optlist)

    def open_document(
        self, file_path: Union[str, Path], optlist: Optional[str] = ""
    ) -> ContextManager[Document]:
        return Document(self, file_path, optlist)

    def read_image(
        self,
        file_path: Union[str, Path],
        image_type: Optional[str] = "auto",
        optlist: Optional[str] = "",
    ) -> ContextManager[Image]:
        return Image(self, file_path, image_type, optlist)

    def fit_datamatrix(self, data: str, point: Point, scale: float = 0.35) -> int:
        return datamatrix(self, data, point, scale)

    def fit_code_128_barcode(self, data: str, box: Box, font_size: int = 24) -> int:
        return code_128(self, data, box, font_size)

    def fit_text_box(
        self,
        text: str,
        box: Box,
        font_name: str = "OpenSans-Regular",
        font_size: int = 12,
        tf_optlist: str = "",
        fit_optlist: str = "",
    ) -> Union[str, int]:
        return text_box(self, text, box, font_name, font_size, tf_optlist, fit_optlist)

    def fit_rectangle(
        self, box: Box, c: float = 0, m: float = 0, y: float = 0, k: float = 0
    ) -> int:
        return rectangle(self, box, c, m, y, k)

    def fit_omr(self, eoc: bool = False, inserts: Optional[list[bool]] = None) -> int:
        return omr(self, eoc, inserts)

    def fit_qr_code(
        self,
        data: str,
        point: Point,
        size: int = 1,
        box_size: int = 1,
        border: int = 0,
    ) -> int:
        return qr_code(self, data, point, size, box_size, border)

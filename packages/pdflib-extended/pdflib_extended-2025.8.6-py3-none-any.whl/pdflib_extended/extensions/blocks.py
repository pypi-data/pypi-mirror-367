from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Union, Optional
from ..core.pdflib_base import PDFlibBase  # noqa: F401

if TYPE_CHECKING:
    from ..pdflib import PDFlib
    from .contexts import Page


class Block(ABC):
    def __init__(
        self, p: "PDFlib", page: "Page", block_index: int, block_type: str
    ) -> None:
        self.p = p
        self.page = page
        self.type = block_type
        self.path = f"pages[{page.page_number - 1}]/blocks[{block_index}]"
        self.name = self._get_name()
        self.text = self._get_text()

    def _get_name(self) -> str:
        name: str = self.p.pcos_get_string(
            self.page.document_handle, f"{self.path}.key"
        )
        return name

    def _get_text(self) -> str:
        text: str = self.p.pcos_get_string(
            self.page.document_handle, f"{self.path}/default{self.type.lower()}"
        )
        return text

    @abstractmethod
    def fill_block(self, content: Union[str, int], optlist: Optional[str]) -> int:
        pass

    @classmethod
    def create_block(
        cls, p: "PDFlib", page: "Page", block_index: int
    ) -> Union["TextBlock", "ImageBlock", "GraphicsBlock", "PDFBlock"]:
        block_type: str = p.pcos_get_string(
            page.document_handle,
            f"pages[{page.page_number - 1}]/blocks[{block_index}]/Subtype",
        )

        if block_type == "Text":
            return TextBlock(p, page, block_index, block_type)
        elif block_type == "Image":
            return ImageBlock(p, page, block_index, block_type)
        elif block_type == "Graphics":
            return GraphicsBlock(p, page, block_index, block_type)
        elif block_type == "PDF":
            return PDFBlock(p, page, block_index, block_type)
        else:
            raise ValueError(f"Unsupported block type: {block_type}")


class TextBlock(Block):
    def fill_block(
        self, content: Union[str, int], optlist: Optional[str] = None
    ) -> int:
        optlist = optlist or "encoding=unicode embedding"
        p_result: int = self.p.fill_textblock(
            self.page.handle, self.name, content, optlist
        )
        return p_result


class ImageBlock(Block):
    def fill_block(
        self, content: Union[str, int], optlist: Optional[str] = None
    ) -> int:
        optlist = optlist or ""
        p_result: int = self.p.fill_imageblock(
            self.page.handle, self.name, content, optlist
        )
        return p_result


class GraphicsBlock(Block):
    def fill_block(
        self, content: Union[str, int], optlist: Optional[str] = None
    ) -> int:
        optlist = optlist or ""
        p_result: int = self.p.fill_graphicsblock(
            self.page.handle, self.name, content, optlist
        )
        return p_result


class PDFBlock(Block):
    def fill_block(
        self, content: Union[str, int], optlist: Optional[str] = None
    ) -> int:
        optlist = optlist or ""
        p_result: int = self.p.fill_pdfblock(
            self.page.handle, self.name, content, optlist
        )
        return p_result

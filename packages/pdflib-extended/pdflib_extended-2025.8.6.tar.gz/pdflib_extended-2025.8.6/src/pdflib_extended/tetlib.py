import sys
from typing import Optional, ContextManager, Union

from .extensions.contexts import TETDocument
from .core.tetlib_base import TETLibBase
from pathlib import Path


class TETLib(TETLibBase):
    def __new__(cls, *args, **kwargs):
        if kwargs.get("load_as_com_object", False):
            if sys.platform != "win32":
                raise RuntimeError("COM objects can only be loaded on Windows")

            from .core.tetlib_base import TETLibCOMBase  # type: ignore

            cls.__bases__ = (TETLibCOMBase,)
            instance = super().__new__(cls)
            instance.__init__(*args, **kwargs)  # type: ignore[misc]
            return instance

        return super().__new__(cls)

    def __init__(
        self, license_key: Optional[str] = None, load_as_com_object: bool = False
    ) -> None:
        super().__init__()

        if license_key:
            self.set_option(f"license={license_key}")

    def open_document_ctx(
        self, file_path: Union[Path, str], optlist: Optional[str] = ""
    ) -> ContextManager[TETDocument]:
        return TETDocument(self, file_path, optlist=optlist)

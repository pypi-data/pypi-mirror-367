###############################################################################
#
# (C) Copyright 2025 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
__all__ = ['FileResponse', 'HTMLResponse', 'JSONResponse', 'PlainTextResponse', 'RedirectResponse', 'Response', 'StreamingResponse']

from typing import Any, Literal

from starlette.responses import Response, FileResponse, HTMLResponse, PlainTextResponse, RedirectResponse, StreamingResponse

from everysk.core.object import BaseObject
from everysk.core.serialize import dumps



###############################################################################
#   JSONResponse Class Implementation
###############################################################################
class DumpsParams(BaseObject):
    add_class_path: bool = True
    date_format: str | None = None
    datetime_format: str | None = None
    indent: int | None = None
    protocol: Literal['json', 'orjson'] = 'json'
    return_type: Literal['bytes', 'str'] = 'bytes'
    separators: tuple[str] = (",", ":")
    sort_keys: bool = False
    use_undefined: bool = True

    def __init__(
            self,
            add_class_path: bool = True,
            date_format: str | None = None,
            datetime_format: str | None = None,
            indent: int | None = None,
            protocol: Literal['json', 'orjson'] = 'json',
            return_type: Literal['bytes', 'str'] = 'bytes',
            separators: tuple[str] = (",", ":"),
            sort_keys: bool = False,
            use_undefined: bool = True,
            **kwargs
        ):
        super().__init__(
            add_class_path=add_class_path,
            date_format=date_format,
            datetime_format=datetime_format,
            indent=indent,
            protocol=protocol,
            return_type=return_type,
            separators=separators,
            sort_keys=sort_keys,
            use_undefined=use_undefined,
            **kwargs
        )

    def to_dict(self): # pylint: disable=arguments-differ
        dct = super().to_dict(add_class_path=True, recursion=True)
        # we remove all private keys because we don't want them in the serialized output
        return {key: value for key, value in dct.items() if not key.startswith('_')}


class JSONResponse(Response):
    ## Public attributes
    media_type = 'application/json; charset=UTF-8'
    serialize_dumps_params: DumpsParams = DumpsParams()

    def render(self, content: Any) -> bytes:
        """
        Serialize the content to JSON format using the dumps function from the core.serialize module.

        Args:
            content (Any): The content to be serialized.
        """
        # with indent=None and separators=(",", ":"), the JSON will be minified
        return dumps(content, **self.serialize_dumps_params.to_dict())

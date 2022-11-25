from contextlib import suppress
from typing import TYPE_CHECKING, Any, Dict

from esmerald.datastructures import UploadFile
from esmerald.enums import EncodingType
from orjson import JSONDecodeError, loads
from pydantic.fields import SHAPE_LIST, SHAPE_SINGLETON

if TYPE_CHECKING:

    from pydantic.fields import ModelField
    from pydantic.typing import DictAny
    from starlette.datastructures import FormData


def validate_media_type(field: "ModelField", values: "DictAny"):
    """
    Validates the media type against the available types.
    """
    if (field.shape) in SHAPE_LIST:
        return list(values.values())
    if field.shape in SHAPE_SINGLETON and field.type_in[UploadFile] and values:
        return list(values.values())[0]


def parse_form_data(media_type: "EncodingType", form_data: "FormData", field: "ModelField") -> Any:
    values: "DictAny" = {}
    for key, value in form_data.multi_items():
        if not isinstance(value, UploadFile):
            with suppress(JSONDecodeError):
                value = loads(value)
        if isinstance(value, UploadFile):
            value = UploadFile(
                filename=value.filename,
                file=value.file,
                content_type=value.content_type,
                headers=value.headers,
            )
        if values.get(key):
            if isinstance(values[key], list):
                values[key].append(value)
            else:
                values[key] = [values[key], value]
        else:
            values[key] = value
    if media_type == EncodingType.MULTI_PART:
        return validate_media_type(field=field, values=values)
    return values

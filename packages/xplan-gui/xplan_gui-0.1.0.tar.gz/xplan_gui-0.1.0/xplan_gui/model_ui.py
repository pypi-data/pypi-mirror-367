from enum import Enum
from types import NoneType, UnionType
from typing import get_args, get_origin
from uuid import UUID

from pydantic.fields import FieldInfo
from pydantic_core import PydanticUndefined
from xplan_tools.model.base import BaseFeature


def model_ui_schema(cls: BaseFeature) -> dict:
    """
    Generate a UI schema from a Pydantic model class.
    Args:
    cls (BaseFeature): A subclass of Pydantic's `BaseModel` representing the model
        class to generate the UI schema from.
    Returns:
        dict: A dictionary containing metadata about the field with the following keys:
            - 'type' (dict or None): The resolved type info via `resolve_type`.
            - 'list' (bool): Whether the field is a list type.
            - 'nullable' (bool): Whether the field is nullable (i.e., allows None).
            - 'description' (str): Field description text, empty string if none.
            - 'default' (optional): The default value of the field, if set and not undefined.
    """
    def resolve_type(arg: type):
        """
        Resolve the UI type representation for a given Python type.
        Args:
        arg (type): The Python type to resolve.        
        """
        if get_origin(arg) == UnionType:
            if UUID in (sub_args := get_args(arg)):
                return {"name": "reference"}
            else:
                return {
                    "name": "choice",
                    "options": [model_ui_schema(sub_arg) for sub_arg in sub_args],
                }
        elif issubclass(arg, Enum):
            return {"name": "enum", "options": [value.value for value in arg]}
        elif issubclass(arg, UUID):
            return {"name": "reference"}
        elif issubclass(arg, BaseFeature):
            return {"name": "object", "options": model_ui_schema(arg)}
        else:
            return {"name": arg.__name__}

    def resolve_field(field: FieldInfo):
        """
        Resolve detailed UI schema information for a Pydantic model field.
        Args:
        field (FieldInfo): The Pydantic field information to analyze.
        """
        data = {
            "type": None,
            "list": False,
            "nullable": False,
            "description": getattr(field, "description") or "",
        }
        if (default := getattr(field, "default", None)) not in (
            None,
            PydanticUndefined,
        ):
            data["default"] = default
        args = get_args(field.annotation)
        if get_origin(field.annotation) is list:
            data["list"] = True
        if args:
            for arg in args:
                if arg == NoneType:
                    data["nullable"] = True
                elif origin := get_origin(arg):
                    if origin is list:
                        data["list"] = True
                        sub_arg = get_args(arg)[0]
                        data["type"] = resolve_type(sub_arg)
                else:
                    data["type"] = resolve_type(arg)
        else:
            data["type"] = resolve_type(field.annotation)
        return data

    return {
        "name": cls.get_name(),
        "description": cls.__doc__.strip(),
        "fields": {
            name: resolve_field(value) for name, value in cls.model_fields.items()
        },
    }

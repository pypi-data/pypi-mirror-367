from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class PartType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PART_TYPE_UNSPECIFIED: _ClassVar[PartType]
    PART_TYPE_SUB_ASSEMBLY: _ClassVar[PartType]
    PART_TYPE_FASTENER: _ClassVar[PartType]
    PART_TYPE_PLATE: _ClassVar[PartType]
    PART_TYPE_LUBRICANT: _ClassVar[PartType]
PART_TYPE_UNSPECIFIED: PartType
PART_TYPE_SUB_ASSEMBLY: PartType
PART_TYPE_FASTENER: PartType
PART_TYPE_PLATE: PartType
PART_TYPE_LUBRICANT: PartType

class PartMessage(_message.Message):
    __slots__ = ("id", "name", "icon", "description", "type", "weight", "model_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ICON_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    WEIGHT_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    icon: str
    description: str
    type: PartType
    weight: int
    model_id: str
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., icon: _Optional[str] = ..., description: _Optional[str] = ..., type: _Optional[_Union[PartType, str]] = ..., weight: _Optional[int] = ..., model_id: _Optional[str] = ...) -> None: ...

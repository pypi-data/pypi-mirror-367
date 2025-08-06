import ft_error_pb2 as _ft_error_pb2
import ft_types_pb2 as _ft_types_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class serverflag(_message.Message):
    __slots__ = ("err", "msgid", "flagname", "dblval", "intval", "boolval", "stringval")
    ERR_FIELD_NUMBER: _ClassVar[int]
    MSGID_FIELD_NUMBER: _ClassVar[int]
    FLAGNAME_FIELD_NUMBER: _ClassVar[int]
    DBLVAL_FIELD_NUMBER: _ClassVar[int]
    INTVAL_FIELD_NUMBER: _ClassVar[int]
    BOOLVAL_FIELD_NUMBER: _ClassVar[int]
    STRINGVAL_FIELD_NUMBER: _ClassVar[int]
    err: _ft_error_pb2.errstatus
    msgid: int
    flagname: str
    dblval: float
    intval: int
    boolval: bool
    stringval: str
    def __init__(self, err: _Optional[_Union[_ft_error_pb2.errstatus, _Mapping]] = ..., msgid: _Optional[int] = ..., flagname: _Optional[str] = ..., dblval: _Optional[float] = ..., intval: _Optional[int] = ..., boolval: bool = ..., stringval: _Optional[str] = ...) -> None: ...

class serverflaglist(_message.Message):
    __slots__ = ("err", "msgid", "flags")
    ERR_FIELD_NUMBER: _ClassVar[int]
    MSGID_FIELD_NUMBER: _ClassVar[int]
    FLAGS_FIELD_NUMBER: _ClassVar[int]
    err: _ft_error_pb2.errstatus
    msgid: int
    flags: _containers.RepeatedCompositeFieldContainer[serverflag]
    def __init__(self, err: _Optional[_Union[_ft_error_pb2.errstatus, _Mapping]] = ..., msgid: _Optional[int] = ..., flags: _Optional[_Iterable[_Union[serverflag, _Mapping]]] = ...) -> None: ...

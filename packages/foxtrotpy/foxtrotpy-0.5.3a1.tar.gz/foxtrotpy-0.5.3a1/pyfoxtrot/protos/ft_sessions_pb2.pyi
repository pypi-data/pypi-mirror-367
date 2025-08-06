import ft_error_pb2 as _ft_error_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
import ft_types_pb2 as _ft_types_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class session_info(_message.Message):
    __slots__ = ("err", "sessionid", "user_identifier", "comment", "devices", "flags", "expiry")
    ERR_FIELD_NUMBER: _ClassVar[int]
    SESSIONID_FIELD_NUMBER: _ClassVar[int]
    USER_IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    DEVICES_FIELD_NUMBER: _ClassVar[int]
    FLAGS_FIELD_NUMBER: _ClassVar[int]
    EXPIRY_FIELD_NUMBER: _ClassVar[int]
    err: _ft_error_pb2.errstatus
    sessionid: bytes
    user_identifier: str
    comment: str
    devices: _containers.RepeatedScalarFieldContainer[int]
    flags: _containers.RepeatedScalarFieldContainer[str]
    expiry: _timestamp_pb2.Timestamp
    def __init__(self, err: _Optional[_Union[_ft_error_pb2.errstatus, _Mapping]] = ..., sessionid: _Optional[bytes] = ..., user_identifier: _Optional[str] = ..., comment: _Optional[str] = ..., devices: _Optional[_Iterable[int]] = ..., flags: _Optional[_Iterable[str]] = ..., expiry: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class session_list(_message.Message):
    __slots__ = ("err", "sessions")
    ERR_FIELD_NUMBER: _ClassVar[int]
    SESSIONS_FIELD_NUMBER: _ClassVar[int]
    err: _ft_error_pb2.errstatus
    sessions: _containers.RepeatedCompositeFieldContainer[session_info]
    def __init__(self, err: _Optional[_Union[_ft_error_pb2.errstatus, _Mapping]] = ..., sessions: _Optional[_Iterable[_Union[session_info, _Mapping]]] = ...) -> None: ...

from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class error_types(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ft_Error: _ClassVar[error_types]
    ft_DeviceError: _ClassVar[error_types]
    ft_ProtocolError: _ClassVar[error_types]
    out_of_range: _ClassVar[error_types]
    unknown_error: _ClassVar[error_types]
    contention_timeout: _ClassVar[error_types]
    ft_ServerError: _ClassVar[error_types]
    ft_AuthError: _ClassVar[error_types]

class warning_types(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ft_DeprecationWarning: _ClassVar[warning_types]
ft_Error: error_types
ft_DeviceError: error_types
ft_ProtocolError: error_types
out_of_range: error_types
unknown_error: error_types
contention_timeout: error_types
ft_ServerError: error_types
ft_AuthError: error_types
ft_DeprecationWarning: warning_types

class errstatus(_message.Message):
    __slots__ = ("tp", "msg", "warntp", "warnstring")
    TP_FIELD_NUMBER: _ClassVar[int]
    MSG_FIELD_NUMBER: _ClassVar[int]
    WARNTP_FIELD_NUMBER: _ClassVar[int]
    WARNSTRING_FIELD_NUMBER: _ClassVar[int]
    tp: error_types
    msg: str
    warntp: warning_types
    warnstring: str
    def __init__(self, tp: _Optional[_Union[error_types, str]] = ..., msg: _Optional[str] = ..., warntp: _Optional[_Union[warning_types, str]] = ..., warnstring: _Optional[str] = ...) -> None: ...

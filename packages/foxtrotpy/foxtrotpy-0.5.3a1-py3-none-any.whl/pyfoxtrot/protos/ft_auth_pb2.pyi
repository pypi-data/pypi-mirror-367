import ft_error_pb2 as _ft_error_pb2
import ft_types_pb2 as _ft_types_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class auth_data(_message.Message):
    __slots__ = ("userid", "token", "authlevel", "authflags", "expiry")
    USERID_FIELD_NUMBER: _ClassVar[int]
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    AUTHLEVEL_FIELD_NUMBER: _ClassVar[int]
    AUTHFLAGS_FIELD_NUMBER: _ClassVar[int]
    EXPIRY_FIELD_NUMBER: _ClassVar[int]
    userid: str
    token: bytes
    authlevel: int
    authflags: int
    expiry: _timestamp_pb2.Timestamp
    def __init__(self, userid: _Optional[str] = ..., token: _Optional[bytes] = ..., authlevel: _Optional[int] = ..., authflags: _Optional[int] = ..., expiry: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class auth_request(_message.Message):
    __slots__ = ("userid",)
    USERID_FIELD_NUMBER: _ClassVar[int]
    userid: str
    def __init__(self, userid: _Optional[str] = ...) -> None: ...

class auth_challenge(_message.Message):
    __slots__ = ("err", "challengeid", "challenge")
    ERR_FIELD_NUMBER: _ClassVar[int]
    CHALLENGEID_FIELD_NUMBER: _ClassVar[int]
    CHALLENGE_FIELD_NUMBER: _ClassVar[int]
    err: _ft_error_pb2.errstatus
    challengeid: int
    challenge: bytes
    def __init__(self, err: _Optional[_Union[_ft_error_pb2.errstatus, _Mapping]] = ..., challengeid: _Optional[int] = ..., challenge: _Optional[bytes] = ...) -> None: ...

class auth_response(_message.Message):
    __slots__ = ("challengeid", "userid", "sig")
    CHALLENGEID_FIELD_NUMBER: _ClassVar[int]
    USERID_FIELD_NUMBER: _ClassVar[int]
    SIG_FIELD_NUMBER: _ClassVar[int]
    challengeid: int
    userid: str
    sig: bytes
    def __init__(self, challengeid: _Optional[int] = ..., userid: _Optional[str] = ..., sig: _Optional[bytes] = ...) -> None: ...

class auth_confirm(_message.Message):
    __slots__ = ("err", "sessionkey", "expiry", "authlevel")
    ERR_FIELD_NUMBER: _ClassVar[int]
    SESSIONKEY_FIELD_NUMBER: _ClassVar[int]
    EXPIRY_FIELD_NUMBER: _ClassVar[int]
    AUTHLEVEL_FIELD_NUMBER: _ClassVar[int]
    err: _ft_error_pb2.errstatus
    sessionkey: bytes
    expiry: int
    authlevel: int
    def __init__(self, err: _Optional[_Union[_ft_error_pb2.errstatus, _Mapping]] = ..., sessionkey: _Optional[bytes] = ..., expiry: _Optional[int] = ..., authlevel: _Optional[int] = ...) -> None: ...

class sasl_auth_data(_message.Message):
    __slots__ = ("err", "sasl_data", "authdat")
    ERR_FIELD_NUMBER: _ClassVar[int]
    SASL_DATA_FIELD_NUMBER: _ClassVar[int]
    AUTHDAT_FIELD_NUMBER: _ClassVar[int]
    err: _ft_error_pb2.errstatus
    sasl_data: bytes
    authdat: auth_data
    def __init__(self, err: _Optional[_Union[_ft_error_pb2.errstatus, _Mapping]] = ..., sasl_data: _Optional[bytes] = ..., authdat: _Optional[_Union[auth_data, _Mapping]] = ...) -> None: ...

class auth_type_list(_message.Message):
    __slots__ = ("err", "mechanism_name")
    ERR_FIELD_NUMBER: _ClassVar[int]
    MECHANISM_NAME_FIELD_NUMBER: _ClassVar[int]
    err: _ft_error_pb2.errstatus
    mechanism_name: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, err: _Optional[_Union[_ft_error_pb2.errstatus, _Mapping]] = ..., mechanism_name: _Optional[_Iterable[str]] = ...) -> None: ...

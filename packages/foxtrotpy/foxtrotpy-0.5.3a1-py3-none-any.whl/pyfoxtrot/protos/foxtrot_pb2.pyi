import ft_error_pb2 as _ft_error_pb2
import ft_types_pb2 as _ft_types_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class broadcast_notification(_message.Message):
    __slots__ = ("err", "msgid", "use_default_title", "title", "body", "use_default_channel", "channel_target")
    ERR_FIELD_NUMBER: _ClassVar[int]
    MSGID_FIELD_NUMBER: _ClassVar[int]
    USE_DEFAULT_TITLE_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    USE_DEFAULT_CHANNEL_FIELD_NUMBER: _ClassVar[int]
    CHANNEL_TARGET_FIELD_NUMBER: _ClassVar[int]
    err: _ft_error_pb2.errstatus
    msgid: int
    use_default_title: bool
    title: str
    body: str
    use_default_channel: bool
    channel_target: str
    def __init__(self, err: _Optional[_Union[_ft_error_pb2.errstatus, _Mapping]] = ..., msgid: _Optional[int] = ..., use_default_title: bool = ..., title: _Optional[str] = ..., body: _Optional[str] = ..., use_default_channel: bool = ..., channel_target: _Optional[str] = ...) -> None: ...

class server_info(_message.Message):
    __slots__ = ("err", "server_version", "rpc_version", "name", "comment", "started", "option_flags", "unique_runid")
    ERR_FIELD_NUMBER: _ClassVar[int]
    SERVER_VERSION_FIELD_NUMBER: _ClassVar[int]
    RPC_VERSION_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    STARTED_FIELD_NUMBER: _ClassVar[int]
    OPTION_FLAGS_FIELD_NUMBER: _ClassVar[int]
    UNIQUE_RUNID_FIELD_NUMBER: _ClassVar[int]
    err: _ft_error_pb2.errstatus
    server_version: int
    rpc_version: int
    name: str
    comment: str
    started: _timestamp_pb2.Timestamp
    option_flags: int
    unique_runid: bytes
    def __init__(self, err: _Optional[_Union[_ft_error_pb2.errstatus, _Mapping]] = ..., server_version: _Optional[int] = ..., rpc_version: _Optional[int] = ..., name: _Optional[str] = ..., comment: _Optional[str] = ..., started: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., option_flags: _Optional[int] = ..., unique_runid: _Optional[bytes] = ...) -> None: ...

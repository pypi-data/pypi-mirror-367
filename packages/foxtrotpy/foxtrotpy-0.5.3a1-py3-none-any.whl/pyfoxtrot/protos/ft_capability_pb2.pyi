import ft_types_pb2 as _ft_types_pb2
import ft_error_pb2 as _ft_error_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import duration_pb2 as _duration_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class capability_types(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    VALUE_READONLY: _ClassVar[capability_types]
    VALUE_READWRITE: _ClassVar[capability_types]
    ACTION: _ClassVar[capability_types]
    STREAM: _ClassVar[capability_types]
    CONSTRUCTOR: _ClassVar[capability_types]

class stream_control_commands(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    stop: _ClassVar[stream_control_commands]
    start: _ClassVar[stream_control_commands]

class async_control_commands(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    dispatch: _ClassVar[async_control_commands]
    check: _ClassVar[async_control_commands]
    get: _ClassVar[async_control_commands]
    defer: _ClassVar[async_control_commands]
    run_all: _ClassVar[async_control_commands]
VALUE_READONLY: capability_types
VALUE_READWRITE: capability_types
ACTION: capability_types
STREAM: capability_types
CONSTRUCTOR: capability_types
stop: stream_control_commands
start: stream_control_commands
dispatch: async_control_commands
check: async_control_commands
get: async_control_commands
defer: async_control_commands
run_all: async_control_commands

class devcapability(_message.Message):
    __slots__ = ("tp", "capname", "capid", "argnames", "argtypes", "rettp", "vecrettp", "dynamic_rettp")
    TP_FIELD_NUMBER: _ClassVar[int]
    CAPNAME_FIELD_NUMBER: _ClassVar[int]
    CAPID_FIELD_NUMBER: _ClassVar[int]
    ARGNAMES_FIELD_NUMBER: _ClassVar[int]
    ARGTYPES_FIELD_NUMBER: _ClassVar[int]
    RETTP_FIELD_NUMBER: _ClassVar[int]
    VECRETTP_FIELD_NUMBER: _ClassVar[int]
    DYNAMIC_RETTP_FIELD_NUMBER: _ClassVar[int]
    tp: capability_types
    capname: str
    capid: int
    argnames: _containers.RepeatedScalarFieldContainer[str]
    argtypes: _containers.RepeatedCompositeFieldContainer[_ft_types_pb2.variant_descriptor]
    rettp: _ft_types_pb2.variant_descriptor
    vecrettp: _ft_types_pb2.byte_data_types
    dynamic_rettp: bool
    def __init__(self, tp: _Optional[_Union[capability_types, str]] = ..., capname: _Optional[str] = ..., capid: _Optional[int] = ..., argnames: _Optional[_Iterable[str]] = ..., argtypes: _Optional[_Iterable[_Union[_ft_types_pb2.variant_descriptor, _Mapping]]] = ..., rettp: _Optional[_Union[_ft_types_pb2.variant_descriptor, _Mapping]] = ..., vecrettp: _Optional[_Union[_ft_types_pb2.byte_data_types, str]] = ..., dynamic_rettp: bool = ...) -> None: ...

class capability_argument(_message.Message):
    __slots__ = ("position", "value")
    POSITION_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    position: int
    value: _ft_types_pb2.ft_variant
    def __init__(self, position: _Optional[int] = ..., value: _Optional[_Union[_ft_types_pb2.ft_variant, _Mapping]] = ...) -> None: ...

class capability_request(_message.Message):
    __slots__ = ("msgid", "devid", "capname", "capid", "args", "contention_timeout")
    MSGID_FIELD_NUMBER: _ClassVar[int]
    DEVID_FIELD_NUMBER: _ClassVar[int]
    CAPNAME_FIELD_NUMBER: _ClassVar[int]
    CAPID_FIELD_NUMBER: _ClassVar[int]
    ARGS_FIELD_NUMBER: _ClassVar[int]
    CONTENTION_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    msgid: int
    devid: int
    capname: str
    capid: int
    args: _containers.RepeatedCompositeFieldContainer[capability_argument]
    contention_timeout: int
    def __init__(self, msgid: _Optional[int] = ..., devid: _Optional[int] = ..., capname: _Optional[str] = ..., capid: _Optional[int] = ..., args: _Optional[_Iterable[_Union[capability_argument, _Mapping]]] = ..., contention_timeout: _Optional[int] = ...) -> None: ...

class capability_response(_message.Message):
    __slots__ = ("msgid", "devid", "capname", "capid", "returnval", "err", "tstamp", "tstamp_dispatch")
    MSGID_FIELD_NUMBER: _ClassVar[int]
    DEVID_FIELD_NUMBER: _ClassVar[int]
    CAPNAME_FIELD_NUMBER: _ClassVar[int]
    CAPID_FIELD_NUMBER: _ClassVar[int]
    RETURNVAL_FIELD_NUMBER: _ClassVar[int]
    ERR_FIELD_NUMBER: _ClassVar[int]
    TSTAMP_FIELD_NUMBER: _ClassVar[int]
    TSTAMP_DISPATCH_FIELD_NUMBER: _ClassVar[int]
    msgid: int
    devid: int
    capname: str
    capid: int
    returnval: _ft_types_pb2.ft_variant
    err: _ft_error_pb2.errstatus
    tstamp: _timestamp_pb2.Timestamp
    tstamp_dispatch: _timestamp_pb2.Timestamp
    def __init__(self, msgid: _Optional[int] = ..., devid: _Optional[int] = ..., capname: _Optional[str] = ..., capid: _Optional[int] = ..., returnval: _Optional[_Union[_ft_types_pb2.ft_variant, _Mapping]] = ..., err: _Optional[_Union[_ft_error_pb2.errstatus, _Mapping]] = ..., tstamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., tstamp_dispatch: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class chunk_request(_message.Message):
    __slots__ = ("msgid", "devid", "capname", "capid", "args", "chunksize", "contention_timeout")
    MSGID_FIELD_NUMBER: _ClassVar[int]
    DEVID_FIELD_NUMBER: _ClassVar[int]
    CAPNAME_FIELD_NUMBER: _ClassVar[int]
    CAPID_FIELD_NUMBER: _ClassVar[int]
    ARGS_FIELD_NUMBER: _ClassVar[int]
    CHUNKSIZE_FIELD_NUMBER: _ClassVar[int]
    CONTENTION_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    msgid: int
    devid: int
    capname: str
    capid: int
    args: _containers.RepeatedCompositeFieldContainer[capability_argument]
    chunksize: int
    contention_timeout: int
    def __init__(self, msgid: _Optional[int] = ..., devid: _Optional[int] = ..., capname: _Optional[str] = ..., capid: _Optional[int] = ..., args: _Optional[_Iterable[_Union[capability_argument, _Mapping]]] = ..., chunksize: _Optional[int] = ..., contention_timeout: _Optional[int] = ...) -> None: ...

class datachunk(_message.Message):
    __slots__ = ("data", "msgid", "devid", "capid", "capname", "err", "dtp")
    DATA_FIELD_NUMBER: _ClassVar[int]
    MSGID_FIELD_NUMBER: _ClassVar[int]
    DEVID_FIELD_NUMBER: _ClassVar[int]
    CAPID_FIELD_NUMBER: _ClassVar[int]
    CAPNAME_FIELD_NUMBER: _ClassVar[int]
    ERR_FIELD_NUMBER: _ClassVar[int]
    DTP_FIELD_NUMBER: _ClassVar[int]
    data: bytes
    msgid: int
    devid: int
    capid: int
    capname: str
    err: _ft_error_pb2.errstatus
    dtp: _ft_types_pb2.byte_data_types
    def __init__(self, data: _Optional[bytes] = ..., msgid: _Optional[int] = ..., devid: _Optional[int] = ..., capid: _Optional[int] = ..., capname: _Optional[str] = ..., err: _Optional[_Union[_ft_error_pb2.errstatus, _Mapping]] = ..., dtp: _Optional[_Union[_ft_types_pb2.byte_data_types, str]] = ...) -> None: ...

class bulkdata_chunk(_message.Message):
    __slots__ = ("data", "dtp", "err", "cpp_type_name", "pagenum", "totalnum")
    DATA_FIELD_NUMBER: _ClassVar[int]
    DTP_FIELD_NUMBER: _ClassVar[int]
    ERR_FIELD_NUMBER: _ClassVar[int]
    CPP_TYPE_NAME_FIELD_NUMBER: _ClassVar[int]
    PAGENUM_FIELD_NUMBER: _ClassVar[int]
    TOTALNUM_FIELD_NUMBER: _ClassVar[int]
    data: bytes
    dtp: _ft_types_pb2.byte_data_types
    err: _ft_error_pb2.errstatus
    cpp_type_name: str
    pagenum: int
    totalnum: int
    def __init__(self, data: _Optional[bytes] = ..., dtp: _Optional[_Union[_ft_types_pb2.byte_data_types, str]] = ..., err: _Optional[_Union[_ft_error_pb2.errstatus, _Mapping]] = ..., cpp_type_name: _Optional[str] = ..., pagenum: _Optional[int] = ..., totalnum: _Optional[int] = ...) -> None: ...

class bulkdata_request(_message.Message):
    __slots__ = ("handle", "chunksize")
    HANDLE_FIELD_NUMBER: _ClassVar[int]
    CHUNKSIZE_FIELD_NUMBER: _ClassVar[int]
    handle: handlechooser
    chunksize: int
    def __init__(self, handle: _Optional[_Union[handlechooser, _Mapping]] = ..., chunksize: _Optional[int] = ...) -> None: ...

class devdescribe(_message.Message):
    __slots__ = ("devid", "devtype", "devcomment", "caps")
    DEVID_FIELD_NUMBER: _ClassVar[int]
    DEVTYPE_FIELD_NUMBER: _ClassVar[int]
    DEVCOMMENT_FIELD_NUMBER: _ClassVar[int]
    CAPS_FIELD_NUMBER: _ClassVar[int]
    devid: int
    devtype: str
    devcomment: str
    caps: _containers.RepeatedCompositeFieldContainer[devcapability]
    def __init__(self, devid: _Optional[int] = ..., devtype: _Optional[str] = ..., devcomment: _Optional[str] = ..., caps: _Optional[_Iterable[_Union[devcapability, _Mapping]]] = ...) -> None: ...

class servdescribe(_message.Message):
    __slots__ = ("servcomment", "version", "devs_attached", "err")
    class DevsAttachedEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: int
        value: devdescribe
        def __init__(self, key: _Optional[int] = ..., value: _Optional[_Union[devdescribe, _Mapping]] = ...) -> None: ...
    SERVCOMMENT_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    DEVS_ATTACHED_FIELD_NUMBER: _ClassVar[int]
    ERR_FIELD_NUMBER: _ClassVar[int]
    servcomment: str
    version: str
    devs_attached: _containers.MessageMap[int, devdescribe]
    err: _ft_error_pb2.errstatus
    def __init__(self, servcomment: _Optional[str] = ..., version: _Optional[str] = ..., devs_attached: _Optional[_Mapping[int, devdescribe]] = ..., err: _Optional[_Union[_ft_error_pb2.errstatus, _Mapping]] = ...) -> None: ...

class devicechooser(_message.Message):
    __slots__ = ("devid",)
    DEVID_FIELD_NUMBER: _ClassVar[int]
    devid: int
    def __init__(self, devid: _Optional[int] = ...) -> None: ...

class device_setup_request(_message.Message):
    __slots__ = ("devtypename", "devcomment", "args")
    DEVTYPENAME_FIELD_NUMBER: _ClassVar[int]
    DEVCOMMENT_FIELD_NUMBER: _ClassVar[int]
    ARGS_FIELD_NUMBER: _ClassVar[int]
    devtypename: str
    devcomment: str
    args: _containers.RepeatedCompositeFieldContainer[capability_argument]
    def __init__(self, devtypename: _Optional[str] = ..., devcomment: _Optional[str] = ..., args: _Optional[_Iterable[_Union[capability_argument, _Mapping]]] = ...) -> None: ...

class device_setup_response(_message.Message):
    __slots__ = ("err", "dev")
    ERR_FIELD_NUMBER: _ClassVar[int]
    DEV_FIELD_NUMBER: _ClassVar[int]
    err: _ft_error_pb2.errstatus
    dev: devdescribe
    def __init__(self, err: _Optional[_Union[_ft_error_pb2.errstatus, _Mapping]] = ..., dev: _Optional[_Union[devdescribe, _Mapping]] = ...) -> None: ...

class handlechooser(_message.Message):
    __slots__ = ("handle", "cpp_type_name")
    HANDLE_FIELD_NUMBER: _ClassVar[int]
    CPP_TYPE_NAME_FIELD_NUMBER: _ClassVar[int]
    handle: int
    cpp_type_name: str
    def __init__(self, handle: _Optional[int] = ..., cpp_type_name: _Optional[str] = ...) -> None: ...

class handlelist(_message.Message):
    __slots__ = ("handles",)
    HANDLES_FIELD_NUMBER: _ClassVar[int]
    handles: _containers.RepeatedCompositeFieldContainer[handlechooser]
    def __init__(self, handles: _Optional[_Iterable[_Union[handlechooser, _Mapping]]] = ...) -> None: ...

class stream_control(_message.Message):
    __slots__ = ("req", "cmd", "interval")
    REQ_FIELD_NUMBER: _ClassVar[int]
    CMD_FIELD_NUMBER: _ClassVar[int]
    INTERVAL_FIELD_NUMBER: _ClassVar[int]
    req: capability_request
    cmd: stream_control_commands
    interval: _duration_pb2.Duration
    def __init__(self, req: _Optional[_Union[capability_request, _Mapping]] = ..., cmd: _Optional[_Union[stream_control_commands, str]] = ..., interval: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ...) -> None: ...

class async_control(_message.Message):
    __slots__ = ("req", "cmd")
    REQ_FIELD_NUMBER: _ClassVar[int]
    CMD_FIELD_NUMBER: _ClassVar[int]
    req: capability_request
    cmd: async_control_commands
    def __init__(self, req: _Optional[_Union[capability_request, _Mapping]] = ..., cmd: _Optional[_Union[async_control_commands, str]] = ...) -> None: ...

class async_response(_message.Message):
    __slots__ = ("done", "resp")
    DONE_FIELD_NUMBER: _ClassVar[int]
    RESP_FIELD_NUMBER: _ClassVar[int]
    done: bool
    resp: capability_response
    def __init__(self, done: bool = ..., resp: _Optional[_Union[capability_response, _Mapping]] = ...) -> None: ...

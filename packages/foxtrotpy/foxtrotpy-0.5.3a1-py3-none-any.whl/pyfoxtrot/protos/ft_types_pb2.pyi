from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class simplevalue_types(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    FLOAT_TYPE: _ClassVar[simplevalue_types]
    INT_TYPE: _ClassVar[simplevalue_types]
    UNSIGNED_TYPE: _ClassVar[simplevalue_types]
    BOOL_TYPE: _ClassVar[simplevalue_types]
    STRING_TYPE: _ClassVar[simplevalue_types]
    VOID_TYPE: _ClassVar[simplevalue_types]
    DATETIME_TYPE: _ClassVar[simplevalue_types]
    REMOTE_HANDLE_TYPE: _ClassVar[simplevalue_types]

class byte_data_types(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UCHAR_TYPE: _ClassVar[byte_data_types]
    CHAR_TYPE: _ClassVar[byte_data_types]
    USHORT_TYPE: _ClassVar[byte_data_types]
    UINT_TYPE: _ClassVar[byte_data_types]
    ULONG_TYPE: _ClassVar[byte_data_types]
    SHORT_TYPE: _ClassVar[byte_data_types]
    IINT_TYPE: _ClassVar[byte_data_types]
    LONG_TYPE: _ClassVar[byte_data_types]
    BFLOAT_TYPE: _ClassVar[byte_data_types]
    BDOUBLE_TYPE: _ClassVar[byte_data_types]
    BCOMPLEX_TYPE: _ClassVar[byte_data_types]
    BDATETIME_TYPE: _ClassVar[byte_data_types]
    BOPAQUE_TYPE: _ClassVar[byte_data_types]

class variant_types(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SIMPLEVAR_TYPE: _ClassVar[variant_types]
    STRUCT_TYPE: _ClassVar[variant_types]
    ENUM_TYPE: _ClassVar[variant_types]
    TUPLE_TYPE: _ClassVar[variant_types]
    HOMOG_ARRAY_TYPE: _ClassVar[variant_types]
    UNION_TYPE: _ClassVar[variant_types]
    DYNAMIC_TYPE: _ClassVar[variant_types]
    MAPPING_TYPE: _ClassVar[variant_types]
    NULLABLE_TYPE: _ClassVar[variant_types]
FLOAT_TYPE: simplevalue_types
INT_TYPE: simplevalue_types
UNSIGNED_TYPE: simplevalue_types
BOOL_TYPE: simplevalue_types
STRING_TYPE: simplevalue_types
VOID_TYPE: simplevalue_types
DATETIME_TYPE: simplevalue_types
REMOTE_HANDLE_TYPE: simplevalue_types
UCHAR_TYPE: byte_data_types
CHAR_TYPE: byte_data_types
USHORT_TYPE: byte_data_types
UINT_TYPE: byte_data_types
ULONG_TYPE: byte_data_types
SHORT_TYPE: byte_data_types
IINT_TYPE: byte_data_types
LONG_TYPE: byte_data_types
BFLOAT_TYPE: byte_data_types
BDOUBLE_TYPE: byte_data_types
BCOMPLEX_TYPE: byte_data_types
BDATETIME_TYPE: byte_data_types
BOPAQUE_TYPE: byte_data_types
SIMPLEVAR_TYPE: variant_types
STRUCT_TYPE: variant_types
ENUM_TYPE: variant_types
TUPLE_TYPE: variant_types
HOMOG_ARRAY_TYPE: variant_types
UNION_TYPE: variant_types
DYNAMIC_TYPE: variant_types
MAPPING_TYPE: variant_types
NULLABLE_TYPE: variant_types

class empty(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class variant_descriptor(_message.Message):
    __slots__ = ("variant_type", "simplevalue_type", "simplevalue_sizeof", "struct_desc", "enum_desc", "tuple_desc", "homog_array_desc", "union_desc", "cpp_type_name", "is_nullable", "mapping_desc")
    VARIANT_TYPE_FIELD_NUMBER: _ClassVar[int]
    SIMPLEVALUE_TYPE_FIELD_NUMBER: _ClassVar[int]
    SIMPLEVALUE_SIZEOF_FIELD_NUMBER: _ClassVar[int]
    STRUCT_DESC_FIELD_NUMBER: _ClassVar[int]
    ENUM_DESC_FIELD_NUMBER: _ClassVar[int]
    TUPLE_DESC_FIELD_NUMBER: _ClassVar[int]
    HOMOG_ARRAY_DESC_FIELD_NUMBER: _ClassVar[int]
    UNION_DESC_FIELD_NUMBER: _ClassVar[int]
    CPP_TYPE_NAME_FIELD_NUMBER: _ClassVar[int]
    IS_NULLABLE_FIELD_NUMBER: _ClassVar[int]
    MAPPING_DESC_FIELD_NUMBER: _ClassVar[int]
    variant_type: variant_types
    simplevalue_type: simplevalue_types
    simplevalue_sizeof: int
    struct_desc: struct_descriptor
    enum_desc: enum_descriptor
    tuple_desc: tuple_descriptor
    homog_array_desc: homog_array_descriptor
    union_desc: union_descriptor
    cpp_type_name: str
    is_nullable: bool
    mapping_desc: mapping_descriptor
    def __init__(self, variant_type: _Optional[_Union[variant_types, str]] = ..., simplevalue_type: _Optional[_Union[simplevalue_types, str]] = ..., simplevalue_sizeof: _Optional[int] = ..., struct_desc: _Optional[_Union[struct_descriptor, _Mapping]] = ..., enum_desc: _Optional[_Union[enum_descriptor, _Mapping]] = ..., tuple_desc: _Optional[_Union[tuple_descriptor, _Mapping]] = ..., homog_array_desc: _Optional[_Union[homog_array_descriptor, _Mapping]] = ..., union_desc: _Optional[_Union[union_descriptor, _Mapping]] = ..., cpp_type_name: _Optional[str] = ..., is_nullable: bool = ..., mapping_desc: _Optional[_Union[mapping_descriptor, _Mapping]] = ...) -> None: ...

class mapping_descriptor(_message.Message):
    __slots__ = ("key_type", "value_type")
    KEY_TYPE_FIELD_NUMBER: _ClassVar[int]
    VALUE_TYPE_FIELD_NUMBER: _ClassVar[int]
    key_type: variant_descriptor
    value_type: variant_descriptor
    def __init__(self, key_type: _Optional[_Union[variant_descriptor, _Mapping]] = ..., value_type: _Optional[_Union[variant_descriptor, _Mapping]] = ...) -> None: ...

class struct_descriptor(_message.Message):
    __slots__ = ("struct_name", "struct_map")
    class StructMapEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: variant_descriptor
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[variant_descriptor, _Mapping]] = ...) -> None: ...
    STRUCT_NAME_FIELD_NUMBER: _ClassVar[int]
    STRUCT_MAP_FIELD_NUMBER: _ClassVar[int]
    struct_name: str
    struct_map: _containers.MessageMap[str, variant_descriptor]
    def __init__(self, struct_name: _Optional[str] = ..., struct_map: _Optional[_Mapping[str, variant_descriptor]] = ...) -> None: ...

class enum_descriptor(_message.Message):
    __slots__ = ("enum_name", "enum_map")
    class EnumMapEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: int
        def __init__(self, key: _Optional[str] = ..., value: _Optional[int] = ...) -> None: ...
    ENUM_NAME_FIELD_NUMBER: _ClassVar[int]
    ENUM_MAP_FIELD_NUMBER: _ClassVar[int]
    enum_name: str
    enum_map: _containers.ScalarMap[str, int]
    def __init__(self, enum_name: _Optional[str] = ..., enum_map: _Optional[_Mapping[str, int]] = ...) -> None: ...

class tuple_descriptor(_message.Message):
    __slots__ = ("tuple_map",)
    TUPLE_MAP_FIELD_NUMBER: _ClassVar[int]
    tuple_map: _containers.RepeatedCompositeFieldContainer[variant_descriptor]
    def __init__(self, tuple_map: _Optional[_Iterable[_Union[variant_descriptor, _Mapping]]] = ...) -> None: ...

class homog_array_descriptor(_message.Message):
    __slots__ = ("has_fixed_size", "fixed_size", "value_type")
    HAS_FIXED_SIZE_FIELD_NUMBER: _ClassVar[int]
    FIXED_SIZE_FIELD_NUMBER: _ClassVar[int]
    VALUE_TYPE_FIELD_NUMBER: _ClassVar[int]
    has_fixed_size: bool
    fixed_size: int
    value_type: variant_descriptor
    def __init__(self, has_fixed_size: bool = ..., fixed_size: _Optional[int] = ..., value_type: _Optional[_Union[variant_descriptor, _Mapping]] = ...) -> None: ...

class union_descriptor(_message.Message):
    __slots__ = ("possible_types",)
    POSSIBLE_TYPES_FIELD_NUMBER: _ClassVar[int]
    possible_types: _containers.RepeatedCompositeFieldContainer[variant_descriptor]
    def __init__(self, possible_types: _Optional[_Iterable[_Union[variant_descriptor, _Mapping]]] = ...) -> None: ...

class ft_variant(_message.Message):
    __slots__ = ("simplevar", "structval", "enumval", "tupleval", "arrayval", "mappingval", "null")
    SIMPLEVAR_FIELD_NUMBER: _ClassVar[int]
    STRUCTVAL_FIELD_NUMBER: _ClassVar[int]
    ENUMVAL_FIELD_NUMBER: _ClassVar[int]
    TUPLEVAL_FIELD_NUMBER: _ClassVar[int]
    ARRAYVAL_FIELD_NUMBER: _ClassVar[int]
    MAPPINGVAL_FIELD_NUMBER: _ClassVar[int]
    NULL_FIELD_NUMBER: _ClassVar[int]
    simplevar: ft_simplevariant
    structval: ft_struct
    enumval: ft_enum
    tupleval: ft_tuple
    arrayval: ft_homog_array
    mappingval: ft_mapping
    null: bool
    def __init__(self, simplevar: _Optional[_Union[ft_simplevariant, _Mapping]] = ..., structval: _Optional[_Union[ft_struct, _Mapping]] = ..., enumval: _Optional[_Union[ft_enum, _Mapping]] = ..., tupleval: _Optional[_Union[ft_tuple, _Mapping]] = ..., arrayval: _Optional[_Union[ft_homog_array, _Mapping]] = ..., mappingval: _Optional[_Union[ft_mapping, _Mapping]] = ..., null: bool = ...) -> None: ...

class ft_simplevariant(_message.Message):
    __slots__ = ("dblval", "intval", "uintval", "boolval", "stringval", "tstampval", "handleval", "size", "is_void")
    DBLVAL_FIELD_NUMBER: _ClassVar[int]
    INTVAL_FIELD_NUMBER: _ClassVar[int]
    UINTVAL_FIELD_NUMBER: _ClassVar[int]
    BOOLVAL_FIELD_NUMBER: _ClassVar[int]
    STRINGVAL_FIELD_NUMBER: _ClassVar[int]
    TSTAMPVAL_FIELD_NUMBER: _ClassVar[int]
    HANDLEVAL_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    IS_VOID_FIELD_NUMBER: _ClassVar[int]
    dblval: float
    intval: int
    uintval: int
    boolval: bool
    stringval: str
    tstampval: _timestamp_pb2.Timestamp
    handleval: int
    size: int
    is_void: bool
    def __init__(self, dblval: _Optional[float] = ..., intval: _Optional[int] = ..., uintval: _Optional[int] = ..., boolval: bool = ..., stringval: _Optional[str] = ..., tstampval: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., handleval: _Optional[int] = ..., size: _Optional[int] = ..., is_void: bool = ...) -> None: ...

class ft_mapping(_message.Message):
    __slots__ = ("keys", "values")
    class ValuesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: int
        value: ft_variant
        def __init__(self, key: _Optional[int] = ..., value: _Optional[_Union[ft_variant, _Mapping]] = ...) -> None: ...
    KEYS_FIELD_NUMBER: _ClassVar[int]
    VALUES_FIELD_NUMBER: _ClassVar[int]
    keys: _containers.RepeatedCompositeFieldContainer[ft_variant]
    values: _containers.MessageMap[int, ft_variant]
    def __init__(self, keys: _Optional[_Iterable[_Union[ft_variant, _Mapping]]] = ..., values: _Optional[_Mapping[int, ft_variant]] = ...) -> None: ...

class ft_struct(_message.Message):
    __slots__ = ("struct_name", "value")
    class ValueEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: ft_variant
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[ft_variant, _Mapping]] = ...) -> None: ...
    STRUCT_NAME_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    struct_name: str
    value: _containers.MessageMap[str, ft_variant]
    def __init__(self, struct_name: _Optional[str] = ..., value: _Optional[_Mapping[str, ft_variant]] = ...) -> None: ...

class ft_enum(_message.Message):
    __slots__ = ("desc", "enum_value")
    DESC_FIELD_NUMBER: _ClassVar[int]
    ENUM_VALUE_FIELD_NUMBER: _ClassVar[int]
    desc: enum_descriptor
    enum_value: int
    def __init__(self, desc: _Optional[_Union[enum_descriptor, _Mapping]] = ..., enum_value: _Optional[int] = ...) -> None: ...

class ft_tuple(_message.Message):
    __slots__ = ("value",)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: _containers.RepeatedCompositeFieldContainer[ft_variant]
    def __init__(self, value: _Optional[_Iterable[_Union[ft_variant, _Mapping]]] = ...) -> None: ...

class ft_homog_array(_message.Message):
    __slots__ = ("arr_decoded", "arr_encoded", "arr_heavy")
    ARR_DECODED_FIELD_NUMBER: _ClassVar[int]
    ARR_ENCODED_FIELD_NUMBER: _ClassVar[int]
    ARR_HEAVY_FIELD_NUMBER: _ClassVar[int]
    arr_decoded: ft_homog_array_decoded
    arr_encoded: ft_homog_array_encoded
    arr_heavy: ft_heavy_array
    def __init__(self, arr_decoded: _Optional[_Union[ft_homog_array_decoded, _Mapping]] = ..., arr_encoded: _Optional[_Union[ft_homog_array_encoded, _Mapping]] = ..., arr_heavy: _Optional[_Union[ft_heavy_array, _Mapping]] = ...) -> None: ...

class ft_homog_array_encoded(_message.Message):
    __slots__ = ("dtp", "data")
    DTP_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    dtp: byte_data_types
    data: bytes
    def __init__(self, dtp: _Optional[_Union[byte_data_types, str]] = ..., data: _Optional[bytes] = ...) -> None: ...

class ft_dynamic_type(_message.Message):
    __slots__ = ("value", "desc")
    VALUE_FIELD_NUMBER: _ClassVar[int]
    DESC_FIELD_NUMBER: _ClassVar[int]
    value: ft_variant
    desc: variant_descriptor
    def __init__(self, value: _Optional[_Union[ft_variant, _Mapping]] = ..., desc: _Optional[_Union[variant_descriptor, _Mapping]] = ...) -> None: ...

class ft_heavy_array(_message.Message):
    __slots__ = ("data",)
    DATA_FIELD_NUMBER: _ClassVar[int]
    data: _containers.RepeatedCompositeFieldContainer[ft_variant]
    def __init__(self, data: _Optional[_Iterable[_Union[ft_variant, _Mapping]]] = ...) -> None: ...

class ft_homog_array_decoded(_message.Message):
    __slots__ = ("arr_uint8", "arr_uint16", "arr_sint16", "arr_uint32", "arr_sint32", "arr_uint64", "arr_sint64", "arr_float", "arr_double")
    ARR_UINT8_FIELD_NUMBER: _ClassVar[int]
    ARR_UINT16_FIELD_NUMBER: _ClassVar[int]
    ARR_SINT16_FIELD_NUMBER: _ClassVar[int]
    ARR_UINT32_FIELD_NUMBER: _ClassVar[int]
    ARR_SINT32_FIELD_NUMBER: _ClassVar[int]
    ARR_UINT64_FIELD_NUMBER: _ClassVar[int]
    ARR_SINT64_FIELD_NUMBER: _ClassVar[int]
    ARR_FLOAT_FIELD_NUMBER: _ClassVar[int]
    ARR_DOUBLE_FIELD_NUMBER: _ClassVar[int]
    arr_uint8: ft_uint8_arr
    arr_uint16: ft_uint32_arr
    arr_sint16: ft_sint32_arr
    arr_uint32: ft_uint32_arr
    arr_sint32: ft_sint32_arr
    arr_uint64: ft_uint64_arr
    arr_sint64: ft_sint64_arr
    arr_float: ft_float_arr
    arr_double: ft_double_arr
    def __init__(self, arr_uint8: _Optional[_Union[ft_uint8_arr, _Mapping]] = ..., arr_uint16: _Optional[_Union[ft_uint32_arr, _Mapping]] = ..., arr_sint16: _Optional[_Union[ft_sint32_arr, _Mapping]] = ..., arr_uint32: _Optional[_Union[ft_uint32_arr, _Mapping]] = ..., arr_sint32: _Optional[_Union[ft_sint32_arr, _Mapping]] = ..., arr_uint64: _Optional[_Union[ft_uint64_arr, _Mapping]] = ..., arr_sint64: _Optional[_Union[ft_sint64_arr, _Mapping]] = ..., arr_float: _Optional[_Union[ft_float_arr, _Mapping]] = ..., arr_double: _Optional[_Union[ft_double_arr, _Mapping]] = ...) -> None: ...

class ft_uint8_arr(_message.Message):
    __slots__ = ("values",)
    VALUES_FIELD_NUMBER: _ClassVar[int]
    values: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, values: _Optional[_Iterable[int]] = ...) -> None: ...

class ft_uint16_arr(_message.Message):
    __slots__ = ("values",)
    VALUES_FIELD_NUMBER: _ClassVar[int]
    values: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, values: _Optional[_Iterable[int]] = ...) -> None: ...

class ft_sint16_arr(_message.Message):
    __slots__ = ("values",)
    VALUES_FIELD_NUMBER: _ClassVar[int]
    values: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, values: _Optional[_Iterable[int]] = ...) -> None: ...

class ft_uint32_arr(_message.Message):
    __slots__ = ("values",)
    VALUES_FIELD_NUMBER: _ClassVar[int]
    values: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, values: _Optional[_Iterable[int]] = ...) -> None: ...

class ft_sint32_arr(_message.Message):
    __slots__ = ("values",)
    VALUES_FIELD_NUMBER: _ClassVar[int]
    values: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, values: _Optional[_Iterable[int]] = ...) -> None: ...

class ft_uint64_arr(_message.Message):
    __slots__ = ("values",)
    VALUES_FIELD_NUMBER: _ClassVar[int]
    values: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, values: _Optional[_Iterable[int]] = ...) -> None: ...

class ft_sint64_arr(_message.Message):
    __slots__ = ("values",)
    VALUES_FIELD_NUMBER: _ClassVar[int]
    values: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, values: _Optional[_Iterable[int]] = ...) -> None: ...

class ft_float_arr(_message.Message):
    __slots__ = ("values",)
    VALUES_FIELD_NUMBER: _ClassVar[int]
    values: _containers.RepeatedScalarFieldContainer[float]
    def __init__(self, values: _Optional[_Iterable[float]] = ...) -> None: ...

class ft_double_arr(_message.Message):
    __slots__ = ("values",)
    VALUES_FIELD_NUMBER: _ClassVar[int]
    values: _containers.RepeatedScalarFieldContainer[float]
    def __init__(self, values: _Optional[_Iterable[float]] = ...) -> None: ...

from clavata.shared.v1 import shared_pb2 as _shared_pb2
from google.protobuf import empty_pb2 as _empty_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetRequest(_message.Message):
    __slots__ = ("content_hash", "query_body", "namespace")
    CONTENT_HASH_FIELD_NUMBER: _ClassVar[int]
    QUERY_BODY_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    content_hash: str
    query_body: _shared_pb2.QueryBody
    namespace: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, content_hash: _Optional[str] = ..., query_body: _Optional[_Union[_shared_pb2.QueryBody, _Mapping]] = ..., namespace: _Optional[_Iterable[str]] = ...) -> None: ...

class GetResponse(_message.Message):
    __slots__ = ("result_code", "result")
    class GetResultCode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        GET_RESULT_CODE_UNSPECIFIED: _ClassVar[GetResponse.GetResultCode]
        GET_RESULT_CODE_HIT: _ClassVar[GetResponse.GetResultCode]
        GET_RESULT_CODE_MISS: _ClassVar[GetResponse.GetResultCode]
    GET_RESULT_CODE_UNSPECIFIED: GetResponse.GetResultCode
    GET_RESULT_CODE_HIT: GetResponse.GetResultCode
    GET_RESULT_CODE_MISS: GetResponse.GetResultCode
    RESULT_CODE_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result_code: GetResponse.GetResultCode
    result: _shared_pb2.QueryResultBody
    def __init__(self, result_code: _Optional[_Union[GetResponse.GetResultCode, str]] = ..., result: _Optional[_Union[_shared_pb2.QueryResultBody, _Mapping]] = ...) -> None: ...

class PutRequest(_message.Message):
    __slots__ = ("content_hash", "query", "result", "namespace")
    CONTENT_HASH_FIELD_NUMBER: _ClassVar[int]
    QUERY_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    content_hash: str
    query: _shared_pb2.QueryBody
    result: _shared_pb2.QueryResultBody
    namespace: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, content_hash: _Optional[str] = ..., query: _Optional[_Union[_shared_pb2.QueryBody, _Mapping]] = ..., result: _Optional[_Union[_shared_pb2.QueryResultBody, _Mapping]] = ..., namespace: _Optional[_Iterable[str]] = ...) -> None: ...

class PutResponse(_message.Message):
    __slots__ = ("result_code", "previous")
    class PutResultCode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        PUT_RESULT_CODE_UNSPECIFIED: _ClassVar[PutResponse.PutResultCode]
        PUT_RESULT_CODE_NEW: _ClassVar[PutResponse.PutResultCode]
        PUT_RESULT_CODE_UPDATED: _ClassVar[PutResponse.PutResultCode]
        PUT_RESULT_CODE_FAILED: _ClassVar[PutResponse.PutResultCode]
    PUT_RESULT_CODE_UNSPECIFIED: PutResponse.PutResultCode
    PUT_RESULT_CODE_NEW: PutResponse.PutResultCode
    PUT_RESULT_CODE_UPDATED: PutResponse.PutResultCode
    PUT_RESULT_CODE_FAILED: PutResponse.PutResultCode
    RESULT_CODE_FIELD_NUMBER: _ClassVar[int]
    PREVIOUS_FIELD_NUMBER: _ClassVar[int]
    result_code: PutResponse.PutResultCode
    previous: _shared_pb2.QueryResultBody
    def __init__(self, result_code: _Optional[_Union[PutResponse.PutResultCode, str]] = ..., previous: _Optional[_Union[_shared_pb2.QueryResultBody, _Mapping]] = ...) -> None: ...

class FlushResponse(_message.Message):
    __slots__ = ("result_code",)
    class FlushResultCode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        FLUSH_RESULT_CODE_UNSPECIFIED: _ClassVar[FlushResponse.FlushResultCode]
        FLUSH_RESULT_CODE_SUCCESS: _ClassVar[FlushResponse.FlushResultCode]
        FLUSH_RESULT_CODE_FAILED: _ClassVar[FlushResponse.FlushResultCode]
    FLUSH_RESULT_CODE_UNSPECIFIED: FlushResponse.FlushResultCode
    FLUSH_RESULT_CODE_SUCCESS: FlushResponse.FlushResultCode
    FLUSH_RESULT_CODE_FAILED: FlushResponse.FlushResultCode
    RESULT_CODE_FIELD_NUMBER: _ClassVar[int]
    result_code: FlushResponse.FlushResultCode
    def __init__(self, result_code: _Optional[_Union[FlushResponse.FlushResultCode, str]] = ...) -> None: ...

class BatchGetRequest(_message.Message):
    __slots__ = ("requests",)
    REQUESTS_FIELD_NUMBER: _ClassVar[int]
    requests: _containers.RepeatedCompositeFieldContainer[GetRequest]
    def __init__(self, requests: _Optional[_Iterable[_Union[GetRequest, _Mapping]]] = ...) -> None: ...

class BatchGetResponse(_message.Message):
    __slots__ = ("responses",)
    RESPONSES_FIELD_NUMBER: _ClassVar[int]
    responses: _containers.RepeatedCompositeFieldContainer[GetResponse]
    def __init__(self, responses: _Optional[_Iterable[_Union[GetResponse, _Mapping]]] = ...) -> None: ...

class BatchPutRequest(_message.Message):
    __slots__ = ("requests",)
    REQUESTS_FIELD_NUMBER: _ClassVar[int]
    requests: _containers.RepeatedCompositeFieldContainer[PutRequest]
    def __init__(self, requests: _Optional[_Iterable[_Union[PutRequest, _Mapping]]] = ...) -> None: ...

class BatchPutResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

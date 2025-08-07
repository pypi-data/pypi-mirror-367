from clavata.shared.v1 import public_pb2 as _public_pb2
from clavata.shared.v1 import shared_pb2 as _shared_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DispatchQueryBatchRequest(_message.Message):
    __slots__ = ("content_data", "query_data", "scoped", "overrides")
    class Scoped(_message.Message):
        __slots__ = ("job_id", "customer_id")
        JOB_ID_FIELD_NUMBER: _ClassVar[int]
        CUSTOMER_ID_FIELD_NUMBER: _ClassVar[int]
        job_id: str
        customer_id: str
        def __init__(self, job_id: _Optional[str] = ..., customer_id: _Optional[str] = ...) -> None: ...
    class Overrides(_message.Message):
        __slots__ = ("bypass_cache", "expedited", "bundle_size")
        BYPASS_CACHE_FIELD_NUMBER: _ClassVar[int]
        EXPEDITED_FIELD_NUMBER: _ClassVar[int]
        BUNDLE_SIZE_FIELD_NUMBER: _ClassVar[int]
        bypass_cache: bool
        expedited: bool
        bundle_size: int
        def __init__(self, bypass_cache: bool = ..., expedited: bool = ..., bundle_size: _Optional[int] = ...) -> None: ...
    CONTENT_DATA_FIELD_NUMBER: _ClassVar[int]
    QUERY_DATA_FIELD_NUMBER: _ClassVar[int]
    SCOPED_FIELD_NUMBER: _ClassVar[int]
    OVERRIDES_FIELD_NUMBER: _ClassVar[int]
    content_data: _public_pb2.ContentData
    query_data: _containers.RepeatedCompositeFieldContainer[_shared_pb2.QueryBody]
    scoped: DispatchQueryBatchRequest.Scoped
    overrides: DispatchQueryBatchRequest.Overrides
    def __init__(self, content_data: _Optional[_Union[_public_pb2.ContentData, _Mapping]] = ..., query_data: _Optional[_Iterable[_Union[_shared_pb2.QueryBody, _Mapping]]] = ..., scoped: _Optional[_Union[DispatchQueryBatchRequest.Scoped, _Mapping]] = ..., overrides: _Optional[_Union[DispatchQueryBatchRequest.Overrides, _Mapping]] = ...) -> None: ...

class DispatchQueryBatchResponse(_message.Message):
    __slots__ = ("results",)
    class Body(_message.Message):
        __slots__ = ("content_hash", "score", "query_data", "query_id")
        CONTENT_HASH_FIELD_NUMBER: _ClassVar[int]
        SCORE_FIELD_NUMBER: _ClassVar[int]
        QUERY_DATA_FIELD_NUMBER: _ClassVar[int]
        QUERY_ID_FIELD_NUMBER: _ClassVar[int]
        content_hash: str
        score: float
        query_data: _shared_pb2.QueryBody
        query_id: str
        def __init__(self, content_hash: _Optional[str] = ..., score: _Optional[float] = ..., query_data: _Optional[_Union[_shared_pb2.QueryBody, _Mapping]] = ..., query_id: _Optional[str] = ...) -> None: ...
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    results: _containers.RepeatedCompositeFieldContainer[DispatchQueryBatchResponse.Body]
    def __init__(self, results: _Optional[_Iterable[_Union[DispatchQueryBatchResponse.Body, _Mapping]]] = ...) -> None: ...

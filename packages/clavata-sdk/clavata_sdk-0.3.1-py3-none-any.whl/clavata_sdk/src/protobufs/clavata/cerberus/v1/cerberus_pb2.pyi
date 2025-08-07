from google.protobuf import empty_pb2 as _empty_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Image(_message.Message):
    __slots__ = ("image_bytes", "image_url", "image_hash")
    IMAGE_BYTES_FIELD_NUMBER: _ClassVar[int]
    IMAGE_URL_FIELD_NUMBER: _ClassVar[int]
    IMAGE_HASH_FIELD_NUMBER: _ClassVar[int]
    image_bytes: bytes
    image_url: str
    image_hash: str
    def __init__(self, image_bytes: _Optional[bytes] = ..., image_url: _Optional[str] = ..., image_hash: _Optional[str] = ...) -> None: ...

class AnalyzeImageRequest(_message.Message):
    __slots__ = ("images",)
    IMAGES_FIELD_NUMBER: _ClassVar[int]
    images: _containers.RepeatedCompositeFieldContainer[Image]
    def __init__(self, images: _Optional[_Iterable[_Union[Image, _Mapping]]] = ...) -> None: ...

class AnalysisMetrics(_message.Message):
    __slots__ = ("load_time_ms", "hash_generation_time_ms", "matching_time_ms", "total_time_ms")
    LOAD_TIME_MS_FIELD_NUMBER: _ClassVar[int]
    HASH_GENERATION_TIME_MS_FIELD_NUMBER: _ClassVar[int]
    MATCHING_TIME_MS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_TIME_MS_FIELD_NUMBER: _ClassVar[int]
    load_time_ms: float
    hash_generation_time_ms: float
    matching_time_ms: float
    total_time_ms: float
    def __init__(self, load_time_ms: _Optional[float] = ..., hash_generation_time_ms: _Optional[float] = ..., matching_time_ms: _Optional[float] = ..., total_time_ms: _Optional[float] = ...) -> None: ...

class AnalysisMetadata(_message.Message):
    __slots__ = ("metrics",)
    METRICS_FIELD_NUMBER: _ClassVar[int]
    metrics: AnalysisMetrics
    def __init__(self, metrics: _Optional[_Union[AnalysisMetrics, _Mapping]] = ...) -> None: ...

class AnalysisResults(_message.Message):
    __slots__ = ("harmful", "metadata")
    HARMFUL_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    harmful: bool
    metadata: AnalysisMetadata
    def __init__(self, harmful: bool = ..., metadata: _Optional[_Union[AnalysisMetadata, _Mapping]] = ...) -> None: ...

class AnalyzeImageResponse(_message.Message):
    __slots__ = ("results",)
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    results: _containers.RepeatedCompositeFieldContainer[AnalysisResults]
    def __init__(self, results: _Optional[_Iterable[_Union[AnalysisResults, _Mapping]]] = ...) -> None: ...

class ReloadReferenceSetResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...

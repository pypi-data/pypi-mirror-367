from clavata.shared.v1 import public_pb2 as _public_pb2
from clavata.shared.v1 import shared_pb2 as _shared_pb2
from clavata.socratic.v1 import ast_pb2 as _ast_pb2
from clavata.socratic.v1 import features_pb2 as _features_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class EvaluateRequest(_message.Message):
    __slots__ = ("content_data", "version_blob", "code", "job_id", "customer_id", "threshold")
    CONTENT_DATA_FIELD_NUMBER: _ClassVar[int]
    VERSION_BLOB_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    CUSTOMER_ID_FIELD_NUMBER: _ClassVar[int]
    THRESHOLD_FIELD_NUMBER: _ClassVar[int]
    content_data: _public_pb2.ContentData
    version_blob: PolicyVersionBlob
    code: str
    job_id: str
    customer_id: str
    threshold: float
    def __init__(self, content_data: _Optional[_Union[_public_pb2.ContentData, _Mapping]] = ..., version_blob: _Optional[_Union[PolicyVersionBlob, _Mapping]] = ..., code: _Optional[str] = ..., job_id: _Optional[str] = ..., customer_id: _Optional[str] = ..., threshold: _Optional[float] = ...) -> None: ...

class EvaluateStreamRequest(_message.Message):
    __slots__ = ("content_data", "version_blob", "code", "job_id", "customer_id", "threshold")
    CONTENT_DATA_FIELD_NUMBER: _ClassVar[int]
    VERSION_BLOB_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    CUSTOMER_ID_FIELD_NUMBER: _ClassVar[int]
    THRESHOLD_FIELD_NUMBER: _ClassVar[int]
    content_data: _containers.RepeatedCompositeFieldContainer[_public_pb2.ContentData]
    version_blob: PolicyVersionBlob
    code: str
    job_id: str
    customer_id: str
    threshold: float
    def __init__(self, content_data: _Optional[_Iterable[_Union[_public_pb2.ContentData, _Mapping]]] = ..., version_blob: _Optional[_Union[PolicyVersionBlob, _Mapping]] = ..., code: _Optional[str] = ..., job_id: _Optional[str] = ..., customer_id: _Optional[str] = ..., threshold: _Optional[float] = ...) -> None: ...

class EvaluateResponse(_message.Message):
    __slots__ = ("report", "job_id")
    REPORT_FIELD_NUMBER: _ClassVar[int]
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    report: _public_pb2.PolicyEvaluationReport
    job_id: str
    def __init__(self, report: _Optional[_Union[_public_pb2.PolicyEvaluationReport, _Mapping]] = ..., job_id: _Optional[str] = ...) -> None: ...

class PolicyVersionBlob(_message.Message):
    __slots__ = ("id", "version_id", "key", "success", "policy_blob", "error", "customer_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    VERSION_ID_FIELD_NUMBER: _ClassVar[int]
    KEY_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    POLICY_BLOB_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    CUSTOMER_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    version_id: str
    key: str
    success: bool
    policy_blob: bytes
    error: _shared_pb2.CompilationError
    customer_id: str
    def __init__(self, id: _Optional[str] = ..., version_id: _Optional[str] = ..., key: _Optional[str] = ..., success: bool = ..., policy_blob: _Optional[bytes] = ..., error: _Optional[_Union[_shared_pb2.CompilationError, _Mapping]] = ..., customer_id: _Optional[str] = ...) -> None: ...

class CompileVersionResult(_message.Message):
    __slots__ = ("code", "dto_revision", "compiled")
    class Representation(_message.Message):
        __slots__ = ("root_node", "feature_set")
        ROOT_NODE_FIELD_NUMBER: _ClassVar[int]
        FEATURE_SET_FIELD_NUMBER: _ClassVar[int]
        root_node: _ast_pb2.RootNode
        feature_set: _features_pb2.FeatureSet
        def __init__(self, root_node: _Optional[_Union[_ast_pb2.RootNode, _Mapping]] = ..., feature_set: _Optional[_Union[_features_pb2.FeatureSet, _Mapping]] = ...) -> None: ...
    CODE_FIELD_NUMBER: _ClassVar[int]
    DTO_REVISION_FIELD_NUMBER: _ClassVar[int]
    COMPILED_FIELD_NUMBER: _ClassVar[int]
    code: str
    dto_revision: int
    compiled: CompileVersionResult.Representation
    def __init__(self, code: _Optional[str] = ..., dto_revision: _Optional[int] = ..., compiled: _Optional[_Union[CompileVersionResult.Representation, _Mapping]] = ...) -> None: ...

class CompileVersionRequest(_message.Message):
    __slots__ = ("code", "lint_only", "customer_id")
    CODE_FIELD_NUMBER: _ClassVar[int]
    LINT_ONLY_FIELD_NUMBER: _ClassVar[int]
    CUSTOMER_ID_FIELD_NUMBER: _ClassVar[int]
    code: str
    lint_only: bool
    customer_id: str
    def __init__(self, code: _Optional[str] = ..., lint_only: bool = ..., customer_id: _Optional[str] = ...) -> None: ...

class CompileVersionResponse(_message.Message):
    __slots__ = ("result", "error")
    RESULT_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    result: CompileVersionResult
    error: _shared_pb2.CompilationError
    def __init__(self, result: _Optional[_Union[CompileVersionResult, _Mapping]] = ..., error: _Optional[_Union[_shared_pb2.CompilationError, _Mapping]] = ...) -> None: ...

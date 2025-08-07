from clavata.shared.v1 import public_pb2 as _public_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GeneratePolicyRequest(_message.Message):
    __slots__ = ("contents", "customer_id", "generate_policy_task_id")
    CONTENTS_FIELD_NUMBER: _ClassVar[int]
    CUSTOMER_ID_FIELD_NUMBER: _ClassVar[int]
    GENERATE_POLICY_TASK_ID_FIELD_NUMBER: _ClassVar[int]
    contents: _containers.RepeatedCompositeFieldContainer[_public_pb2.ContentData]
    customer_id: str
    generate_policy_task_id: str
    def __init__(self, contents: _Optional[_Iterable[_Union[_public_pb2.ContentData, _Mapping]]] = ..., customer_id: _Optional[str] = ..., generate_policy_task_id: _Optional[str] = ...) -> None: ...

class GeneratePolicyResponse(_message.Message):
    __slots__ = ("policy_text",)
    POLICY_TEXT_FIELD_NUMBER: _ClassVar[int]
    policy_text: str
    def __init__(self, policy_text: _Optional[str] = ...) -> None: ...

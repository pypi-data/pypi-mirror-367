from clavata.shared.v1 import public_pb2 as _public_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Operator(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    OPERATOR_UNSPECIFIED: _ClassVar[Operator]
    OPERATOR_AND: _ClassVar[Operator]
    OPERATOR_OR: _ClassVar[Operator]
    OPERATOR_NOT: _ClassVar[Operator]
    OPERATOR_ALL: _ClassVar[Operator]
    OPERATOR_ANY: _ClassVar[Operator]
    OPERATOR_NONE: _ClassVar[Operator]
    OPERATOR_RAW: _ClassVar[Operator]
    OPERATOR_SENTIMENT: _ClassVar[Operator]
    OPERATOR_FUZZY: _ClassVar[Operator]
    OPERATOR_EXACT: _ClassVar[Operator]
OPERATOR_UNSPECIFIED: Operator
OPERATOR_AND: Operator
OPERATOR_OR: Operator
OPERATOR_NOT: Operator
OPERATOR_ALL: Operator
OPERATOR_ANY: Operator
OPERATOR_NONE: Operator
OPERATOR_RAW: Operator
OPERATOR_SENTIMENT: Operator
OPERATOR_FUZZY: Operator
OPERATOR_EXACT: Operator

class FeatureNode(_message.Message):
    __slots__ = ("feature_id", "expression", "source_range")
    FEATURE_ID_FIELD_NUMBER: _ClassVar[int]
    EXPRESSION_FIELD_NUMBER: _ClassVar[int]
    SOURCE_RANGE_FIELD_NUMBER: _ClassVar[int]
    feature_id: int
    expression: str
    source_range: _public_pb2.SourceRange
    def __init__(self, feature_id: _Optional[int] = ..., expression: _Optional[str] = ..., source_range: _Optional[_Union[_public_pb2.SourceRange, _Mapping]] = ...) -> None: ...

class LogicNode(_message.Message):
    __slots__ = ("operator", "children", "source_range")
    OPERATOR_FIELD_NUMBER: _ClassVar[int]
    CHILDREN_FIELD_NUMBER: _ClassVar[int]
    SOURCE_RANGE_FIELD_NUMBER: _ClassVar[int]
    operator: Operator
    children: _containers.RepeatedCompositeFieldContainer[InternalNode]
    source_range: _public_pb2.SourceRange
    def __init__(self, operator: _Optional[_Union[Operator, str]] = ..., children: _Optional[_Iterable[_Union[InternalNode, _Mapping]]] = ..., source_range: _Optional[_Union[_public_pb2.SourceRange, _Mapping]] = ...) -> None: ...

class InternalNode(_message.Message):
    __slots__ = ("logic_node", "feature_node", "source_range")
    LOGIC_NODE_FIELD_NUMBER: _ClassVar[int]
    FEATURE_NODE_FIELD_NUMBER: _ClassVar[int]
    SOURCE_RANGE_FIELD_NUMBER: _ClassVar[int]
    logic_node: LogicNode
    feature_node: FeatureNode
    source_range: _public_pb2.SourceRange
    def __init__(self, logic_node: _Optional[_Union[LogicNode, _Mapping]] = ..., feature_node: _Optional[_Union[FeatureNode, _Mapping]] = ..., source_range: _Optional[_Union[_public_pb2.SourceRange, _Mapping]] = ...) -> None: ...

class AssertionNode(_message.Message):
    __slots__ = ("expr", "source_range")
    EXPR_FIELD_NUMBER: _ClassVar[int]
    SOURCE_RANGE_FIELD_NUMBER: _ClassVar[int]
    expr: InternalNode
    source_range: _public_pb2.SourceRange
    def __init__(self, expr: _Optional[_Union[InternalNode, _Mapping]] = ..., source_range: _Optional[_Union[_public_pb2.SourceRange, _Mapping]] = ...) -> None: ...

class UnlessNode(_message.Message):
    __slots__ = ("assertions", "source_range")
    ASSERTIONS_FIELD_NUMBER: _ClassVar[int]
    SOURCE_RANGE_FIELD_NUMBER: _ClassVar[int]
    assertions: _containers.RepeatedCompositeFieldContainer[AssertionNode]
    source_range: _public_pb2.SourceRange
    def __init__(self, assertions: _Optional[_Iterable[_Union[AssertionNode, _Mapping]]] = ..., source_range: _Optional[_Union[_public_pb2.SourceRange, _Mapping]] = ...) -> None: ...

class LabelNode(_message.Message):
    __slots__ = ("name", "message", "assertions", "unless", "unless_labels", "source_range")
    NAME_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    ASSERTIONS_FIELD_NUMBER: _ClassVar[int]
    UNLESS_FIELD_NUMBER: _ClassVar[int]
    UNLESS_LABELS_FIELD_NUMBER: _ClassVar[int]
    SOURCE_RANGE_FIELD_NUMBER: _ClassVar[int]
    name: str
    message: str
    assertions: _containers.RepeatedCompositeFieldContainer[AssertionNode]
    unless: UnlessNode
    unless_labels: _containers.RepeatedScalarFieldContainer[str]
    source_range: _public_pb2.SourceRange
    def __init__(self, name: _Optional[str] = ..., message: _Optional[str] = ..., assertions: _Optional[_Iterable[_Union[AssertionNode, _Mapping]]] = ..., unless: _Optional[_Union[UnlessNode, _Mapping]] = ..., unless_labels: _Optional[_Iterable[str]] = ..., source_range: _Optional[_Union[_public_pb2.SourceRange, _Mapping]] = ...) -> None: ...

class RootNode(_message.Message):
    __slots__ = ("labels", "unless")
    LABELS_FIELD_NUMBER: _ClassVar[int]
    UNLESS_FIELD_NUMBER: _ClassVar[int]
    labels: _containers.RepeatedCompositeFieldContainer[LabelNode]
    unless: UnlessNode
    def __init__(self, labels: _Optional[_Iterable[_Union[LabelNode, _Mapping]]] = ..., unless: _Optional[_Union[UnlessNode, _Mapping]] = ...) -> None: ...

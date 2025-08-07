from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class FeatureType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    FEATURE_TYPE_UNSPECIFIED: _ClassVar[FeatureType]
    FEATURE_TYPE_OBJECT: _ClassVar[FeatureType]
    FEATURE_TYPE_CONCEPT: _ClassVar[FeatureType]
    FEATURE_TYPE_RAW: _ClassVar[FeatureType]
    FEATURE_TYPE_SENTIMENT: _ClassVar[FeatureType]
    FEATURE_TYPE_FUZZY: _ClassVar[FeatureType]
    FEATURE_TYPE_EXACT: _ClassVar[FeatureType]
FEATURE_TYPE_UNSPECIFIED: FeatureType
FEATURE_TYPE_OBJECT: FeatureType
FEATURE_TYPE_CONCEPT: FeatureType
FEATURE_TYPE_RAW: FeatureType
FEATURE_TYPE_SENTIMENT: FeatureType
FEATURE_TYPE_FUZZY: FeatureType
FEATURE_TYPE_EXACT: FeatureType

class Feature(_message.Message):
    __slots__ = ("feature_id", "type", "value", "context")
    class Context(_message.Message):
        __slots__ = ("relationship", "value")
        RELATIONSHIP_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        relationship: str
        value: str
        def __init__(self, relationship: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    FEATURE_ID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    CONTEXT_FIELD_NUMBER: _ClassVar[int]
    feature_id: int
    type: FeatureType
    value: str
    context: Feature.Context
    def __init__(self, feature_id: _Optional[int] = ..., type: _Optional[_Union[FeatureType, str]] = ..., value: _Optional[str] = ..., context: _Optional[_Union[Feature.Context, _Mapping]] = ...) -> None: ...

class FeatureSet(_message.Message):
    __slots__ = ("features",)
    FEATURES_FIELD_NUMBER: _ClassVar[int]
    features: _containers.RepeatedCompositeFieldContainer[Feature]
    def __init__(self, features: _Optional[_Iterable[_Union[Feature, _Mapping]]] = ...) -> None: ...

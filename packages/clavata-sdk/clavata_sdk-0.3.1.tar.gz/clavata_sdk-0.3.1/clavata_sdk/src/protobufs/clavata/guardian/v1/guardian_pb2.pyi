from clavata.shared.v1 import shared_pb2 as _shared_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AuthResponseType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    AUTH_RESPONSE_TYPE_UNSPECIFIED: _ClassVar[AuthResponseType]
    AUTH_RESPONSE_TYPE_INIT: _ClassVar[AuthResponseType]
    AUTH_RESPONSE_TYPE_SUCCESS: _ClassVar[AuthResponseType]
    AUTH_RESPONSE_TYPE_FAILURE: _ClassVar[AuthResponseType]
AUTH_RESPONSE_TYPE_UNSPECIFIED: AuthResponseType
AUTH_RESPONSE_TYPE_INIT: AuthResponseType
AUTH_RESPONSE_TYPE_SUCCESS: AuthResponseType
AUTH_RESPONSE_TYPE_FAILURE: AuthResponseType

class LoginRequest(_message.Message):
    __slots__ = ("email",)
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    email: str
    def __init__(self, email: _Optional[str] = ...) -> None: ...

class LoginResponse(_message.Message):
    __slots__ = ("type", "url", "user_info", "error")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    USER_INFO_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    type: AuthResponseType
    url: str
    user_info: _shared_pb2.UserInfo
    error: str
    def __init__(self, type: _Optional[_Union[AuthResponseType, str]] = ..., url: _Optional[str] = ..., user_info: _Optional[_Union[_shared_pb2.UserInfo, _Mapping]] = ..., error: _Optional[str] = ...) -> None: ...

class RegisterRequest(_message.Message):
    __slots__ = ("email",)
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    email: str
    def __init__(self, email: _Optional[str] = ...) -> None: ...

class RegisterResponse(_message.Message):
    __slots__ = ("type", "redirect_url", "user_info", "error")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    REDIRECT_URL_FIELD_NUMBER: _ClassVar[int]
    USER_INFO_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    type: AuthResponseType
    redirect_url: str
    user_info: _shared_pb2.UserInfo
    error: str
    def __init__(self, type: _Optional[_Union[AuthResponseType, str]] = ..., redirect_url: _Optional[str] = ..., user_info: _Optional[_Union[_shared_pb2.UserInfo, _Mapping]] = ..., error: _Optional[str] = ...) -> None: ...

class LogoutRequest(_message.Message):
    __slots__ = ("user_info",)
    USER_INFO_FIELD_NUMBER: _ClassVar[int]
    user_info: _shared_pb2.UserInfo
    def __init__(self, user_info: _Optional[_Union[_shared_pb2.UserInfo, _Mapping]] = ...) -> None: ...

class LogoutResponse(_message.Message):
    __slots__ = ("url", "error")
    URL_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    url: str
    error: str
    def __init__(self, url: _Optional[str] = ..., error: _Optional[str] = ...) -> None: ...

class ValidateRequest(_message.Message):
    __slots__ = ("user_info",)
    USER_INFO_FIELD_NUMBER: _ClassVar[int]
    user_info: _shared_pb2.UserInfo
    def __init__(self, user_info: _Optional[_Union[_shared_pb2.UserInfo, _Mapping]] = ...) -> None: ...

class ValidateResponse(_message.Message):
    __slots__ = ("user_info",)
    USER_INFO_FIELD_NUMBER: _ClassVar[int]
    user_info: _shared_pb2.UserInfo
    def __init__(self, user_info: _Optional[_Union[_shared_pb2.UserInfo, _Mapping]] = ...) -> None: ...

class ExchangeCognitoAccessTokenRequest(_message.Message):
    __slots__ = ("cognito_access_token",)
    COGNITO_ACCESS_TOKEN_FIELD_NUMBER: _ClassVar[int]
    cognito_access_token: str
    def __init__(self, cognito_access_token: _Optional[str] = ...) -> None: ...

class ExchangeCognitoAccessTokenResponse(_message.Message):
    __slots__ = ("user_info",)
    USER_INFO_FIELD_NUMBER: _ClassVar[int]
    user_info: _shared_pb2.UserInfo
    def __init__(self, user_info: _Optional[_Union[_shared_pb2.UserInfo, _Mapping]] = ...) -> None: ...

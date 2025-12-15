from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class InvoiceRecognizeReq(_message.Message):
    __slots__ = ("file_name", "flag")
    FILE_NAME_FIELD_NUMBER: _ClassVar[int]
    FLAG_FIELD_NUMBER: _ClassVar[int]
    file_name: str
    flag: int
    def __init__(self, file_name: _Optional[str] = ..., flag: _Optional[int] = ...) -> None: ...

class InvoiceRecognizeResp(_message.Message):
    __slots__ = ("result", "msg", "id")
    RESULT_FIELD_NUMBER: _ClassVar[int]
    MSG_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    result: int
    msg: str
    id: str
    def __init__(self, result: _Optional[int] = ..., msg: _Optional[str] = ..., id: _Optional[str] = ...) -> None: ...

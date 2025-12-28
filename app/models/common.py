from typing import Generic, TypeVar, Optional
from pydantic import BaseModel

T = TypeVar('T')


class ApiResponse(BaseModel, Generic[T]):
    code: int = 0
    msg: str = ""
    data: Optional[T] = None
    traceId: Optional[str] = None

    @classmethod
    def success(cls, data: T = None, msg: str = ""):
        return cls(code=0, msg=msg, data=data)

    @classmethod
    def error(cls, code: int = 500, msg: str = "Internal Server Error", trace_id: str = None):
        return cls(code=code, msg=msg, data=None, traceId=trace_id)

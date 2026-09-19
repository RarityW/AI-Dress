import time
from typing import Any, Generic, TypeVar, Optional
from pydantic import BaseModel, Field

T = TypeVar('T')

class ApiResponse(BaseModel, Generic[T]):
    code: int = Field(default=200)
    success: bool = Field(default=True)
    message: str = Field(default="操作成功")
    data: Optional[T] = None
    request_id: str = Field(default="")
    timestamp: float = Field(default_factory=time.time)

def success_response(data: Any = None, message: str = "操作成功") -> ApiResponse:
    return ApiResponse(code=200, success=True, message=message, data=data)

def error_response(code: int = 400, message: str = "操作失败") -> ApiResponse:
    return ApiResponse(code=code, success=False, message=message, data=None)

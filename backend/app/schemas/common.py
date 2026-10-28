from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class StandardErrorDetail(BaseModel):
    code: str
    message: str
    request_id: str


class StandardErrorResponse(BaseModel):
    error: StandardErrorDetail


class MessageResponse(BaseModel):
    message: str
    success: bool = True

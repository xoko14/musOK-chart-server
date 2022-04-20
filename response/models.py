from pydantic import BaseModel

class HTTPException(BaseModel):
    detail: str
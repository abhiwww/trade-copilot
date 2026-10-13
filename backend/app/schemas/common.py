from pydantic import BaseModel

class PaginationParams(BaseModel):
    limit: int = 10
    offset: int = 0

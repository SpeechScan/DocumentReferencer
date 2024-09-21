from typing import List
from pydantic import BaseModel, Field

class Statement(BaseModel):
    statement: str = Field(description="A statement said by a person")
    isStatementTrue: bool = Field(
        description="Can statement be confirmed by your knowledge?"
    )
    rejectionReasons: List[str] = Field(
        description="Array of sections from your knowledge based on which you rejected the statement. If statement is not false and can be confirmed by your knowledge, then make this array empty."
    )

from pydantic import BaseModel
from typing import List

class ChatReq(BaseModel):
    message: str

class ChatRes(BaseModel):
    reply: str
    providers: List[str]

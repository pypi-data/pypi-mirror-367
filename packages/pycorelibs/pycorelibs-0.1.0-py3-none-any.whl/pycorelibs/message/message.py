from pydantic import BaseModel,Field
from typing import Optional
from datetime import datetime as dt
import uuid

class MessageModel(BaseModel):
    text: str
    msg_id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))  # 从 Redis pop 时注入
    priority: Optional[int] = 0  # 消息优先级
    created: Optional[float] = Field(default_factory=lambda: dt.now().timestamp()) # 消息创建时间

# -*- coding: utf-8 -*-
from typing import Dict, Any
from pydantic import BaseModel, Field
import uuid
from datetime import datetime

class CycleHistoryRecord(BaseModel):
    id: str = Field(default_factory=lambda: f"ch_{uuid.uuid4()}", description="本条循环历史记录的唯一ID。")
    session_id: str = Field(description="关联的会话ID。")
    cycle_index: int = Field(description="外循环的轮次序号，从0或1开始。")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z", description="记录产生的UTC时间戳(UTC ISO8601)。")
    mcp: Dict[str, Any] = Field(description="该轮次结束时的 MCP 快照(JSON)。")
    working_memory: Dict[str, Any] = Field(description="该轮次结束时的 WorkingMemory 快照(JSON)。")
    cognition: Dict[str, Any] = Field(default_factory=dict, description="该轮次的 cognition 策略快照或增量(JSON)。")
    extras: Dict[str, Any] = Field(default_factory=dict, description="其他与该轮次相关的上下文或元数据(JSON)。")

    class Config:
        validate_assignment = True
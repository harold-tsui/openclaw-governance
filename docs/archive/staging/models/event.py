"""
AnomalyEvent 数据类
NUCLEUS-4.0 D1 - 事件模型定义

定义质量管理系统中的核心异常事件数据结构。
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional
import json


@dataclass
class AnomalyEvent:
    """
    异常事件数据类
    
    属性：
        event_id: 唯一标识符（UUID）
        timestamp: 事件发生时间
        anomaly_type: 异常类型（如 'welding_defect', 'dimension_deviation', 'equipment_failure'）
        severity: 严重度（1-10）
        occurrence: 发生频率（1-10）
        detection_difficulty: 检测难度（1-10）
        rpn: 风险优先级数（S×O×D，自动计算）
        location: 发生位置（如 'Assembly-Line-01', 'Welding-Station-A'）
        description: 异常描述
        tags: 标签列表（用于知识检索）
        source: 数据来源（'real', 'standard', 'inferred'）
        created_by: 创建者
        metadata: 额外元数据
    """
    
    anomaly_type: str
    severity: int
    occurrence: int
    detection_difficulty: int
    location: str
    description: str
    tags: list[str] = field(default_factory=list)
    source: str = 'real'  # 'real', 'standard', 'inferred'
    event_id: Optional[str] = None
    timestamp: Optional[str] = None
    rpn: Optional[int] = None
    created_by: str = 'system'
    metadata: dict = field(default_factory=dict)
    
    def __post_init__(self):
        """初始化后处理：自动计算 RPN 和生成 ID/时间戳"""
        # 验证字段范围
        self._validate_fields()
        
        # 自动计算 RPN
        if self.rpn is None:
            self.rpn = self.severity * self.occurrence * self.detection_difficulty
        
        # 自动生成 UUID
        if self.event_id is None:
            import uuid
            self.event_id = str(uuid.uuid4())
        
        # 自动生成时间戳
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
        
        # 自动标注推断数据来源
        if self.source == 'inferred' and 'source' not in self.metadata:
            self.metadata['source'] = 'inferred'
    
    def _validate_fields(self):
        """验证字段范围"""
        if not 1 <= self.severity <= 10:
            raise ValueError(f"severity 必须在 1-10 之间，当前值：{self.severity}")
        if not 1 <= self.occurrence <= 10:
            raise ValueError(f"occurrence 必须在 1-10 之间，当前值：{self.occurrence}")
        if not 1 <= self.detection_difficulty <= 10:
            raise ValueError(f"detection_difficulty 必须在 1-10 之间，当前值：{self.detection_difficulty}")
        if self.source not in ['real', 'standard', 'inferred']:
            raise ValueError(f"source 必须是 'real', 'standard' 或 'inferred'，当前值：{self.source}")
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return asdict(self)
    
    def to_json(self) -> str:
        """序列化为 JSON 字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'AnomalyEvent':
        """从字典创建实例"""
        return cls(**data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'AnomalyEvent':
        """从 JSON 字符串创建实例"""
        return cls.from_dict(json.loads(json_str))
    
    def get_common_tags(self, other: 'AnomalyEvent') -> list[str]:
        """获取与另一个事件的共同标签"""
        return list(set(self.tags) & set(other.tags))
    
    def is_similar_to(self, other: 'AnomalyEvent', min_common_tags: int = 2) -> bool:
        """
        判断是否与另一个事件相似（用于知识检索）
        
        相似度判断标准：至少 min_common_tags 个共同标签
        """
        return len(self.get_common_tags(other)) >= min_common_tags
    
    def __str__(self) -> str:
        return f"AnomalyEvent(id={self.event_id[:8]}..., type={self.anomaly_type}, RPN={self.rpn})"
    
    def __repr__(self) -> str:
        return self.__str__()

"""
ILearn - 知识学习接口
NUCLEUS-4.0 D2 - 核心接口定义

定义知识学习模块的抽象接口。
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

# 使用相对导入
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.event import AnomalyEvent
from interfaces.act import ExecutionResult


class KnowledgeType(Enum):
    """知识类型枚举"""
    LESSON = 'lesson'           # 经验教训
    SOLUTION = 'solution'       # 解决方案
    PATTERN = 'pattern'         # 异常模式
    THRESHOLD = 'threshold'     # 阈值调整
    RULE = 'rule'               # 决策规则


@dataclass
class Knowledge:
    """
    知识条目
    
    属性：
        knowledge_id: 知识 ID
        knowledge_type: 知识类型
        title: 标题
        content: 内容
        keywords: 关键词列表（用于检索）
        related_events: 相关事件 ID 列表
        effectiveness: 有效性评分（0-100）
        created_at: 创建时间
        updated_at: 更新时间
        source: 来源（'auto', 'manual', 'inferred'）
        metadata: 额外元数据
    """
    knowledge_id: str
    knowledge_type: KnowledgeType
    title: str
    content: str
    keywords: List[str] = None
    related_events: List[str] = None
    effectiveness: int = 0
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    source: str = 'auto'
    metadata: dict = None
    
    def __post_init__(self):
        if self.keywords is None:
            self.keywords = []
        if self.related_events is None:
            self.related_events = []
        if self.metadata is None:
            self.metadata = {}
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.updated_at is None:
            self.updated_at = self.created_at


class ILearn(ABC):
    """
    知识学习接口
    
    负责从执行结果中提取知识，并提供知识检索功能。
    
    核心方法：
        record(): 记录新知识
        retrieve_similar(): 检索相似知识（核心知识复用功能）
        update_effectiveness(): 更新知识有效性
        get_all(): 获取所有知识
    """
    
    @abstractmethod
    def record(self, event: AnomalyEvent, result: ExecutionResult) -> Optional[Knowledge]:
        """
        从执行结果中提取并记录知识
        
        参数：
            event: 异常事件
            result: 执行结果
            
        返回值：
            Optional[Knowledge]: 提取的知识条目（如果值得记录），否则 None
        """
        pass
    
    @abstractmethod
    def retrieve_similar(self, event: AnomalyEvent, limit: int = 5) -> List[Knowledge]:
        """
        检索与事件相似的知识 ⭐ D13 核心功能
        
        参数：
            event: 异常事件
            limit: 返回数量上限
            
        返回值：
            List[Knowledge]: 相似知识列表（按相似度排序）
            
        注意（D13 边界条件）：
            匹配失败时返回空列表，不抛异常，系统应降级到标准流程
        """
        pass
    
    @abstractmethod
    def update_effectiveness(self, knowledge_id: str, effectiveness: int) -> bool:
        """
        更新知识有效性评分
        
        参数：
            knowledge_id: 知识 ID
            effectiveness: 新的评分（0-100）
            
        返回值：
            bool: 更新是否成功
        """
        pass
    
    @abstractmethod
    def get_all(self) -> List[Knowledge]:
        """
        获取所有知识条目
        
        返回值：
            List[Knowledge]: 所有知识列表
        """
        pass


class MockLearn(ILearn):
    """
    Mock 实现用于单元测试
    
    使用内存存储知识条目。
    """
    
    def __init__(self):
        self._knowledge: List[Knowledge] = []
        self._counter = 0
    
    def record(self, event: AnomalyEvent, result: ExecutionResult) -> Optional[Knowledge]:
        """记录知识"""
        # 只记录成功的执行结果
        if result.status.value not in ['success', 'confirmed']:
            return None
        
        self._counter += 1
        knowledge = Knowledge(
            knowledge_id=f"knowledge-{self._counter}",
            knowledge_type=KnowledgeType.LESSON,
            title=f"处理 {event.anomaly_type} 的经验",
            content=f"成功处理事件 {event.event_id}: {result.message}",
            keywords=event.tags + [event.anomaly_type],
            related_events=[event.event_id],
            effectiveness=80,
            source='auto'
        )
        self._knowledge.append(knowledge)
        return knowledge
    
    def retrieve_similar(self, event: AnomalyEvent, limit: int = 5) -> List[Knowledge]:
        """检索相似知识（关键词匹配）"""
        matches = []
        event_keywords = set(event.tags + [event.anomaly_type])
        
        for k in self._knowledge:
            k_keywords = set(k.keywords)
            # 计算关键词交集作为相似度
            similarity = len(event_keywords & k_keywords)
            if similarity > 0:
                matches.append((similarity, k))
        
        # 按相似度排序
        matches.sort(key=lambda x: x[0], reverse=True)
        return [k for _, k in matches[:limit]]
    
    def update_effectiveness(self, knowledge_id: str, effectiveness: int) -> bool:
        """更新有效性"""
        for k in self._knowledge:
            if k.knowledge_id == knowledge_id:
                k.effectiveness = effectiveness
                k.updated_at = datetime.now().isoformat()
                return True
        return False
    
    def get_all(self) -> List[Knowledge]:
        """获取所有知识"""
        return self._knowledge.copy()


class LearnError(Exception):
    """知识学习模块异常"""
    pass
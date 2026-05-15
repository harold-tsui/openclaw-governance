"""
IDecide - 决策评估接口
NUCLEUS-4.0 D2 - 核心接口定义

定义决策评估模块的抽象接口。
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# 使用相对导入引用 D1 定义的事件模型和 RPN 结构
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.event import AnomalyEvent
from models.rpn import RPNThreshold


class ActionType(Enum):
    """动作类型枚举"""
    AUTO = 'auto'           # 自动创建 Task
    STANDARD = 'standard'   # 标准创建 Task（需确认）
    MONITOR = 'monitor'     # 观察级别
    IGNORE = 'ignore'       # 忽略
    EMERGENCY = 'emergency' # 紧急处理


@dataclass
class TaskSpec:
    """
    Task 规范
    
    属性：
        task_type: Task 类型
        priority: 优先级（P0-P3）
        target_event: 目标事件 ID
        suggested_action: 建议动作
        confirmation_required: 是否需要人工确认
        metadata: 额外元数据
    """
    task_type: str
    priority: str  # 'P0', 'P1', 'P2', 'P3'
    target_event: str
    suggested_action: str
    confirmation_required: bool = True
    metadata: dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class IDecide(ABC):
    """
    决策评估接口
    
    负责评估异常事件的 RPN 并决定后续动作。
    
    核心方法：
        evaluate(): 计算 RPN 和动作级别
        decide(): 生成 Task 规范
        batch_decide(): 批量决策
    """
    
    @abstractmethod
    def evaluate(self, event: AnomalyEvent) -> Tuple[int, ActionType]:
        """
        计算事件的 RPN 并确定动作级别
        
        参数：
            event: 异常事件对象
            
        返回值：
            Tuple[int, ActionType]: (RPN 值, 动作级别)
        """
        pass
    
    @abstractmethod
    def decide(self, event: AnomalyEvent) -> Optional[TaskSpec]:
        """
        根据事件生成 Task 规范
        
        参数：
            event: 异常事件对象
            
        返回值：
            Optional[TaskSpec]: Task 规范（如果需要创建 Task），否则 None
        """
        pass
    
    @abstractmethod
    def batch_decide(self, events: List[AnomalyEvent]) -> List[TaskSpec]:
        """
        批量决策多个事件
        
        参数：
            events: 异常事件列表
            
        返回值：
            List[TaskSpec]: 需要创建的 Task 规范列表
        """
        pass
    
    @abstractmethod
    def set_threshold(self, threshold: RPNThreshold) -> bool:
        """
        设置 RPN 阈值配置
        
        参数：
            threshold: RPN 阈值对象
            
        返回值：
            bool: 设置是否成功
        """
        pass


class MockDecide(IDecide):
    """
    Mock 实现用于单元测试
    
    使用固定的 RPN 阈值进行决策。
    """
    
    def __init__(self, threshold: Optional[RPNThreshold] = None):
        self._threshold = threshold or RPNThreshold()
    
    def evaluate(self, event: AnomalyEvent) -> Tuple[int, ActionType]:
        """计算 RPN 并返回动作级别"""
        rpn = event.rpn or (event.severity * event.occurrence * event.detection_difficulty)
        action_level = self._threshold.get_action_level(rpn, event.severity)
        action_type = ActionType(action_level)
        return (rpn, action_type)
    
    def decide(self, event: AnomalyEvent) -> Optional[TaskSpec]:
        """根据 RPN 生成 Task 规范"""
        rpn, action_type = self.evaluate(event)
        
        # 只为 standard 和 auto 级别创建 Task
        if action_type in [ActionType.STANDARD, ActionType.AUTO, ActionType.EMERGENCY]:
            priority = 'P0' if action_type == ActionType.EMERGENCY else 'P1'
            return TaskSpec(
                task_type='improvement',
                priority=priority,
                target_event=event.event_id,
                suggested_action=f"处理异常事件 (RPN={rpn})",
                confirmation_required=(action_type == ActionType.STANDARD)
            )
        return None
    
    def batch_decide(self, events: List[AnomalyEvent]) -> List[TaskSpec]:
        """批量决策"""
        results = []
        for event in events:
            task_spec = self.decide(event)
            if task_spec:
                results.append(task_spec)
        return results
    
    def set_threshold(self, threshold: RPNThreshold) -> bool:
        """设置阈值"""
        self._threshold = threshold
        return True


class DecideError(Exception):
    """决策模块异常"""
    pass
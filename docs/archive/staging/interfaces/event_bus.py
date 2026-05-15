"""
IEventBus - 事件总线接口
NUCLEUS-4.0 D2 - 核心接口定义

定义事件总线的抽象接口，用于模块间异步通信。
"""

from abc import ABC, abstractmethod
from typing import Callable, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

# 使用相对导入
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.event import AnomalyEvent


class EventType(Enum):
    """事件类型枚举"""
    ANOMALY_DETECTED = 'anomaly_detected'
    DECISION_MADE = 'decision_made'
    TASK_CREATED = 'task_created'
    TASK_EXECUTED = 'task_executed'
    KNOWNESS_RECORD = 'knowledge_recorded'
    SYSTEM_ERROR = 'system_error'
    HEARTBEAT = 'heartbeat'


@dataclass
class BusEvent:
    """
    总线事件
    
    属性：
        event_type: 事件类型
        payload: 事件数据
        source: 事件来源模块
        timestamp: 时间戳
        event_id: 事件 ID
        metadata: 额外元数据
    """
    event_type: EventType
    payload: Any
    source: str
    timestamp: Optional[str] = None
    event_id: Optional[str] = None
    metadata: dict = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
        if self.metadata is None:
            self.metadata = {}


# 定义回调函数类型
EventHandler = Callable[[BusEvent], None]


class IEventBus(ABC):
    """
    事件总线接口
    
    负责模块间的异步事件传递。
    
    核心方法：
        publish(): 发布事件
        subscribe(): 订阅事件
        unsubscribe(): 取消订阅
        get_history(): 获取事件历史
    """
    
    @abstractmethod
    def publish(self, event_type: EventType, payload: Any, source: str) -> bool:
        """
        发布事件
        
        参数：
            event_type: 事件类型
            payload: 事件数据
            source: 事件来源
            
        返回值：
            bool: 发布是否成功
            
        注意：
            发布失败不应阻塞调用方，应记录日志并继续
        """
        pass
    
    @abstractmethod
    def subscribe(self, event_type: EventType, handler: EventHandler) -> str:
        """
        订阅事件
        
        参数：
            event_type: 事件类型
            handler: 事件处理函数
            
        返回值：
            str: 订阅 ID（用于取消订阅）
        """
        pass
    
    @abstractmethod
    def unsubscribe(self, subscription_id: str) -> bool:
        """
        取消订阅
        
        参数：
            subscription_id: 订阅 ID
            
        返回值：
            bool: 取消是否成功
        """
        pass
    
    @abstractmethod
    def get_history(self, event_type: Optional[EventType] = None, limit: int = 100) -> List[BusEvent]:
        """
        获取事件历史
        
        参数：
            event_type: 过滤的事件类型（可选）
            limit: 返回数量上限
            
        返回值：
            List[BusEvent]: 事件历史列表
        """
        pass
    
    @abstractmethod
    def get_stats(self) -> dict:
        """
        获取总线统计信息
        
        返回值：
            dict: 统计信息（如：total_events, subscribers_count, last_event_time）
        """
        pass


class MockEventBus(IEventBus):
    """
    Mock 实现用于单元测试
    
    使用内存存储事件和订阅。
    """
    
    def __init__(self):
        self._history: List[BusEvent] = []
        self._subscribers: dict = {}  # {event_type: [(subscription_id, handler)]}
        self._subscription_counter = 0
        self._event_counter = 0
        self._stats = {
            'total_events': 0,
            'subscribers_count': 0,
            'last_event_time': None
        }
    
    def publish(self, event_type: EventType, payload: Any, source: str) -> bool:
        """发布事件"""
        self._event_counter += 1
        bus_event = BusEvent(
            event_type=event_type,
            payload=payload,
            source=source,
            event_id=f"bus-{self._event_counter}"
        )
        
        self._history.append(bus_event)
        self._stats['total_events'] += 1
        self._stats['last_event_time'] = bus_event.timestamp
        
        # 调用订阅者
        handlers = self._subscribers.get(event_type, [])
        for _, handler in handlers:
            try:
                handler(bus_event)
            except Exception:
                # Mock 中忽略异常
                pass
        
        return True
    
    def subscribe(self, event_type: EventType, handler: EventHandler) -> str:
        """订阅事件"""
        self._subscription_counter += 1
        subscription_id = f"sub-{self._subscription_counter}"
        
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        
        self._subscribers[event_type].append((subscription_id, handler))
        self._stats['subscribers_count'] += 1
        
        return subscription_id
    
    def unsubscribe(self, subscription_id: str) -> bool:
        """取消订阅"""
        for event_type, subscribers in self._subscribers.items():
            for i, (sid, _) in enumerate(subscribers):
                if sid == subscription_id:
                    subscribers.pop(i)
                    self._stats['subscribers_count'] -= 1
                    return True
        return False
    
    def get_history(self, event_type: Optional[EventType] = None, limit: int = 100) -> List[BusEvent]:
        """获取事件历史"""
        if event_type:
            filtered = [e for e in self._history if e.event_type == event_type]
        else:
            filtered = self._history
        
        return filtered[-limit:]
    
    def get_stats(self) -> dict:
        """获取统计信息"""
        return self._stats.copy()


class EventBusError(Exception):
    """事件总线异常"""
    pass
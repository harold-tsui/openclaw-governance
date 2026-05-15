"""
IMonitor - 异常检测接口
NUCLEUS-4.0 D2 - 核心接口定义

定义异常检测模块的抽象接口。
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from dataclasses import dataclass

# 使用相对导入引用 D1 定义的事件模型
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.event import AnomalyEvent


@dataclass
class MonitorConfig:
    """
    监控配置
    
    属性：
        scan_interval: 扫描间隔（秒）
        max_events_per_cycle: 每周期最大事件数
        enabled_sources: 启用的数据源列表
    """
    scan_interval: int = 60
    max_events_per_cycle: int = 100
    enabled_sources: List[str] = None
    
    def __post_init__(self):
        if self.enabled_sources is None:
            self.enabled_sources = ['real', 'standard', 'inferred']


class IMonitor(ABC):
    """
    异常检测接口
    
    负责从数据源检测异常事件并生成 AnomalyEvent 对象。
    
    核心方法：
        detect(): 执行一次检测周期，返回检测到的异常事件列表
        configure(): 配置监控参数
        get_status(): 获取当前监控状态
    """
    
    @abstractmethod
    def detect(self) -> List[AnomalyEvent]:
        """
        执行一次检测周期
        
        返回值：
            List[AnomalyEvent]: 检测到的异常事件列表
            
        异常：
            MonitorError: 检测过程中发生错误
        """
        pass
    
    @abstractmethod
    def configure(self, config: MonitorConfig) -> bool:
        """
        配置监控参数
        
        参数：
            config: 监控配置对象
            
        返回值：
            bool: 配置是否成功
        """
        pass
    
    @abstractmethod
    def get_status(self) -> dict:
        """
        获取当前监控状态
        
        返回值：
            dict: 包含状态信息的字典（如：last_scan_time, total_events, enabled）
        """
        pass


class MockMonitor(IMonitor):
    """
    Mock 实现用于单元测试
    
    返回预设的模拟事件列表。
    """
    
    def __init__(self, mock_events: Optional[List[AnomalyEvent]] = None):
        self._mock_events = mock_events or []
        self._config: Optional[MonitorConfig] = None
        self._status = {
            'last_scan_time': None,
            'total_events': 0,
            'enabled': True
        }
    
    def detect(self) -> List[AnomalyEvent]:
        """返回预设的模拟事件"""
        self._status['total_events'] += len(self._mock_events)
        return self._mock_events
    
    def configure(self, config: MonitorConfig) -> bool:
        """配置 Mock 监控器"""
        self._config = config
        return True
    
    def get_status(self) -> dict:
        """返回 Mock 状态"""
        return self._status.copy()


class MonitorError(Exception):
    """监控模块异常"""
    pass
"""
IAct - 动作执行接口
NUCLEUS-4.0 D2 - 核心接口定义

定义动作执行模块的抽象接口。
"""

from abc import ABC, abstractmethod
from typing import Optional, List
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

# 使用相对导入
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from interfaces.decide import TaskSpec


class ExecutionStatus(Enum):
    """执行状态枚举"""
    SUCCESS = 'success'
    FAILURE = 'failure'
    PENDING = 'pending'
    SKIPPED = 'skipped'
    CONFIRMED = 'confirmed'
    REJECTED = 'rejected'


@dataclass
class ExecutionResult:
    """
    执行结果
    
    属性：
        task_id: Task ID
        status: 执行状态
        start_time: 开始时间
        end_time: 结束时间
        message: 结果消息
        metadata: 额外元数据
    """
    task_id: str
    status: ExecutionStatus
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    message: str = ''
    metadata: dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.start_time is None:
            self.start_time = datetime.now().isoformat()


class IAct(ABC):
    """
    动作执行接口
    
    负责执行决策模块生成的 Task，并记录执行结果。
    
    核心方法：
        execute(): 执行 Task
        confirm(): 人工确认
        record_outcome(): 记录执行结果
        get_pending(): 获取待确认的 Task
    """
    
    @abstractmethod
    def execute(self, task_spec: TaskSpec) -> ExecutionResult:
        """
        执行 Task
        
        参数：
            task_spec: Task 规范
            
        返回值：
            ExecutionResult: 执行结果
            
        注意：
            如 task_spec.confirmation_required=True，则进入 PENDING 状态等待确认
        """
        pass
    
    @abstractmethod
    def confirm(self, task_id: str, approved: bool) -> ExecutionResult:
        """
        人工确认 Task
        
        参数：
            task_id: Task ID
            approved: 是否批准
            
        返回值：
            ExecutionResult: 更新后的执行结果
        """
        pass
    
    @abstractmethod
    def record_outcome(self, result: ExecutionResult) -> bool:
        """
        记录执行结果
        
        参数：
            result: 执行结果
            
        返回值：
            bool: 记录是否成功
        """
        pass
    
    @abstractmethod
    def get_pending(self) -> List[ExecutionResult]:
        """
        获取待确认的 Task
        
        返回值：
            List[ExecutionResult]: 处于 PENDING 状态的执行结果列表
        """
        pass


class MockAct(IAct):
    """
    Mock 实现用于单元测试
    
    自动批准所有 Task。
    """
    
    def __init__(self):
        self._pending: List[ExecutionResult] = []
        self._history: List[ExecutionResult] = []
        self._task_counter = 0
    
    def execute(self, task_spec: TaskSpec) -> ExecutionResult:
        """执行 Task"""
        self._task_counter += 1
        task_id = f"task-{self._task_counter}"
        
        result = ExecutionResult(
            task_id=task_id,
            status=ExecutionStatus.PENDING if task_spec.confirmation_required else ExecutionStatus.SUCCESS,
            message=f"执行 Task: {task_spec.task_type}"
        )
        
        if task_spec.confirmation_required:
            self._pending.append(result)
        else:
            self._history.append(result)
        
        return result
    
    def confirm(self, task_id: str, approved: bool) -> ExecutionResult:
        """确认 Task"""
        for result in self._pending:
            if result.task_id == task_id:
                result.status = ExecutionStatus.CONFIRMED if approved else ExecutionStatus.REJECTED
                result.end_time = datetime.now().isoformat()
                self._pending.remove(result)
                self._history.append(result)
                return result
        
        return ExecutionResult(
            task_id=task_id,
            status=ExecutionStatus.FAILURE,
            message=f"Task {task_id} 未找到"
        )
    
    def record_outcome(self, result: ExecutionResult) -> bool:
        """记录结果"""
        self._history.append(result)
        return True
    
    def get_pending(self) -> List[ExecutionResult]:
        """获取待确认 Task"""
        return self._pending.copy()


class ActError(Exception):
    """动作执行模块异常"""
    pass
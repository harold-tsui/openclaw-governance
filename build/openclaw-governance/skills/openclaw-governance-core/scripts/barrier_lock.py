#!/usr/bin/env python3
"""
barrier_lock.py - Phase Barrier Lock Implementation

Phase 屏障状态快照锁定机制，用于防止 Phase 执行期间的状态竞态。

Version: 7.0.0
Author: Governance Core Team
Created: 2026-04-04
Updated: 2026-04-22

Usage:
    with PhaseBarrierLock() as barrier:
        barrier.lock_snapshot(current_module_states)
        execute_phase()  # Phase 执行过程中使用快照状态
        # 离开 with 块时自动 unlock，异常也不例外

References:
    - SKILL.md §三.2 屏障规则
    - references/barrier-design.md 详细设计
"""

import datetime
from typing import Dict, Optional


class PhaseBarrierLock:
    """屏障状态快照锁定
    
    v6.1.3 修复：
    - FIX-1: 补充 unlock 机制（上下文管理器）
    - FIX-2: snapshot.get(module, 'unknown') 改为返回 'failed'
    """
    
    def __init__(self):
        self.snapshot: Optional[Dict[str, str]] = None
        self.locked: bool = False
        self.lock_timestamp: Optional[datetime.datetime] = None
    
    def lock_snapshot(self, module_states: Dict[str, str]) -> None:
        """锁定状态快照，Phase 执行期间状态冻结
        
        Args:
            module_states: 模块状态字典，如 {"core": "success", "config": "degraded"}
        """
        self.snapshot = module_states.copy()
        self.locked = True
        self.lock_timestamp = datetime.datetime.now()
        # 通知所有模块：状态更新在下一屏障生效
        self.broadcast("STATE_FREEZE", self.snapshot)
    
    def unlock_snapshot(self) -> None:
        """释放锁，允许状态更新
        
        重要：必须在 Phase 完成后调用，否则系统进入永久状态冻结
        """
        self.snapshot = None
        self.locked = False
        self.lock_timestamp = None
        # 通知所有模块：可以更新状态
        self.broadcast("STATE_RELEASE", None)
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口 - 无论正常还是异常退出，都释放锁
        
        这确保了 Phase 执行过程中即使抛出异常，锁也会被正确释放
        """
        self.unlock_snapshot()
        return False  # 不吞异常，让异常继续传播
    
    def get_state(self, module: str) -> str:
        """获取状态（Phase 执行期间返回快照值）
        
        Args:
            module: 模块名称
            
        Returns:
            模块状态（success/degraded/failed/loading）
            
        v6.1.3 FIX-2: 返回 'failed' 而非 'unknown'
        - 'unknown' 不在状态表（success/degraded/failed/loading）中
        - 调用方收到 'failed' 后可明确处理
        """
        if self.locked and self.snapshot:
            # FIX-2: 返回 'failed' 而非 'unknown'
            return self.snapshot.get(module, "failed")
        # 未锁定时返回实时状态
        return self.get_realtime_state(module)
    
    def broadcast(self, event_type: str, data: Optional[Dict]) -> None:
        """广播事件到所有模块
        
        Args:
            event_type: 事件类型（STATE_FREEZE/STATE_RELEASE）
            data: 事件数据
        """
        # 实际实现应调用治理系统的广播机制
        # 这里仅作为接口定义
        pass
    
    def get_realtime_state(self, module: str) -> str:
        """获取模块实时状态
        
        Args:
            module: 模块名称
            
        Returns:
            模块实时状态
        """
        # 实际实现应调用治理系统的状态查询接口
        # 这里仅作为接口定义，默认返回 'loading'
        return 'loading'


# 使用示例
if __name__ == "__main__":
    # 推荐方式：使用上下文管理器
    current_module_states = {
        "core": "success",
        "config": "degraded",
        "dispatch": "success"
    }
    
    with PhaseBarrierLock() as barrier:
        barrier.lock_snapshot(current_module_states)
        print(f"Core state: {barrier.get_state('core')}")
        print(f"Config state: {barrier.get_state('config')}")
        # Phase 执行过程中使用快照状态
        # ...
        # 离开 with 块时自动 unlock，异常也不例外
    
    print("Barrier lock released")
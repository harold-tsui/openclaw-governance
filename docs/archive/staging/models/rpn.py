"""
RPN 数据结构
NUCLEUS-4.0 D1 - RPN 计算和阈值定义

定义风险优先级的数据结构和建议阈值。
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class RPNThreshold:
    """
    RPN 阈值配置
    
    属性：
        auto_action_rpn: 自动创建 Task 的 RPN 阈值（>200）
        standard_action_rpn: 标准创建 Task 的 RPN 阈值（100-200）
        monitor_rpn: 观察级别 RPN 阈值（50-100）
        ignore_rpn: 忽略级别（<50）
        severity_emergency: 紧急严重度阈值（S≥9 自动处理）
    """
    
    auto_action_rpn: int = 200      # >200: 自动创建 Task
    standard_action_rpn: int = 100   # 100-200: 标准创建 Task
    monitor_rpn: int = 50           # 50-100: 观察
    ignore_rpn: int = 50             # <50: 忽略
    severity_emergency: int = 9      # S≥9: 紧急处理
    
    def get_action_level(self, rpn: int, severity: Optional[int] = None) -> str:
        """
        根据 RPN 获取动作级别
        
        返回值：
            'auto': 自动创建 Task（无需确认）
            'standard': 标准创建 Task（需确认）
            'monitor': 观察级别
            'ignore': 忽略
            'emergency': 紧急处理（S≥9）
        """
        # 紧急处理规则优先
        if severity is not None and severity >= self.severity_emergency:
            return 'emergency'
        
        if rpn > self.auto_action_rpn:
            return 'auto'
        elif rpn >= self.standard_action_rpn:
            return 'standard'
        elif rpn >= self.monitor_rpn:
            return 'monitor'
        else:
            return 'ignore'
    
    def requires_confirmation(self, rpn: int, severity: Optional[int] = None) -> bool:
        """判断是否需要人工确认"""
        level = self.get_action_level(rpn, severity)
        # standard 和 monitor 需要确认，auto 和 emergency 不需要
        return level in ['standard', 'monitor']
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'auto_action_rpn': self.auto_action_rpn,
            'standard_action_rpn': self.standard_action_rpn,
            'monitor_rpn': self.monitor_rpn,
            'ignore_rpn': self.ignore_rpn,
            'severity_emergency': self.severity_emergency,
        }


@dataclass 
class RPNCalculation:
    """
    RPN 计算结果
    
    属性：
        severity: 严重度（1-10）
        occurrence: 发生频率（1-10）
        detection_difficulty: 检测难度（1-10）
        rpn: 计算得到的 RPN 值
        action_level: 建议的动作级别
        requires_confirmation: 是否需要确认
    """
    
    severity: int
    occurrence: int
    detection_difficulty: int
    threshold: RPNThreshold = field(default_factory=RPNThreshold)
    
    def __post_init__(self):
        self.rpn = self.severity * self.occurrence * self.detection_difficulty
        self.action_level = self.threshold.get_action_level(self.rpn, self.severity)
        self.requires_confirmation = self.threshold.requires_confirmation(self.rpn, self.severity)
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'severity': self.severity,
            'occurrence': self.occurrence,
            'detection_difficulty': self.detection_difficulty,
            'rpn': self.rpn,
            'action_level': self.action_level,
            'requires_confirmation': self.requires_confirmation,
        }
    
    def __str__(self) -> str:
        return f"RPNCalculation(S={self.severity}, O={self.occurrence}, D={self.detection_difficulty}) = {self.rpn} [{self.action_level}]"
    
    def __repr__(self) -> str:
        return self.__str__()


def calculate_rpn(severity: int, occurrence: int, detection_difficulty: int) -> int:
    """
    计算 RPN 值
    
    参数：
        severity: 严重度（1-10）
        occurrence: 发生频率（1-10）
        detection_difficulty: 检测难度（1-10）
    
    返回：
        RPN 值（S × O × D）
    """
    return severity * occurrence * detection_difficulty


def get_action_recommendation(rpn: int, severity: int = None, threshold: RPNThreshold = None) -> dict:
    """
    获取动作建议
    
    参数：
        rpn: RPN 值
        severity: 严重度（可选）
        threshold: 阈值配置（可选）
    
    返回：
        包含动作级别、描述和建议的字典
    """
    if threshold is None:
        threshold = RPNThreshold()
    
    level = threshold.get_action_level(rpn, severity)
    
    recommendations = {
        'auto': {
            'level': 'auto',
            'title': '自动创建 Task',
            'description': 'RPN 超过阈值，立即创建处理 Task',
            'confirmation_required': False,
        },
        'standard': {
            'level': 'standard', 
            'title': '标准创建 Task',
            'description': 'RPN 在标准范围内，创建 Task 并等待确认',
            'confirmation_required': True,
        },
        'monitor': {
            'level': 'monitor',
            'title': '观察级别',
            'description': 'RPN 较低，记录并观察趋势',
            'confirmation_required': True,
        },
        'ignore': {
            'level': 'ignore',
            'title': '忽略',
            'description': 'RPN 低于阈值，无需处理',
            'confirmation_required': False,
        },
        'emergency': {
            'level': 'emergency',
            'title': '紧急处理',
            'description': '严重度达到紧急阈值，立即处理',
            'confirmation_required': False,
        },
    }
    
    return recommendations.get(level, recommendations['ignore'])

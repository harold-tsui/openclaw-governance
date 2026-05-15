"""
接口单元测试
NUCLEUS-4.0 D2 - 验收门控测试

验证 5 个核心接口的语法和 Mock 实现。

验收门控：
- F4: 5 个接口文件通过语法检查
- F5: 每个接口有 Mock 实现并通过单元测试
- P1: 接口文件不含业务关键词（如"welding"、"defect"）
"""

import unittest
import sys
import os
import re

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from interfaces.monitor import IMonitor, MockMonitor, MonitorConfig, MonitorError
from interfaces.decide import IDecide, MockDecide, TaskSpec, ActionType, DecideError
from interfaces.act import IAct, MockAct, ExecutionResult, ExecutionStatus, ActError
from interfaces.learn import ILearn, MockLearn, Knowledge, KnowledgeType, LearnError
from interfaces.event_bus import IEventBus, MockEventBus, BusEvent, EventType, EventBusError
from models.event import AnomalyEvent
from models.rpn import RPNThreshold


class TestMonitorInterface(unittest.TestCase):
    """测试 IMonitor 接口"""
    
    def test_mock_monitor_detect(self):
        """测试 Mock 监控器检测"""
        mock_events = [
            AnomalyEvent(
                anomaly_type='test_type',
                severity=5,
                occurrence=3,
                detection_difficulty=2,
                location='test_location',
                description='test description'
            )
        ]
        monitor = MockMonitor(mock_events)
        events = monitor.detect()
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].anomaly_type, 'test_type')
    
    def test_monitor_configure(self):
        """测试监控器配置"""
        monitor = MockMonitor()
        config = MonitorConfig(scan_interval=30)
        result = monitor.configure(config)
        self.assertTrue(result)
    
    def test_monitor_status(self):
        """测试监控器状态"""
        monitor = MockMonitor()
        status = monitor.get_status()
        self.assertIn('enabled', status)
        self.assertTrue(status['enabled'])


class TestDecideInterface(unittest.TestCase):
    """测试 IDecide 接口"""
    
    def test_mock_decide_evaluate(self):
        """测试 Mock 决策器评估"""
        event = AnomalyEvent(
            anomaly_type='test_type',
            severity=8,
            occurrence=5,
            detection_difficulty=4,
            location='test_location',
            description='test description'
        )
        decide = MockDecide()
        rpn, action = decide.evaluate(event)
        self.assertEqual(rpn, 160)  # 8*5*4
        self.assertEqual(action, ActionType.STANDARD)
    
    def test_mock_decide_task_generation(self):
        """测试 Task 规范生成"""
        event = AnomalyEvent(
            anomaly_type='test_type',
            severity=10,  # 紧急
            occurrence=5,
            detection_difficulty=4,
            location='test_location',
            description='test description'
        )
        decide = MockDecide()
        task = decide.decide(event)
        self.assertIsNotNone(task)
        self.assertEqual(task.priority, 'P0')
    
    def test_batch_decide(self):
        """测试批量决策"""
        events = [
            AnomalyEvent(
                anomaly_type='test_type_1',
                severity=5,
                occurrence=4,
                detection_difficulty=5,
                location='loc1',
                description='desc1'
            ),
            AnomalyEvent(
                anomaly_type='test_type_2',
                severity=2,
                occurrence=2,
                detection_difficulty=2,
                location='loc2',
                description='desc2'
            )
        ]
        decide = MockDecide()
        tasks = decide.batch_decide(events)
        self.assertEqual(len(tasks), 1)  # 只有第一个事件需要 Task


class TestActInterface(unittest.TestCase):
    """测试 IAct 接口"""
    
    def test_mock_act_execute(self):
        """测试 Mock 执行器"""
        task_spec = TaskSpec(
            task_type='improvement',
            priority='P1',
            target_event='event-1',
            suggested_action='test action',
            confirmation_required=False
        )
        act = MockAct()
        result = act.execute(task_spec)
        self.assertEqual(result.status, ExecutionStatus.SUCCESS)
    
    def test_mock_act_confirm(self):
        """测试人工确认"""
        task_spec = TaskSpec(
            task_type='improvement',
            priority='P1',
            target_event='event-1',
            suggested_action='test action',
            confirmation_required=True
        )
        act = MockAct()
        result = act.execute(task_spec)
        self.assertEqual(result.status, ExecutionStatus.PENDING)
        
        # 确认
        confirmed = act.confirm(result.task_id, True)
        self.assertEqual(confirmed.status, ExecutionStatus.CONFIRMED)
    
    def test_get_pending(self):
        """测试获取待确认 Task"""
        task_spec = TaskSpec(
            task_type='improvement',
            priority='P1',
            target_event='event-1',
            suggested_action='test action',
            confirmation_required=True
        )
        act = MockAct()
        act.execute(task_spec)
        pending = act.get_pending()
        self.assertEqual(len(pending), 1)


class TestLearnInterface(unittest.TestCase):
    """测试 ILearn 接口"""
    
    def test_mock_learn_record(self):
        """测试知识记录"""
        event = AnomalyEvent(
            anomaly_type='test_type',
            severity=5,
            occurrence=3,
            detection_difficulty=2,
            location='test_location',
            description='test description',
            tags=['tag1', 'tag2']
        )
        result = ExecutionResult(
            task_id='task-1',
            status=ExecutionStatus.SUCCESS,
            message='成功处理'
        )
        learn = MockLearn()
        knowledge = learn.record(event, result)
        self.assertIsNotNone(knowledge)
        self.assertEqual(knowledge.knowledge_type, KnowledgeType.LESSON)
    
    def test_retrieve_similar(self):
        """测试相似知识检索"""
        # 先记录一些知识
        event1 = AnomalyEvent(
            anomaly_type='type_a',
            severity=5,
            occurrence=3,
            detection_difficulty=2,
            location='loc1',
            description='desc1',
            tags=['common_tag']
        )
        result1 = ExecutionResult(
            task_id='task-1',
            status=ExecutionStatus.SUCCESS,
            message='success'
        )
        learn = MockLearn()
        learn.record(event1, result1)
        
        # 检索相似
        event2 = AnomalyEvent(
            anomaly_type='type_a',
            severity=4,
            occurrence=2,
            detection_difficulty=3,
            location='loc2',
            description='desc2',
            tags=['common_tag', 'other_tag']
        )
        similar = learn.retrieve_similar(event2)
        self.assertEqual(len(similar), 1)
    
    def test_retrieve_empty(self):
        """测试无匹配时的空列表返回（D13 边界条件）"""
        learn = MockLearn()
        event = AnomalyEvent(
            anomaly_type='unknown_type',
            severity=1,
            occurrence=1,
            detection_difficulty=1,
            location='loc',
            description='desc',
            tags=['unknown_tag']
        )
        similar = learn.retrieve_similar(event)
        self.assertEqual(len(similar), 0)  # 应返回空列表，不抛异常


class TestEventBusInterface(unittest.TestCase):
    """测试 IEventBus 接口"""
    
    def test_mock_bus_publish(self):
        """测试事件发布"""
        bus = MockEventBus()
        result = bus.publish(
            event_type=EventType.ANOMALY_DETECTED,
            payload={'test': 'data'},
            source='monitor'
        )
        self.assertTrue(result)
    
    def test_mock_bus_subscribe(self):
        """测试事件订阅"""
        bus = MockEventBus()
        received = []
        
        def handler(event: BusEvent):
            received.append(event)
        
        sub_id = bus.subscribe(EventType.ANOMALY_DETECTED, handler)
        self.assertIsNotNone(sub_id)
        
        # 发布事件
        bus.publish(EventType.ANOMALY_DETECTED, {'data': 'test'}, 'monitor')
        self.assertEqual(len(received), 1)
    
    def test_bus_history(self):
        """测试事件历史"""
        bus = MockEventBus()
        bus.publish(EventType.ANOMALY_DETECTED, {'1': 'a'}, 'monitor')
        bus.publish(EventType.TASK_CREATED, {'2': 'b'}, 'decide')
        
        history = bus.get_history()
        self.assertEqual(len(history), 2)
        
        # 过滤
        filtered = bus.get_history(EventType.ANOMALY_DETECTED)
        self.assertEqual(len(filtered), 1)


class TestP1NoBusinessKeywords(unittest.TestCase):
    """测试 P1：接口文件不含业务关键词"""
    
    def test_no_business_keywords(self):
        """验证接口文件不含业务关键词"""
        business_keywords = ['welding', 'defect', 'weld', 'assembly', 'equipment']
        interfaces_dir = os.path.dirname(os.path.abspath(__file__))
        
        for filename in ['monitor.py', 'decide.py', 'act.py', 'learn.py', 'event_bus.py']:
            filepath = os.path.join(interfaces_dir, filename)
            with open(filepath, 'r') as f:
                content = f.read()
            
            # 检查是否包含业务关键词（不区分大小写）
            for keyword in business_keywords:
                matches = re.findall(keyword, content, re.IGNORECASE)
                self.assertEqual(len(matches), 0, 
                    f"文件 {filename} 包含业务关键词 '{keyword}'")


if __name__ == '__main__':
    unittest.main(verbosity=2)
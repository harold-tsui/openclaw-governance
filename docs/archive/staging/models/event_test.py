"""
AnomalyEvent 单元测试
NUCLEUS-4.0 D1 - 事件模型测试

测试事件序列化、反序列化、字段验证和相似度判断。
"""

import pytest
import json
from datetime import datetime
from models.event import AnomalyEvent


class TestAnomalyEventCreation:
    """测试 AnomalyEvent 创建"""
    
    def test_create_minimal_event(self):
        """测试创建最小事件"""
        event = AnomalyEvent(
            anomaly_type='welding_defect',
            severity=7,
            occurrence=5,
            detection_difficulty=3,
            location='Welding-Station-A',
            description='焊接点气孔缺陷'
        )
        
        assert event.anomaly_type == 'welding_defect'
        assert event.severity == 7
        assert event.occurrence == 5
        assert event.detection_difficulty == 3
        assert event.rpn == 7 * 5 * 3  # 105
        assert event.event_id is not None
        assert event.timestamp is not None
    
    def test_create_event_with_all_fields(self):
        """测试创建完整事件"""
        event = AnomalyEvent(
            anomaly_type='equipment_failure',
            severity=8,
            occurrence=3,
            detection_difficulty=4,
            location='Assembly-Line-01',
            description='机器人焊接臂伺服电机故障',
            tags=['robot', 'welding', 'motor', 'urgent'],
            source='real',
            event_id='test-uuid-123',
            created_by='test_user'
        )
        
        assert event.event_id == 'test-uuid-123'
        assert event.created_by == 'test_user'
        assert event.tags == ['robot', 'welding', 'motor', 'urgent']
        assert event.source == 'real'
    
    def test_create_inferred_event_auto_annotation(self):
        """测试创建推断事件时自动标注来源"""
        event = AnomalyEvent(
            anomaly_type='dimension_deviation',
            severity=5,
            occurrence=4,
            detection_difficulty=6,
            location='Assembly-Line-02',
            description='推算的尺寸偏差',
            source='inferred'
        )
        
        assert event.source == 'inferred'
        assert event.metadata.get('source') == 'inferred'


class TestAnomalyEventValidation:
    """测试字段验证"""
    
    def test_invalid_severity_raises_error(self):
        """测试无效严重度"""
        with pytest.raises(ValueError, match="severity 必须在 1-10 之间"):
            AnomalyEvent(
                anomaly_type='test',
                severity=11,  # 无效
                occurrence=5,
                detection_difficulty=3,
                location='test',
                description='test'
            )
    
    def test_invalid_occurrence_raises_error(self):
        """测试无效发生频率"""
        with pytest.raises(ValueError, match="occurrence 必须在 1-10 之间"):
            AnomalyEvent(
                anomaly_type='test',
                severity=5,
                occurrence=0,  # 无效
                detection_difficulty=3,
                location='test',
                description='test'
            )
    
    def test_invalid_detection_difficulty_raises_error(self):
        """测试无效检测难度"""
        with pytest.raises(ValueError, match="detection_difficulty 必须在 1-10 之间"):
            AnomalyEvent(
                anomaly_type='test',
                severity=5,
                occurrence=3,
                detection_difficulty=15,  # 无效
                location='test',
                description='test'
            )
    
    def test_invalid_source_raises_error(self):
        """测试无效数据来源"""
        with pytest.raises(ValueError, match="source 必须是"):
            AnomalyEvent(
                anomaly_type='test',
                severity=5,
                occurrence=3,
                detection_difficulty=3,
                location='test',
                description='test',
                source='invalid_source'
            )


class TestAnomalyEventSerialization:
    """测试序列化/反序列化"""
    
    def test_to_dict(self):
        """测试转换为字典"""
        event = AnomalyEvent(
            anomaly_type='welding_defect',
            severity=7,
            occurrence=5,
            detection_difficulty=3,
            location='Welding-Station-A',
            description='焊接缺陷',
            tags=['welding'],
            source='real',
            event_id='test-id',
            timestamp='2026-04-01T10:00:00'
        )
        
        data = event.to_dict()
        
        assert isinstance(data, dict)
        assert data['anomaly_type'] == 'welding_defect'
        assert data['severity'] == 7
        assert data['occurrence'] == 5
        assert data['detection_difficulty'] == 3
        assert data['rpn'] == 105
        assert data['event_id'] == 'test-id'
        assert data['tags'] == ['welding']
    
    def test_to_json(self):
        """测试转换为 JSON"""
        event = AnomalyEvent(
            anomaly_type='test',
            severity=5,
            occurrence=3,
            detection_difficulty=2,
            location='test',
            description='test'
        )
        
        json_str = event.to_json()
        
        assert isinstance(json_str, str)
        data = json.loads(json_str)
        assert data['anomaly_type'] == 'test'
    
    def test_from_dict(self):
        """测试从字典创建"""
        data = {
            'anomaly_type': 'equipment_failure',
            'severity': 8,
            'occurrence': 4,
            'detection_difficulty': 3,
            'location': 'Line-01',
            'description': '设备故障',
            'tags': ['equipment'],
            'source': 'standard',
            'event_id': 'dict-id',
            'timestamp': '2026-04-01T12:00:00'
        }
        
        event = AnomalyEvent.from_dict(data)
        
        assert event.anomaly_type == 'equipment_failure'
        assert event.event_id == 'dict-id'
        assert event.tags == ['equipment']
    
    def test_from_json(self):
        """测试从 JSON 创建"""
        json_str = '{"anomaly_type": "test", "severity": 6, "occurrence": 3, "detection_difficulty": 4, "location": "L1", "description": "d"}'
        
        event = AnomalyEvent.from_json(json_str)
        
        assert event.anomaly_type == 'test'
        assert event.severity == 6
        assert event.rpn == 6 * 3 * 4  # 72
    
    def test_roundtrip_serialization(self):
        """测试往返序列化"""
        original = AnomalyEvent(
            anomaly_type='complex_event',
            severity=9,
            occurrence=7,
            detection_difficulty=4,
            location='Complex-Location',
            description='复杂测试事件',
            tags=['complex', 'test', 'high-priority'],
            source='real'
        )
        
        # 序列化 -> 反序列化
        json_str = original.to_json()
        restored = AnomalyEvent.from_json(json_str)
        
        # 验证字段一致
        assert restored.anomaly_type == original.anomaly_type
        assert restored.severity == original.severity
        assert restored.occurrence == original.occurrence
        assert restored.detection_difficulty == original.detection_difficulty
        assert restored.rpn == original.rpn
        assert restored.location == original.location
        assert restored.tags == original.tags
        assert restored.source == original.source


class TestAnomalyEventSimilarity:
    """测试相似度判断"""
    
    def test_get_common_tags(self):
        """测试获取共同标签"""
        event1 = AnomalyEvent(
            anomaly_type='test1',
            severity=5,
            occurrence=3,
            detection_difficulty=2,
            location='L1',
            description='d1',
            tags=['welding', 'robot', 'urgent']
        )
        
        event2 = AnomalyEvent(
            anomaly_type='test2',
            severity=6,
            occurrence=4,
            detection_difficulty=3,
            location='L2',
            description='d2',
            tags=['welding', 'robot', 'quality']
        )
        
        common = event1.get_common_tags(event2)
        
        assert len(common) == 2
        assert 'welding' in common
        assert 'robot' in common
    
    def test_is_similar_with_sufficient_tags(self):
        """测试相似度判断 - 足够共同标签"""
        event1 = AnomalyEvent(
            anomaly_type='test1',
            severity=5,
            occurrence=3,
            detection_difficulty=2,
            location='L1',
            description='d1',
            tags=['welding', 'robot', 'urgent', 'quality']
        )
        
        event2 = AnomalyEvent(
            anomaly_type='test2',
            severity=6,
            occurrence=4,
            detection_difficulty=3,
            location='L2',
            description='d2',
            tags=['welding', 'robot', 'urgent']
        )
        
        assert event1.is_similar_to(event2, min_common_tags=2) is True
        assert event1.is_similar_to(event2, min_common_tags=3) is True
    
    def test_is_not_similar_with_insufficient_tags(self):
        """测试相似度判断 - 共同标签不足"""
        event1 = AnomalyEvent(
            anomaly_type='test1',
            severity=5,
            occurrence=3,
            detection_difficulty=2,
            location='L1',
            description='d1',
            tags=['welding', 'quality']
        )
        
        event2 = AnomalyEvent(
            anomaly_type='test2',
            severity=6,
            occurrence=4,
            detection_difficulty=3,
            location='L2',
            description='d2',
            tags=['robot', 'urgent']
        )
        
        assert event1.is_similar_to(event2, min_common_tags=2) is False
    
    def test_is_similar_with_default_threshold(self):
        """测试相似度判断 - 默认阈值（2个共同标签）"""
        event1 = AnomalyEvent(
            anomaly_type='test1',
            severity=5,
            occurrence=3,
            detection_difficulty=2,
            location='L1',
            description='d1',
            tags=['welding', 'robot']
        )
        
        event2 = AnomalyEvent(
            anomaly_type='test2',
            severity=6,
            occurrence=4,
            detection_difficulty=3,
            location='L2',
            description='d2',
            tags=['welding', 'quality']
        )
        
        # 默认 min_common_tags=2
        assert event1.is_similar_to(event2) is True


class TestAnomalyEventStringRepresentation:
    """测试字符串表示"""
    
    def test_str_representation(self):
        """测试 __str__ 方法"""
        event = AnomalyEvent(
            anomaly_type='welding_defect',
            severity=7,
            occurrence=5,
            detection_difficulty=3,
            location='Welding-Station-A',
            description='test'
        )
        
        str_repr = str(event)
        
        assert 'welding_defect' in str_repr
        assert 'RPN=105' in str_repr
    
    def test_repr_representation(self):
        """测试 __repr__ 方法"""
        event = AnomalyEvent(
            anomaly_type='test',
            severity=5,
            occurrence=3,
            detection_difficulty=2,
            location='L1',
            description='test'
        )
        
        repr_str = repr(event)
        
        assert 'test' in repr_str
        assert '30' in repr_str  # RPN = 5*3*2 = 30


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

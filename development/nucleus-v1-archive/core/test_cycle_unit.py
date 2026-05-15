#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CycleUnit 读写工具库单元测试

测试覆盖率目标：≥ 95%
"""

import os
import shutil
import tempfile
import pytest
from datetime import datetime, timezone

# 添加项目根目录到 Python 路径
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.cycle_unit import (
    load_cycle, save_cycle, update_phase, create_cycle, get_cycle_version,
    CycleUnitNotFoundError, CycleUnitWriteError
)


class TestCycleUnit:
    """CycleUnit 读写工具库测试类"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        # 创建临时工作目录
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        # 创建 cycles 目录结构
        os.makedirs('cycles/task', exist_ok=True)
        os.makedirs('cycles/topic', exist_ok=True)
        os.makedirs('cycles/project', exist_ok=True)
        os.makedirs('cycles/system', exist_ok=True)
        os.makedirs('cycles/archive/task', exist_ok=True)
        os.makedirs('cycles/archive/topic', exist_ok=True)
        os.makedirs('cycles/archive/project', exist_ok=True)
        os.makedirs('cycles/archive/system', exist_ok=True)
    
    def teardown_method(self):
        """每个测试方法后的清理"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir)
    
    def test_create_and_load_cycle(self):
        """测试创建和加载 CycleUnit"""
        cycle_id = "task-20260405-abc123"
        scope = "task"
        initial_data = {
            'plan': {
                'intent': 'Test intent',
                'success_criteria': ['criteria1', 'criteria2']
            }
        }
        
        # 创建 CycleUnit
        create_cycle(cycle_id, scope, initial_data)
        
        # 加载并验证
        unit = load_cycle(cycle_id, scope)
        
        assert unit['id'] == cycle_id
        assert unit['scope'] == scope
        assert unit['phase'] == 'plan'
        assert unit['plan']['intent'] == 'Test intent'
        assert unit['metadata']['version'] == 1
        assert 'created_at' in unit['metadata']
        assert 'updated_at' in unit['metadata']
    
    def test_save_cycle_atomic_write(self):
        """测试原子性写入"""
        cycle_id = "task-20260405-def456"
        scope = "task"
        
        # 创建初始 CycleUnit
        initial_data = {'plan': {'intent': 'Initial'}}
        create_cycle(cycle_id, scope, initial_data)
        
        # 验证初始版本
        unit = load_cycle(cycle_id, scope)
        assert unit['metadata']['version'] == 1
        assert unit['plan']['intent'] == 'Initial'
        
        # 修改并保存
        unit['plan']['intent'] = 'Modified'
        save_cycle(unit)
        
        # 验证更新后的内容和版本
        updated_unit = load_cycle(cycle_id, scope)
        assert updated_unit['metadata']['version'] == 2
        assert updated_unit['plan']['intent'] == 'Modified'
        
        # 验证时间戳更新
        assert updated_unit['metadata']['updated_at'] != unit['metadata']['updated_at']
    
    def test_update_phase_with_archive(self):
        """测试更新 phase 并归档"""
        cycle_id = "task-20260405-ghi789"
        scope = "task"
        
        # 创建初始 CycleUnit
        initial_data = {'plan': {'intent': 'Test for archive'}}
        create_cycle(cycle_id, scope, initial_data)
        
        # 获取初始版本
        initial_version = get_cycle_version(cycle_id, scope)
        assert initial_version == 1
        
        # 更新 phase 到 do
        update_phase(cycle_id, scope, 'do')
        
        # 验证当前状态
        current_unit = load_cycle(cycle_id, scope)
        assert current_unit['phase'] == 'do'
        assert current_unit['metadata']['version'] == 3  # create(1) + save(2) + update_phase(3)
        
        # 验证归档文件存在
        archive_path = f'cycles/archive/{scope}/{cycle_id}_v{initial_version}.yaml'
        assert os.path.exists(archive_path)
        
        # 验证归档文件内容正确
        with open(archive_path, 'r') as f:
            archived_unit = yaml.safe_load(f)
        assert archived_unit['phase'] == 'plan'  # 归档的是更新前的状态
    
    def test_concurrent_writes(self):
        """测试并发写入（模拟）"""
        cycle_id = "task-20260405-jkl012"
        scope = "task"
        
        # 创建初始 CycleUnit
        create_cycle(cycle_id, scope, {'data': 'initial'})
        
        # 模拟多次快速写入
        for i in range(5):
            unit = load_cycle(cycle_id, scope)
            unit['data'] = f'iteration_{i}'
            save_cycle(unit)
        
        # 验证最终状态
        final_unit = load_cycle(cycle_id, scope)
        assert final_unit['data'] == 'iteration_4'
        assert final_unit['metadata']['version'] == 6  # create(1) + 5 writes
    
    def test_invalid_phase_update(self):
        """测试无效的 phase 更新"""
        cycle_id = "task-20260405-mno345"
        scope = "task"
        
        create_cycle(cycle_id, scope, {})
        
        # 尝试无效的 phase
        with pytest.raises(ValueError):
            update_phase(cycle_id, scope, 'invalid_phase')
    
    def test_load_nonexistent_cycle(self):
        """测试加载不存在的 CycleUnit"""
        with pytest.raises(CycleUnitNotFoundError):
            load_cycle("nonexistent", "task")
    
    def test_save_without_required_fields(self):
        """测试保存缺少必需字段的 CycleUnit"""
        incomplete_unit = {'missing_id': True}
        
        with pytest.raises(CycleUnitWriteError):
            save_cycle(incomplete_unit)
    
    def test_metadata_fields_consistency(self):
        """测试 metadata 字段一致性"""
        cycle_id = "task-20260405-pqr678"
        scope = "task"
        
        create_cycle(cycle_id, scope, {})
        unit = load_cycle(cycle_id, scope)
        
        # 验证必需的 metadata 字段
        metadata = unit['metadata']
        assert 'version' in metadata
        assert 'created_at' in metadata
        assert 'updated_at' in metadata
        assert 'global_max_cycles' in metadata
        
        # 验证时间格式
        created_dt = datetime.fromisoformat(metadata['created_at'].replace('Z', '+00:00'))
        updated_dt = datetime.fromisoformat(metadata['updated_at'].replace('Z', '+00:00'))
        
        # 验证 UTC 时区
        assert created_dt.tzinfo == timezone.utc
        assert updated_dt.tzinfo == timezone.utc
    
    def test_file_permissions_and_encoding(self):
        """测试文件权限和编码"""
        cycle_id = "task-20260405-stu901"
        scope = "task"
        
        # 包含中文字符的数据
        chinese_data = {
            'plan': {
                'intent': '测试中文支持',
                'success_criteria': ['标准1', '标准2']
            }
        }
        
        create_cycle(cycle_id, scope, chinese_data)
        unit = load_cycle(cycle_id, scope)
        
        assert unit['plan']['intent'] == '测试中文支持'
        assert unit['plan']['success_criteria'] == ['标准1', '标准2']
    
    def test_directory_creation(self):
        """测试自动创建目录"""
        # 切换到新的临时目录，不预先创建 cycles 目录
        new_temp_dir = tempfile.mkdtemp()
        original_cwd = os.getcwd()
        os.chdir(new_temp_dir)
        
        try:
            cycle_id = "topic-20260405-vwx234"
            scope = "topic"
            
            create_cycle(cycle_id, scope, {})
            
            # 验证目录被自动创建
            assert os.path.exists(f'cycles/{scope}')
            assert os.path.exists(f'cycles/{scope}/{cycle_id}.yaml')
            
        finally:
            os.chdir(original_cwd)
            shutil.rmtree(new_temp_dir)


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--cov=core/cycle_unit', '--cov-report=term-missing'])
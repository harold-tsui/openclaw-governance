# NUCLEUS-4.0 分析工具集

这套工具集旨在帮助监控、分析和优化NUCLEUS-4.0的PDCA流程。

## 工具列表

### 1. PDCA 仪表板 (pdca_dashboard.py)
实时查看所有任务的PDCA状态和关键指标。

```bash
cd /Users/haroldtsui/Workspaces/openclaw/main/10_Projects/ZT-P015_NUCLEUS-4-0
python scripts/pdca_dashboard.py
```

### 2. PDCA 分析器 (pdca_analyzer.py)
深度分析PDCA执行数据，提供详细统计报告。

```bash
cd /Users/haroldtsui/Workspaces/openclaw/main/10_Projects/ZT-P015_NUCLEUS-4-0
python scripts/pdca_analyzer.py
```

### 3. PDCA 优化器 (pdca_optimizer.py)
识别流程瓶颈和低效环节，提供优化建议。

```bash
cd /Users/haroldtsui/Workspaces/openclaw/main/10_Projects/ZT-P015_NUCLEUS-4-0
python scripts/pdca_optimizer.py
```

## 功能特性

- **实时监控**: 提供当前任务状态的快照
- **历史分析**: 分析PDCA执行历史和趋势
- **瓶颈识别**: 识别流程中的瓶颈和问题区域
- **优化建议**: 提供基于数据的改进建议
- **可视化报告**: 清晰展示关键指标和状态

## 使用场景

- 项目健康状况检查
- 流程效率分析
- 优化策略制定
- 定期报告生成
- 异常检测和响应

## 集成

这些工具已经集成到openclaw的治理系统中，可以通过`nucleus-tools-dashboard`技能访问。

## 维护

- 工具位于 `/Users/haroldtsui/Workspaces/openclaw/main/10_Projects/ZT-P015_NUCLEUS-4-0/scripts/`
- 数据源为 `pdca/` 目录中的YAML文件
- 与NUCLEUS-4.0架构完全兼容
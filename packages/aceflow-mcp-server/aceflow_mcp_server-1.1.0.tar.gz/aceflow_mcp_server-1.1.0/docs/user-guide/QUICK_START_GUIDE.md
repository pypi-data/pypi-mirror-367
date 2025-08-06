# AceFlow MCP 工具快速开始指南

## 🚀 5分钟快速上手

### 第一步：初始化项目 (1分钟)
```json
// 创建一个标准的Web应用项目
{
  "tool": "aceflow_init",
  "parameters": {
    "mode": "standard",
    "project_name": "my-web-app"
  }
}
```

### 第二步：查看项目状态 (30秒)
```json
// 检查项目当前状态和进度
{
  "tool": "aceflow_stage",
  "parameters": {
    "action": "status"
  }
}
```

### 第三步：验证项目配置 (1分钟)
```json
// 确保项目配置正确
{
  "tool": "aceflow_validate",
  "parameters": {
    "mode": "basic"
  }
}
```

### 第四步：查看工作流阶段 (30秒)
```json
// 了解完整的开发流程
{
  "tool": "aceflow_stage",
  "parameters": {
    "action": "list"
  }
}
```

### 第五步：开始开发 (2分钟)
现在你已经有了一个完整的 AceFlow 项目！可以开始按照工作流阶段进行开发。

## 🎯 常用操作速查

### 项目管理
```json
// 查看当前状态
{"tool": "aceflow_stage", "parameters": {"action": "status"}}

// 推进到下一阶段
{"tool": "aceflow_stage", "parameters": {"action": "next"}}

// 重置项目状态
{"tool": "aceflow_stage", "parameters": {"action": "reset"}}
```

### 质量检查
```json
// 快速验证
{"tool": "aceflow_validate", "parameters": {"mode": "basic"}}

// 详细验证
{"tool": "aceflow_validate", "parameters": {"mode": "detailed", "report": true}}

// 自动修复
{"tool": "aceflow_validate", "parameters": {"mode": "basic", "fix": true}}
```

### 模板管理
```json
// 查看可用模板
{"tool": "aceflow_template", "parameters": {"action": "list"}}

// 应用新模板
{"tool": "aceflow_template", "parameters": {"action": "apply", "template": "complete"}}
```

## 📋 项目类型推荐

### Web应用项目
```json
{
  "mode": "standard",
  "project_name": "my-web-app"
}
```

### 移动应用项目
```json
{
  "mode": "complete",
  "project_name": "my-mobile-app"
}
```

### 快速原型
```json
{
  "mode": "minimal",
  "project_name": "prototype"
}
```

### AI/ML项目
```json
{
  "mode": "smart",
  "project_name": "ai-project"
}
```

## ⚡ 效率提升技巧

### 1. 使用模板快速切换
不同阶段可以使用不同的模板：
- 原型阶段：`minimal`
- 开发阶段：`standard`
- 发布阶段：`complete`

### 2. 定期验证保证质量
建议在每个阶段完成后运行验证：
```json
{"tool": "aceflow_validate", "parameters": {"mode": "basic"}}
```

### 3. 并行工作提高效率
可以同时进行：
- 状态检查 + 质量验证
- 模板调整 + 配置优化

### 4. 利用自动修复功能
遇到简单问题时启用自动修复：
```json
{"tool": "aceflow_validate", "parameters": {"fix": true}}
```

## 🔧 故障快速排查

### 问题：工具调用失败
1. 检查参数格式是否正确
2. 确认必需参数已提供
3. 验证枚举值是否有效

### 问题：项目状态异常
1. 运行状态检查：`aceflow_stage({"action": "status"})`
2. 运行详细验证：`aceflow_validate({"mode": "detailed"})`
3. 必要时重置状态：`aceflow_stage({"action": "reset"})`

### 问题：阶段推进失败
1. 确认当前阶段工作已完成
2. 运行质量验证确保符合标准
3. 检查是否有阻塞性问题

## 📚 进阶学习路径

### 初学者 (第1-2周)
1. 熟悉基本工具使用
2. 理解工作流阶段概念
3. 掌握基础验证和调试

### 进阶用户 (第3-4周)
1. 学习模板定制和切换
2. 掌握并行工作模式
3. 了解性能优化技巧

### 专家用户 (第5周+)
1. 深入理解各种模式差异
2. 掌握复杂项目管理技巧
3. 能够指导团队使用最佳实践

## 🎉 恭喜！

你现在已经掌握了 AceFlow MCP 工具的基本使用方法。继续探索更多高级功能，让AI助力你的开发工作流程！

---

💡 **提示**: 遇到问题时，可以随时查看 [完整使用指南](./TOOL_USAGE_GUIDE.md) 获取更详细的信息。
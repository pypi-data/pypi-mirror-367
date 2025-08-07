# AI Develop Assistant

协助AI开发者进行智能化需求完善、模块设计、技术架构设计的MCP工具

## 🔧 核心工具
1. **start_new_project** - 开始新项目
2. **create_requirement_blueprint** - 创建需求蓝图
3. **requirement_clarifier** - 获取需求澄清提示
4. **save_clarification_tasks** - 保存澄清任务
5. **update_branch_status** - 更新分支状态
6. **requirement_manager** - 需求文档管理器
7. **check_architecture_prerequisites** - 检查架构前置条件
8. **get_architecture_design_prompt** - 获取架构设计提示
9. **save_generated_architecture** - 保存生成的架构设计
10. **export_final_document** - 导出完整文档
11. **view_requirements_status** - 查看需求状态

## 📁 配置方法

### Claude Desktop配置

1. **找到配置文件位置**
   ```
   Windows: %APPDATA%\Claude\claude_desktop_config.json
   macOS: ~/Library/Application Support/Claude/claude_desktop_config.json
   Linux: ~/.config/claude/claude_desktop_config.json
   ```

2. **添加配置内容**
   ```json
   {
     "mcpServers": {
       "ai-develop-assistant": {
         "command": "uvx",
         "args": ["ai-develop-assistant@latest"],
         "env": {
           "MCP_STORAGE_DIR": "/path/to/your/storage"
         }
       }
     }
   }
   ```

3. **重启Claude Desktop**

## 📊 存储结构

配置成功后，会在指定目录生成以下文件：

```
your_storage_directory/
├── requirements.json      # 实时需求文档
└── final_document_*.md   # Markdown格式报告
```


## 💬 交流群

<div align="center">
<img src="./assets/qr-code.jpg" width="200" alt="交流群">
<br>
交流群
</div>



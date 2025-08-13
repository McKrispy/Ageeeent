# LLM 测试界面

这是一个基于Streamlit构建的LLM测试GUI界面，用于测试不同AI模型的交互效果。

## 🚀 功能特性

- **多模型支持**: 支持OpenAI、Anthropic、Google等主流AI模型
- **灵活配置**: 可配置API密钥、模型参数等
- **参数调优**: 支持Temperature、Max Tokens、Top P等参数调整
- **快速提示**: 内置常用提示词模板
- **历史记录**: 保存对话历史，方便回顾
- **响应操作**: 支持复制、保存、重新生成等操作

## 📁 项目结构

```
GUI/
├── app.py                 # 主应用入口
├── components/            # 界面组件
│   ├── llm_interface.py  # 主界面组件
│   ├── config_panel.py   # 配置面板
│   ├── prompt_panel.py   # 提示词输入面板
│   └── result_panel.py   # 结果显示面板
├── config/               # 配置管理
│   └── settings.py       # 配置管理器
├── utils/                # 工具函数
│   └── helpers.py        # 辅助函数
├── requirements.txt      # 依赖包列表
└── README.md            # 说明文档
```

## 🛠️ 安装和运行

### 1. 安装依赖

```bash
cd GUI
pip install -r requirements.txt
```

### 2. 运行应用

```bash
streamlit run app.py
```

### 3. 访问界面

应用启动后，在浏览器中打开显示的地址（通常是 http://localhost:8501）

## 🎯 使用说明

### 配置设置
1. 在左侧配置面板中选择要使用的AI模型
2. 输入相应的API密钥
3. 点击"保存配置"按钮

### 测试交互
1. 在右侧输入提示词
2. 可选择快速提示词模板
3. 调整生成参数（可选）
4. 点击"发送请求"按钮
5. 查看AI响应结果

### 参数说明
- **Temperature**: 控制输出的随机性（0.0-2.0）
- **Max Tokens**: 限制输出的最大Token数量
- **Top P**: 控制词汇选择的多样性（0.0-1.0）
- **Frequency Penalty**: 减少重复内容的生成（-2.0-2.0）

## 🔧 配置说明

配置文件 `llm_config.json` 会自动创建，包含：
- 支持的模型列表
- 默认选中的模型
- API密钥配置
- 默认提示词模板

## 🚧 开发状态

**当前版本**: v1.0.0 (演示版)

**已完成功能**:
- ✅ 基础界面框架
- ✅ 配置管理
- ✅ 提示词输入
- ✅ 模拟响应显示
- ✅ 参数配置界面

**待实现功能**:
- 🔄 实际LLM API调用
- 🔄 响应流式显示
- 🔄 对话历史持久化
- 🔄 导出功能
- 🔄 批量测试

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目！

## �� 许可证

本项目采用MIT许可证。

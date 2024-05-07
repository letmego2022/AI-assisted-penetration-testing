# AI辅助渗透测试工具

该存储库包含使用Tkinter构建的Python应用程序，用作AI辅助渗透测试工具。该工具允许用户分析包含有关URL、MIME类型和其他请求/响应数据的XML文件，并执行基于AI的测试，以识别潜在的安全问题和进一步调查的领域。

## 功能

- **打开XML文件**：允许用户选择包含用于分析的请求/响应数据的XML文件。
- **AI测试**：对选定的请求/响应数据执行基于AI的测试，以识别安全问题和潜在的攻击面。
- **结果分析**：提供AI测试结果的分析，包括识别的安全问题、拓展的攻击面和基本系统信息。
- **GUI界面**：提供用户友好的图形界面，用于与工具进行交互。
- **自动测试**：提供一键按钮，自动AI分析并对结果进行聚合展示。(5.7添加)

## 要求

- Python 3.x
- Tkinter（通常与Python一起提供）
- xml.etree.ElementTree
- base64
- openai

## 用法

1. 将存储库克隆到本地计算机。
2. 使用 `pip install -r requirements.txt` 安装所需的依赖项。
3. 使用 `python main.py` 运行应用程序。
4. 单击“选择XML文件”按钮选择要分析的XML文件。
5. 使用“AI测试”按钮对选定的数据执行基于AI的测试。
6. 使用“结果分析”按钮分析结果。

## 截图



## 贡献

欢迎贡献！如果您想为此项目做出贡献，请按照以下步骤进行：

1. Fork该存储库。
2. 创建一个新分支（`git checkout -b feature/your-feature-name`）。
3. 进行更改。
4. 提交更改（`git commit -am 'Add new feature'`）。
5. 推送到分支（`git push origin feature/your-feature-name`）。
6. 创建一个新的Pull请求。

## 许可证

[如果适用，请在此处包含许可证信息]


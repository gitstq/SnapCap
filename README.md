<p align="center">
  <img src="https://img.shields.io/badge/version-1.0.0-blue.svg" alt="Version" />
  <img src="https://img.shields.io/badge/python-3.9+-green.svg" alt="Python" />
  <img src="https://img.shields.io/badge/license-MIT-orange.svg" alt="License" />
  <img src="https://img.shields.io/badge/tests-81%20passed-success.svg" alt="Tests" />
  <img src="https://img.shields.io/badge/dependencies-minimal-critical.svg" alt="Dependencies" />
</p>

<h1 align="center">📸 SnapCap</h1>

<p align="center">
  <strong>轻量级终端截图标注与分享工具</strong><br/>
  <em>Lightweight Terminal Screenshot Annotation & Sharing CLI Tool</em>
</p>

<p align="center">
  <a href="#-简体中文">简体中文</a> ·
  <a href="#-繁體中文">繁體中文</a> ·
  <a href="#-english">English</a>
</p>

---

## 🇨🇳 简体中文

### 🎉 项目介绍

**SnapCap** 是一款专为开发者打造的轻量级终端截图标注与分享工具。灵感来源于开发者日常工作中频繁的截图、标注、分享需求——写技术文档需要标注截图、提交 Bug 需要圈出问题区域、代码评审需要高亮关键部分。

与 ShareX 等重量级桌面应用不同，SnapCap 采用 **纯 CLI 驱动** 的设计理念，完美融入开发者的终端工作流。支持截图 → 标注 → 上传的完整链路，可通过管道操作一键完成，让截图分享像执行命令一样简单。

#### ✨ 自研差异化亮点

- 🚀 **纯 CLI 驱动**：无需 GUI，完美融入终端工作流，支持管道操作
- 🎨 **7 种标注类型**：矩形框、箭头、文字、马赛克、模糊、高亮、序号标记
- ☁️ **多图床支持**：内置 file.io、imgbb，支持自定义 API 端点
- 📋 **智能剪贴板**：上传后自动复制 Markdown 格式链接
- 🔧 **零配置启动**：开箱即用，仅需 Pillow 一个外部依赖
- 📜 **历史追踪**：自动记录每次截图，方便回溯查找
- 🖥️ **跨平台兼容**：Windows / macOS / Linux 全平台支持

### ✨ 核心特性

| 功能模块 | 说明 |
|---------|------|
| 📸 **截图引擎** | 支持全屏、窗口选择、区域坐标三种截图模式 |
| 🖊️ **标注引擎** | 矩形框、箭头、文字、马赛克、模糊、高亮、序号标记，支持自定义颜色和线宽 |
| ☁️ **图床上传** | file.io（免费临时）、imgbb（免费永久）、自定义 API 端点 |
| 📋 **剪贴板** | 跨平台剪贴板操作，自动复制分享链接 |
| ⚙️ **配置管理** | JSON 配置文件，支持导入/导出/重置 |
| 📜 **截图历史** | 自动记录截图时间、路径、文件大小 |
| 🔗 **管道操作** | 支持 `capture → annotate → upload` 一键链式操作 |

### 🚀 快速开始

#### 环境要求

- **Python** 3.9 或更高版本
- **Pillow** >= 9.0.0（唯一外部依赖）
- **操作系统**：Windows / macOS / Linux

#### 安装

```bash
# 从 PyPI 安装（推荐）
pip install snapcap

# 从源码安装
git clone https://github.com/gitstq/SnapCap.git
cd SnapCap
pip install -e .
```

#### 快速使用

```bash
# 全屏截图
snapcap capture --mode fullscreen

# 窗口截图
snapcap capture --mode window --window-title "Chrome"

# 区域截图
snapcap capture --mode region --region 100 100 500 400

# 标注截图 - 矩形框
snapcap annotate screenshot.png --rect 10 10 200 200

# 标注截图 - 箭头
snapcap annotate screenshot.png --arrow 50 50 300 300

# 标注截图 - 文字
snapcap annotate screenshot.png --text 100 100 "重点区域"

# 标注截图 - 马赛克
snapcap annotate screenshot.png --mosaic 200 200 400 400

# 上传到图床
snapcap upload screenshot.png --provider fileio

# 一键管道操作：截图 → 标注 → 上传
snapcap capture | snapcap annotate --rect 10 10 200 200 | snapcap upload
```

### 📖 详细使用指南

#### 截图命令

```bash
snapcap capture [选项]

选项：
  --mode, -m       截图模式：fullscreen（全屏）/ window（窗口）/ region（区域）
  --output, -o     输出目录路径（默认：./screenshots/）
  --filename, -f   自定义输出文件名
  --region, -r     区域坐标（格式：x1 y1 x2 y2）
  --window-title, -w  窗口标题（支持部分匹配）
```

#### 标注命令

```bash
snapcap annotate <图片路径> [选项]

选项：
  --rect X1 Y1 X2 Y2        矩形框标注
  --arrow X1 Y1 X2 Y2       箭头标注
  --text X Y "内容"          文字标注
  --mosaic X1 Y1 X2 Y2      马赛克效果
  --blur X1 Y1 X2 Y2        模糊效果
  --highlight X1 Y1 X2 Y2   高亮标注
  --number X Y              序号标记（可多次使用）
  --color                   标注颜色（十六进制，如 #FF0000）
  --width                   线条宽度（默认：3）
  --font-size               文字大小（默认：24）
  --output, -o              输出文件路径
```

#### 上传命令

```bash
snapcap upload <图片路径> [选项]

选项：
  --provider, -p   图床提供商：fileio / imgbb / custom
  --api-key        API 密钥（imgbb 需要）
  --endpoint       自定义 API 端点（custom 需要）
  --format         输出格式：url / markdown / html / json
  --copy           自动复制链接到剪贴板
```

#### 配置管理

```bash
# 查看当前配置
snapcap config --show

# 修改配置
snapcap config --set capture.default_mode=region
snapcap config --set annotate.rect_color=#00FF00
snapcap config --set upload.imgbb_api_key=YOUR_API_KEY

# 导出/导入配置
snapcap config --export config_backup.json
snapcap config --import config_backup.json

# 重置为默认配置
snapcap config --reset
```

#### 查看截图历史

```bash
snapcap history
```

### 💡 设计思路与迭代规划

#### 设计理念

SnapCap 的核心理念是 **"让截图分享回归终端"**。作为开发者，我们大部分时间都在终端中工作，而传统的截图工具往往需要打开 GUI 应用、手动操作多个步骤。SnapCap 将整个流程简化为一条命令，真正实现"所想即所得"。

#### 技术选型

- **Python**：开发者生态最成熟的语言，标准库丰富
- **Pillow**：Python 图像处理事实标准，稳定可靠
- **argparse**：标准库 CLI 框架，零额外依赖
- **JSON**：配置文件格式，人类可读可编辑

#### 后续迭代计划

- [ ] 🎬 添加 GIF 录制功能
- [ ] 🔍 添加 OCR 文字识别集成
- [ ] 🌐 添加更多图床支持（SM.MS、腾讯云 COS 等）
- [ ] 🎨 添加主题配置（暗色/亮色标注样式）
- [ ] 📦 添加打包为独立可执行文件（PyInstaller）
- [ ] 🔄 添加插件系统，支持自定义标注类型

### 📦 安装与部署

```bash
# 通过 pip 安装
pip install snapcap

# 从源码安装
git clone https://github.com/gitstq/SnapCap.git
cd SnapCap
pip install -e .

# 安装依赖
pip install -r requirements.txt
```

**依赖说明：**
| 依赖 | 版本 | 说明 |
|------|------|------|
| Pillow | >= 9.0.0 | 图像处理库（唯一外部依赖） |

### 🤝 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. 🍴 Fork 本仓库
2. 🌿 创建特性分支：`git checkout -b feature/your-feature`
3. 💾 提交更改：`git commit -m "feat: add your feature"`
4. 🚀 推送分支：`git push origin feature/your-feature`
5. 📝 提交 Pull Request

**提交规范：**
- `feat:` 新增功能
- `fix:` 修复问题
- `docs:` 文档更新
- `refactor:` 代码重构
- `test:` 测试相关
- `chore:` 构建/工具链相关

### 📄 开源协议

本项目基于 [MIT License](LICENSE) 开源。

---

## 🇹🇼 繁體中文

### 🎉 專案介紹

**SnapCap** 是一款專為開發者打造的輕量級終端截圖標註與分享工具。靈感來自於開發者日常工作中頻繁的截圖、標註、分享需求——撰寫技術文件需要標註截圖、提交 Bug 需要圈出問題區域、程式碼審查需要高亮關鍵部分。

與 ShareX 等重量級桌面應用不同，SnapCap 採用 **純 CLI 驅動** 的設計理念，完美融入開發者的終端工作流。支援截圖 → 標註 → 上傳的完整鏈路，可透過管道操作一鍵完成，讓截圖分享像執行命令一樣簡單。

#### ✨ 自研差異化亮點

- 🚀 **純 CLI 驅動**：無需 GUI，完美融入終端工作流，支援管道操作
- 🎨 **7 種標註類型**：矩形框、箭頭、文字、馬賽克、模糊、高亮、序號標記
- ☁️ **多圖床支援**：內建 file.io、imgbb，支援自訂 API 端點
- 📋 **智慧剪貼簿**：上傳後自動複製 Markdown 格式連結
- 🔧 **零配置啟動**：開箱即用，僅需 Pillow 一個外部依賴
- 📜 **歷史追蹤**：自動記錄每次截圖，方便回溯查找
- 🖥️ **跨平台相容**：Windows / macOS / Linux 全平台支援

### ✨ 核心特性

| 功能模組 | 說明 |
|---------|------|
| 📸 **截圖引擎** | 支援全螢幕、視窗選擇、區域座標三種截圖模式 |
| 🖊️ **標註引擎** | 矩形框、箭頭、文字、馬賽克、模糊、高亮、序號標記，支援自訂顏色和線寬 |
| ☁️ **圖床上傳** | file.io（免費暫時）、imgbb（免費永久）、自訂 API 端點 |
| 📋 **剪貼簿** | 跨平台剪貼簿操作，自動複製分享連結 |
| ⚙️ **配置管理** | JSON 配置檔案，支援匯入/匯出/重置 |
| 📜 **截圖歷史** | 自動記錄截圖時間、路徑、檔案大小 |
| 🔗 **管道操作** | 支援 `capture → annotate → upload` 一鍵鏈式操作 |

### 🚀 快速開始

#### 環境要求

- **Python** 3.9 或更高版本
- **Pillow** >= 9.0.0（唯一外部依賴）
- **作業系統**：Windows / macOS / Linux

#### 安裝

```bash
# 從 PyPI 安裝（推薦）
pip install snapcap

# 從原始碼安裝
git clone https://github.com/gitstq/SnapCap.git
cd SnapCap
pip install -e .
```

#### 快速使用

```bash
# 全螢幕截圖
snapcap capture --mode fullscreen

# 視窗截圖
snapcap capture --mode window --window-title "Chrome"

# 區域截圖
snapcap capture --mode region --region 100 100 500 400

# 標註截圖 - 矩形框
snapcap annotate screenshot.png --rect 10 10 200 200

# 標註截圖 - 箭頭
snapcap annotate screenshot.png --arrow 50 50 300 300

# 標註截圖 - 文字
snapcap annotate screenshot.png --text 100 100 "重點區域"

# 標註截圖 - 馬賽克
snapcap annotate screenshot.png --mosaic 200 200 400 400

# 上傳到圖床
snapcap upload screenshot.png --provider fileio

# 一鍵管道操作：截圖 → 標註 → 上傳
snapcap capture | snapcap annotate --rect 10 10 200 200 | snapcap upload
```

### 📖 詳細使用指南

#### 截圖命令

```bash
snapcap capture [選項]

選項：
  --mode, -m       截圖模式：fullscreen（全螢幕）/ window（視窗）/ region（區域）
  --output, -o     輸出目錄路徑（預設：./screenshots/）
  --filename, -f   自訂輸出檔案名稱
  --region, -r     區域座標（格式：x1 y1 x2 y2）
  --window-title, -w  視窗標題（支援部分匹配）
```

#### 標註命令

```bash
snapcap annotate <圖片路徑> [選項]

選項：
  --rect X1 Y1 X2 Y2        矩形框標註
  --arrow X1 Y1 X2 Y2       箭頭標註
  --text X Y "內容"          文字標註
  --mosaic X1 Y1 X2 Y2      馬賽克效果
  --blur X1 Y1 X2 Y2        模糊效果
  --highlight X1 Y1 X2 Y2   高亮標註
  --number X Y              序號標記（可多次使用）
  --color                   標註顏色（十六進位，如 #FF0000）
  --width                   線條寬度（預設：3）
  --font-size               文字大小（預設：24）
  --output, -o              輸出檔案路徑
```

#### 上傳命令

```bash
snapcap upload <圖片路徑> [選項]

選項：
  --provider, -p   圖床提供商：fileio / imgbb / custom
  --api-key        API 金鑰（imgbb 需要）
  --endpoint       自訂 API 端點（custom 需要）
  --format         輸出格式：url / markdown / html / json
  --copy           自動複製連結到剪貼簿
```

#### 配置管理

```bash
# 查看當前配置
snapcap config --show

# 修改配置
snapcap config --set capture.default_mode=region
snapcap config --set annotate.rect_color=#00FF00
snapcap config --set upload.imgbb_api_key=YOUR_API_KEY

# 匯出/匯入配置
snapcap config --export config_backup.json
snapcap config --import config_backup.json

# 重置為預設配置
snapcap config --reset
```

#### 查看截圖歷史

```bash
snapcap history
```

### 💡 設計思路與迭代規劃

#### 設計理念

SnapCap 的核心理念是 **「讓截圖分享回歸終端」**。作為開發者，我們大部分時間都在終端中工作，而傳統的截圖工具往往需要開啟 GUI 應用、手動操作多個步驟。SnapCap 將整個流程簡化為一條命令，真正實現「所想即所得」。

#### 技術選型

- **Python**：開發者生態最成熟的語言，標準函式庫豐富
- **Pillow**：Python 影像處理事實標準，穩定可靠
- **argparse**：標準函式庫 CLI 框架，零額外依賴
- **JSON**：配置檔案格式，人類可讀可編輯

#### 後續迭代計畫

- [ ] 🎬 新增 GIF 錄製功能
- [ ] 🔍 新增 OCR 文字辨識整合
- [ ] 🌐 新增更多圖床支援（SM.MS、騰訊雲 COS 等）
- [ ] 🎨 新增主題配置（暗色/亮色標註樣式）
- [ ] 📦 新增打包為獨立可執行檔（PyInstaller）
- [ ] 🔄 新增外掛系統，支援自訂標註類型

### 📦 安裝與部署

```bash
# 透過 pip 安裝
pip install snapcap

# 從原始碼安裝
git clone https://github.com/gitstq/SnapCap.git
cd SnapCap
pip install -e .

# 安裝依賴
pip install -r requirements.txt
```

**依賴說明：**
| 依賴 | 版本 | 說明 |
|------|------|------|
| Pillow | >= 9.0.0 | 影像處理函式庫（唯一外部依賴） |

### 🤝 貢獻指南

歡迎貢獻程式碼！請遵循以下步驟：

1. 🍴 Fork 本倉庫
2. 🌿 建立特性分支：`git checkout -b feature/your-feature`
3. 💾 提交變更：`git commit -m "feat: add your feature"`
4. 🚀 推送分支：`git push origin feature/your-feature`
5. 📝 提交 Pull Request

**提交規範：**
- `feat:` 新增功能
- `fix:` 修復問題
- `docs:` 文件更新
- `refactor:` 程式碼重構
- `test:` 測試相關
- `chore:` 建構/工具鏈相關

### 📄 開源協議

本專案基於 [MIT License](LICENSE) 開源。

---

## 🇬🇧 English

### 🎉 Introduction

**SnapCap** is a lightweight terminal screenshot annotation and sharing tool built specifically for developers. Inspired by the frequent need for screenshots, annotations, and sharing in daily development workflows — annotating screenshots for technical documentation, highlighting problem areas for bug reports, or marking key sections during code reviews.

Unlike heavyweight desktop applications like ShareX, SnapCap adopts a **pure CLI-driven** design philosophy, seamlessly integrating into the developer's terminal workflow. It supports the complete pipeline of capture → annotate → upload, which can be accomplished in one step through pipe operations, making screenshot sharing as simple as executing a command.

#### ✨ Differentiated Highlights

- 🚀 **Pure CLI Driven**: No GUI needed, perfectly integrated into terminal workflows with pipe support
- 🎨 **7 Annotation Types**: Rectangle, arrow, text, mosaic, blur, highlight, and numbered markers
- ☁️ **Multi-Host Support**: Built-in file.io, imgbb, and custom API endpoints
- 📋 **Smart Clipboard**: Auto-copies Markdown-formatted links after upload
- 🔧 **Zero-Config Start**: Ready to use out of the box, only requires Pillow as external dependency
- 📜 **History Tracking**: Automatically records every screenshot for easy retrieval
- 🖥️ **Cross-Platform**: Full support for Windows / macOS / Linux

### ✨ Core Features

| Module | Description |
|--------|-------------|
| 📸 **Capture Engine** | Fullscreen, window selection, and region coordinate capture modes |
| 🖊️ **Annotation Engine** | Rectangle, arrow, text, mosaic, blur, highlight, number markers with custom colors and line widths |
| ☁️ **Image Uploader** | file.io (free temporary), imgbb (free permanent), custom API endpoints |
| 📋 **Clipboard** | Cross-platform clipboard operations with auto-copy share links |
| ⚙️ **Config Manager** | JSON config file with import/export/reset support |
| 📜 **Screenshot History** | Auto-records capture time, path, and file size |
| 🔗 **Pipe Operations** | Supports `capture → annotate → upload` one-step chain operations |

### 🚀 Quick Start

#### Requirements

- **Python** 3.9 or higher
- **Pillow** >= 9.0.0 (only external dependency)
- **OS**: Windows / macOS / Linux

#### Installation

```bash
# Install from PyPI (recommended)
pip install snapcap

# Install from source
git clone https://github.com/gitstq/SnapCap.git
cd SnapCap
pip install -e .
```

#### Quick Usage

```bash
# Fullscreen capture
snapcap capture --mode fullscreen

# Window capture
snapcap capture --mode window --window-title "Chrome"

# Region capture
snapcap capture --mode region --region 100 100 500 400

# Annotate - Rectangle
snapcap annotate screenshot.png --rect 10 10 200 200

# Annotate - Arrow
snapcap annotate screenshot.png --arrow 50 50 300 300

# Annotate - Text
snapcap annotate screenshot.png --text 100 100 "Important Area"

# Annotate - Mosaic
snapcap annotate screenshot.png --mosaic 200 200 400 400

# Upload to image host
snapcap upload screenshot.png --provider fileio

# One-step pipe: capture → annotate → upload
snapcap capture | snapcap annotate --rect 10 10 200 200 | snapcap upload
```

### 📖 Detailed Usage Guide

#### Capture Command

```bash
snapcap capture [options]

Options:
  --mode, -m       Capture mode: fullscreen / window / region
  --output, -o     Output directory (default: ./screenshots/)
  --filename, -f   Custom output filename
  --region, -r     Region coordinates (format: x1 y1 x2 y2)
  --window-title, -w  Window title (supports partial match)
```

#### Annotate Command

```bash
snapcap annotate <image_path> [options]

Options:
  --rect X1 Y1 X2 Y2        Rectangle annotation
  --arrow X1 Y1 X2 Y2       Arrow annotation
  --text X Y "content"       Text annotation
  --mosaic X1 Y1 X2 Y2      Mosaic effect
  --blur X1 Y1 X2 Y2        Blur effect
  --highlight X1 Y1 X2 Y2   Highlight annotation
  --number X Y              Number marker (can be used multiple times)
  --color                   Annotation color (hex, e.g. #FF0000)
  --width                   Line width (default: 3)
  --font-size               Font size (default: 24)
  --output, -o              Output file path
```

#### Upload Command

```bash
snapcap upload <image_path> [options]

Options:
  --provider, -p   Image host: fileio / imgbb / custom
  --api-key        API key (required for imgbb)
  --endpoint       Custom API endpoint (required for custom)
  --format         Output format: url / markdown / html / json
  --copy           Auto-copy link to clipboard
```

#### Configuration Management

```bash
# Show current config
snapcap config --show

# Set config values
snapcap config --set capture.default_mode=region
snapcap config --set annotate.rect_color=#00FF00
snapcap config --set upload.imgbb_api_key=YOUR_API_KEY

# Export/Import config
snapcap config --export config_backup.json
snapcap config --import config_backup.json

# Reset to defaults
snapcap config --reset
```

#### View Screenshot History

```bash
snapcap history
```

### 💡 Design Philosophy & Roadmap

#### Design Philosophy

SnapCap's core philosophy is **"Bring screenshot sharing back to the terminal"**. As developers, we spend most of our time in the terminal, yet traditional screenshot tools require opening GUI applications and performing multiple manual steps. SnapCap simplifies the entire workflow into a single command, truly achieving "what you think is what you get."

#### Tech Stack

- **Python**: The most mature developer ecosystem with rich standard library
- **Pillow**: The de facto standard for Python image processing, stable and reliable
- **argparse**: Standard library CLI framework with zero extra dependencies
- **JSON**: Human-readable and editable configuration file format

#### Roadmap

- [ ] 🎬 GIF recording support
- [ ] 🔍 OCR text recognition integration
- [ ] 🌐 More image hosts (SM.MS, Tencent Cloud COS, etc.)
- [ ] 🎨 Theme configuration (dark/light annotation styles)
- [ ] 📦 Package as standalone executable (PyInstaller)
- [ ] 🔄 Plugin system for custom annotation types

### 📦 Installation & Deployment

```bash
# Install via pip
pip install snapcap

# Install from source
git clone https://github.com/gitstq/SnapCap.git
cd SnapCap
pip install -e .

# Install dependencies
pip install -r requirements.txt
```

**Dependencies:**
| Dependency | Version | Description |
|-----------|---------|-------------|
| Pillow | >= 9.0.0 | Image processing library (only external dependency) |

### 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. 🍴 Fork this repository
2. 🌿 Create a feature branch: `git checkout -b feature/your-feature`
3. 💾 Commit your changes: `git commit -m "feat: add your feature"`
4. 🚀 Push to the branch: `git push origin feature/your-feature`
5. 📝 Submit a Pull Request

**Commit Convention:**
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation update
- `refactor:` Code refactoring
- `test:` Test related
- `chore:` Build/toolchain related

### 📄 License

This project is licensed under the [MIT License](LICENSE).

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/gitstq">gitstq</a>
</p>

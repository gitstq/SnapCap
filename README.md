# SnapCap

SnapCap - 轻量级终端截图标注与分享工具

## 安装

```bash
pip install -e .
```

## 使用

```bash
# 截图
snapcap capture --mode fullscreen --output ./screenshots/
snapcap capture --mode window
snapcap capture --mode region

# 标注
snapcap annotate screenshot.png --rect 10 10 200 200
snapcap annotate screenshot.png --arrow 10 10 200 200
snapcap annotate screenshot.png --text 50 50 "Hello"
snapcap annotate screenshot.png --mosaic 100 100 300 300
snapcap annotate screenshot.png --highlight 100 100 300 300

# 上传
snapcap upload screenshot.png --provider fileio
snapcap upload screenshot.png --provider imgbb --api-key YOUR_KEY

# 管道操作
snapcap capture | snapcap annotate --rect 10 10 200 200 | snapcap upload

# 配置
snapcap config --show
snapcap config --set capture.default_mode=region

# 历史
snapcap history
```

## 许可证

MIT License

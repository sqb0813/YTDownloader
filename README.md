# YouTube 视频下载器

一个基于 FastAPI 和 yt-dlp 的 YouTube 视频下载器，支持进度显示和视频管理。

## 功能特性

- 支持 YouTube 视频下载
- 实时显示下载进度
- 视频管理界面
- 响应式设计
- 支持高质量视频下载

## 安装步骤

### 安装 FFmpeg

#### Windows:

1. 下载 FFmpeg:

   - 访问 https://github.com/yt-dlp/FFmpeg-Builds/releases
   - 下载最新的 ffmpeg-master-latest-win64-gpl.zip

2. 解压安装:

   - 解压下载的 zip 文件到任意目录(如 C:\ffmpeg)
   - 记住 bin 目录的完整路径(如 C:\ffmpeg\bin)

3. 配置环境变量:

   - 右键"此电脑" -> 属性 -> 高级系统设置 -> 环境变量
   - 在"系统变量"中找到 Path 变量并双击
   - 点击"新建"并添加 bin 目录的路径(如 C:\ffmpeg\bin)
   - 点击"确定"保存所有窗口

4. 验证安装:
   - 打开新的命令提示符窗口
   - 输入 `ffmpeg -version`
   - 如果显示版本信息则安装成功

#### Linux:

##### Ubuntu/Debian:

pip install -i https://pypi.tuna.tsinghua.edu.cn/simple some-package fastapi uvicorn jinja2 yt-dlp humanize python-multipart pyinstaller

## 激活虚拟环境

### Windows PowerShell/CMD:

# 创建虚拟环境(没有 venv 目录的情况下)

python -m venv venv

# 激活虚拟环境

.\venv\Scripts\activate

### Linux/Mac:

source venv/bin/activate

## 启动服务

uvicorn main:app --reload

## 访问网址

http://localhost:8000

# 生成 exe 文件步骤

## 安装 pyinstaller

pip install pyinstaller

## 生成 exe 文件

pyinstaller --add-data "templates:templates" --add-data "static:static" main.py

## 打包成 electron 软件

.\venv\Scripts\activate
npm run prepare-backend
npm run pack-backend
npm run build

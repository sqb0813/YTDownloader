from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
import yt_dlp
import os
import asyncio
from pathlib import Path
import humanize
import time
import socket
import re
import unicodedata
from concurrent.futures import ThreadPoolExecutor

# 创建必要的目录
DOWNLOAD_DIR = Path("downloads")
STATIC_DIR = Path("static")
DOWNLOAD_DIR.mkdir(exist_ok=True)
STATIC_DIR.mkdir(exist_ok=True)
CACHE_DIR = Path("cache")
CACHE_DIR.mkdir(exist_ok=True)

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/downloads", StaticFiles(directory="downloads"), name="downloads")

# 存储下载状态
download_status = {}

# 添加代理配置
PROXY_HOST = os.getenv("PROXY_HOST", "127.0.0.1")
PROXY_PORT = int(os.getenv("PROXY_PORT", "1080"))
USE_PROXY = os.getenv("USE_PROXY", "0") == "1"

# 添加下载配置
CONCURRENT_DOWNLOADS = 3  # 同时下载数量
THREAD_POOL = ThreadPoolExecutor(max_workers=CONCURRENT_DOWNLOADS)

# 在文件开头添加图片扩展名列表
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.gif'}

def get_video_info(video_path):
    stats = os.stat(video_path)
    # 查找对应的缩略图文件
    # 尝试查找多种格式的缩略图
    thumbnail_formats = ['.webp', '.jpeg', '.jpg', '.png']
    thumbnail_path = None
    for fmt in thumbnail_formats:
        tmp_path = video_path.with_suffix(fmt)
        if tmp_path.exists():
            thumbnail_path = tmp_path
            break
    if not thumbnail_path:
        thumbnail_path = video_path.with_suffix('.webp')  # 默认使用webp格式
    thumbnail_url = None
    if thumbnail_path.exists():
        thumbnail_url = f"/downloads/{thumbnail_path.name}"
        
    return {
        "title": video_path.stem,
        "size": humanize.naturalsize(stats.st_size),
        "modified": time.ctime(stats.st_mtime),
        "path": str(video_path),
        "filename": video_path.name,
        "download_url": f"/download_file/{video_path.name}",
        "thumbnail": thumbnail_url
    }

def check_proxy(host=PROXY_HOST, port=PROXY_PORT):
    if not USE_PROXY:
        return True
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex((host, port))
    sock.close()
    return result == 0

def sanitize_filename(filename):
    """清理文件名,移除非法字符"""
    # 移除非法字符
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # 移除控制字符
    filename = "".join(char for char in filename if unicodedata.category(char)[0] != "C")
    # 限制长度(Windows最大路径长度限制)
    filename = filename[:200]
    # 移除首尾空格和点
    filename = filename.strip('. ')
    # 如果文件名为空,使用默认名称
    return filename or 'video'

async def download_video(url: str):
    download_status[url] = {"status": "downloading", "progress": 0}
    
    def progress_hook(d):
        if d["status"] == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate", 0)
            downloaded = d.get("downloaded_bytes", 0)
            if total > 0:
                progress = (downloaded / total) * 100
                download_status[url].update({
                    "status": "downloading",
                    "progress": round(progress, 2),
                    "speed": d.get("speed", 0),  # 原始速度数值(bytes/s)
                    "speed_str": d.get("_speed_str", "N/A"),
                    "eta": d.get("eta", 0),      # 原始剩余时间(秒)
                    "eta_str": d.get("_eta_str", "N/A"),
                    "total_bytes": total,
                    "downloaded_bytes": downloaded
                })
        elif d["status"] == "finished":
            if "thumbnail" in d:
                download_status[url]["thumbnail"] = d["thumbnail"]
            download_status[url].update({
                "status": "processing",  # 添加处理中状态
                "progress": 100
            })

    ydl_opts = {
        'format': 'best',
        'outtmpl': str(DOWNLOAD_DIR / '%(title).200s.%(ext)s'),
        'progress_hooks': [progress_hook],
        'cachedir': str(CACHE_DIR),
        'writethumbnail': True,
        'retries': 10,
        'fragment_retries': 10,
        'skip_unavailable_fragments': True,
        'restrictfilenames': True,
        'concurrent_fragment_downloads': 5,  # 并发分片下载
        'buffersize': 1024 * 1024,  # 增加缓冲区大小到1MB
        'http_chunk_size': 10485760,  # 10MB的块大小
        # 使用aria2作为外部下载器
        'external_downloader': 'aria2c',
        'external_downloader_args': [
            '--min-split-size=1M',
            '--max-connection-per-server=16',
            '--max-concurrent-downloads=3',
            '--split=16'
        ],
    }
    
    if USE_PROXY:
        if not check_proxy():
            download_status[url] = {"status": "error", "error": "代理服务器未运行,请检查代理设置"}
            return
        ydl_opts['proxy'] = f'socks5://{PROXY_HOST}:{PROXY_PORT}'

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            
            # 清理文件名
            safe_title = sanitize_filename(info['title'])
            file_path = DOWNLOAD_DIR / f"{safe_title}.{info['ext']}"
            
            # 确保文件存在
            if not file_path.exists():
                actual_files = list(DOWNLOAD_DIR.glob(f"{safe_title}*.{info['ext']}"))
                if actual_files:
                    file_path = actual_files[0]
            
            download_status[url] = {
                "status": "completed",
                "progress": 100,
                "info": {
                    "title": info["title"],
                    "file_size": humanize.naturalsize(os.path.getsize(file_path)),
                    "file_path": str(file_path),
                    "relative_path": f"/downloads/{file_path.name}"
                }
            }
    except Exception as e:
        download_status[url] = {"status": "error", "error": str(e)}

@app.get("/")
async def home(request: Request):
    videos = []
    for file in DOWNLOAD_DIR.glob("*"):
        if file.is_file() and file.suffix.lower() not in IMAGE_EXTENSIONS:
            videos.append(get_video_info(file))
    videos.sort(key=lambda x: x["modified"], reverse=True)
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "videos": videos
    })

@app.post("/download")
async def start_download(url: dict):
    video_url = url['url']
    if video_url in download_status:
        return {"status": "already_downloading"}
    download_status[video_url] = {'status': 'downloading', 'progress': 0}
    asyncio.create_task(download_video(video_url))
    return {"status": "started"}

@app.get("/status/{url:path}")
async def get_status(url: str):
    return JSONResponse(download_status.get(url, {'status': 'not_found'}))

@app.get("/download_file/{filename}")
async def download_file(filename: str):
    file_path = DOWNLOAD_DIR / filename
    if not file_path.exists():
        return JSONResponse({"error": "File not found"}, status_code=404)
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type='application/octet-stream'
    ) 
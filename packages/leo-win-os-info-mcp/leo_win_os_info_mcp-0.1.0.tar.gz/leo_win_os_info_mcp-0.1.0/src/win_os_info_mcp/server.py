# src/win_os_info_mcp/server.py

import platform
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

# 创建一个 FastAPI 应用实例
app = FastAPI(
    title="Windows OS Info MCP",
    description="一个提供 Windows 操作系统基本信息的 MCP 服务。",
    version="0.1.0",
)

# 定义返回数据模型，让 API 文档更清晰
class OsInfo(BaseModel):
    system: str
    release: str
    version: str
    machine: str
    processor: str
    node_name: str

@app.get("/os-info", response_model=OsInfo)
def get_os_information():
    """
    获取并返回当前操作系统的详细信息。
    """
    return OsInfo(
        system=platform.system(),       # => 'Windows'
        release=platform.release(),     # => '10'
        version=platform.version(),     # => '10.0.19045'
        machine=platform.machine(),     # => 'AMD64'
        processor=platform.processor(),
        node_name=platform.node(),      # => 您的计算机名
    )

def main():
    """
    这是 uvx 的入口函数，用于启动服务。
    """
    print("🚀 启动 Windows OS Info MCP 服务...")
    print("🌐 服务运行在 http://127.0.0.1:8008")
    print("💡 在浏览器中访问 http://127.0.0.1:8008/docs 查看 API 文档。")
    uvicorn.run(app, host="127.0.0.1", port=8008, log_level="warning")

# 这允许我们也能直接通过 python server.py 运行此文件进行测试
if __name__ == "__main__":
    main()
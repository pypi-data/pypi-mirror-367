# src/win_os_info_mcp/server.py

import platform
import uvicorn
from pydantic import BaseModel
from fastmcp import FastMCP # 导入 FastMCP
from fastapi import FastAPI # 导入 FastAPI

# 创建一个 FastMCP 应用实例
# 注意：FastMCP 的构造函数不接受 title, description, version 参数
mcp_app = FastMCP()

# 定义返回数据模型，让 API 文档更清晰
class OsInfo(BaseModel):
    system: str
    release: str
    version: str
    machine: str
    processor: str
    node_name: str

# 使用 mcp_app.tool 装饰器来定义一个 MCP 工具
@mcp_app.tool()
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

# 创建一个 FastAPI 应用实例，它将作为服务的核心
app = FastAPI(
    title="Windows OS Info MCP Service",
    description="一个通过MCP协议提供Windows操作系统信息的服务",
    version="0.1.0",
)

# 将 FastMCP 应用挂载到 FastAPI 应用上，使其成为一个子应用
# 使用 mcp_app.as_asgi() 将 FastMCP 转换为一个可调用的 ASGI 应用
app.mount("/mcp", mcp_app.as_asgi())

def main():
    """
    这是 uvx 的入口函数，用于启动服务。
    """
    print("🚀 启动 Windows OS Info MCP 服务...")
    # 打印 MCP 服务的完整文档URL
    print("🌐 服务运行在 http://127.0.0.1:8008/mcp/tools")
    print("💡 在浏览器中访问 http://127.0.0.1:8008/docs 查看 API 文档。")
    uvicorn.run(app, host="127.0.0.1", port=8008, log_level="warning")

# 这允许我们也能直接通过 python server.py 运行此文件进行测试
if __name__ == "__main__":
    main()

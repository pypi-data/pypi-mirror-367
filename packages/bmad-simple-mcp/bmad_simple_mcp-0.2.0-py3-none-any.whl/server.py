#!/usr/bin/env python3
"""
BMad Simple MCP - 轻量级MCP文档服务器
功能：
- 通过resource template暴露document文件夹3层内的md、txt文件
- listresource返回index.md内容和资源清单
- readdocument读取具体文件内容

Usage:
    python server.py --transport stdio
    python server.py --transport sse --port 8080
"""
from __future__ import annotations

import argparse
import os
import mcp.types as types
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
from typing import List, Optional

from fastapi import FastAPI, Request
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.responses import Response
from mcp.server.sse import SseServerTransport
import uvicorn
import shutil
from pathlib import Path

# ---------- 文档目录初始化 ----------
def initialize_document_directory():
    """
    初始化document目录
    如果当前目录没有document文件夹，则从打包文件中复制
    """
    current_dir = Path.cwd()
    document_dir = current_dir / "document"
    
    # 如果document目录已存在，直接返回
    if document_dir.exists() and document_dir.is_dir():
        print(f"[OK] Document目录已存在: {document_dir}")
        return
    
    print(f"[INFO] Document目录不存在，开始初始化...")
    
    try:
        # 尝试从打包文件中获取document目录
        package_dir = Path(__file__).parent
        source_document_dir = package_dir / "document"
        
        if source_document_dir.exists():
            # 从同级目录复制
            print(f"[COPY] 从源码目录复制: {source_document_dir} -> {document_dir}")
            shutil.copytree(source_document_dir, document_dir)
        else:
            # 尝试从包资源中获取
            try:
                import importlib.resources as resources
                # 这里需要根据实际的包结构调整
                print("[INIT] 尝试从包资源中初始化document目录...")
                
                # 创建document目录
                document_dir.mkdir(exist_ok=True)
                
                # 创建默认的index.md
                default_index = """# BMad Agent 文档索引

这是BMad项目的agent文档索引页面。

## 可用文档

本目录包含BMad项目的各种agent配置和使用文档。

## 使用说明

通过MCP服务器可以访问document文件夹下3层深度内的所有.md和.txt文件。

## 初始化说明

此document目录是在运行时自动创建的。你可以在此目录中添加自己的文档文件。
"""
                
                index_file = document_dir / "index.md"
                index_file.write_text(default_index, encoding='utf-8')
                
                print("[OK] 已创建默认index.md文件")
                
            except ImportError:
                # 如果无法导入resources，创建基本目录结构
                print("[WARN] 无法从包资源初始化，创建基本目录结构...")
                document_dir.mkdir(exist_ok=True)
                
                # 创建基本的index.md
                basic_index = """# 文档索引

欢迎使用BMad Simple MCP！

## 使用说明

请在此目录中添加你的.md和.txt文档文件。

服务器会自动扫描并提供这些文件的访问。
"""
                index_file = document_dir / "index.md"
                index_file.write_text(basic_index, encoding='utf-8')
        
        print(f"[SUCCESS] Document目录初始化完成: {document_dir}")
        
        # 列出初始化后的文件
        if document_dir.exists():
            files = list(document_dir.rglob("*"))
            file_count = len([f for f in files if f.is_file()])
            print(f"[FILES] 初始化的文件数量: {file_count}")
            for file in files:
                if file.is_file():
                    print(f"   - {file.relative_to(document_dir)}")
    
    except Exception as e:
        print(f"[ERROR] 初始化document目录失败: {e}")
        print("[INFO] 请手动创建document目录并添加文档文件")

# 在服务器启动时初始化document目录
initialize_document_directory()

# ---------- SSE 实现 ----------
def make_sse_app(mcp_server):
    """创建支持SSE的FastAPI应用"""
    
    # 创建SSE传输层
    sse_transport = SseServerTransport("/messages/")
    
    async def handle_sse(request: Request):
        """处理SSE连接"""
        async with sse_transport.connect_sse(
            request.scope, request.receive, request._send
        ) as streams:
            await mcp_server.run(
                streams[0], 
                streams[1], 
                InitializationOptions(
                    server_name="document-server",
                    server_version="0.2.0",
                    capabilities=mcp_server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                )
            )
        # 返回空响应避免NoneType错误
        return Response()
    
    # 创建Starlette路由
    routes = [
        Route("/sse", endpoint=handle_sse, methods=["GET"]),
        Mount("/messages/", app=sse_transport.handle_post_message),
    ]
    
    # 创建Starlette应用
    starlette_app = Starlette(routes=routes)
    return starlette_app

# -------------------------------------------------
# DocumentStore 文档存储管理类
# -------------------------------------------------
class DocumentStore:
    ROOT: str = "document"
    INDEX: str = os.path.join(ROOT, "index.md")
    MAX_DEPTH: int = 3

    @staticmethod
    def _abs(path: str) -> str:
        """获取绝对路径"""
        return os.path.abspath(path)

    @classmethod
    def _get_relative_path(cls, abs_path: str) -> str:
        """获取相对于document目录的路径"""
        return os.path.relpath(abs_path, cls._abs(cls.ROOT)).replace(os.sep, "/")

    @classmethod
    def iter_files(cls) -> List[str]:
        """扫描document目录下3层深度内的所有.md和.txt文件"""
        root_abs = cls._abs(cls.ROOT)
        if not os.path.exists(root_abs):
            return []
        
        files: List[str] = []
        for dirpath, _, filenames in os.walk(root_abs):
            # 计算当前目录相对于根目录的深度
            depth = dirpath[len(root_abs):].count(os.sep)
            if depth > cls.MAX_DEPTH:
                continue
            
            for filename in filenames:
                if filename.lower().endswith((".md", ".txt")):
                    abs_path = os.path.join(dirpath, filename)
                    files.append(abs_path)
        
        return sorted(files)

    @classmethod
    def read_file(cls, file_path: str) -> str:
        """读取文件内容，支持相对路径和绝对路径"""
        # 如果是相对路径，转换为绝对路径
        if not os.path.isabs(file_path):
            abs_path = cls._abs(os.path.join(cls.ROOT, file_path))
        else:
            abs_path = file_path
        
        # 安全检查：确保文件在document目录内
        if not abs_path.startswith(cls._abs(cls.ROOT)):
            raise ValueError(f"访问被拒绝：文件不在document目录内 - {file_path}")
        
        if not os.path.isfile(abs_path):
            raise FileNotFoundError(f"文件不存在：{file_path}")
        
        try:
            with open(abs_path, "r", encoding="utf-8") as fp:
                return fp.read()
        except UnicodeDecodeError:
            # 如果UTF-8解码失败，尝试其他编码
            with open(abs_path, "r", encoding="gbk") as fp:
                return fp.read()

    @classmethod
    def get_index_content(cls) -> Optional[str]:
        """获取index.md文件内容"""
        try:
            return cls.read_file("index.md")  # 使用相对路径
        except (FileNotFoundError, ValueError):
            return None


# -------------------------------------------------
# MCP Server 实现
# -------------------------------------------------
server = Server("document-server")


@server.list_resources()
async def list_resources() -> List[types.Resource]:
    """
    列出所有可用资源：
    1. 返回index.md的完整内容
    2. 返回其他文档文件的清单信息
    3. 通过notification发送index.md内容到客户端
    """
    resources: List[types.Resource] = []

    # 获取所有文档文件
    all_files = DocumentStore.iter_files()
    
    # 1. 优先处理index.md - 直接返回内容
    index_content = DocumentStore.get_index_content()
    if index_content is not None:
        index_resource = types.Resource(
            uri=f"document://index.md",
            name="index.md",
            description="文档索引页面 - 包含完整内容",
            mimeType="text/markdown",
            text=index_content,
        )
        resources.append(index_resource)
        
        # 通过notification发送index.md内容到客户端
        try:
            session = server.request_context.session
            await session.send_resource_updated(uri="document://index.md")
            
            # 发送日志消息通知，data字段包含index.md的完整内容
            await session.send_log_message(
                level="info",
                data=index_content,  # 直接发送index.md的完整内容
                logger="document-server"
            )
        except LookupError:
            # 如果不在请求上下文中（比如测试时），忽略notification
            pass
        except Exception as e:
            # 记录错误但不影响资源列表返回
            print(f"Warning: Failed to send notification: {e}")

    # 2. 处理其他文档文件 - 仅返回清单信息
    for abs_path in all_files:
        rel_path = DocumentStore._get_relative_path(abs_path)
        
        # 跳过index.md，已在上面处理
        if rel_path == "index.md":
            continue
        
        # 确定MIME类型
        mime_type = "text/markdown" if rel_path.endswith(".md") else "text/plain"
        
        resources.append(
            types.Resource(
                uri=f"document://{rel_path}",
                name=rel_path,
                description=f"文档文件：{rel_path}",
                mimeType=mime_type,
            )
        )
    
    return resources


@server.read_resource()
async def read_resource(uri) -> str:
    """
    读取具体文档内容
    支持格式：document://filename.md 或 document://subfolder/filename.txt
    """
    # 将URI转换为字符串（处理AnyUrl对象）
    uri_str = str(uri)
    
    if not uri_str.startswith("document://"):
        raise ValueError("仅支持 document:// URI格式")
    
    # 提取文件路径
    file_path = uri_str[11:]  # 去掉 "document://" 前缀
    
    try:
        content = DocumentStore.read_file(file_path)
        return content
    except FileNotFoundError as e:
        raise ValueError(f"文档不存在：{file_path}")
    except Exception as e:
        raise ValueError(f"读取文档失败：{str(e)}")


# 添加工具函数支持
@server.list_tools()
async def list_tools() -> List[types.Tool]:
    """列出可用的工具"""
    return [
        types.Tool(
            name="read_document",
            description="读取指定文档的内容",
            inputSchema={
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "要读取的文档文件名（相对于document目录）"
                    }
                },
                "required": ["filename"]
            }
        ),
        types.Tool(
            name="list_documents",
            description="列出所有可用的文档文件",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> List[types.TextContent]:
    """处理工具调用"""
    if name == "read_document":
        filename = arguments.get("filename")
        if not filename:
            return [types.TextContent(type="text", text="错误：未提供文件名")]
        
        try:
            content = DocumentStore.read_file(filename)
            return [types.TextContent(
                type="text", 
                text=f"文档内容 ({filename}):\n\n{content}"
            )]
        except Exception as e:
            return [types.TextContent(type="text", text=f"读取失败：{str(e)}")]
    
    elif name == "list_documents":
        files = DocumentStore.iter_files()
        if not files:
            return [types.TextContent(type="text", text="document目录下没有找到.md或.txt文件")]
        
        file_list = []
        for abs_path in files:
            rel_path = DocumentStore._get_relative_path(abs_path)
            file_size = os.path.getsize(abs_path)
            file_list.append(f"- {rel_path} ({file_size} bytes)")
        
        result = f"找到 {len(files)} 个文档文件：\n\n" + "\n".join(file_list)
        return [types.TextContent(type="text", text=result)]
    
    else:
        return [types.TextContent(type="text", text=f"未知工具：{name}")]


# -------------------------------------------------
# 运行入口
# -------------------------------------------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--transport", choices=["stdio", "sse"], default="stdio", help="传输方式"
    )
    parser.add_argument("--host", default="0.0.0.0", help="SSE host")
    parser.add_argument("--port", type=int, default=8000, help="SSE port")
    args = parser.parse_args()

    if args.transport == "stdio":
        # stdio 模式
        import asyncio

        async def run_stdio():
            async with mcp.server.stdio.stdio_server() as (read, write):
                await server.run(
                    read,
                    write,
                    InitializationOptions(
                        server_name="document-server",
                        server_version="0.2.0",
                        capabilities=server.get_capabilities(
                            notification_options=NotificationOptions(),
                            experimental_capabilities={},
                        ),
                    ),
                )

        asyncio.run(run_stdio())

    else:
        # SSE 模式
        app = make_sse_app(server)
        uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
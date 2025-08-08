"""
Undoom Sketch MCP - 图片素描化转换服务器

一个基于 MCP (Model Context Protocol) 的图片素描化服务器，
可以将普通图片转换为素描效果，支持多种风格和批量处理。
"""

__version__ = "0.1.3"
__author__ = "Undoom"
__email__ = "kaikaihuhu666@163.com"

from .server import main

__all__ = ["main"]
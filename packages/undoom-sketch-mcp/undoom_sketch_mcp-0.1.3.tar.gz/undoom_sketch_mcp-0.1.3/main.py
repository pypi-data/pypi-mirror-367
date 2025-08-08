# -*- coding: utf-8 -*-

"""
图片素描化 MCP 服务器。

提供图片素描化功能的 MCP 服务器，可以将输入的图片转换为素描效果。
支持多种素描风格和批量处理功能。
"""

# 导入必要的库
import cv2
import numpy as np
import os
import base64
import glob
from pathlib import Path
from mcp.server.fastmcp import FastMCP

# 创建一个 MCP 服务器实例，并将其命名为 "SketchConverter"。
# 这个名字会向连接到此服务器的 AI 客户端展示。
mcp = FastMCP("SketchConverter")

# 支持的图片格式
SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp'}

def dodgeV2(image, mask, contrast=256.0):
    """图像混合函数，用于生成素描效果"""
    return cv2.divide(image, 255 - mask, scale=contrast)

def validate_image_path(image_path: str) -> tuple[bool, str]:
    """验证图片路径和格式"""
    if not os.path.exists(image_path):
        return False, f"错误: 文件不存在 - {image_path}"
    
    file_ext = Path(image_path).suffix.lower()
    if file_ext not in SUPPORTED_FORMATS:
        return False, f"错误: 不支持的图片格式 - {file_ext}。支持的格式: {', '.join(SUPPORTED_FORMATS)}"
    
    return True, "验证通过"

def load_image_safely(image_path: str):
    """安全加载图片，支持中文路径"""
    try:
        # 使用numpy读取图片，支持中文路径
        img_array = np.fromfile(image_path, dtype=np.uint8)
        image = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        return image
    except Exception as e:
        return None

def save_image_safely(image, output_path: str) -> bool:
    """安全保存图片，支持中文路径"""
    try:
        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # 获取文件扩展名
        ext = os.path.splitext(output_path)[1].lower()
        
        # 编码图片
        success, encoded_img = cv2.imencode(ext, image)
        if success:
            # 写入文件
            with open(output_path, 'wb') as f:
                f.write(encoded_img.tobytes())
            return True
        return False
    except Exception as e:
        return False

@mcp.tool()
def convert_image_to_sketch(image_path: str, blur_size: int = 21, contrast: float = 256.0, style: str = "classic") -> str:
    """
    将输入的图片转换为素描效果。
    
    参数:
    - image_path: 图片文件的路径
    - blur_size: 高斯模糊的核大小，必须为奇数，默认为21
    - contrast: 对比度参数，默认为256.0
    - style: 素描风格 ("classic", "detailed", "soft")
    
    返回:
    - 成功时返回保存的素描图片路径，失败时返回错误信息
    """
    try:
        # 验证图片路径
        is_valid, message = validate_image_path(image_path)
        if not is_valid:
            return message
        
        # 确保blur_size是奇数且在合理范围内
        blur_size = max(3, min(101, blur_size))  # 限制在3-101之间
        if blur_size % 2 == 0:
            blur_size += 1
        
        # 限制对比度参数
        contrast = max(50.0, min(500.0, contrast))  # 限制在50-500之间
        
        # 加载图片
        src_image = load_image_safely(image_path)
        if src_image is None:
            return f"错误: 无法加载图片 - {image_path}"
        
        # 转换为灰度图
        img_gray = cv2.cvtColor(src_image, cv2.COLOR_BGR2GRAY)
        
        # 根据风格调整处理参数
        if style == "detailed":
            # 详细风格：更小的模糊核，更高的对比度
            blur_size = max(3, blur_size // 2)
            if blur_size % 2 == 0:
                blur_size += 1
            contrast *= 1.2
        elif style == "soft":
            # 柔和风格：更大的模糊核，更低的对比度
            blur_size = min(51, blur_size * 2)
            if blur_size % 2 == 0:
                blur_size += 1
            contrast *= 0.8
        
        # 反转灰度图
        img_gray_inv = 255 - img_gray
        
        # 应用高斯模糊
        img_blur = cv2.GaussianBlur(img_gray_inv, ksize=(blur_size, blur_size), sigmaX=0, sigmaY=0)
        
        # 使用dodgeV2函数进行混合
        sketch_image = dodgeV2(img_gray, img_blur, contrast)
        
        # 后处理：增强对比度和锐化
        if style == "detailed":
            # 对详细风格进行锐化处理
            kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
            sketch_image = cv2.filter2D(sketch_image, -1, kernel)
            sketch_image = np.clip(sketch_image, 0, 255).astype(np.uint8)
        
        # 生成输出文件名
        original_filename = os.path.basename(image_path)
        filename_without_ext = os.path.splitext(original_filename)[0]
        output_dir = os.path.dirname(image_path)
        output_path = os.path.join(output_dir, f"Sketch_{style}_{filename_without_ext}.jpg")
        
        # 保存素描图片
        if save_image_safely(sketch_image, output_path):
            return f"素描转换成功! 风格: {style}, 输出文件: {output_path}"
        else:
            return f"错误: 保存图片失败 - {output_path}"
        
    except Exception as e:
        return f"错误: 转换过程中出现异常 - {str(e)}"

@mcp.tool()
def batch_convert_images(folder_path: str, blur_size: int = 21, contrast: float = 256.0, style: str = "classic") -> str:
    """
    批量转换文件夹中的所有图片为素描效果。
    
    参数:
    - folder_path: 包含图片的文件夹路径
    - blur_size: 高斯模糊的核大小，默认为21
    - contrast: 对比度参数，默认为256.0
    - style: 素描风格 ("classic", "detailed", "soft")
    
    返回:
    - 处理结果统计信息
    """
    try:
        if not os.path.exists(folder_path):
            return f"错误: 文件夹不存在 - {folder_path}"
        
        if not os.path.isdir(folder_path):
            return f"错误: 路径不是文件夹 - {folder_path}"
        
        # 查找所有支持的图片文件
        image_files = []
        for ext in SUPPORTED_FORMATS:
            pattern = os.path.join(folder_path, f"*{ext}")
            image_files.extend(glob.glob(pattern))
            pattern = os.path.join(folder_path, f"*{ext.upper()}")
            image_files.extend(glob.glob(pattern))
        
        if not image_files:
            return f"在文件夹中未找到支持的图片文件: {folder_path}"
        
        success_count = 0
        error_count = 0
        error_messages = []
        
        for image_file in image_files:
            result = convert_image_to_sketch(image_file, blur_size, contrast, style)
            if result.startswith("素描转换成功"):
                success_count += 1
            else:
                error_count += 1
                error_messages.append(f"{os.path.basename(image_file)}: {result}")
        
        result_summary = f"批量处理完成!\n"
        result_summary += f"成功转换: {success_count} 张图片\n"
        result_summary += f"失败: {error_count} 张图片\n"
        
        if error_messages:
            result_summary += f"\n错误详情:\n" + "\n".join(error_messages[:5])  # 只显示前5个错误
            if len(error_messages) > 5:
                result_summary += f"\n... 还有 {len(error_messages) - 5} 个错误"
        
        return result_summary
        
    except Exception as e:
        return f"错误: 批量处理过程中出现异常 - {str(e)}"

@mcp.tool()
def get_image_info(image_path: str) -> str:
    """
    获取图片的基本信息。
    
    参数:
    - image_path: 图片文件的路径
    
    返回:
    - 图片信息字符串
    """
    try:
        # 验证图片路径
        is_valid, message = validate_image_path(image_path)
        if not is_valid:
            return message
        
        # 加载图片
        image = load_image_safely(image_path)
        if image is None:
            return f"错误: 无法加载图片 - {image_path}"
        
        # 获取图片信息
        height, width = image.shape[:2]
        channels = image.shape[2] if len(image.shape) == 3 else 1
        file_size = os.path.getsize(image_path)
        file_size_mb = file_size / (1024 * 1024)
        
        info = f"图片信息:\n"
        info += f"文件名: {os.path.basename(image_path)}\n"
        info += f"尺寸: {width} x {height} 像素\n"
        info += f"通道数: {channels}\n"
        info += f"文件大小: {file_size_mb:.2f} MB\n"
        info += f"格式: {Path(image_path).suffix.upper()}\n"
        
        # 建议的处理参数
        if width * height > 2000000:  # 大于200万像素
            info += f"\n建议参数 (大图片):\n"
            info += f"- blur_size: 31-51\n"
            info += f"- contrast: 200-300\n"
        elif width * height > 500000:  # 大于50万像素
            info += f"\n建议参数 (中等图片):\n"
            info += f"- blur_size: 21-31\n"
            info += f"- contrast: 256\n"
        else:
            info += f"\n建议参数 (小图片):\n"
            info += f"- blur_size: 11-21\n"
            info += f"- contrast: 300-400\n"
        
        return info
        
    except Exception as e:
        return f"错误: 获取图片信息时出现异常 - {str(e)}"

# 使用 @mcp.resource() 装饰器来定义一个"资源"。
# 资源代表 AI 可以访问的数据或信息。这里提供素描转换的帮助信息。
@mcp.resource("sketch://help")
def get_sketch_help() -> str:
    """
    获取图片素描转换功能的帮助信息。
    """
    help_text = """
🎨 图片素描转换工具使用说明

📋 功能列表：
1. convert_image_to_sketch - 单张图片素描转换
2. batch_convert_images - 批量图片素描转换
3. get_image_info - 获取图片信息和建议参数

🖼️ 支持的图片格式：
JPG, JPEG, PNG, BMP, GIF, TIFF, WEBP

🎭 素描风格：
- classic: 经典素描风格 (默认)
- detailed: 详细素描风格 (更清晰的线条)
- soft: 柔和素描风格 (更柔和的效果)

⚙️ 参数说明：
- image_path: 图片文件的完整路径 (必需)
- blur_size: 高斯模糊核大小 (3-101，奇数，默认21)
- contrast: 对比度参数 (50-500，默认256.0)
- style: 素描风格 (classic/detailed/soft，默认classic)

📝 使用示例：
1. 单张转换：
   convert_image_to_sketch("/path/to/image.jpg", 21, 256.0, "classic")

2. 批量转换：
   batch_convert_images("/path/to/folder", 21, 256.0, "detailed")

3. 获取图片信息：
   get_image_info("/path/to/image.jpg")

💡 使用技巧：
- 大图片建议使用较大的blur_size (31-51)
- 小图片建议使用较小的blur_size (11-21)
- detailed风格适合人像和细节丰富的图片
- soft风格适合风景和需要柔和效果的图片
- 可以先用get_image_info查看图片信息和建议参数

📁 输出文件：
- 单张转换：原目录下，文件名格式为 "Sketch_{style}_{原文件名}.jpg"
- 批量转换：每张图片都在原目录下生成对应的素描版本

⚠️ 注意事项：
- 确保图片文件存在且可读
- 支持中文路径和文件名
- 处理大图片时可能需要较长时间
- 建议在处理前备份原图片
    """
    return help_text

if __name__ == "__main__":
    mcp.run(transport="sse")
#!/usr/bin/env python3
"""
PyMuPDF 元数据提取演示

这个示例展示了如何使用 PyMuPDF 提取 PDF 文件的元数据。
"""

import os
import sys
from typing import Dict, Union, List

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from ebook_mcp.tools.pdf_helper import get_meta
    DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    print(f"导入错误: {e}")
    DEPENDENCIES_AVAILABLE = False

def print_metadata_analysis(pdf_path: str):
    """
    分析 PDF 文件的元数据
    
    Args:
        pdf_path: PDF 文件路径
    """
    if not DEPENDENCIES_AVAILABLE:
        print("❌ 依赖库不可用，无法运行演示")
        return
    
    if not os.path.exists(pdf_path):
        print(f"❌ 文件不存在: {pdf_path}")
        return
    
    print(f"📄 分析 PDF 文件: {pdf_path}")
    print("=" * 60)
    
    try:
        # 使用 PyMuPDF 提取元数据
        print("🔍 使用 PyMuPDF 提取元数据:")
        meta = get_meta(pdf_path)
        
        print("提取的元数据字段:")
        for key, value in meta.items():
            print(f"  {key}: {value}")
        
        print("\n" + "=" * 60)
        
        # 分析元数据
        print("📊 元数据分析:")
        print(f"总字段数: {len(meta)}")
        
        # 基本信息
        if 'title' in meta:
            print(f"📖 标题: {meta['title']}")
        if 'author' in meta:
            print(f"👤 作者: {meta['author']}")
        if 'pages' in meta:
            print(f"📄 页数: {meta['pages']}")
        if 'file_size' in meta:
            size_mb = meta['file_size'] / (1024 * 1024)
            print(f"📁 文件大小: {size_mb:.2f} MB")
        
        # 技术信息
        if 'pdf_version' in meta:
            print(f"🔧 PDF 版本: {meta['pdf_version']}")
        if 'is_encrypted' in meta:
            print(f"🔐 加密状态: {'是' if meta['is_encrypted'] else '否'}")
        if 'page_width' in meta and 'page_height' in meta:
            print(f"📏 页面尺寸: {meta['page_width']:.1f} x {meta['page_height']:.1f}")
        
        # 创建信息
        if 'creator' in meta:
            print(f"🛠️ 创建工具: {meta['creator']}")
        if 'producer' in meta:
            print(f"🏭 生产工具: {meta['producer']}")
        if 'creation_date' in meta:
            print(f"📅 创建日期: {meta['creation_date']}")
        if 'modification_date' in meta:
            print(f"📅 修改日期: {meta['modification_date']}")
        
        # 其他信息
        if 'keywords' in meta:
            print(f"🏷️ 关键词: {meta['keywords']}")
        if 'format' in meta:
            print(f"📝 格式: {meta['format']}")
        
    except Exception as e:
        print(f"❌ 提取元数据时出错: {e}")

def demonstrate_pymupdf_advantages():
    """
    演示 PyMuPDF 的优势
    """
    print("\n🚀 PyMuPDF 的优势:")
    print("1. 📏 页面尺寸信息: 可以获取页面的宽度和高度")
    print("2. 🔐 加密状态: 可以检测 PDF 是否加密")
    print("3. 📊 PDF 版本: 获取 PDF 文件版本信息")
    print("4. 📁 文件大小: 获取文件大小信息")
    print("5. 🏷️ 关键词: 提取 PDF 关键词信息")
    print("6. 📝 格式信息: 获取文档格式信息")
    print("7. ⚡ 性能: 更快的处理速度")
    print("8. 🛠️ 功能丰富: 支持更多 PDF 操作")
    print("9. 🎯 专注性: 专门为 PDF 处理优化")
    print("10. 🔧 现代化: 使用最新的 PDF 处理技术")

def main():
    """主函数"""
    print("🎯 PyMuPDF PDF 元数据提取演示")
    print("=" * 60)
    
    # 演示 PyMuPDF 的优势
    demonstrate_pymupdf_advantages()
    
    # 如果有命令行参数，使用指定的 PDF 文件
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        print_metadata_analysis(pdf_path)
    else:
        print("\n💡 使用方法:")
        print("python pymupdf_metadata_demo.py <PDF文件路径>")
        print("\n例如:")
        print("python pymupdf_metadata_demo.py /path/to/your/document.pdf")
        
        # 尝试在常见位置查找 PDF 文件
        common_paths = [
            os.path.expanduser("~/Downloads"),
            os.path.expanduser("~/Documents"),
            "."
        ]
        
        pdf_files = []
        for path in common_paths:
            if os.path.exists(path):
                for file in os.listdir(path):
                    if file.lower().endswith('.pdf'):
                        pdf_files.append(os.path.join(path, file))
        
        if pdf_files:
            print(f"\n📁 在常见位置找到 {len(pdf_files)} 个 PDF 文件:")
            for i, pdf_file in enumerate(pdf_files[:5], 1):  # 只显示前5个
                print(f"  {i}. {pdf_file}")
            
            if len(pdf_files) > 5:
                print(f"  ... 还有 {len(pdf_files) - 5} 个文件")
            
            print(f"\n💡 可以运行: python pymupdf_metadata_demo.py '{pdf_files[0]}'")
        else:
            print("\n❌ 未找到 PDF 文件")

if __name__ == "__main__":
    main()

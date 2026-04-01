#!/usr/bin/env python3
"""
打开逐字稿手动下载工具
"""

import webbrowser
import os

# 工具文件路径
TOOL_PATH = "/Users/cyberrwiz/Desktop/黄有璨系列课程/高阶活动运营/逐字稿/手动下载工具.html"

# 检查文件是否存在
if os.path.exists(TOOL_PATH):
    # 使用默认浏览器打开
    webbrowser.open('file://' + TOOL_PATH)
    print("已打开逐字稿下载工具！")
    print("\n使用说明：")
    print("1. 在工具页面点击课时的\"打开课时\"按钮")
    print("2. 在三节课页面点击\"文稿\"标签")
    print("3. 复制文稿内容")
    print("4. 回到工具页面点击\"粘贴保存\"")
    print("5. 文稿将自动保存为Markdown文件")
else:
    print(f"错误：找不到工具文件 {TOOL_PATH}")

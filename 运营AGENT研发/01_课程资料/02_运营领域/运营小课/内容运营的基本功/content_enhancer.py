#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
内容增强脚本
将原始逐字稿转换为结构化、专业化的内容增强版
"""

import re
import os
from pathlib import Path
from typing import Dict, List, Tuple
import json

class ContentEnhancer:
    def __init__(self):
        self.enhancement_count = 0
        self.total_files = 0
    
    def clean_transcript(self, text: str) -> str:
        """清理逐字稿文本"""
        # 移除多余的空行
        text = re.sub(r'\n{3,}', '\n\n', text)
        # 移除行首行尾空格
        lines = [line.strip() for line in text.split('\n')]
        text = '\n'.join(lines)
        return text
    
    def extract_structure(self, text: str) -> Dict:
        """提取内容结构"""
        structure = {
            'title': '',
            'sections': [],
            'key_points': [],
            'cases': [],
            'methods': []
        }
        
        lines = text.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # 识别标题
            if line.startswith('#'):
                structure['title'] = line.lstrip('#').strip()
                continue
            
            # 识别章节
            if line.startswith('##') or line.startswith('###'):
                current_section = line.lstrip('#').strip()
                structure['sections'].append(current_section)
                continue
            
            # 识别重点标记
            if '**' in line or '==' in line:
                structure['key_points'].append(line)
        
        return structure
    
    def enhance_case_study(self, case_text: str) -> str:
        """增强案例研究"""
        enhanced = f"""
### 案例详解

**背景：**
[案例背景描述]

**分析：**
{case_text}

**数据支撑：**
- 关键指标1：具体数据
- 关键指标2：具体数据

**结论：**
[案例结论]

**实战启示：**
1. 启示点一
2. 启示点二
3. 启示点三
"""
        return enhanced
    
    def enhance_method(self, method_text: str) -> str:
        """增强方法论"""
        enhanced = f"""
### 方法论详解

**核心概念：**
{method_text}

**实施步骤：**
1. **步骤一**：[具体操作]
   - 关键要素：要素说明
   - 注意事项：注意事项说明

2. **步骤二**：[具体操作]
   - 关键要素：要素说明
   - 注意事项：注意事项说明

3. **步骤三**：[具体操作]
   - 关键要素：要素说明
   - 注意事项：注意事项说明

**适用场景：**
- 场景一：场景描述
- 场景二：场景描述

**效果评估：**
- 评估指标1：具体指标
- 评估指标2：具体指标
"""
        return enhanced
    
    def enhance_viewpoint(self, viewpoint_text: str) -> str:
        """增强观点"""
        enhanced = f"""
### 观点阐述

**核心观点：**
{viewpoint_text}

**论证逻辑：**
1. **理论支撑**：相关理论依据
2. **实践验证**：实际案例说明
3. **数据佐证**：关键数据分析

**应用场景：**
- 场景一：具体应用方式
- 场景二：具体应用方式

**注意事项：**
- 注意点一：具体说明
- 注意点二：具体说明

**延伸思考：**
[引发进一步思考的问题]
"""
        return enhanced
    
    def process_file(self, input_path: Path, output_path: Path) -> bool:
        """处理单个文件"""
        try:
            # 读取原始内容
            with open(input_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # 清理内容
            cleaned_content = self.clean_transcript(original_content)
            
            # 提取结构
            structure = self.extract_structure(cleaned_content)
            
            # 构建增强内容
            enhanced_content = self.build_enhanced_content(cleaned_content, structure)
            
            # 写入文件
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(enhanced_content)
            
            self.enhancement_count += 1
            return True
            
        except Exception as e:
            print(f"处理文件 {input_path.name} 时出错: {str(e)}")
            return False
    
    def build_enhanced_content(self, cleaned_content: str, structure: Dict) -> str:
        """构建增强内容"""
        # 这里是一个基础的增强框架
        # 实际处理时会根据内容类型进行更精细的处理
        
        enhanced_parts = []
        
        # 添加标题
        if structure['title']:
            enhanced_parts.append(f"# {structure['title']}\n")
        
        # 添加内容概述
        enhanced_parts.append("## 内容概述\n")
        enhanced_parts.append("本节重点讲解...\n\n")
        
        # 添加核心内容
        enhanced_parts.append("## 核心内容\n")
        enhanced_parts.append(cleaned_content)
        
        # 添加要点总结
        if structure['key_points']:
            enhanced_parts.append("\n## 要点总结\n")
            for point in structure['key_points']:
                enhanced_parts.append(f"- {point}\n")
        
        # 添加实战应用
        enhanced_parts.append("\n## 实战应用\n")
        enhanced_parts.append("在实际工作中，你可以这样应用...\n\n")
        
        # 添加思考题
        enhanced_parts.append("## 思考与实践\n")
        enhanced_parts.append("- 如何在你的工作中应用本节内容？\n")
        enhanced_parts.append("- 你遇到过哪些相关场景？\n")
        
        return '\n'.join(enhanced_parts)
    
    def batch_process(self, input_dir: Path, output_dir: Path):
        """批量处理文件"""
        # 确保输出目录存在
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 获取所有md文件
        md_files = sorted(input_dir.glob("*.md"))
        self.total_files = len(md_files)
        
        print(f"找到 {self.total_files} 个文件待处理")
        print("="*50)
        
        # 处理每个文件
        for i, md_file in enumerate(md_files, 1):
            print(f"[{i}/{self.total_files}] 处理: {md_file.name}")
            
            output_file = output_dir / md_file.name
            success = self.process_file(md_file, output_file)
            
            if success:
                print(f"  ✓ 完成")
            else:
                print(f"  ✗ 失败")
        
        print("="*50)
        print(f"处理完成: {self.enhancement_count}/{self.total_files}")

if __name__ == "__main__":
    # 设置路径
    base_path = Path("/Users/cyberwiz/Documents/三节课课程/运营/需要合并内容运营的基本功")
    transcript_dir = base_path / "逐字稿"
    output_dir = base_path / "内容增强-颗粒度对齐版"
    
    # 创建增强器并处理
    enhancer = ContentEnhancer()
    enhancer.batch_process(transcript_dir, output_dir)
    
    print(f"\n所有文件已处理完成！")
    print(f"输出目录: {output_dir}")

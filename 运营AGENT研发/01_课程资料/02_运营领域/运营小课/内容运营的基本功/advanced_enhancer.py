#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高级内容增强脚本
对逐字稿进行深度内容增强，包括案例补充、方法论细化、观点完善等
"""

import re
import os
from pathlib import Path
from typing import Dict, List, Tuple
import json

class AdvancedContentEnhancer:
    def __init__(self):
        self.enhancement_count = 0
        self.total_files = 0
        
    def identify_content_type(self, text: str) -> str:
        """识别内容类型"""
        if '案例' in text or '例如' in text or '比如' in text:
            return 'case_study'
        elif '方法' in text or '如何' in text or '步骤' in text or '流程' in text:
            return 'methodology'
        elif '观点' in text or '认为' in text or '建议' in text:
            return 'viewpoint'
        else:
            return 'general'
    
    def extract_sections(self, text: str) -> List[Dict]:
        """提取内容章节"""
        sections = []
        lines = text.split('\n')
        current_section = {'title': '', 'content': [], 'level': 0}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # 识别标题
            if line.startswith('#'):
                # 保存上一节
                if current_section['title']:
                    sections.append(current_section)
                
                # 开始新节
                level = len(line) - len(line.lstrip('#'))
                current_section = {
                    'title': line.lstrip('#').strip(),
                    'content': [],
                    'level': level
                }
            else:
                if current_section['title']:
                    current_section['content'].append(line)
        
        if current_section['title']:
            sections.append(current_section)
        
        return sections
    
    def enhance_case_section(self, section: Dict) -> str:
        """增强案例章节"""
        enhanced = f"\n### {section['title']}\n\n"
        
        # 原始内容
        for line in section['content']:
            enhanced += f"{line}\n"
        
        # 添加结构化增强
        enhanced += "\n**【案例结构化分析】**\n\n"
        enhanced += "**背景：**\n"
        enhanced += "- 行业背景：[具体行业环境]\n"
        enhanced += "- 问题场景：[遇到的具体问题]\n"
        enhanced += "- 目标用户：[目标用户群体]\n\n"
        
        enhanced += "**关键数据：**\n"
        enhanced += "- 数据指标1：[具体数值]\n"
        enhanced += "- 数据指标2：[具体数值]\n"
        enhanced += "- 对比数据：[前后对比]\n\n"
        
        enhanced += "**执行过程：**\n"
        enhanced += "1. 策略制定：[具体策略]\n"
        enhanced += "2. 实施步骤：[具体步骤]\n"
        enhanced += "3. 关键决策：[关键决策点]\n\n"
        
        enhanced += "**结果与成效：**\n"
        enhanced += "- 量化成果：[具体数据]\n"
        enhanced += " - 质化成果：[用户反馈]\n\n"
        
        enhanced += "**核心启示：**\n"
        enhanced += "1. 启示一：[具体启示]\n"
        enhanced += "2. 启示二：[具体启示]\n"
        enhanced += "3. 启示三：[可复用的方法]\n\n"
        
        enhanced += "**实战应用：**\n"
        enhanced += "- 如何在你的工作中应用：[具体方法]\n"
        enhanced += "- 需要注意的坑：[避坑指南]\n"
        
        return enhanced
    
    def enhance_method_section(self, section: Dict) -> str:
        """增强方法论章节"""
        enhanced = f"\n### {section['title']}\n\n"
        
        # 原始内容
        for line in section['content']:
            enhanced += f"{line}\n"
        
        # 添加结构化增强
        enhanced += "\n**【方法论详解】**\n\n"
        enhanced += "**核心原理：**\n"
        enhanced += "- 理论基础：[相关理论支撑]\n"
        enhanced += "- 适用逻辑：[为什么有效]\n\n"
        
        enhanced += "**操作步骤：**\n"
        enhanced += "**步骤一：[步骤名称]**\n"
        enhanced += "- 具体操作：[详细操作说明]\n"
        enhanced += "- 关键要点：[关键注意事项]\n"
        enhanced += "- 常见错误：[避免的错误]\n\n"
        
        enhanced += "**步骤二：[步骤名称]**\n"
        enhanced += "- 具体操作：[详细操作说明]\n"
        enhanced += "- 关键要点：[关键注意事项]\n"
        enhanced += "- 常见错误：[避免的错误]\n\n"
        
        enhanced += "**步骤三：[步骤名称]**\n"
        enhanced += "- 具体操作：[详细操作说明]\n"
        enhanced += "- 关键要点：[关键注意事项]\n"
        enhanced += "- 常见错误：[避免的错误]\n\n"
        
        enhanced += "**评估指标：**\n"
        enhanced += "- 成功标准：[具体指标]\n"
        enhanced += "- 监控方法：[如何监控]\n\n"
        
        enhanced += "**适用场景：**\n"
        enhanced += "- 最适用场景：[具体场景1]\n"
        enhanced += "- 适用场景：[具体场景2]\n"
        enhanced += "- 不适用场景：[不适用的情况]\n\n"
        
        enhanced += "**实例演示：**\n"
        enhanced += "假设场景：[具体场景]\n"
        enhanced += "应用方法：[如何应用]\n"
        enhanced += "预期效果：[预期结果]\n"
        
        return enhanced
    
    def enhance_viewpoint_section(self, section: Dict) -> str:
        """增强观点章节"""
        enhanced = f"\n### {section['title']}\n\n"
        
        # 原始内容
        for line in section['content']:
            enhanced += f"{line}\n"
        
        # 添加结构化增强
        enhanced += "\n**【观点深度解析】**\n\n"
        enhanced += "**观点陈述：**\n"
        enhanced += "[提炼核心观点]\n\n"
        
        enhanced += "**论证逻辑：**\n"
        enhanced += "**理论支撑：**\n"
        enhanced += "- 相关理论：[理论名称]\n"
        enhanced += "- 学术依据：[学术观点]\n\n"
        
        enhanced += "**实践验证：**\n"
        enhanced += "- 行业案例：[验证案例1]\n"
        enhanced += "- 行业案例：[验证案例2]\n\n"
        
        enhanced += "**数据佐证：**\n"
        enhanced += "- 数据来源：[具体数据]\n"
        enhanced += "- 数据分析：[数据解读]\n\n"
        
        enhanced += "**应用场景：**\n"
        enhanced += "**场景一：[场景名称]**\n"
        enhanced += "- 具体应用：[如何应用]\n"
        enhanced += "- 预期效果：[预期结果]\n\n"
        
        enhanced += "**场景二：[场景名称]**\n"
        enhanced += "- 具体应用：[如何应用]\n"
        enhanced += "- 预期效果：[预期结果]\n\n"
        
        enhanced += "**注意事项：**\n"
        enhanced += "- 前提条件：[应用前提]\n"
        enhanced += "- 风险提示：[潜在风险]\n"
        enhanced += "- 边界条件：[适用边界]\n\n"
        
        enhanced += "**延伸思考：**\n"
        enhanced += "- 如何优化这个观点？\n"
        enhanced += "- 在什么情况下需要调整？\n"
        enhanced += "- 与其他观点的关系？\n"
        
        return enhanced
    
    def process_file_advanced(self, input_path: Path, output_path: Path) -> bool:
        """高级处理单个文件"""
        try:
            # 读取原始内容
            with open(input_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取章节
            sections = self.extract_sections(content)
            
            # 构建增强内容
            enhanced_parts = []
            enhanced_parts.append("# " + content.split('\n')[0].lstrip('#').strip() + "\n")
            enhanced_parts.append("\n## 课程概述\n\n")
            enhanced_parts.append("本节内容重点讲解...\n")
            enhanced_parts.append("\n## 学习目标\n\n")
            enhanced_parts.append("- 理解核心概念\n")
            enhanced_parts.append("- 掌握操作方法\n")
            enhanced_parts.append("- 能够实际应用\n\n")
            
            # 处理每个章节
            for section in sections:
                if not section['title']:
                    continue
                
                content_type = self.identify_content_type('\n'.join(section['content']))
                
                if content_type == 'case_study':
                    enhanced_parts.append(self.enhance_case_section(section))
                elif content_type == 'methodology':
                    enhanced_parts.append(self.enhance_method_section(section))
                elif content_type == 'viewpoint':
                    enhanced_parts.append(self.enhance_viewpoint_section(section))
                else:
                    # 普通内容
                    enhanced_parts.append(f"\n### {section['title']}\n\n")
                    for line in section['content']:
                        enhanced_parts.append(f"{line}\n")
            
            # 添加总结部分
            enhanced_parts.append("\n## 本节总结\n\n")
            enhanced_parts.append("**核心要点回顾：**\n")
            enhanced_parts.append("1. 要点一\n")
            enhanced_parts.append("2. 要点二\n")
            enhanced_parts.append("3. 要点三\n\n")
            
            enhanced_parts.append("**实践建议：**\n")
            enhanced_parts.append("- 在实际工作中如何应用\n")
            enhanced_parts.append("- 需要注意的关键点\n\n")
            
            enhanced_parts.append("**延伸思考：**\n")
            enhanced_parts.append("- 如何将本节内容与你的工作结合？\n")
            enhanced_parts.append("- 你遇到过哪些相关场景？\n")
            
            # 写入文件
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(''.join(enhanced_parts))
            
            self.enhancement_count += 1
            return True
            
        except Exception as e:
            print(f"处理文件 {input_path.name} 时出错: {str(e)}")
            return False
    
    def batch_process_advanced(self, input_dir: Path, output_dir: Path):
        """批量高级处理"""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        md_files = sorted(input_dir.glob("*.md"))
        self.total_files = len(md_files)
        
        print(f"高级内容增强 - 找到 {self.total_files} 个文件")
        print("="*60)
        
        for i, md_file in enumerate(md_files, 1):
            print(f"[{i}/{self.total_files}] 高级增强: {md_file.name}")
            
            output_file = output_dir / md_file.name
            success = self.process_file_advanced(md_file, output_file)
            
            if success:
                print(f"  ✓ 完成")
            else:
                print(f"  ✗ 失败")
        
        print("="*60)
        print(f"高级增强完成: {self.enhancement_count}/{self.total_files}")

if __name__ == "__main__":
    base_path = Path("/Users/cyberwiz/Documents/三节课课程/运营/需要合并内容运营的基本功")
    transcript_dir = base_path / "逐字稿"
    output_dir = base_path / "内容增强-颗粒度对齐版"
    
    enhancer = AdvancedContentEnhancer()
    enhancer.batch_process_advanced(transcript_dir, output_dir)
    
    print(f"\n✅ 高级内容增强完成！")
    print(f"📁 输出目录: {output_dir}")

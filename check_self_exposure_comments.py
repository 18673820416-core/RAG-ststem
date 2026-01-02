#!/usr/bin/env python
# @self-expose: {"id": "check_self_exposure_comments", "name": "自曝光注释检查脚本", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["检查自曝光注释格式", "验证自曝光注释内容", "生成自曝光注释检查报告"]}}
# -*- coding: utf-8 -*-
"""
检查所有文件的自曝光注释格式和内容
"""

import os
import re
import json
from pathlib import Path

def check_self_exposure_comment(file_path):
    """
    检查单个文件的自曝光注释
    
    Args:
        file_path: 文件路径
    
    Returns:
        dict: 检查结果
    """
    result = {
        "file_path": file_path,
        "has_comment": False,
        "format_correct": False,
        "missing_fields": [],
        "content_issues": [],
        "error_message": None
    }
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否包含@self-expose注释
        if '# @self-expose' not in content:
            result["error_message"] = "缺少自曝光注释"
            return result
        
        result["has_comment"] = True
        
        # 提取自曝光注释
        expose_start = content.find('# @self-expose')
        brace_start = content.find('{', expose_start)
        if brace_start == -1:
            result["error_message"] = "自曝光注释格式错误，缺少{"
            return result
        
        # 找到完整的JSON对象
        brace_count = 0
        brace_end = -1
        for i in range(brace_start, len(content)):
            char = content[i]
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    brace_end = i
                    break
        
        if brace_end == -1:
            result["error_message"] = "自曝光注释格式错误，缺少}"
            return result
        
        # 提取JSON字符串
        json_str = content[brace_start:brace_end+1]
        
        try:
            # 解析JSON
            data = json.loads(json_str)
            
            # 检查必需字段
            required_fields = ["id", "name", "type", "version", "needs", "provides"]
            for field in required_fields:
                if field not in data:
                    result["missing_fields"].append(field)
            
            # 检查needs字段结构
            if "needs" in data:
                if not isinstance(data["needs"], dict):
                    result["content_issues"].append("needs字段应为字典类型")
                else:
                    if "deps" not in data["needs"]:
                        data["needs"]["deps"] = []
                    if "resources" not in data["needs"]:
                        data["needs"]["resources"] = []
            
            # 检查provides字段结构
            if "provides" in data:
                if not isinstance(data["provides"], dict):
                    result["content_issues"].append("provides字段应为字典类型")
                else:
                    if "capabilities" not in data["provides"]:
                        result["content_issues"].append("provides字段缺少capabilities子字段")
            
            # 检查id字段
            if "id" in data:
                expected_id = Path(file_path).stem
                if data["id"] != expected_id:
                    result["content_issues"].append(f"id字段应为{expected_id}，实际为{data['id']}")
            
            # 如果没有缺失字段和内容问题，格式正确
            if not result["missing_fields"] and not result["content_issues"]:
                result["format_correct"] = True
                
        except json.JSONDecodeError as e:
            result["error_message"] = f"JSON格式错误: {str(e)}"
            return result
        
    except Exception as e:
        result["error_message"] = f"文件读取错误: {str(e)}"
        return result
    
    return result

def main():
    """
    主函数
    """
    # 读取文件列表
    with open('python_files_list.txt', 'r', encoding='utf-8') as f:
        file_paths = [line.strip() for line in f if line.strip()]
    
    print(f"开始检查 {len(file_paths)} 个文件的自曝光注释...")
    
    # 检查结果统计
    total_files = len(file_paths)
    files_with_comment = 0
    files_with_correct_format = 0
    files_with_issues = 0
    
    # 详细结果
    all_results = []
    
    # 检查每个文件
    for file_path in file_paths:
        result = check_self_exposure_comment(file_path)
        all_results.append(result)
        
        if result["has_comment"]:
            files_with_comment += 1
            if result["format_correct"]:
                files_with_correct_format += 1
            else:
                files_with_issues += 1
        else:
            files_with_issues += 1
    
    # 生成检查报告
    report = "# 自曝光注释检查报告\n\n"
    report += f"## 总体统计\n"
    report += f"- 总文件数: {total_files}\n"
    report += f"- 包含自曝光注释: {files_with_comment}\n"
    report += f"- 格式正确: {files_with_correct_format}\n"
    report += f"- 存在问题: {files_with_issues}\n\n"
    
    report += "## 详细问题\n\n"
    
    for result in all_results:
        if not result["has_comment"]:
            report += f"### {result['file_path']}\n"
            report += f"- 错误: {result['error_message']}\n\n"
        elif not result["format_correct"]:
            report += f"### {result['file_path']}\n"
            if result["missing_fields"]:
                report += f"- 缺失字段: {', '.join(result['missing_fields'])}\n"
            if result["content_issues"]:
                report += f"- 内容问题: {', '.join(result['content_issues'])}\n"
            if result["error_message"]:
                report += f"- 错误: {result['error_message']}\n"
            report += "\n"
    
    # 保存报告
    with open('self_exposure_check_report.md', 'w', encoding='utf-8') as f:
        f.write(report)
    
    # 打印简要结果
    print(f"检查完成！")
    print(f"总文件数: {total_files}")
    print(f"包含自曝光注释: {files_with_comment}")
    print(f"格式正确: {files_with_correct_format}")
    print(f"存在问题: {files_with_issues}")
    print(f"详细报告已保存到 self_exposure_check_report.md")

if __name__ == "__main__":
    main()
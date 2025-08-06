#!/usr/bin/env python3
"""
AgentOS2 文档收集脚本
自动收集核心文件内容并生成综合文档
"""

import os
import sys
import importlib.util
import inspect
from datetime import datetime


def get_utility_docstrings():
    """获取utility.py中所有对外函数的docstring"""
    # 动态导入utility模块
    utility_path = os.path.join(os.path.dirname(__file__), 'agent_os', 'utility.py')
    spec = importlib.util.spec_from_file_location("agent_os.utility", utility_path)
    utility = importlib.util.module_from_spec(spec)
    sys.modules['agent_os.utility'] = utility
    spec.loader.exec_module(utility)
    
    # 直接调用_generate_docstring函数
    return utility._generate_docstring()


def collect_file_content(file_path):
    """读取文件内容"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"读取文件时出错: {str(e)}"


def collect_directory_files(directory_path, prefix=""):
    """递归收集目录下所有.py文件的路径"""
    collected_files = []
    try:
        for root, dirs, files in os.walk(directory_path):
            # 跳过__pycache__目录
            if '__pycache__' in dirs:
                dirs.remove('__pycache__')
            
            for file in files:
                if file.endswith('.py'):
                    rel_path = os.path.relpath(os.path.join(root, file), directory_path)
                    full_path = os.path.join(root, file)
                    display_path = os.path.join(prefix, rel_path).replace('\\', '/')
                    collected_files.append((full_path, display_path))
    except Exception as e:
        print(f"收集目录 {directory_path} 时出错: {str(e)}")
    return collected_files


def main():
    """主函数：收集所有指定文件的内容"""
    # 获取agent_os2的根目录
    root_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 询问用户是否包含examples目录
    print("是否包含 examples/story_generate_example 目录？")
    print("1. 包含")
    print("2. 不包含（默认）")
    choice = input("请输入选择 (1/2): ").strip()
    
    # 定义要收集的文件
    files_to_collect = [
        ('agent_os/base_agent.py', 'agent_os2/agent_os/base_agent.py'),
        ('agent_os/flow.py', 'agent_os2/agent_os/flow.py'),
        ('README.md', 'agent_os2/README.md'),
        ('DEVELOPING_GUIDE.md', 'agent_os2/DEVELOPING_GUIDE.md'),
    ]
    
    # 如果用户选择包含examples
    if choice == '1':
        examples_path = os.path.join(root_dir, 'agents', 'examples', 'story_generate_example')
        if os.path.exists(examples_path):
            print(f"\n将包含 {examples_path} 目录下的所有.py文件")
            example_files = collect_directory_files(
                examples_path, 
                'agent_os2/agents/examples/story_generate_example'
            )
            files_to_collect.extend(example_files)
        else:
            print(f"\n警告：目录 {examples_path} 不存在，跳过")
    else:
        print("\n不包含examples目录")
    
    # 输出文件名
    output_filename = f"agent_os2_docs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    output_path = os.path.join(root_dir, output_filename)
    
    # 开始收集
    print(f"开始收集AgentOS2文档...")
    print(f"输出文件: {output_path}")
    
    with open(output_path, 'w', encoding='utf-8') as output_file:
        # 写入头部信息
        output_file.write(f"# AgentOS2 核心文档汇总\n")
        output_file.write(f"# 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        output_file.write("=" * 80 + "\n\n")
        
        # 收集每个文件的内容
        for file_info in files_to_collect:
            if isinstance(file_info, tuple) and len(file_info) == 2:
                # 处理元组格式 (相对路径或绝对路径, 显示路径)
                path_or_relative, display_path = file_info
                
                # 判断是绝对路径还是相对路径
                if os.path.isabs(path_or_relative):
                    file_path = path_or_relative
                else:
                    file_path = os.path.join(root_dir, path_or_relative)
                
                print(f"正在处理: {display_path}")
                
                output_file.write(f"{display_path}:\n")
                output_file.write("-" * 80 + "\n")
                
                if os.path.exists(file_path):
                    content = collect_file_content(file_path)
                    output_file.write(content)
                else:
                    output_file.write(f"文件不存在: {file_path}")
                
                output_file.write("\n\n" + "=" * 80 + "\n\n")
        
        # 收集utility.py的docstrings
        print("正在处理: agent_os2/agent_os/utility.py (函数文档)")
        output_file.write("agent_os2/agent_os/utility.py (对外函数文档):\n")
        output_file.write("-" * 80 + "\n")
        
        utility_docs = get_utility_docstrings()
        output_file.write(utility_docs)
        
        output_file.write("\n\n" + "=" * 80 + "\n")
    
    print(f"\n✅ 文档收集完成！")
    print(f"📄 输出文件: {output_filename}")
    print(f"📍 文件路径: {output_path}")
    
    # 显示文件大小
    file_size = os.path.getsize(output_path)
    print(f"📊 文件大小: {file_size:,} 字节 ({file_size/1024:.2f} KB)")
    
    return output_path


if __name__ == "__main__":
    try:
        output_path = main()
        
        # 询问是否要查看前100行
        print("\n是否要查看生成文档的前100行? (y/n): ", end="")
        response = input().strip().lower()
        
        if response == 'y':
            print("\n" + "=" * 80)
            print("文档前100行预览:")
            print("=" * 80 + "\n")
            
            with open(output_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                for i, line in enumerate(lines[:100], 1):
                    print(line, end='')
                
                if len(lines) > 100:
                    print(f"\n... (共 {len(lines)} 行)")
    
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断操作")
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")
        import traceback
        traceback.print_exc() 
"""
文件上传边界测试用例
测试各种极端情况和边界条件

测试覆盖：
1. 超大文件测试（>100KB）
2. 特殊字符文件名测试
3. 不同编码文件测试（UTF-8, GBK, GB2312）
4. 二进制文件测试
5. 空文件测试
6. 不存在的文件测试
"""

import os
import sys
import json
import time

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.base_agent import BaseAgent


def create_test_file(filename: str, content: str, encoding: str = 'utf-8'):
    """创建测试文件"""
    test_dir = os.path.join(os.path.dirname(__file__), 'test_files')
    os.makedirs(test_dir, exist_ok=True)
    
    file_path = os.path.join(test_dir, filename)
    with open(file_path, 'w', encoding=encoding) as f:
        f.write(content)
    
    return file_path


def test_large_file():
    """测试1: 超大文件（>100KB）"""
    print("\n" + "="*60)
    print("测试1: 超大文件测试（>100KB）")
    print("="*60)
    
    # 生成120KB的内容
    large_content = "这是测试内容。" * 10000  # 约120KB
    file_path = create_test_file("large_test.txt", large_content)
    
    print(f"✅ 创建测试文件: {file_path}")
    print(f"   文件大小: {len(large_content)} 字符 ({len(large_content)/1024:.2f} KB)")
    
    # 测试读取
    agent = BaseAgent(agent_id="test_agent", agent_type="test")
    result = agent._read_uploaded_file(file_path)
    
    if result:
        print(f"✅ 文件读取成功")
        if len(result) < len(large_content):
            print(f"✅ 文件已截断: {len(result)} 字符（原始 {len(large_content)} 字符）")
        else:
            print(f"⚠️  文件未截断: {len(result)} 字符")
    else:
        print(f"❌ 文件读取失败")
    
    # 清理
    os.remove(file_path)
    return result is not None


def test_special_characters_filename():
    """测试2: 特殊字符文件名"""
    print("\n" + "="*60)
    print("测试2: 特殊字符文件名测试")
    print("="*60)
    
    test_cases = [
        ("中文文件名.txt", "这是中文文件名测试"),
        ("file with spaces.txt", "This is a file with spaces"),
        ("file_with_underscore.txt", "File with underscore"),
        ("file-with-dash.txt", "File with dash"),
    ]
    
    agent = BaseAgent(agent_id="test_agent", agent_type="test")
    results = []
    
    for filename, content in test_cases:
        try:
            file_path = create_test_file(filename, content)
            print(f"\n测试文件: {filename}")
            print(f"   路径: {file_path}")
            
            result = agent._read_uploaded_file(file_path)
            if result and content in result:
                print(f"   ✅ 读取成功")
                results.append(True)
            else:
                print(f"   ❌ 读取失败或内容不匹配")
                results.append(False)
            
            # 清理
            os.remove(file_path)
        except Exception as e:
            print(f"   ❌ 异常: {str(e)}")
            results.append(False)
    
    success_count = sum(results)
    print(f"\n总结: {success_count}/{len(test_cases)} 个测试通过")
    return all(results)


def test_different_encodings():
    """测试3: 不同编码文件"""
    print("\n" + "="*60)
    print("测试3: 不同编码文件测试")
    print("="*60)
    
    test_cases = [
        ("utf8_test.txt", "UTF-8编码测试：你好世界！", 'utf-8'),
        ("gbk_test.txt", "GBK编码测试：你好世界！", 'gbk'),
        ("gb2312_test.txt", "GB2312编码测试：你好世界！", 'gb2312'),
    ]
    
    agent = BaseAgent(agent_id="test_agent", agent_type="test")
    results = []
    
    for filename, content, encoding in test_cases:
        try:
            file_path = create_test_file(filename, content, encoding)
            print(f"\n测试文件: {filename} ({encoding})")
            
            result = agent._read_uploaded_file(file_path)
            if result and "你好世界" in result:
                print(f"   ✅ 读取成功，编码正确识别")
                results.append(True)
            else:
                print(f"   ❌ 读取失败或编码识别错误")
                results.append(False)
            
            # 清理
            os.remove(file_path)
        except Exception as e:
            print(f"   ❌ 异常: {str(e)}")
            results.append(False)
    
    success_count = sum(results)
    print(f"\n总结: {success_count}/{len(test_cases)} 个测试通过")
    return all(results)


def test_binary_files():
    """测试4: 二进制文件"""
    print("\n" + "="*60)
    print("测试4: 二进制文件测试")
    print("="*60)
    
    binary_extensions = [
        '.exe', '.pdf', '.docx', '.zip', 
        '.jpg', '.png', '.mp3', '.mp4'
    ]
    
    agent = BaseAgent(agent_id="test_agent", agent_type="test")
    results = []
    
    for ext in binary_extensions:
        filename = f"test_binary{ext}"
        file_path = os.path.join(os.path.dirname(__file__), 'test_files', filename)
        
        # 创建空二进制文件
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'wb') as f:
            f.write(b'\x00' * 100)  # 写入100字节的二进制数据
        
        print(f"\n测试文件: {filename}")
        result = agent._read_uploaded_file(file_path)
        
        if result and "二进制文件" in result:
            print(f"   ✅ 正确识别为二进制文件")
            results.append(True)
        else:
            print(f"   ❌ 未能正确识别二进制文件")
            results.append(False)
        
        # 清理
        os.remove(file_path)
    
    success_count = sum(results)
    print(f"\n总结: {success_count}/{len(binary_extensions)} 个测试通过")
    return all(results)


def test_empty_file():
    """测试5: 空文件"""
    print("\n" + "="*60)
    print("测试5: 空文件测试")
    print("="*60)
    
    file_path = create_test_file("empty_test.txt", "")
    print(f"✅ 创建空文件: {file_path}")
    
    agent = BaseAgent(agent_id="test_agent", agent_type="test")
    result = agent._read_uploaded_file(file_path)
    
    if result == "":
        print(f"✅ 空文件读取成功，返回空字符串")
        success = True
    elif result is None:
        print(f"⚠️  空文件读取返回None")
        success = False
    else:
        print(f"❌ 空文件读取返回意外值: {result}")
        success = False
    
    # 清理
    os.remove(file_path)
    return success


def test_nonexistent_file():
    """测试6: 不存在的文件"""
    print("\n" + "="*60)
    print("测试6: 不存在的文件测试")
    print("="*60)
    
    fake_path = "E:\\RAG系统\\test_files\\nonexistent_file.txt"
    print(f"测试路径: {fake_path}")
    
    agent = BaseAgent(agent_id="test_agent", agent_type="test")
    result = agent._read_uploaded_file(fake_path)
    
    if result is None:
        print(f"✅ 正确处理不存在的文件（返回None）")
        return True
    else:
        print(f"❌ 不存在的文件处理异常: {result}")
        return False


def test_performance():
    """测试7: 性能测试"""
    print("\n" + "="*60)
    print("测试7: 性能测试")
    print("="*60)
    
    # 测试不同大小文件的读取耗时
    test_sizes = [
        (1000, "1KB"),
        (10000, "10KB"),
        (50000, "50KB"),
        (100000, "100KB"),
    ]
    
    agent = BaseAgent(agent_id="test_agent", agent_type="test")
    
    for size, label in test_sizes:
        content = "测试" * (size // 2)  # 每个中文字符2字节
        file_path = create_test_file(f"perf_{label}.txt", content)
        
        start_time = time.time()
        result = agent._read_uploaded_file(file_path)
        elapsed = time.time() - start_time
        
        print(f"\n文件大小: {label}")
        print(f"   读取耗时: {elapsed:.3f}秒")
        
        if elapsed < 1.0:
            print(f"   ✅ 性能良好（<1秒）")
        elif elapsed < 2.0:
            print(f"   ⚠️  性能一般（1-2秒）")
        else:
            print(f"   ❌ 性能较差（>2秒）")
        
        # 清理
        os.remove(file_path)
    
    return True


def run_all_tests():
    """运行所有测试"""
    print("\n" + "="*60)
    print("文件上传边界测试套件")
    print("="*60)
    
    tests = [
        ("超大文件测试", test_large_file),
        ("特殊字符文件名测试", test_special_characters_filename),
        ("不同编码测试", test_different_encodings),
        ("二进制文件测试", test_binary_files),
        ("空文件测试", test_empty_file),
        ("不存在文件测试", test_nonexistent_file),
        ("性能测试", test_performance),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = "✅ 通过" if result else "❌ 失败"
        except Exception as e:
            results[test_name] = f"❌ 异常: {str(e)}"
    
    # 打印测试总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    
    for test_name, result in results.items():
        print(f"{test_name}: {result}")
    
    # 统计
    passed = sum(1 for r in results.values() if "✅" in r)
    total = len(results)
    
    print(f"\n总计: {passed}/{total} 个测试通过")
    
    # 清理测试目录
    test_dir = os.path.join(os.path.dirname(__file__), 'test_files')
    if os.path.exists(test_dir):
        try:
            import shutil
            shutil.rmtree(test_dir)
            print(f"\n✅ 已清理测试目录: {test_dir}")
        except Exception as e:
            print(f"\n⚠️  清理测试目录失败: {str(e)}")


if __name__ == "__main__":
    run_all_tests()

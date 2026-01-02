# @self-expose: {"id": "error_decorator", "name": "Error Decorator", "type": "component", "version": "1.0.0", "needs": {"deps": [], "resources": []}, "provides": {"capabilities": ["Error Decorator功能"]}}
import functools
import traceback
from datetime import datetime
from error_reporting import report_component_error


def error_catcher(component_name):
    """
    统一的错误捕获装饰器，用于捕获组件级错误并上报
    
    Args:
        component_name: 组件名称，用于错误上报时标识错误来源
    
    Returns:
        装饰后的函数，会自动捕获并上报错误
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # 捕获错误并生成详细的错误信息
                error_data = {
                    "error_id": f"{component_name}-{type(e).__name__}-{datetime.now().timestamp()}-{hash(str(e))}",
                    "level": "component",
                    "type": type(e).__name__,
                    "message": str(e),
                    "timestamp": datetime.now().isoformat(),
                    "component": component_name,
                    "function": func.__name__,
                    "file_path": func.__code__.co_filename,
                    "line_number": func.__code__.co_firstlineno,
                    "stack_trace": traceback.format_exc(),
                    "severity": "error",
                    "context": {
                        "args_repr": str(args[:3]),  # 只保留前3个参数，避免敏感信息泄露
                        "kwargs_keys": list(kwargs.keys())  # 只保留关键字参数名，不保留值
                    }
                }
                
                # 上报错误
                try:
                    report_component_error(error_data)
                except Exception as report_error:
                    # 如果上报失败，记录到日志
                    print(f"Error reporting failed: {report_error}")
                    print(f"Original error: {error_data}")
                
                # 重新抛出原始错误，确保程序正常流程
                raise
        return wrapper
    return decorator


def async_error_catcher(component_name):
    """
    异步函数的错误捕获装饰器
    
    Args:
        component_name: 组件名称，用于错误上报时标识错误来源
    
    Returns:
        装饰后的异步函数，会自动捕获并上报错误
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                # 捕获错误并生成详细的错误信息
                error_data = {
                    "error_id": f"{component_name}-{type(e).__name__}-{datetime.now().timestamp()}-{hash(str(e))}",
                    "level": "component",
                    "type": type(e).__name__,
                    "message": str(e),
                    "timestamp": datetime.now().isoformat(),
                    "component": component_name,
                    "function": func.__name__,
                    "file_path": func.__code__.co_filename,
                    "line_number": func.__code__.co_firstlineno,
                    "stack_trace": traceback.format_exc(),
                    "severity": "error",
                    "context": {
                        "args_repr": str(args[:3]),  # 只保留前3个参数，避免敏感信息泄露
                        "kwargs_keys": list(kwargs.keys())  # 只保留关键字参数名，不保留值
                    }
                }
                
                # 上报错误
                try:
                    report_component_error(error_data)
                except Exception as report_error:
                    # 如果上报失败，记录到日志
                    print(f"Error reporting failed: {report_error}")
                    print(f"Original error: {error_data}")
                
                # 重新抛出原始错误，确保程序正常流程
                raise
        return wrapper
    return decorator

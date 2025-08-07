
import sys
import os
import re
import glob
import json
import numpy as np
import math
import shutil

import time
import functools
import logging
from typing import Any, Callable, Dict
import datetime

from io import StringIO
import traceback

def say(*args, **kw):
    # add flush to print
    print(*args, **kw, flush=True)


def smonitor(func_name, log_file):
    # {{{
    """
    装饰器：监控函数中的say语句并记录执行时间到日志文件
    
    Args:
        func_name: 函数名称（用于日志标识）
        log_file: 日志文件路径
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_times = {}  # 存储每个步骤的开始时间
            last_completion_time = None  # 记录上一个完成的时间
            last_completion_step = None  # 记录上一个完成的步骤名称
            
            # 创建监控版本的say函数
            def say(message):
                """
                监控版本的say函数，会同时输出到控制台和记录日志
                """
                nonlocal last_completion_time, last_completion_step
                
                # 检查消息内容并记录日志
                current_time = datetime.datetime.now()
                
                # 检查是否是"xxx开始"模式
                start_match = re.search(r'(.+?)开始', str(message))
                if start_match:
                    step_name = start_match.group(1).strip()
                    start_times[step_name] = current_time
                    log_message = f"[{current_time.strftime('%Y-%m-%d %H:%M:%S')}] {func_name} - {step_name} 开始执行\n"
                    with open(log_file, 'a', encoding='utf-8') as f:
                        f.write(log_message)
                    print(log_message.strip())
                
                # 检查是否是"xxx完成"模式
                end_match = re.search(r'(.+?)完成', str(message))
                if end_match:
                    step_name = end_match.group(1).strip()
                    end_time = current_time
                    
                    # 如果找到对应的开始时间
                    if step_name in start_times:
                        duration = (end_time - start_times[step_name]).total_seconds()
                        log_message = f"[{end_time.strftime('%Y-%m-%d %H:%M:%S')}] {func_name} - {step_name} 执行完成，耗时: {duration:.2f}秒\n"
                        del start_times[step_name]  # 清除已完成的步骤
                    
                    # 如果没有找到对应的开始时间，但有上一个完成时间
                    elif last_completion_time is not None:
                        duration = (end_time - last_completion_time).total_seconds()
                        log_message = f"[{end_time.strftime('%Y-%m-%d %H:%M:%S')}] {func_name} - {step_name} 执行完成，耗时: {duration:.2f}秒（基于上一步完成时间）\n"
                    
                    # 既没有开始时间，也没有上一个完成时间
                    else:
                        log_message = f"[{end_time.strftime('%Y-%m-%d %H:%M:%S')}] {func_name} - {step_name} 执行完成（无法计算耗时）\n"
                    
                    # 更新上一个完成时间和步骤
                    last_completion_time = end_time
                    last_completion_step = step_name
                    
                    with open(log_file, 'a', encoding='utf-8') as f:
                        f.write(log_message)
                    print(log_message.strip())
                
                # 如果既不是开始也不是完成，只是普通消息
                if not start_match and not end_match:
                    print(str(message))
            
            # 将say函数注入到函数的全局命名空间中
            if hasattr(func, '__globals__'):
                original_say = func.__globals__.get('say', None)
                func.__globals__['say'] = say
            
            try:
                # 记录函数整体开始时间
                func_start_time = datetime.datetime.now()
                last_completion_time = func_start_time  # 初始化上一个完成时间为函数开始时间
                
                with open(log_file, 'a', encoding='utf-8') as f:
                    f.write(f"[{func_start_time.strftime('%Y-%m-%d %H:%M:%S')}] {func_name} 函数开始执行\n")
                print(f"[{func_start_time.strftime('%Y-%m-%d %H:%M:%S')}] {func_name} 函数开始执行")
                
                # 执行原函数
                result = func(*args, **kwargs)
                
                # 记录函数整体结束时间
                func_end_time = datetime.datetime.now()
                func_duration = (func_end_time - func_start_time).total_seconds()
                with open(log_file, 'a', encoding='utf-8') as f:
                    f.write(f"[{func_end_time.strftime('%Y-%m-%d %H:%M:%S')}] {func_name} 函数执行完成，总耗时: {func_duration:.2f}秒\n")
                    f.write("-" * 50 + "\n")
                print(f"[{func_end_time.strftime('%Y-%m-%d %H:%M:%S')}] {func_name} 函数执行完成，总耗时: {func_duration:.2f}秒")
                print("-" * 50)
                
                return result
            
            finally:
                # 恢复原来的say函数（如果存在）
                if hasattr(func, '__globals__'):
                    if original_say is not None:
                        func.__globals__['say'] = original_say
                    else:
                        func.__globals__.pop('say', None)
        
        return wrapper
    return decorator
    # }}}


def monitor(func_name, log_file):
    # {{{
    """
    装饰器：监控函数中的print语句并记录执行时间到日志文件
    
    Args:
        func_name: 函数名称（用于日志标识）
        log_file: 日志文件路径
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 用于捕获print输出
            captured_output = StringIO()
            start_times = {}  # 存储每个步骤的开始时间
            
            # 重写print函数来监控特定模式
            original_print = print
            
            def monitored_print(*print_args, **print_kwargs):
                # 先正常打印
                # original_print(*print_args, **print_kwargs)
                
                # 检查打印内容
                if print_args:
                    content = str(print_args[0])
                    current_time = datetime.datetime.now()
                    
                    # 检查是否是"xxx开始"模式
                    start_match = re.search(r'(.+?)开始$', content)
                    if start_match:
                        step_name = start_match.group(1).strip()
                        start_times[step_name] = current_time
                        log_message = f"[{current_time.strftime('%Y-%m-%d %H:%M:%S')}] {func_name} - {step_name} 开始执行"
                        with open(log_file, 'a', encoding='utf-8') as f:
                            f.write(log_message+"\n")
                            original_print(log_message)
                    
                    # 检查是否是"xxx完成"模式
                    end_match = re.search(r'(.+?)完成$', content)
                    if end_match:
                        step_name = end_match.group(1).strip()
                        end_time = current_time
                        
                        if step_name in start_times:
                            duration = (end_time - start_times[step_name]).total_seconds()
                            log_message = f"[{end_time.strftime('%Y-%m-%d %H:%M:%S')}] {func_name} - {step_name} 执行完成，耗时: {duration:.2f}秒"
                            del start_times[step_name]  # 清除已完成的步骤
                        else:
                            log_message = f"[{end_time.strftime('%Y-%m-%d %H:%M:%S')}] {func_name} - {step_name} 执行完成（未找到对应的开始时间）"
                        
                        with open(log_file, 'a', encoding='utf-8') as f:
                            f.write(log_message+"\n")
                            original_print(log_message)

            
            # 临时替换print函数
            import builtins
            original_builtin_print = builtins.print
            builtins.print = monitored_print
            
            try:
                # 记录函数整体开始时间
                func_start_time = datetime.datetime.now()
                with open(log_file, 'a', encoding='utf-8') as f:
                    log_message = f"[{func_start_time.strftime('%Y-%m-%d %H:%M:%S')}] {func_name} 函数开始执行"
                    f.write(log_message+"\n")
                    original_print(log_message)
                
                # 执行原函数
                result = func(*args, **kwargs)
                
                # 记录函数整体结束时间
                func_end_time = datetime.datetime.now()
                func_duration = (func_end_time - func_start_time).total_seconds()
                with open(log_file, 'a', encoding='utf-8') as f:
                    log_message = f"[{func_end_time.strftime('%Y-%m-%d %H:%M:%S')}] {func_name} 函数执行完成，总耗时: {func_duration:.2f}秒"
                    f.write(log_message+"\n")
                    original_print(log_message)
                    log_message = "-" * 50
                    f.write(log_message+"\n")
                    original_print(log_message)
                
                return result
            
            finally:
                # 恢复原来的print函数
                builtins.print = original_builtin_print
        
        return wrapper
    return decorator
    # }}}


def setup_elegant_logger(log_file, func_name):
    # {{{
    """设置华丽的日志格式"""
    logger = logging.getLogger(f"{func_name}_monitor")
    logger.setLevel(logging.INFO)
    
    # 清除已有的处理器
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # 文件处理器
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_formatter = logging.Formatter(
        '%(asctime)s,%(msecs)03d - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter(
        '\033[96m%(asctime)s\033[0m - \033[94m%(name)s\033[0m - \033[92m%(levelname)s\033[0m - %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger
    # }}}


def emonitor(func_name, log_file):
    # {{{
    """
    华丽版装饰器：监控函数中的say语句并记录执行时间到日志文件
    
    Args:
        func_name: 函数名称（用于日志标识）
        log_file: 日志文件路径
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 获取类名（如果是方法）
            class_name = None
            if args and hasattr(args[0], '__class__'):
                class_name = args[0].__class__.__name__
            
            # 构建函数标识
            if class_name:
                func_identifier = f"{class_name}({class_name})"
            else:
                func_identifier = func_name
            
            # 设置日志器
            logger = setup_elegant_logger(log_file, func_name)
            
            start_times = {}  # 存储每个步骤的开始时间
            last_completion_time = None  # 记录上一个完成的时间
            last_completion_step = None  # 记录上一个完成的步骤名称
            
            # 创建监控版本的say函数
            def say(message):
                """
                华丽版监控say函数，支持emoji和彩色输出
                """
                nonlocal last_completion_time, last_completion_step
                
                current_time = datetime.datetime.now()
                
                # 检查是否是"xxx开始"模式
                start_match = re.search(r'(.+?)开始', str(message))
                if start_match:
                    step_name = start_match.group(1).strip()
                    start_times[step_name] = current_time
                    logger.info(f"🚀 [{func_identifier}] 开始执行 {step_name}")
                
                # 检查是否是"xxx完成"模式
                end_match = re.search(r'(.+?)完成', str(message))
                if end_match:
                    step_name = end_match.group(1).strip()
                    end_time = current_time
                    
                    # 如果找到对应的开始时间
                    if step_name in start_times:
                        duration = (end_time - start_times[step_name]).total_seconds()
                        logger.info(f"✅ [{func_identifier}] {step_name} 执行成功")
                        logger.info(f"⏱️  执行时间: {duration:.3f}秒")
                        del start_times[step_name]  # 清除已完成的步骤
                    
                    # 如果没有找到对应的开始时间，但有上一个完成时间
                    elif last_completion_time is not None:
                        duration = (end_time - last_completion_time).total_seconds()
                        logger.info(f"✅ [{func_identifier}] {step_name} 执行成功")
                        logger.info(f"⏱️  执行时间: {duration:.3f}秒（基于上一步完成时间）")
                    
                    # 既没有开始时间，也没有上一个完成时间
                    else:
                        logger.info(f"✅ [{func_identifier}] {step_name} 执行成功")
                        logger.info(f"⚠️  无法计算执行时间")
                    
                    # 更新上一个完成时间和步骤
                    last_completion_time = end_time
                    last_completion_step = step_name
                
                # 如果既不是开始也不是完成，只是普通消息
                if not start_match and not end_match:
                    logger.info(f"💬 {message}")
            
            # 将say函数注入到函数的全局命名空间中
            if hasattr(func, '__globals__'):
                original_say = func.__globals__.get('say', None)
                func.__globals__['say'] = say
            
            # 格式化参数信息
            args_str = ', '.join([repr(arg) for arg in args])
            kwargs_str = ', '.join([f"{k}={repr(v)}" for k, v in kwargs.items()])
            params_info = f"args=({args_str})" + (f", kwargs={{{kwargs_str}}}" if kwargs_str else ", kwargs={}")
            
            try:
                # 记录函数整体开始时间
                func_start_time = datetime.datetime.now()
                last_completion_time = func_start_time  # 初始化上一个完成时间为函数开始时间
                
                logger.info(f"🚀 [{func_identifier}] 开始执行 {func.__name__}")
                logger.info(f"📝 参数: {params_info}")
                
                # 执行原函数
                result = func(*args, **kwargs)
                
                # 记录函数整体结束时间
                func_end_time = datetime.datetime.now()
                func_duration = (func_end_time - func_start_time).total_seconds()
                
                logger.info(f"✅ [{func_identifier}] {func.__name__} 执行成功")
                logger.info(f"⏱️  执行时间: {func_duration:.3f}秒")
                logger.info(f"📤 返回结果: {repr(result)}")
                logger.info("🎉 " + "="*50)
                
                return result
            
            except Exception as e:
                # 记录异常信息
                func_end_time = datetime.datetime.now()
                func_duration = (func_end_time - func_start_time).total_seconds()
                
                logger.error(f"❌ [{func_identifier}] {func.__name__} 执行失败")
                logger.error(f"⏱️  执行时间: {func_duration:.3f}秒")
                logger.error(f"🚫 异常信息: {str(e)}")
                logger.error(f"📍 异常类型: {type(e).__name__}")
                logger.error("💥 " + "="*50)
                
                # 重新抛出异常
                raise
            
            finally:
                # 恢复原来的say函数（如果存在）
                if hasattr(func, '__globals__'):
                    if original_say is not None:
                        func.__globals__['say'] = original_say
                    else:
                        func.__globals__.pop('say', None)
        
        return wrapper
    return decorator
    # }}}


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class MonkeyPatcher:
    """Monkey Patch 工具类"""
    
    def __init__(self):
        self.original_methods: Dict[str, Callable] = {}
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def add_logging_and_timing(self, cls: type, method_names: list = None):
        """
        为指定类的方法添加日志和性能计时功能
        
        Args:
            cls: 要打补丁的类
            method_names: 要增强的方法名列表，None表示所有公有方法
        """
        if method_names is None:
            # 获取所有公有方法（不以_开头的可调用属性）
            method_names = [
                name for name in dir(cls) 
                if not name.startswith('_') and callable(getattr(cls, name))
            ]
        
        for method_name in method_names:
            if hasattr(cls, method_name):
                self._patch_method(cls, method_name)
    
    def _patch_method(self, cls: type, method_name: str):
        """为单个方法打补丁"""
        # 保存原始方法
        original_method = getattr(cls, method_name)
        method_key = f"{cls.__name__}.{method_name}"
        self.original_methods[method_key] = original_method
        
        # 创建增强的方法
        @functools.wraps(original_method)
        def enhanced_method(self, *args, **kwargs):
            # 获取类名和方法名
            class_name = self.__class__.__name__
            instance_name = getattr(self, 'name', 'Unknown')
            
            # 使用方法级别的logger，而不是实例的logger
            method_logger = logging.getLogger(f"{class_name}")
            
            # 记录方法调用开始
            method_logger.info(f"🚀 [{class_name}({instance_name})] 开始执行 {method_name}")
            method_logger.info(f"📝 参数: args={args}, kwargs={kwargs}")
            
            # 记录开始时间
            start_time = time.time()
            
            try:
                # 调用原始方法
                result = original_method(self, *args, **kwargs)
                
                # 计算执行时间
                execution_time = time.time() - start_time
                
                # 记录成功结果
                method_logger.info(f"✅ [{class_name}({instance_name})] {method_name} 执行成功")
                method_logger.info(f"⏱️  执行时间: {execution_time:.3f}秒")
                method_logger.info(f"📤 返回结果: {result}")
                
                return result
                
            except Exception as e:
                # 计算执行时间（即使出错）
                execution_time = time.time() - start_time
                
                # 记录错误
                method_logger.error(f"❌ [{class_name}({instance_name})] {method_name} 执行失败")
                method_logger.error(f"⏱️  执行时间: {execution_time:.3f}秒")
                method_logger.error(f"🚨 错误信息: {str(e)}")
                
                # 重新抛出异常
                raise
        
        # 替换原方法
        setattr(cls, method_name, enhanced_method)
    
    def restore_method(self, cls: type, method_name: str):
        """恢复指定方法到原始状态"""
        method_key = f"{cls.__name__}.{method_name}"
        if method_key in self.original_methods:
            setattr(cls, method_name, self.original_methods[method_key])
            del self.original_methods[method_key]
            self.logger.info(f"🔄 已恢复 {method_key} 到原始状态")
    
    def restore_all(self):
        """恢复所有被修改的方法"""
        for method_key, original_method in list(self.original_methods.items()):
            cls_name, method_name = method_key.split('.', 1)
            # 这里简化处理，实际应用中可能需要更复杂的类查找逻辑
            print(f"请手动恢复 {method_key}")
        self.original_methods.clear()

# ================================
# 装饰器方式的 Monkey Patch
# ================================

def log_and_time(logger_name: str = None):
    """装饰器方式的日志和计时功能"""
    def decorator(func):
        logger = logging.getLogger(logger_name or func.__module__)
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            func_name = func.__name__
            logger.info(f"🎯 开始执行函数 {func_name}")
            logger.info(f"📝 参数: args={args[1:] if args else []}, kwargs={kwargs}")
            
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                logger.info(f"✅ {func_name} 执行成功，耗时 {execution_time:.3f}秒")
                logger.info(f"📤 返回: {result}")
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(f"❌ {func_name} 执行失败，耗时 {execution_time:.3f}秒")
                logger.error(f"🚨 错误: {str(e)}")
                raise
        
        return wrapper
    return decorator


class UNIT:
    d = '°'
    du = '°'
    degree = '°'


def safe_remove(path):
    try:
        if os.path.isfile(path):
            os.remove(path)
            print(f"文件 {path} 已删除")
        elif os.path.isdir(path):
            shutil.rmtree(path)
            print(f"目录 {path} 已删除")
        else:
            print(f"{path} 不存在")
    except Exception as e:
        print(f"删除 {path} 时出错: {e}")


def runs(cmds, num):
    from multiprocessing import Pool
    pool = Pool(processes = num)
    for cmd in cmds:
        pool.apply_async(os.system, (cmd,))
    pool.close()
    pool.join()


def llr2xyz(lon, lat, R=6371):
    pi = 3.141592654
    r = R*np.cos(lat/180*math.pi)
    z = R*np.sin(lat/180*math.pi)
    x = r*np.cos(lon/180*math.pi)
    y = r*np.sin(lon/180*math.pi)
    return x,y,z


def Rotate(a, theta, x, y, z):
    # {{{
    '''对坐标进行旋转操作'''

    theta = theta/180*math.pi

    if a == 1:
        rotate = np.array([[1, 0, 0], [0, np.cos(theta), -np.sin(theta)], [0, np.sin(theta), np.cos(theta)]])
    elif a == 2:
        rotate = np.array([[np.cos(theta), 0, np.sin(theta)], [0, 1, 0], [-np.sin(theta), 0, np.cos(theta)]])
    elif a == 3:
        rotate = np.array([[np.cos(theta), -np.sin(theta), 0], [np.sin(theta), np.cos(theta), 0], [0, 0, 1]])

    temp = np.dot(rotate,np.vstack((x.flatten(), y.flatten(), z.flatten())))
    xn = temp[0,:].reshape(x.shape)
    yn = temp[1,:].reshape(x.shape)
    zn = temp[2,:].reshape(x.shape)
    return xn, yn, zn
    # }}}


def local_xyz2lonlat(xj_1, yj_1, zj_1, lon0, lat0, alt0=0):
    # {{{
    xj = xj_1.flatten()
    yj = yj_1.flatten()
    zj = zj_1.flatten()

    x0, y0, z0 = llr2xyz(0, 0, R=6371)
    x = zj+x0+alt0
    y = xj
    z = yj

    x, y, z = Rotate(2, 0-lat0, x, y, z)
    x, y, z = Rotate(3, lon0, x, y, z)
    alt = np.sqrt(x**2+y**2+z**2) - 6371

    lon = np.arctan2(y,x)
    lat = np.arctan2(z,np.sqrt(x**2 + y**2))
    lon = lon / np.pi * 180
    lat = lat / np.pi * 180
    return lon.reshape(xj_1.shape),\
            lat.reshape(xj_1.shape),\
            alt.reshape(xj_1.shape),\
    # }}}


def get_range_id(lon, lat, z, i, j, k, xlim, ylim, zlim):
    # {{{
    id =\
         (lon.flatten()[i] >= xlim[0]) &\
         (lon.flatten()[j] >= xlim[0]) &\
         (lon.flatten()[k] >= xlim[0]) &\
         (lon.flatten()[i] <= xlim[1]) &\
         (lon.flatten()[j] <= xlim[1]) &\
         (lon.flatten()[k] <= xlim[1]) &\
         (lat.flatten()[i] >= ylim[0]) &\
         (lat.flatten()[j] >= ylim[0]) &\
         (lat.flatten()[k] >= ylim[0]) &\
         (lat.flatten()[i] <= ylim[1]) &\
         (lat.flatten()[j] <= ylim[1]) &\
         (lat.flatten()[k] <= ylim[1]) &\
         (z.flatten()[i] >= zlim[0]) &\
         (z.flatten()[j] >= zlim[0]) &\
         (z.flatten()[k] >= zlim[0]) &\
         (z.flatten()[i] <= zlim[1]) &\
         (z.flatten()[j] <= zlim[1]) &\
         (z.flatten()[k] <= zlim[1])
    return id
    # }}}


def triangle_area_3d(x1, x2, x3, y1, y2, y3, z1, z2, z3):
    # {{{
    
    # 计算每个三角形的顶点坐标
    A = np.column_stack((x1, y1, z1))
    B = np.column_stack((x2, y2, z2))
    C = np.column_stack((x3, y3, z3))

    # 计算向量 AB 和 AC
    AB = B - A
    AC = C - A

    # 计算叉积
    cross_product = np.cross(AB, AC)

    # 计算每个三角形的面积
    areas = 0.5 * np.linalg.norm(cross_product, axis=1)
    return areas
    # }}}


def area_by_xyz(x1, y1, x2, y2, x3, y3):
    return 0.5 * np.abs(x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2))


def geotiff2cogtiff(input_path, output_path):
    # {{{
    """
    将输入 TIFF 转换为 Cloud Optimized GeoTIFF (COG)

    参数：
    input_path (str): 输入 TIFF 文件路径
    output_path (str): 输出 COG 文件路径
    """
    from osgeo import gdal
    try:
        # 注册所有 GDAL 驱动
        gdal.AllRegister()

        # 打开原始文件
        src_ds = gdal.Open(input_path, gdal.GA_ReadOnly)
        if src_ds is None:
            raise RuntimeError(f"无法打开输入文件: {input_path}")

        # 获取原始波段信息
        band = src_ds.GetRasterBand(1)
        nodata = band.GetNoDataValue()
        dtype = gdal.GetDataTypeName(band.DataType)

        # 检查 NoData 值兼容性（针对 Byte 类型）
        if dtype == 'Byte' and nodata is not None:
            if nodata > 255 or nodata < 0:
                print(f"警告: NoData 值 {nodata} 超出 Byte 范围(0-255)，自动重置为 255")
                nodata = 255

        # COG 转换选项
        options = [
            'TILED=YES',               # 启用分块
            'BLOCKXSIZE=512',          # 分块宽度
            'BLOCKYSIZE=512',          # 分块高度
            'COMPRESS=LZW',            # 压缩算法
            'OVERVIEWS=AUTO',          # 自动生成金字塔
            'OVERVIEW_RESAMPLING=AVERAGE',  # 重采样方法
            'BIGTIFF=IF_NEEDED',       # 处理大文件
            'COPY_SRC_OVERVIEWS=YES',  # 复制现有金字塔（如果有）
            'NUM_THREADS=ALL_CPUS'     # 多线程加速
        ]

        # 执行转换
        print(f"开始转换: {input_path} -> {output_path}")
        cog_ds = gdal.Translate(
            output_path,
            src_ds,
            format='COG',
            creationOptions=options,
            noData=nodata
        )

        if cog_ds is None:
            raise RuntimeError("COG 转换失败")

        # 显式关闭数据集（重要！确保数据写入磁盘）
        cog_ds = None
        src_ds = None

        print("转换成功！")
        print(f"输出文件: {output_path}")

    except Exception as e:
        print(f"错误发生: {str(e)}")
        sys.exit(1)
    # }}}


def array2cogtiff(data_array, lats, lons, output_path, epsg=4326):
    # {{{
    """
    将二维数组 + 经纬度坐标存储为 COG
    
    参数：
    data_array : numpy.ndarray  二维数据矩阵（行对应纬度，列对应经度）
    lats       : numpy.ndarray  纬度数组（从北到南递减）
    lons       : numpy.ndarray  经度数组（从西到东递增）
    output_path: str            输出文件路径
    epsg       : int            坐标系 EPSG 代码（默认 WGS84）
    """
    from osgeo import gdal, osr
    try:
        # 验证输入数据
        assert data_array.ndim == 2, "数据必须是二维数组"
        assert len(lats) == data_array.shape[0], "纬度维度不匹配"
        assert len(lons) == data_array.shape[1], "经度维度不匹配"

        # 获取栅格尺寸
        rows, cols = data_array.shape
        
        # 计算地理变换参数 (GeoTransform)
        # 格式: (左上角经度, 经度分辨率, 旋转, 左上角纬度, 旋转, 纬度分辨率)
        lon_res = (lons[-1] - lons[0]) / (len(lons) - 1)
        lat_res = (lats[-1] - lats[0]) / (len(lats) - 1)
        geotransform = (
            lons[0] - lon_res/2,  # 左上角经度 (像元中心对齐)
            lon_res,              # 经度方向分辨率
            0,                    # 旋转参数（通常为0）
            lats[0] - lat_res/2,  # 左上角纬度
            0,                    # 旋转参数（通常为0）
            lat_res               # 纬度方向分辨率（通常为负）
        )

        # 创建内存数据集
        driver = gdal.GetDriverByName('MEM')  # 先在内存中创建
        ds = driver.Create('', cols, rows, 1, gdal.GDT_Float32)

        # 设置地理参考
        ds.SetGeoTransform(geotransform)
        srs = osr.SpatialReference()
        srs.ImportFromEPSG(epsg)
        ds.SetProjection(srs.ExportToWkt())

        # 写入数据
        band = ds.GetRasterBand(1)
        band.WriteArray(data_array)
        band.FlushCache()

        # COG 转换选项
        cog_options = [
            'TILED=YES',
            'BLOCKXSIZE=512', 
            'BLOCKYSIZE=512',
            'COMPRESS=LZW',
            'OVERVIEWS=AUTO',
            'OVERVIEW_RESAMPLING=AVERAGE',
            'BIGTIFF=IF_NEEDED'
        ]

        # 转换为 COG
        driver = gdal.GetDriverByName('COG')
        cog_ds = driver.CreateCopy(output_path, ds, options=cog_options)
        
        # 显式释放资源
        cog_ds = None
        ds = None
        
        print(f"成功生成 COG: {output_path}")

    except Exception as e:
        print(f"生成 COG 失败: {str(e)}")
        raise
    # }}}

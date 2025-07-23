#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import time
import os
import sys
from ppadb.client import Client as AdbClient
from ppadb.device import Device
import cv2
import numpy as np
from PIL import Image
import io
import json
import threading
import socket

class AndroidController:
    """MacBook Air 控制安卓手机的主控制器"""
    
    def __init__(self, host="127.0.0.1", port=5037):
        self.host = host
        self.port = port
        self.client = None
        self.device = None
        self.is_connected = False
        self.screenshot_thread = None
        self.is_monitoring = False
        
    def connect(self):
        """连接到ADB服务器并获取设备"""
        try:
            # 启动ADB服务器
            subprocess.run(["adb", "start-server"], check=True)
            
            # 连接到ADB客户端
            self.client = AdbClient(host=self.host, port=self.port)
            
            # 获取设备列表
            devices = self.client.devices()
            if not devices:
                print("❌ 没有找到连接的安卓设备")
                print("请确保:")
                print("1. 手机已通过USB连接到电脑")
                print("2. 已启用USB调试模式")
                print("3. 已信任此计算机")
                return False
            
            # 选择第一个设备
            self.device = devices[0]
            self.is_connected = True
            
            print(f"✅ 已连接到设备: {self.device.serial}")
            print(f"📱 设备型号: {self.get_device_info()}")
            
            return True
            
        except subprocess.CalledProcessError:
            print("❌ 无法启动ADB服务器")
            print("请确保已安装Android SDK并配置好环境变量")
            return False
        except Exception as e:
            print(f"❌ 连接失败: {str(e)}")
            return False
    
    def get_device_info(self):
        """获取设备信息"""
        if not self.device:
            return "未连接"
        
        try:
            brand = self.device.shell("getprop ro.product.brand").strip()
            model = self.device.shell("getprop ro.product.model").strip()
            version = self.device.shell("getprop ro.build.version.release").strip()
            return f"{brand} {model} (Android {version})"
        except:
            return "未知设备"
    
    def take_screenshot(self):
        """截取屏幕截图"""
        if not self.device:
            return None
        
        try:
            # 使用ADB获取屏幕截图
            screenshot = self.device.screencap()
            # 转换为PIL Image
            image = Image.open(io.BytesIO(screenshot))
            # 转换为OpenCV格式
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            return cv_image
        except Exception as e:
            print(f"❌ 截图失败: {str(e)}")
            return None
    
    def tap(self, x, y):
        """点击屏幕指定坐标"""
        if not self.device:
            return False
        
        try:
            self.device.shell(f"input tap {x} {y}")
            print(f"🖱️ 点击坐标: ({x}, {y})")
            return True
        except Exception as e:
            print(f"❌ 点击失败: {str(e)}")
            return False
    
    def swipe(self, x1, y1, x2, y2, duration=500):
        """滑动手势"""
        if not self.device:
            return False
        
        try:
            self.device.shell(f"input swipe {x1} {y1} {x2} {y2} {duration}")
            print(f"👆 滑动: ({x1}, {y1}) -> ({x2}, {y2})")
            return True
        except Exception as e:
            print(f"❌ 滑动失败: {str(e)}")
            return False
    
    def input_text(self, text):
        """输入文本"""
        if not self.device:
            return False
        
        try:
            # 转义特殊字符
            escaped_text = text.replace(' ', '%s').replace("'", "\\'")
            self.device.shell(f"input text '{escaped_text}'")
            print(f"⌨️ 输入文本: {text}")
            return True
        except Exception as e:
            print(f"❌ 输入失败: {str(e)}")
            return False
    
    def press_key(self, keycode):
        """按键操作"""
        if not self.device:
            return False
        
        try:
            self.device.shell(f"input keyevent {keycode}")
            print(f"🔘 按键: {keycode}")
            return True
        except Exception as e:
            print(f"❌ 按键失败: {str(e)}")
            return False
    
    def press_home(self):
        """按Home键"""
        return self.press_key(3)
    
    def press_back(self):
        """按返回键"""
        return self.press_key(4)
    
    def press_menu(self):
        """按菜单键"""
        return self.press_key(82)
    
    def launch_app(self, package_name):
        """启动应用"""
        if not self.device:
            return False
        
        try:
            self.device.shell(f"monkey -p {package_name} -c android.intent.category.LAUNCHER 1")
            print(f"🚀 启动应用: {package_name}")
            return True
        except Exception as e:
            print(f"❌ 启动应用失败: {str(e)}")
            return False
    
    def get_current_activity(self):
        """获取当前Activity"""
        if not self.device:
            return None
        
        try:
            result = self.device.shell("dumpsys window windows | grep -E 'mCurrentFocus|mFocusedApp'")
            return result.strip()
        except Exception as e:
            print(f"❌ 获取当前Activity失败: {str(e)}")
            return None
    
    def get_installed_apps(self):
        """获取已安装应用列表"""
        if not self.device:
            return []
        
        try:
            result = self.device.shell("pm list packages")
            packages = []
            for line in result.split('\n'):
                if line.startswith('package:'):
                    packages.append(line.replace('package:', '').strip())
            return packages
        except Exception as e:
            print(f"❌ 获取应用列表失败: {str(e)}")
            return []
    
    def start_scrcpy(self):
        """启动scrcpy进行屏幕镜像"""
        try:
            # 检查scrcpy是否安装
            subprocess.run(["which", "scrcpy"], check=True, capture_output=True)
            
            # 启动scrcpy
            print("🖥️ 启动scrcpy屏幕镜像...")
            subprocess.Popen(["scrcpy", "--window-title", "Android Remote Control"])
            return True
        except subprocess.CalledProcessError:
            print("❌ scrcpy未安装")
            print("请使用 brew install scrcpy 安装")
            return False
        except Exception as e:
            print(f"❌ 启动scrcpy失败: {str(e)}")
            return False
    
    def find_element_by_text(self, text):
        """通过文本查找元素"""
        if not self.device:
            return None
        
        try:
            # 获取UI hierarchy
            ui_xml = self.device.shell("uiautomator dump /dev/stdout")
            
            # 简单的文本搜索（实际应用中可能需要更复杂的XML解析）
            if text in ui_xml:
                print(f"🔍 找到包含文本的元素: {text}")
                return True
            else:
                print(f"❌ 未找到包含文本的元素: {text}")
                return False
        except Exception as e:
            print(f"❌ 查找元素失败: {str(e)}")
            return False
    
    def disconnect(self):
        """断开连接"""
        if self.is_monitoring:
            self.is_monitoring = False
            if self.screenshot_thread:
                self.screenshot_thread.join()
        
        self.is_connected = False
        self.device = None
        self.client = None
        print("🔌 已断开连接")
    
    def get_screen_size(self):
        """获取屏幕尺寸"""
        if not self.device:
            return None
        
        try:
            result = self.device.shell("wm size")
            # 解析类似 "Physical size: 1080x2340" 的输出
            size_line = result.split('\n')[0]
            if 'x' in size_line:
                dimensions = size_line.split(':')[-1].strip()
                width, height = map(int, dimensions.split('x'))
                return (width, height)
        except Exception as e:
            print(f"❌ 获取屏幕尺寸失败: {str(e)}")
        
        return None
    
    def start_monitoring(self):
        """开始监控屏幕"""
        if not self.device:
            return False
        
        self.is_monitoring = True
        self.screenshot_thread = threading.Thread(target=self._screenshot_loop)
        self.screenshot_thread.daemon = True
        self.screenshot_thread.start()
        
        print("👀 开始屏幕监控...")
        return True
    
    def _screenshot_loop(self):
        """屏幕截图循环"""
        while self.is_monitoring:
            screenshot = self.take_screenshot()
            if screenshot is not None:
                # 这里可以添加图像处理逻辑
                # 例如：保存到文件、发送到web界面等
                pass
            time.sleep(0.5)  # 每0.5秒截图一次 
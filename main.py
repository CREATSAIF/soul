#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import time
import threading
import subprocess
from android_controller import AndroidController

class AndroidRemoteControl:
    """MacBook Air 安卓手机远程控制主程序"""
    
    def __init__(self):
        self.controller = AndroidController()
        self.running = False
        
    def show_menu(self):
        """显示主菜单"""
        print("\n" + "="*50)
        print("🚀 MacBook Air 安卓手机远程控制器")
        print("="*50)
        print("1. 连接设备")
        print("2. 启动屏幕镜像 (scrcpy)")
        print("3. 设备信息")
        print("4. 基本控制")
        print("5. 应用管理")
        print("6. 自动化操作")
        print("7. 断开连接")
        print("0. 退出程序")
        print("="*50)
        
    def connect_device(self):
        """连接设备"""
        print("\n🔄 正在连接设备...")
        if self.controller.connect():
            print("✅ 设备连接成功!")
            return True
        else:
            print("❌ 设备连接失败!")
            return False
    
    def start_screen_mirror(self):
        """启动屏幕镜像"""
        if not self.controller.is_connected:
            print("❌ 请先连接设备")
            return
        
        print("\n🖥️ 启动屏幕镜像...")
        if self.controller.start_scrcpy():
            print("✅ 屏幕镜像已启动!")
            print("💡 您现在可以在新窗口中看到手机屏幕并进行控制")
        else:
            print("❌ 启动屏幕镜像失败!")
            print("请确保已安装 scrcpy: brew install scrcpy")
    
    def show_device_info(self):
        """显示设备信息"""
        if not self.controller.is_connected:
            print("❌ 请先连接设备")
            return
        
        print("\n📱 设备信息:")
        print(f"设备型号: {self.controller.get_device_info()}")
        print(f"序列号: {self.controller.device.serial}")
        
        screen_size = self.controller.get_screen_size()
        if screen_size:
            print(f"屏幕尺寸: {screen_size[0]}x{screen_size[1]}")
        
        current_activity = self.controller.get_current_activity()
        if current_activity:
            print(f"当前Activity: {current_activity}")
    
    def basic_control_menu(self):
        """基本控制菜单"""
        if not self.controller.is_connected:
            print("❌ 请先连接设备")
            return
        
        while True:
            print("\n🎮 基本控制:")
            print("1. 点击坐标")
            print("2. 滑动手势")
            print("3. 输入文本")
            print("4. 按Home键")
            print("5. 按返回键")
            print("6. 按菜单键")
            print("7. 截取屏幕")
            print("0. 返回主菜单")
            
            choice = input("\n请选择操作: ").strip()
            
            if choice == '1':
                self.click_coordinate()
            elif choice == '2':
                self.swipe_gesture()
            elif choice == '3':
                self.input_text()
            elif choice == '4':
                self.controller.press_home()
            elif choice == '5':
                self.controller.press_back()
            elif choice == '6':
                self.controller.press_menu()
            elif choice == '7':
                self.take_screenshot()
            elif choice == '0':
                break
            else:
                print("❌ 无效选择，请重新输入")
    
    def click_coordinate(self):
        """点击坐标"""
        try:
            x = int(input("请输入X坐标: "))
            y = int(input("请输入Y坐标: "))
            self.controller.tap(x, y)
        except ValueError:
            print("❌ 请输入有效的数字")
    
    def swipe_gesture(self):
        """滑动手势"""
        try:
            x1 = int(input("请输入起始X坐标: "))
            y1 = int(input("请输入起始Y坐标: "))
            x2 = int(input("请输入结束X坐标: "))
            y2 = int(input("请输入结束Y坐标: "))
            duration = int(input("请输入滑动时间(毫秒，默认500): ") or "500")
            self.controller.swipe(x1, y1, x2, y2, duration)
        except ValueError:
            print("❌ 请输入有效的数字")
    
    def input_text(self):
        """输入文本"""
        text = input("请输入要发送的文本: ")
        if text:
            self.controller.input_text(text)
    
    def take_screenshot(self):
        """截取屏幕"""
        print("📸 正在截取屏幕...")
        screenshot = self.controller.take_screenshot()
        if screenshot is not None:
            import cv2
            filename = f"screenshot_{int(time.time())}.png"
            cv2.imwrite(filename, screenshot)
            print(f"✅ 截图已保存为: {filename}")
        else:
            print("❌ 截图失败")
    
    def app_management_menu(self):
        """应用管理菜单"""
        if not self.controller.is_connected:
            print("❌ 请先连接设备")
            return
        
        while True:
            print("\n📱 应用管理:")
            print("1. 启动应用")
            print("2. 查看已安装应用")
            print("3. 查看当前应用")
            print("0. 返回主菜单")
            
            choice = input("\n请选择操作: ").strip()
            
            if choice == '1':
                self.launch_app()
            elif choice == '2':
                self.list_installed_apps()
            elif choice == '3':
                self.show_current_app()
            elif choice == '0':
                break
            else:
                print("❌ 无效选择，请重新输入")
    
    def launch_app(self):
        """启动应用"""
        package_name = input("请输入应用包名 (例如: com.android.settings): ")
        if package_name:
            self.controller.launch_app(package_name)
    
    def list_installed_apps(self):
        """列出已安装应用"""
        print("\n📦 正在获取应用列表...")
        apps = self.controller.get_installed_apps()
        if apps:
            print(f"共找到 {len(apps)} 个应用:")
            for i, app in enumerate(apps[:20]):  # 只显示前20个
                print(f"{i+1}. {app}")
            if len(apps) > 20:
                print(f"... 还有 {len(apps) - 20} 个应用")
        else:
            print("❌ 获取应用列表失败")
    
    def show_current_app(self):
        """显示当前应用"""
        activity = self.controller.get_current_activity()
        if activity:
            print(f"当前Activity: {activity}")
        else:
            print("❌ 获取当前应用失败")
    
    def automation_menu(self):
        """自动化操作菜单"""
        if not self.controller.is_connected:
            print("❌ 请先连接设备")
            return
        
        while True:
            print("\n🤖 自动化操作:")
            print("1. 打开设置应用")
            print("2. 自动滚动页面")
            print("3. 查找文本元素")
            print("4. 批量点击操作")
            print("0. 返回主菜单")
            
            choice = input("\n请选择操作: ").strip()
            
            if choice == '1':
                self.open_settings()
            elif choice == '2':
                self.auto_scroll()
            elif choice == '3':
                self.find_text_element()
            elif choice == '4':
                self.batch_click()
            elif choice == '0':
                break
            else:
                print("❌ 无效选择，请重新输入")
    
    def open_settings(self):
        """打开设置应用"""
        print("🔧 正在打开设置应用...")
        self.controller.launch_app("com.android.settings")
    
    def auto_scroll(self):
        """自动滚动页面"""
        try:
            times = int(input("请输入滚动次数: ") or "5")
            screen_size = self.controller.get_screen_size()
            if screen_size:
                x = screen_size[0] // 2
                y1 = screen_size[1] * 3 // 4
                y2 = screen_size[1] // 4
                
                print(f"🔄 开始自动滚动 {times} 次...")
                for i in range(times):
                    self.controller.swipe(x, y1, x, y2, 500)
                    time.sleep(1)
                    print(f"已完成第 {i+1} 次滚动")
                print("✅ 自动滚动完成")
            else:
                print("❌ 无法获取屏幕尺寸")
        except ValueError:
            print("❌ 请输入有效的数字")
    
    def find_text_element(self):
        """查找文本元素"""
        text = input("请输入要查找的文本: ")
        if text:
            self.controller.find_element_by_text(text)
    
    def batch_click(self):
        """批量点击操作"""
        try:
            count = int(input("请输入点击次数: ") or "5")
            x = int(input("请输入X坐标: "))
            y = int(input("请输入Y坐标: "))
            interval = float(input("请输入点击间隔(秒): ") or "1.0")
            
            print(f"🖱️ 开始批量点击 {count} 次...")
            for i in range(count):
                self.controller.tap(x, y)
                time.sleep(interval)
                print(f"已完成第 {i+1} 次点击")
            print("✅ 批量点击完成")
        except ValueError:
            print("❌ 请输入有效的数字")
    
    def run(self):
        """运行主程序"""
        print("🚀 欢迎使用 MacBook Air 安卓手机远程控制器!")
        print("💡 请确保您的安卓手机已启用USB调试模式")
        
        self.running = True
        
        while self.running:
            self.show_menu()
            choice = input("\n请选择操作: ").strip()
            
            if choice == '1':
                self.connect_device()
            elif choice == '2':
                self.start_screen_mirror()
            elif choice == '3':
                self.show_device_info()
            elif choice == '4':
                self.basic_control_menu()
            elif choice == '5':
                self.app_management_menu()
            elif choice == '6':
                self.automation_menu()
            elif choice == '7':
                self.controller.disconnect()
            elif choice == '0':
                self.running = False
                if self.controller.is_connected:
                    self.controller.disconnect()
                print("👋 再见!")
            else:
                print("❌ 无效选择，请重新输入")
    
    def check_dependencies(self):
        """检查依赖项"""
        print("🔍 检查系统依赖项...")
        
        # 检查ADB
        try:
            subprocess.run(["adb", "version"], capture_output=True, check=True)
            print("✅ ADB 已安装")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ ADB 未安装")
            print("请安装 Android SDK 或使用 brew install android-platform-tools")
            return False
        
        # 检查scrcpy
        try:
            subprocess.run(["which", "scrcpy"], capture_output=True, check=True)
            print("✅ scrcpy 已安装")
        except subprocess.CalledProcessError:
            print("⚠️ scrcpy 未安装 (可选)")
            print("建议安装以获得更好的屏幕镜像体验: brew install scrcpy")
        
        return True

def main():
    """主函数"""
    app = AndroidRemoteControl()
    
    # 检查依赖项
    if not app.check_dependencies():
        print("❌ 系统依赖项检查失败，请安装必要的工具后重试")
        sys.exit(1)
    
    # 运行主程序
    try:
        app.run()
    except KeyboardInterrupt:
        print("\n\n⏹️ 程序被用户中断")
        if app.controller.is_connected:
            app.controller.disconnect()
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 程序运行出错: {str(e)}")
        if app.controller.is_connected:
            app.controller.disconnect()
        sys.exit(1)

if __name__ == "__main__":
    main() 
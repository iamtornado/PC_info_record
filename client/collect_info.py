#!/usr/bin/env python3
"""
Windows 系统信息采集客户端
==========================

功能说明
--------
自动收集 Windows 计算机的硬件和系统信息，并通过 API 提交到 PC 信息记录系统。

系统要求
--------
- Windows 7/10/11 或 Windows Server
- Python 3.11+
- 管理员权限（推荐，用于获取完整硬件信息）

安装依赖
--------
pip install -r requirements.txt

配置方法
--------
方式1: 编辑脚本中的 SERVER_URL 变量（第31行）
    SERVER_URL = 'http://your-server:8000'

方式2: 设置环境变量
    set SERVER_URL=http://your-server:8000
    python collect_info.py

方式3: 使用 .env 文件（可选）
    创建 .env 文件并添加：
    SERVER_URL=http://your-server:8000

使用方法
--------
# 手动运行（需要管理员权限）
python collect_info.py

# 或者以管理员身份运行
右键 -> 以管理员身份运行

# 定时任务
使用 Windows 任务计划程序设置定时运行

收集的信息
----------
- 基本信息: 资产编码、SN序列号、设备型号、设备类型
- 硬件信息: CPU型号、内存大小
- 系统信息: 操作系统版本
- 用户信息: 用户名、计算机名
- 日志信息: 执行日志、错误日志

注意事项
--------
1. 需要管理员权限才能获取完整的硬件信息
2. 确保网络连接正常，能够访问服务器
3. 首次运行前请检查防火墙设置
4. 数据会自动保存到 computer_info.json（用于调试）

故障排除
--------
1. 权限不足: 以管理员身份运行
2. 网络连接失败: 检查 SERVER_URL 和网络连接
3. 依赖包缺失: pip install -r requirements.txt
4. WMI访问失败: 检查 Windows Management Instrumentation 服务

API 端点
--------
POST http://your-server:8000/api/computers/

示例
----
python collect_info.py
"""

import os
import sys
import json
import socket
import platform
import subprocess
import requests
from datetime import datetime
from dotenv import load_dotenv

try:
    import psutil
    import wmi
except ImportError:
    print("请先安装依赖: pip install -r requirements.txt")
    sys.exit(1)

# 加载环境变量
load_dotenv()

class SystemInfoCollector:
    """系统信息采集器"""
    
    def __init__(self):
        self.server_url = os.getenv('SERVER_URL', 'http://localhost:8000')
        self.api_endpoint = f"{self.server_url}/api/computers/"
        
    def get_system_info(self):
        """获取系统基本信息"""
        return {
            'os_version': f"{platform.system()} {platform.release()} {platform.version()}",
            'os_internal_version': platform.version(),
            'hostname': socket.gethostname(),
            'architecture': platform.architecture()[0],
        }
    
    def get_cpu_info(self):
        """获取CPU信息"""
        try:
            c = wmi.WMI()
            cpu = c.Win32_Processor()[0]
            return {
                'cpu_model': cpu.Name.strip(),
                'cpu_cores': cpu.NumberOfCores,
                'cpu_logical_processors': cpu.NumberOfLogicalProcessors,
                'cpu_max_clock_speed': cpu.MaxClockSpeed,
            }
        except Exception as e:
            print(f"获取CPU信息失败: {e}")
            return {
                'cpu_model': 'Unknown',
                'cpu_cores': psutil.cpu_count(logical=False),
                'cpu_logical_processors': psutil.cpu_count(logical=True),
                'cpu_max_clock_speed': 0,
            }
    
    def get_memory_info(self):
        """获取内存信息"""
        memory = psutil.virtual_memory()
        return {
            'memory_size': round(memory.total / (1024**3)),  # 转换为GB
            'memory_available': round(memory.available / (1024**3)),
            'memory_used_percent': memory.percent,
        }
    
    def get_disk_info(self):
        """获取磁盘信息"""
        disks = []
        for partition in psutil.disk_partitions():
            try:
                partition_usage = psutil.disk_usage(partition.mountpoint)
                disks.append({
                    'device': partition.device,
                    'mountpoint': partition.mountpoint,
                    'fstype': partition.fstype,
                    'total_size': round(partition_usage.total / (1024**3)),
                    'used_size': round(partition_usage.used / (1024**3)),
                    'free_size': round(partition_usage.free / (1024**3)),
                })
            except PermissionError:
                continue
        return disks
    
    def get_network_info(self):
        """获取网络信息"""
        network_info = []
        for interface, addrs in psutil.net_if_addrs().items():
            for addr in addrs:
                if addr.family == socket.AF_INET:
                    network_info.append({
                        'interface': interface,
                        'ip_address': addr.address,
                        'netmask': addr.netmask,
                    })
        return network_info
    
    def get_user_info(self):
        """获取当前用户信息"""
        try:
            # 获取当前登录用户
            current_user = os.getenv('USERNAME', os.getenv('USER', 'Unknown'))
            
            # 尝试获取域用户信息
            domain_user = None
            try:
                result = subprocess.run(['whoami'], capture_output=True, text=True, shell=True)
                if result.returncode == 0:
                    domain_user = result.stdout.strip()
            except:
                pass
            
            return {
                'current_user': current_user,
                'domain_user': domain_user,
                'user_domain': os.getenv('USERDOMAIN', ''),
            }
        except Exception as e:
            print(f"获取用户信息失败: {e}")
            return {
                'current_user': 'Unknown',
                'domain_user': None,
                'user_domain': '',
            }
    
    def get_hardware_info(self):
        """获取硬件信息"""
        try:
            c = wmi.WMI()
            
            # 获取主板信息
            motherboard = c.Win32_BaseBoard()[0]
            
            # 获取BIOS信息
            bios = c.Win32_BIOS()[0]
            
            return {
                'motherboard_manufacturer': motherboard.Manufacturer,
                'motherboard_product': motherboard.Product,
                'motherboard_version': motherboard.Version,
                'bios_manufacturer': bios.Manufacturer,
                'bios_version': bios.SMBIOSBIOSVersion,
                'bios_release_date': bios.ReleaseDate,
            }
        except Exception as e:
            print(f"获取硬件信息失败: {e}")
            return {
                'motherboard_manufacturer': 'Unknown',
                'motherboard_product': 'Unknown',
                'motherboard_version': 'Unknown',
                'bios_manufacturer': 'Unknown',
                'bios_version': 'Unknown',
                'bios_release_date': 'Unknown',
            }
    
    def get_asset_info(self):
        """获取资产信息（需要手动配置或从其他系统获取）"""
        # 这里可以从配置文件、注册表或其他系统获取资产信息
        # 暂时返回默认值，实际使用时需要根据实际情况修改
        return {
            'asset_code': os.getenv('ASSET_CODE', f"PC-{socket.gethostname()}"),
            'sn_code': self.get_serial_number(),
            'model': self.get_computer_model(),
            'device_type': 'Desktop',  # 或 'Laptop'
        }
    
    def get_serial_number(self):
        """获取序列号"""
        try:
            c = wmi.WMI()
            bios = c.Win32_BIOS()[0]
            return bios.SerialNumber
        except:
            return 'Unknown'
    
    def get_computer_model(self):
        """获取计算机型号"""
        try:
            c = wmi.WMI()
            computer_system = c.Win32_ComputerSystem()[0]
            return computer_system.Model
        except:
            return 'Unknown'
    
    def get_user_name_info(self):
        """获取用户名和计算机名"""
        try:
            user_name = os.getenv('USERNAME', os.getenv('USER', 'Unknown'))
            computer_name = socket.gethostname()
            
            return {
                'user_name': user_name,
                'computer_name': computer_name,
            }
        except Exception as e:
            print(f"获取用户名信息失败: {e}")
            return {
                'user_name': 'Unknown',
                'computer_name': 'Unknown',
            }
    
    def generate_execution_log(self, system_info, cpu_info, memory_info, disk_info, network_info, user_info, hardware_info):
        """生成执行日志"""
        log_lines = []
        log_lines.append("=== 系统信息收集日志 ===")
        log_lines.append(f"收集时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        log_lines.append(f"主机名: {system_info.get('hostname', 'Unknown')}")
        log_lines.append(f"架构: {system_info.get('architecture', 'Unknown')}")
        log_lines.append(f"CPU: {cpu_info.get('cpu_model', 'Unknown')} ({cpu_info.get('cpu_cores', 0)} 核)")
        log_lines.append(f"内存: {memory_info.get('memory_size', 0)} GB")
        log_lines.append(f"磁盘信息: {len(disk_info)} 个磁盘")
        log_lines.append(f"网络接口: {len(network_info)} 个")
        log_lines.append(f"当前用户: {user_info.get('current_user', 'Unknown')}")
        log_lines.append(f"域用户: {user_info.get('domain_user', 'N/A')}")
        log_lines.append("=== 收集完成 ===")
        return "\n".join(log_lines)
    
    def collect_all_info(self):
        """收集所有信息"""
        print("开始收集系统信息...")
        
        error_messages = []
        
        # 收集各类信息
        system_info = self.get_system_info()
        cpu_info = self.get_cpu_info()
        memory_info = self.get_memory_info()
        disk_info = self.get_disk_info()
        network_info = self.get_network_info()
        user_info = self.get_user_info()
        hardware_info = self.get_hardware_info()
        asset_info = self.get_asset_info()
        user_name_info = self.get_user_name_info()
        
        # 生成执行日志
        execution_log = self.generate_execution_log(
            system_info, cpu_info, memory_info, disk_info, 
            network_info, user_info, hardware_info
        )
        
        # 组装 API 数据（只包含服务器需要的字段）
        computer_data = {
            # 基本信息
            'asset_code': asset_info['asset_code'],
            'sn_code': asset_info['sn_code'],
            'model': asset_info['model'],
            'device_type': asset_info['device_type'],
            
            # 硬件信息
            'cpu_model': cpu_info['cpu_model'],
            'memory_size': memory_info['memory_size'],
            
            # 系统信息
            'os_version': system_info['os_version'],
            'os_internal_version': system_info['os_internal_version'],
            
            # 用户信息
            'user_name': user_name_info['user_name'],
            'computer_name': user_name_info['computer_name'],
            
            # 日志信息
            'execution_log': execution_log,
            'log_size': len(execution_log),
            'error_log': "\n".join(error_messages) if error_messages else "",
            'has_errors': len(error_messages) > 0,
            
            # 系统字段
            'uploader': 'Robot',
        }
        
        # 保存详细信息到本地（用于调试）
        debug_data = {
            **computer_data,
            'extra_info': {
                'hostname': system_info['hostname'],
                'architecture': system_info['architecture'],
                'cpu_cores': cpu_info['cpu_cores'],
                'cpu_logical_processors': cpu_info['cpu_logical_processors'],
                'memory_available': memory_info['memory_available'],
                'memory_used_percent': memory_info['memory_used_percent'],
                'disk_info': disk_info,
                'network_info': network_info,
                'user_info': user_info,
                'hardware_info': hardware_info,
                'collect_time': datetime.now().isoformat(),
            }
        }
        
        print("系统信息收集完成")
        
        # 返回debug_data用于本地保存，但发送到服务器时只用computer_data
        return debug_data, computer_data
    
    def send_to_server(self, data):
        """发送数据到服务器"""
        try:
            print(f"正在发送数据到服务器: {self.api_endpoint}")
            
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'PC-Info-Collector/1.0'
            }
            
            response = requests.post(
                self.api_endpoint,
                json=data,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 201:
                print("数据发送成功!")
                print(f"服务器响应: {response.json()}")
                return True
            else:
                print(f"数据发送失败! 状态码: {response.status_code}")
                print(f"错误信息: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"网络请求失败: {e}")
            return False
        except Exception as e:
            print(f"发送数据时发生错误: {e}")
            return False
    
    def save_to_file(self, data, filename='computer_info.json'):
        """保存数据到本地文件（用于调试）"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"数据已保存到文件: {filename}")
        except Exception as e:
            print(f"保存文件失败: {e}")
    
    def run(self):
        """运行采集程序"""
        print("=" * 50)
        print("PC信息采集客户端")
        print("=" * 50)
        
        # 收集信息（返回两份数据：详细数据和API数据）
        debug_data, api_data = self.collect_all_info()
        
        # 显示收集到的信息摘要
        print("\n收集到的信息摘要:")
        print(f"资产编码: {api_data['asset_code']}")
        print(f"序列号: {api_data['sn_code']}")
        print(f"用户名: {api_data['user_name']}")
        print(f"计算机名: {api_data['computer_name']}")
        print(f"型号: {api_data['model']}")
        print(f"CPU: {api_data['cpu_model']}")
        print(f"内存: {api_data['memory_size']}GB")
        print(f"操作系统: {api_data['os_version']}")
        print(f"有错误: {'是' if api_data['has_errors'] else '否'}")
        
        # 保存详细信息到本地文件（用于调试）
        self.save_to_file(debug_data)
        
        # 发送API数据到服务器
        success = self.send_to_server(api_data)
        
        if success:
            print("\n✅ 信息采集和上传完成!")
        else:
            print("\n❌ 信息上传失败，请检查网络连接和服务器状态")
            print("数据已保存到本地文件，可以稍后手动上传")
        
        return success


def main():
    """主函数"""
    collector = SystemInfoCollector()
    collector.run()


if __name__ == '__main__':
    main()

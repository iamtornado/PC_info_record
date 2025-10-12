#!/usr/bin/env python
"""
LDAP/Active Directory连接测试脚本
用于验证LDAP配置是否正确
"""

import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pc_info_record.settings')
django.setup()

from django.contrib.auth import authenticate
from django_auth_ldap.backend import LDAPBackend
from django.conf import settings
import ldap


def print_header(text):
    """打印带格式的标题"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def test_ldap_settings():
    """测试LDAP配置"""
    print_header("检查LDAP配置")
    
    print(f"✓ LDAP服务器: {settings.AUTH_LDAP_SERVER_URI}")
    print(f"✓ 绑定DN: {settings.AUTH_LDAP_BIND_DN}")
    print(f"✓ 用户搜索基准DN: {settings.AUTH_LDAP_USER_SEARCH.base_dn}")
    print(f"✓ 搜索过滤器: {settings.AUTH_LDAP_USER_SEARCH.filterstr}")
    print(f"✓ 认证后端: {settings.AUTHENTICATION_BACKENDS}")


def test_ldap_connection():
    """测试LDAP服务器连接"""
    print_header("测试LDAP服务器连接")
    
    try:
        # 创建LDAP连接
        conn = ldap.initialize(settings.AUTH_LDAP_SERVER_URI)
        conn.set_option(ldap.OPT_REFERRALS, 0)
        conn.set_option(ldap.OPT_NETWORK_TIMEOUT, 10.0)
        
        print(f"✓ 连接到LDAP服务器: {settings.AUTH_LDAP_SERVER_URI}")
        
        # 尝试绑定
        conn.simple_bind_s(
            settings.AUTH_LDAP_BIND_DN,
            settings.AUTH_LDAP_BIND_PASSWORD
        )
        print(f"✓ 服务账号绑定成功")
        
        # 测试搜索
        base_dn = settings.AUTH_LDAP_USER_SEARCH.base_dn
        search_filter = "(objectClass=person)"
        
        result = conn.search_s(
            base_dn,
            ldap.SCOPE_SUBTREE,
            search_filter,
            ['sAMAccountName', 'cn', 'mail']
        )
        
        print(f"✓ 搜索测试成功，找到 {len(result)} 个用户对象")
        
        conn.unbind_s()
        return True
        
    except ldap.INVALID_CREDENTIALS:
        print("✗ 错误: 服务账号用户名或密码错误")
        return False
    except ldap.SERVER_DOWN:
        print(f"✗ 错误: 无法连接到LDAP服务器 {settings.AUTH_LDAP_SERVER_URI}")
        print("  请检查:")
        print("  1. 服务器地址是否正确")
        print("  2. 网络连接是否正常")
        print("  3. 防火墙端口389是否开放")
        return False
    except ldap.NO_SUCH_OBJECT:
        print(f"✗ 错误: 搜索基准DN不存在: {base_dn}")
        print("  请检查LDAP_USER_BASE_DN配置")
        return False
    except Exception as e:
        print(f"✗ 连接错误: {e}")
        return False


def test_user_search(username):
    """测试用户搜索"""
    print_header(f"测试用户搜索: {username}")
    
    try:
        conn = ldap.initialize(settings.AUTH_LDAP_SERVER_URI)
        conn.set_option(ldap.OPT_REFERRALS, 0)
        conn.simple_bind_s(
            settings.AUTH_LDAP_BIND_DN,
            settings.AUTH_LDAP_BIND_PASSWORD
        )
        
        # 搜索用户
        base_dn = settings.AUTH_LDAP_USER_SEARCH.base_dn
        search_filter = f"(sAMAccountName={username})"
        
        result = conn.search_s(
            base_dn,
            ldap.SCOPE_SUBTREE,
            search_filter,
            ['sAMAccountName', 'cn', 'givenName', 'sn', 'mail', 'distinguishedName']
        )
        
        if result:
            print(f"✓ 找到用户: {username}")
            for dn, attrs in result:
                print(f"\n  DN: {dn}")
                print(f"  账号: {attrs.get('sAMAccountName', [b''])[0].decode('utf-8')}")
                print(f"  姓名: {attrs.get('cn', [b''])[0].decode('utf-8')}")
                print(f"  名: {attrs.get('givenName', [b''])[0].decode('utf-8')}")
                print(f"  姓: {attrs.get('sn', [b''])[0].decode('utf-8')}")
                print(f"  邮箱: {attrs.get('mail', [b''])[0].decode('utf-8')}")
        else:
            print(f"✗ 未找到用户: {username}")
            print(f"  搜索位置: {base_dn}")
            print(f"  搜索条件: {search_filter}")
        
        conn.unbind_s()
        return bool(result)
        
    except Exception as e:
        print(f"✗ 搜索错误: {e}")
        return False


def test_authentication(username, password):
    """测试用户认证"""
    print_header(f"测试用户认证: {username}")
    
    try:
        # 使用Django的authenticate方法（会调用LDAP后端）
        user = authenticate(username=username, password=password)
        
        if user is not None:
            print(f"✓ 认证成功!")
            print(f"\n  用户信息:")
            print(f"  - 用户名: {user.username}")
            print(f"  - 姓名: {user.get_full_name() or '(未设置)'}")
            print(f"  - 邮箱: {user.email or '(未设置)'}")
            print(f"  - 是否激活: {user.is_active}")
            print(f"  - 是否管理员: {user.is_staff}")
            print(f"  - 是否超级用户: {user.is_superuser}")
            return True
        else:
            print(f"✗ 认证失败: 用户名或密码错误")
            return False
            
    except Exception as e:
        print(f"✗ 认证错误: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    print("\n" + "🔧" * 35)
    print("  LDAP/Active Directory 连接测试工具")
    print("🔧" * 35)
    
    # 1. 测试配置
    test_ldap_settings()
    
    # 2. 测试连接
    if not test_ldap_connection():
        print("\n❌ LDAP服务器连接失败，请检查配置后重试")
        return
    
    print("\n✅ LDAP服务器连接成功!")
    
    # 3. 交互式测试
    print("\n" + "-" * 70)
    print("现在可以测试用户认证")
    print("-" * 70)
    
    while True:
        print("\n选择操作:")
        print("1. 搜索用户")
        print("2. 测试用户登录")
        print("3. 退出")
        
        choice = input("\n请选择 (1-3): ").strip()
        
        if choice == '1':
            username = input("请输入用户名: ").strip()
            if username:
                test_user_search(username)
        
        elif choice == '2':
            username = input("请输入用户名: ").strip()
            password = input("请输入密码: ").strip()
            if username and password:
                test_authentication(username, password)
        
        elif choice == '3':
            print("\n👋 再见!")
            break
        
        else:
            print("无效的选择，请重试")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 测试中断")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()


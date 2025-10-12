from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Computer


@login_required
def computer_list(request):
    """计算机列表页"""
    computers = Computer.objects.all()
    
    # 搜索功能
    search_query = request.GET.get('search', '')
    if search_query:
        computers = computers.filter(
            Q(asset_code__icontains=search_query) |
            Q(user_name__icontains=search_query) |
            Q(computer_name__icontains=search_query) |
            Q(model__icontains=search_query) |
            Q(sn_code__icontains=search_query)
        )
    
    # 设备类型筛选
    device_type = request.GET.get('device_type')
    if device_type:
        computers = computers.filter(device_type=device_type)
    
    # 错误状态筛选
    has_errors = request.GET.get('has_errors')
    if has_errors:
        if has_errors == 'true':
            computers = computers.filter(has_errors=True)
        elif has_errors == 'false':
            computers = computers.filter(has_errors=False)
    
    # 分页
    paginator = Paginator(computers, 20)  # 每页显示20条
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # 获取筛选选项 - 使用set去重，因为PostgreSQL的distinct对TEXT字段可能不按预期工作
    device_types = list(set(Computer.objects.values_list('device_type', flat=True)))
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'device_types': device_types,
        'selected_device_type': device_type,
        'selected_has_errors': has_errors,
    }
    
    return render(request, 'computers/computer_list.html', context)


@login_required
def computer_detail(request, pk):
    """计算机详情页"""
    computer = get_object_or_404(Computer, pk=pk)
    
    context = {
        'computer': computer,
    }
    
    return render(request, 'computers/computer_detail.html', context)


@login_required
def search(request):
    """高级搜索页面"""
    # 获取搜索参数
    search_params = {
        'user_name': request.GET.get('user_name', ''),
        'asset_code': request.GET.get('asset_code', ''),
    }
    
    # 构建查询
    computers = Computer.objects.all()
    
    if search_params['user_name']:
        computers = computers.filter(user_name__icontains=search_params['user_name'])
    
    if search_params['asset_code']:
        computers = computers.filter(asset_code__icontains=search_params['asset_code'])
    
    # 分页
    paginator = Paginator(computers, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_params': search_params,
    }
    
    return render(request, 'computers/search.html', context)


def login_view(request):
    """用户登录视图"""
    # 如果用户已登录，重定向到首页
    if request.user.is_authenticated:
        return redirect('computer_list')
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        
        if not username or not password:
            messages.error(request, '请输入用户名和密码')
            return render(request, 'computers/login.html')
        
        # 使用Django认证系统（会自动调用LDAP后端）
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'欢迎回来，{user.get_full_name() or user.username}！')
            
            # 重定向到之前访问的页面，或首页
            next_url = request.GET.get('next', '/')
            return redirect(next_url)
        else:
            messages.error(request, '用户名或密码错误，或您没有访问权限')
    
    return render(request, 'computers/login.html')


def logout_view(request):
    """用户登出视图"""
    username = request.user.username
    logout(request)
    messages.info(request, f'{username}，您已成功登出')
    return redirect('login')

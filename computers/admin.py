from django.contrib import admin
from .models import Computer


@admin.register(Computer)
class ComputerAdmin(admin.ModelAdmin):
    list_display = [
        'asset_code', 'user_name', 'computer_name', 'model', 'cpu_model', 
        'memory_size', 'os_version', 'has_errors', 'log_size', 'upload_time'
    ]
    list_filter = [
        'device_type', 'has_errors', 'upload_time'
    ]
    search_fields = [
        'asset_code', 'sn_code', 'user_name', 'computer_name', 
        'model', 'cpu_model', 'execution_log', 'error_log'
    ]
    readonly_fields = ['upload_time', 'last_update']
    ordering = ['-upload_time']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('asset_code', 'sn_code', 'model', 'device_type')
        }),
        ('硬件信息', {
            'fields': ('cpu_model', 'memory_size')
        }),
        ('系统信息', {
            'fields': ('os_version', 'os_internal_version')
        }),
        ('用户信息', {
            'fields': ('user_name', 'computer_name')
        }),
        ('日志信息', {
            'fields': ('execution_log', 'log_size'),
            'classes': ('collapse',)
        }),
        ('错误信息', {
            'fields': ('has_errors', 'error_log'),
            'classes': ('collapse',)
        }),
        ('系统字段', {
            'fields': ('uploader', 'upload_time', 'last_update'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """优化查询"""
        qs = super().get_queryset(request)
        return qs
    
    # 自定义列表显示
    def has_errors(self, obj):
        """显示错误状态"""
        if obj.has_errors:
            return "❌ 有错误"
        return "✅ 正常"
    has_errors.short_description = "状态"
    has_errors.admin_order_field = 'has_errors'

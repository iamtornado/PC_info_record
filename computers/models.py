from django.db import models
from django.utils import timezone


class Computer(models.Model):
    """计算机模型 - 简化版（支持历史记录）"""
    # 基本信息
    asset_code = models.CharField(max_length=50, verbose_name="资产编码", db_index=True)
    sn_code = models.CharField(max_length=50, verbose_name="SN码")
    model = models.CharField(max_length=100, verbose_name="型号")
    device_type = models.CharField(max_length=50, verbose_name="设备类型", default="Default string")
    
    # 硬件信息
    cpu_model = models.CharField(max_length=100, verbose_name="CPU型号")
    memory_size = models.IntegerField(verbose_name="内存大小(GB)")
    
    # 系统信息
    os_version = models.CharField(max_length=100, verbose_name="操作系统版本")
    os_internal_version = models.CharField(max_length=50, verbose_name="操作系统内部版本")
    
    # 用户信息（直接存储，不再关联其他模型）
    user_name = models.CharField(max_length=100, verbose_name="用户名", default="")
    computer_name = models.CharField(max_length=100, verbose_name="计算机名", default="")
    
    # 日志信息字段
    execution_log = models.TextField(verbose_name="执行日志", blank=True, null=True, help_text="PowerShell脚本的完整执行日志")
    log_size = models.IntegerField(verbose_name="日志大小(字节)", default=0)
    
    # 错误信息字段
    error_log = models.TextField(verbose_name="错误日志", blank=True, null=True, help_text="业务逻辑错误信息")
    has_errors = models.BooleanField(verbose_name="是否有错误", default=False, db_index=True)
    
    # 系统字段
    uploader = models.CharField(max_length=50, default="Robot", verbose_name="上传者")
    upload_time = models.DateTimeField(auto_now_add=True, verbose_name="上传时间")
    last_update = models.DateTimeField(auto_now=True, verbose_name="最后更新时间")

    class Meta:
        verbose_name = "计算机"
        verbose_name_plural = "计算机"
        ordering = ['-upload_time']

    def __str__(self):
        return f"{self.asset_code} - {self.user_name}"

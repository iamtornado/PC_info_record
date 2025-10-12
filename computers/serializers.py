from rest_framework import serializers
from .models import Computer


class ComputerSerializer(serializers.ModelSerializer):
    """计算机序列化器"""
    
    class Meta:
        model = Computer
        fields = [
            'id', 'asset_code', 'sn_code', 'model', 'device_type',
            'cpu_model', 'memory_size', 'os_version', 'os_internal_version',
            'user_name', 'computer_name', 'execution_log', 'log_size',
            'error_log', 'has_errors', 'uploader', 'upload_time', 'last_update'
        ]
        read_only_fields = ['id', 'upload_time', 'last_update']


class ComputerCreateSerializer(serializers.ModelSerializer):
    """用于创建计算机记录的序列化器 - 支持历史记录和错误日志"""
    
    class Meta:
        model = Computer
        fields = [
            'asset_code', 'sn_code', 'model', 'device_type',
            'cpu_model', 'memory_size', 'os_version', 'os_internal_version',
            'user_name', 'computer_name', 'execution_log', 'log_size',
            'error_log', 'has_errors', 'uploader'
        ]
    
    def create(self, validated_data):
        """
        每次提交都创建新记录，支持历史记录追踪
        自动设置has_errors字段
        """
        # 如果有错误日志，自动设置has_errors为True
        if validated_data.get('error_log'):
            validated_data['has_errors'] = True
        
        # 直接创建新记录，不检查是否已存在
        computer = Computer.objects.create(**validated_data)
        return computer

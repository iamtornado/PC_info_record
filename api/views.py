import base64
import logging

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from computers.models import Computer
from computers.serializers import ComputerCreateSerializer, ComputerSerializer

logger = logging.getLogger(__name__)


@api_view(['POST'])
def create_computer(request):
    """接收客户端提交的计算机信息
    
    支持 execution_log 的 Base64 编码传输：
    - 如果请求中包含 execution_log_encoding='base64'，则自动解码
    - 解码后移除 execution_log_encoding 字段
    """
    # 记录请求基本信息
    logger.info(f"收到 API 请求 - User-Agent: {request.META.get('HTTP_USER_AGENT', 'Unknown')}")
    logger.info(f"请求来源 IP: {request.META.get('REMOTE_ADDR', 'Unknown')}")
    logger.info(f"Content-Type: {request.META.get('CONTENT_TYPE', 'Unknown')}")
    
    # 创建可变的字典副本
    data = dict(request.data)
    
    # 记录关键字段
    logger.info(f"接收到数据 - asset_code: {data.get('asset_code')}, computer_name: {data.get('computer_name')}")
    logger.info(f"数据字段: {list(data.keys())}")
    logger.info(f"os_version 原始值: {repr(data.get('os_version', ''))}")
    logger.info(f"os_version 显示值: {data.get('os_version', '')}")
    
    # 检查是否使用 Base64 编码传输日志
    if data.get('execution_log_encoding') == 'base64':
        logger.info("检测到 execution_log_encoding=base64，开始解码...")
        try:
            execution_log_base64 = data.get('execution_log', '')
            if execution_log_base64:
                # Base64 解码
                execution_log_bytes = base64.b64decode(execution_log_base64)
                # 转换为 UTF-8 字符串，忽略无法解码的字符
                decoded_log = execution_log_bytes.decode('utf-8', errors='ignore')
                # ⭐ 关键修复：移除空字符（\x00），Django CharField 不允许空字符
                data['execution_log'] = decoded_log.replace('\x00', '')
                logger.info(f"成功解码 Base64 日志，原始大小: {len(execution_log_base64)}, 解码后大小: {len(data['execution_log'])}")
                # 检查是否包含其他控制字符
                null_count = decoded_log.count('\x00')
                if null_count > 0:
                    logger.warning(f"日志中包含 {null_count} 个空字符（已移除）")
            else:
                logger.warning("execution_log 为空字符串")
                data['execution_log'] = ''
            # 移除编码标记字段
            data.pop('execution_log_encoding', None)
        except Exception as e:
            logger.error(f"Base64 日志解码失败: {e}")
            return Response(
                {'detail': f'日志解码失败: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
    else:
        logger.info(f"未使用 Base64 编码，execution_log 长度: {len(data.get('execution_log', ''))}")
    
    serializer = ComputerCreateSerializer(data=data)
    
    if serializer.is_valid():
        logger.info("数据验证通过，正在保存...")
        computer = serializer.save()
        logger.info(f"记录已创建 - ID: {computer.id}, asset_code: {computer.asset_code}")
        response_serializer = ComputerSerializer(computer)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    # 验证失败，记录详细错误
    logger.error(f"数据验证失败: {serializer.errors}")
    logger.error(f"提交的数据摘要: asset_code={data.get('asset_code')}, sn_code={data.get('sn_code')}, model={data.get('model')}")
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def computer_list_api(request):
    """获取计算机列表API"""
    computers = Computer.objects.all()
    serializer = ComputerSerializer(computers, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def computer_detail_api(request, pk):
    """获取计算机详情API"""
    try:
        computer = Computer.objects.get(pk=pk)
        serializer = ComputerSerializer(computer)
        return Response(serializer.data)
    except Computer.DoesNotExist:
        return Response({'error': 'Computer not found'}, status=status.HTTP_404_NOT_FOUND)

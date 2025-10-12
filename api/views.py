from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from computers.models import Computer
from computers.serializers import ComputerCreateSerializer, ComputerSerializer


@api_view(['POST'])
def create_computer(request):
    """接收客户端提交的计算机信息"""
    serializer = ComputerCreateSerializer(data=request.data)
    
    if serializer.is_valid():
        computer = serializer.save()
        response_serializer = ComputerSerializer(computer)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
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

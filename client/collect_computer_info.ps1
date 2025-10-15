# ==============================================================================
# PC 信息收集脚本 - 适配新版 API
# ==============================================================================
# 用途: 收集 Windows 计算机信息并发送到 PC Info Record 系统
# 使用: .\collect_computer_info.ps1
# ==============================================================================

param(
    [string]$ServerUrl = "http://10.65.37.238",
    [string]$ApiEndpoint = "$ServerUrl/api/computers/create/"
)

# 设置错误处理
$ErrorActionPreference = "Continue"

# 创建日志文件
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$logFile = "$env:TEMP\PC_Info_Collection_$timestamp.log"
Start-Transcript -Path $logFile -Append

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "🖥️  PC 信息收集脚本" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "服务器: $ServerUrl" -ForegroundColor Yellow
Write-Host "时间: $(Get-Date)" -ForegroundColor Yellow
Write-Host ""

try {
    # ==============================================================================
    # 收集系统信息
    # ==============================================================================
    Write-Host "📋 步骤 1: 收集系统信息" -ForegroundColor Green
    Write-Host "----------------------------------------" -ForegroundColor Green

    # 基本信息
    $computerName = $env:COMPUTERNAME
    $userName = $env:USERNAME
    
    # 硬件信息
    $cpu = (Get-CimInstance -ClassName Win32_Processor).Name
    $totalMemory = [math]::Round((Get-CimInstance -ClassName Win32_PhysicalMemory | Measure-Object -Property Capacity -Sum).sum / 1GB)
    $brand = Get-CimInstance -ClassName Win32_SystemEnclosure | Select-Object -ExpandProperty Manufacturer
    
    # 系统信息
    $osCurrentVersionInfo = Get-ItemProperty -Path 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\'
    $buildRelease = $osCurrentVersionInfo.UBR
    $win32OperatingSystem = Get-CimInstance -ClassName Win32_OperatingSystem -Property Caption, OSArchitecture, Version
    $osVersion = $win32OperatingSystem.Caption + ' ' + $osCurrentVersionInfo.DisplayVersion + ' ' + $win32OperatingSystem.OSArchitecture
    $osInternalVersion = $win32OperatingSystem.Version + '.' + $buildRelease
    
    # 计算机型号（根据品牌选择不同的获取方式）
    if ($brand -eq 'LENOVO') {
        $computerModel = (Get-CimInstance -ClassName Win32_ComputerSystemProduct).Version
    } else {
        $computerModel = (Get-CimInstance -ClassName Win32_ComputerSystem).Model
    }
    
    # 序列号
    $serialNumber = (Get-CimInstance -ClassName Win32_BIOS).SerialNumber
    
    # 设备类型判断
    $chassisType = (Get-CimInstance -ClassName Win32_SystemEnclosure -Property ChassisTypes | Select-Object -ExpandProperty ChassisTypes)
    $deviceType = switch ($chassisType) {
        3 { "Desktop" }
        6 { "Mini Tower" }
        7 { "Tower" }
        8 { "Portable" }
        9 { "Laptop" }
        10 { "Notebook" }
        11 { "Hand Held" }
        12 { "Docking Station" }
        13 { "All in One" }
        14 { "Sub Notebook" }
        15 { "Space-Saving" }
        16 { "Lunch Box" }
        17 { "Main System Chassis" }
        18 { "Expansion Chassis" }
        19 { "SubChassis" }
        20 { "Bus Expansion Chassis" }
        21 { "Peripheral Chassis" }
        22 { "Storage Chassis" }
        23 { "Rack Mount Chassis" }
        24 { "Sealed-Case PC" }
        default { "Unknown" }
    }

    Write-Host "✅ 系统信息收集完成" -ForegroundColor Green
    Write-Host "  计算机名: $computerName" -ForegroundColor Cyan
    Write-Host "  用户名: $userName" -ForegroundColor Cyan
    Write-Host "  CPU: $cpu" -ForegroundColor Cyan
    Write-Host "  内存: $totalMemory GB" -ForegroundColor Cyan
    Write-Host "  品牌: $brand" -ForegroundColor Cyan
    Write-Host "  型号: $computerModel" -ForegroundColor Cyan
    Write-Host "  序列号: $serialNumber" -ForegroundColor Cyan
    Write-Host "  设备类型: $deviceType" -ForegroundColor Cyan
    Write-Host "  操作系统: $osVersion" -ForegroundColor Cyan
    Write-Host ""

    # ==============================================================================
    # 准备 API 数据
    # ==============================================================================
    Write-Host "📋 步骤 2: 准备 API 数据" -ForegroundColor Green
    Write-Host "----------------------------------------" -ForegroundColor Green

    # 生成资产编码（使用序列号或计算机名）
    $assetCode = if ($serialNumber -and $serialNumber -ne "System Serial Number") {
        "PC-$serialNumber"
    } else {
        "PC-$computerName"
    }

    # 构建 API 数据
    $apiData = @{
        asset_code = $assetCode
        sn_code = $serialNumber
        model = $computerModel
        device_type = $deviceType
        cpu_model = $cpu
        memory_size = $totalMemory
        os_version = $osVersion
        os_internal_version = $osInternalVersion
        user_name = $userName
        computer_name = $computerName
        execution_log = "PowerShell script executed successfully at $(Get-Date)"
        log_size = (Get-Content $logFile | Measure-Object -Line).Lines
        error_log = ""
        has_errors = $false
        uploader = "powershell_collector"
    }

    Write-Host "✅ API 数据准备完成" -ForegroundColor Green
    Write-Host "  资产编码: $assetCode" -ForegroundColor Cyan
    Write-Host ""

    # ==============================================================================
    # 获取 CSRF Token
    # ==============================================================================
    Write-Host "📋 步骤 3: 获取 CSRF Token" -ForegroundColor Green
    Write-Host "----------------------------------------" -ForegroundColor Green

    try {
        $loginResponse = Invoke-WebRequest -Uri "$ServerUrl/login/" -Method Get -TimeoutSec 10
        
        if ($loginResponse.StatusCode -eq 200) {
            $csrfToken = ""
            if ($loginResponse.Content -match 'name="csrfmiddlewaretoken" value="([^"]+)"') {
                $csrfToken = $matches[1]
                Write-Host "✅ 获取到 CSRF Token: $($csrfToken.Substring(0, 20))..." -ForegroundColor Green
            } else {
                Write-Host "⚠️  未找到 CSRF Token，将尝试不使用 token" -ForegroundColor Yellow
            }
        } else {
            Write-Host "⚠️  获取 CSRF Token 失败，状态码: $($loginResponse.StatusCode)" -ForegroundColor Yellow
            $csrfToken = ""
        }
    } catch {
        Write-Host "⚠️  获取 CSRF Token 时出错: $($_.Exception.Message)" -ForegroundColor Yellow
        $csrfToken = ""
    }

    Write-Host ""

    # ==============================================================================
    # 发送数据到服务器
    # ==============================================================================
    Write-Host "📋 步骤 4: 发送数据到服务器" -ForegroundColor Green
    Write-Host "----------------------------------------" -ForegroundColor Green

    try {
        # 准备请求头
        $headers = @{
            'Content-Type' = 'application/json'
            'User-Agent' = 'PC-Info-Collector/2.0'
        }
        
        # 如果有 CSRF token，添加到请求头
        if ($csrfToken) {
            $headers['X-CSRFToken'] = $csrfToken
        }
        
        # 将数据转换为 JSON
        $jsonData = $apiData | ConvertTo-Json -Depth 3
        
        Write-Host "正在发送数据到: $ApiEndpoint" -ForegroundColor Cyan
        Write-Host "数据大小: $($jsonData.Length) 字节" -ForegroundColor Cyan
        
        # 发送 POST 请求
        $apiResponse = Invoke-WebRequest -Uri $ApiEndpoint -Method Post -Body $jsonData -Headers $headers -TimeoutSec 30
        
        if ($apiResponse.StatusCode -eq 201) {
            Write-Host "✅ 数据发送成功!" -ForegroundColor Green
            Write-Host "状态码: $($apiResponse.StatusCode)" -ForegroundColor Green
            
            # 解析响应
            $responseData = $apiResponse.Content | ConvertFrom-Json
            Write-Host "创建的记录 ID: $($responseData.id)" -ForegroundColor Green
            Write-Host "服务器响应: $($apiResponse.Content)" -ForegroundColor Cyan
            
            $uploadSuccess = $true
        } else {
            Write-Host "❌ 数据发送失败! 状态码: $($apiResponse.StatusCode)" -ForegroundColor Red
            Write-Host "响应内容: $($apiResponse.Content)" -ForegroundColor Red
            $uploadSuccess = $false
        }
        
    } catch {
        Write-Host "❌ 发送数据时发生错误: $($_.Exception.Message)" -ForegroundColor Red
        
        if ($_.Exception.Response) {
            $statusCode = $_.Exception.Response.StatusCode
            Write-Host "HTTP 状态码: $statusCode" -ForegroundColor Red
            
            # 尝试读取错误响应
            try {
                $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
                $errorContent = $reader.ReadToEnd()
                Write-Host "错误详情: $errorContent" -ForegroundColor Red
            } catch {
                Write-Host "无法读取错误详情" -ForegroundColor Red
            }
        }
        
        $uploadSuccess = $false
    }

    Write-Host ""

    # ==============================================================================
    # 验证结果
    # ==============================================================================
    Write-Host "📋 步骤 5: 验证结果" -ForegroundColor Green
    Write-Host "----------------------------------------" -ForegroundColor Green

    if ($uploadSuccess) {
        try {
            $listResponse = Invoke-WebRequest -Uri "$ServerUrl/api/computers/" -Method Get -TimeoutSec 10
            $computerList = $listResponse.Content | ConvertFrom-Json
            
            Write-Host "✅ 成功获取计算机列表，共 $($computerList.Count) 条记录" -ForegroundColor Green
            
            # 查找我们刚创建的记录
            $ourRecord = $computerList | Where-Object { $_.asset_code -eq $assetCode }
            if ($ourRecord) {
                Write-Host "🎉 验证成功! 找到我们刚创建的记录:" -ForegroundColor Green
                Write-Host "   ID: $($ourRecord.id)" -ForegroundColor Cyan
                Write-Host "   资产编码: $($ourRecord.asset_code)" -ForegroundColor Cyan
                Write-Host "   用户名: $($ourRecord.user_name)" -ForegroundColor Cyan
                Write-Host "   计算机名: $($ourRecord.computer_name)" -ForegroundColor Cyan
                Write-Host "   上传时间: $($ourRecord.upload_time)" -ForegroundColor Cyan
            } else {
                Write-Host "⚠️  未找到刚创建的记录，可能需要等待同步" -ForegroundColor Yellow
            }
            
        } catch {
            Write-Host "❌ 验证失败: $($_.Exception.Message)" -ForegroundColor Red
        }
    } else {
        Write-Host "⚠️  由于上传失败，跳过验证步骤" -ForegroundColor Yellow
    }

    Write-Host ""

    # ==============================================================================
    # 保存本地备份
    # ==============================================================================
    Write-Host "📋 步骤 6: 保存本地备份" -ForegroundColor Green
    Write-Host "----------------------------------------" -ForegroundColor Green

    $backupFile = "$env:TEMP\PC_Info_Backup_$timestamp.json"
    try {
        $backupData = @{
            timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
            computer_info = $apiData
            upload_success = $uploadSuccess
            server_url = $ServerUrl
        }
        
        $backupData | ConvertTo-Json -Depth 3 | Out-File -FilePath $backupFile -Encoding UTF8
        Write-Host "✅ 本地备份已保存到: $backupFile" -ForegroundColor Green
    } catch {
        Write-Host "⚠️  保存本地备份失败: $($_.Exception.Message)" -ForegroundColor Yellow
    }

    Write-Host ""

} catch {
    Write-Host "❌ 脚本执行过程中发生严重错误: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "错误详情: $($_.Exception)" -ForegroundColor Red
    $uploadSuccess = $false
}

# ==============================================================================
# 总结
# ==============================================================================
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "✅ 脚本执行完成" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

if ($uploadSuccess) {
    Write-Host "🎉 计算机信息收集和上传成功!" -ForegroundColor Green
    Write-Host "📊 收集的信息摘要:" -ForegroundColor Cyan
    Write-Host "   - 资产编码: $assetCode" -ForegroundColor White
    Write-Host "   - 计算机名: $computerName" -ForegroundColor White
    Write-Host "   - 用户名: $userName" -ForegroundColor White
    Write-Host "   - 设备类型: $deviceType" -ForegroundColor White
    Write-Host "   - 操作系统: $osVersion" -ForegroundColor White
} else {
    Write-Host "❌ 信息收集完成，但上传失败" -ForegroundColor Red
    Write-Host "💾 数据已保存到本地备份文件，可以稍后手动上传" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🌐 查看结果:" -ForegroundColor Cyan
Write-Host "   - 主页: $ServerUrl/" -ForegroundColor White
Write-Host "   - API 列表: $ServerUrl/api/computers/" -ForegroundColor White
Write-Host ""
Write-Host "📝 日志文件: $logFile" -ForegroundColor Cyan
Write-Host "💾 备份文件: $backupFile" -ForegroundColor Cyan
Write-Host ""

# 停止日志记录
Stop-Transcript

# 返回成功状态
if ($uploadSuccess) {
    exit 0
} else {
    exit 1
}

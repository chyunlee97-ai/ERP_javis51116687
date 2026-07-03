$PSScriptRoot = Split-Path -Parent -Path $MyInvocation.MyCommand.Path
if (-not $PSScriptRoot) { $PSScriptRoot = Get-Location }

# Force UTF-8 Encoding for the console session and Python processes
[Console]::InputEncoding = [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUTF8 = "1"

Write-Host "이전 실행 중인 프로세스를 종료하고 재시작합니다..." -ForegroundColor Cyan

# 1. 8001번 및 8002번 포트(서버)를 사용하는 프로세스 종료
foreach ($port in @(8001, 8002)) {
    $portConn = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    if ($portConn) {
        $portConn | ForEach-Object {
            if ($_.OwningProcess -and $_.OwningProcess -ne 0) {
                Write-Host "포트 $port 사용하는 프로세스 종료 중 (PID: $($_.OwningProcess))..." -ForegroundColor Yellow
                Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue
            }
        }
    }
}
Start-Sleep -Seconds 1

# 2. server\main.py 또는 client\main.py 스크립트 실행 중인 python 프로세스 종료
Get-CimInstance Win32_Process -Filter "Name like 'python%'" -ErrorAction SilentlyContinue | Where-Object {
    $_.CommandLine -like "*server\main.py*" -or $_.CommandLine -like "*client\main.py*"
} | ForEach-Object {
    Write-Host "실행 중인 프로세스 종료 중 (PID: $($_.ProcessId))..." -ForegroundColor Yellow
    Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
}

Write-Host "ERP JAVIS 챗봇을 실행합니다..." -ForegroundColor Cyan

Write-Host "[1/2] API 서버 시작 중..." -ForegroundColor Green
Start-Process python -ArgumentList "server\main.py" -WorkingDirectory $PSScriptRoot -WindowStyle Hidden

Start-Sleep -Seconds 3

Write-Host "[2/2] 클라이언트 시작 중..." -ForegroundColor Green
Start-Process pythonw -ArgumentList "client\main.py" -WorkingDirectory $PSScriptRoot -WindowStyle Hidden

Write-Host "완료되었습니다! 우측 하단의 챗봇 창을 확인하세요." -ForegroundColor Cyan

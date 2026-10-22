# PowerShell launcher for Resource Allocation Simulator
$pyExe = "C:\Users\Yash\AppData\Local\Programs\Python\Python311\python.exe"
if (-not (Test-Path $pyExe)) {
    $pyExe = (Get-Command python -ErrorAction SilentlyContinue).Source
}

Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "  RESOURCE ALLOCATION SIMULATOR - BANKER'S ALGORITHM" -ForegroundColor Green
Write-Host "  Deadlock Avoidance Interactive Simulator" -ForegroundColor Yellow
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host ""

Set-Location -Path $PSScriptRoot
Write-Host "[1/2] Verifying Python and dependencies..." -ForegroundColor Gray
& $pyExe -m pip install -r requirements.txt --quiet

Write-Host "[2/2] Launching Streamlit web application on http://localhost:8501..." -ForegroundColor Green
& $pyExe -m streamlit run app.py

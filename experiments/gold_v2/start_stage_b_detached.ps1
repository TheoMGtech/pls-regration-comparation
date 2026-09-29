$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$python = (Get-Command python -ErrorAction Stop).Source
$worker = Join-Path $PSScriptRoot 'run_stage_b_extended.py'
$active = Get-CimInstance Win32_Process -Filter "Name = 'python.exe'" | Where-Object { $_.CommandLine -like "*$worker*" }
if (-not $active) {
    Start-Process -FilePath $python -ArgumentList ('"{0}"' -f $worker) -WorkingDirectory $root -WindowStyle Hidden
}

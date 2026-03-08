param(
    [string]$VenvPath = ".venv",
    [string]$PythonExe = "python"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $VenvPath)) {
    & $PythonExe -m venv $VenvPath
}

$VenvPython = Join-Path $VenvPath "Scripts\python.exe"

& $VenvPython -m pip install --upgrade pip
& $VenvPython -m pip install -e '.[lora,eval,dev]'

Write-Host "Environment ready. Activate with: $VenvPath\Scripts\Activate.ps1"

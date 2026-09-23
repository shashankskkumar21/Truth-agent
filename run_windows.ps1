$ErrorActionPreference = "Stop"
Write-Host "Product Truth Agent — 3D Visual Edition" -ForegroundColor Cyan

if (-not (Test-Path ".venv")) {
    python -m venv .venv
}

& ".\.venv\Scripts\Activate.ps1"
python -m pip install -r requirements.txt

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Created .env. Add the approved Luna endpoint/key, then run this script again." -ForegroundColor Yellow
    exit
}

streamlit run app.py

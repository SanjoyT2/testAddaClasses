@echo off
title Loan Company Dashboard
echo.
echo ================================
echo   LOAN COMPANY DASHBOARD
echo ================================
echo.
echo Installing required packages...
pip install -r requirements.txt >nul 2>&1

echo.
echo Starting the dashboard...
echo.
echo Dashboard will be available at:
echo   Local URL:  http://localhost:8501
echo   Network URL: http://192.168.29.225:8501
echo.
echo Press Ctrl+C to stop the dashboard
echo.

python -m streamlit run loan_company_dashboard.py --server.headless true

pause

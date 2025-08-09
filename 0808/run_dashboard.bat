@echo off
echo Installing required packages...
pip install -r requirements.txt

echo.
echo Starting the Loan Company Dashboard...
echo Open your browser and go to: http://localhost:8501
echo.
echo Press Ctrl+C to stop the dashboard
echo.

streamlit run loan_company_dashboard.py

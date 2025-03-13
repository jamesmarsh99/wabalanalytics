@echo off

:: Set the PYTHONPATH to include the directory of graphing_utils.py
set PYTHONPATH=%PYTHONPATH%;C:\Users\James\Documents\codingProjects\wabalanalytics\src

:: Run the Streamlit app
streamlit run C:\Users\James\Documents\codingProjects\wabalanalytics\src\frontend\app.py
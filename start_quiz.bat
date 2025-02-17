@echo off
echo Starting Quiz Application...
echo Once the server starts, you can access the quiz at http://localhost:8501

cd /d %~dp0
call venv\Scripts\activate
start http://localhost:8501
python game/start_server.py 

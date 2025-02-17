@echo off
echo Installing Quiz App Service...

REM Get the full path to the current directory
set "CURRENT_DIR=%~dp0"

REM Install the service using NSSM
nssm install QuizApp "%CURRENT_DIR%start_quiz.bat"
nssm set QuizApp AppDirectory "%CURRENT_DIR%"
nssm set QuizApp DisplayName "Quiz Application"
nssm set QuizApp Description "Adaptive Learning Quiz Application"
nssm set QuizApp Start SERVICE_AUTO_START

REM Start the service
nssm start QuizApp

echo Service installation complete!
echo You can now access the quiz at http://localhost:8501
pause 
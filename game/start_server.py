import subprocess
import os
from pathlib import Path

def start_streamlit():
    # Get the directory containing this script
    current_dir = Path(__file__).parent
    
    # Command to run streamlit
    command = [
        "streamlit", "run",
        str(current_dir / "streamlit_app.py"),
        "--server.port", "8501",  # Specify port
        "--server.address", "0.0.0.0",  # Allow external access
        "--browser.serverAddress", "localhost",  # Use localhost
        "--server.headless", "true",  # Run in headless mode
        "--server.enableCORS", "false"  # Disable CORS for local development
    ]
    
    # Start the server
    subprocess.run(command)

if __name__ == "__main__":
    start_streamlit() 
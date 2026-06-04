import os
import subprocess
import requests
from langchain_core.tools import tool

@tool
def execute_bash(command: str) -> str:
    """Executes a bash command in the terminal and returns the output or error."""

    try: 
        # Runs the command and captures the output with a 30-second timeout
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=30
        )
        return result.stdout
    except subprocess.TimeoutExpired as e:
        # Capture and report tool timeouts for the triage logic
        return f"ExecutionTimeoutError: Command exceeded the 30-second limit."
    except subprocess.CalledProcessError as e:
        # If the command fails, it returns the error so the Triage Node can read it
        return f"Error executing command: {e.stderr}"


@tool
def read_file(filepath: str) -> str:
    """Reads the contents of a specified file on the local filesystem."""
    try:
        with open(filepath, 'r') as file:
            return file.read()
    except Exception as e:
        return f"FileReadError: {str(e)}" 


@tool
def write_file(filepath: str, content: str, mode: str = 'w') -> str:
    """Writes or appends content to a file. Mode should be 'w' for write or 'a' for append."""
    try:
        with open(filepath, mode) as file:
            file.write(content)
        return f"Successfully wrote to {filepath}"
    except Exception as e:
        return f"FileWriteError: {str(e)}"


@tool
def download_file(url: str, destination_path: str) -> str:
    """Downloads a file from a URL and saves it to the destination path."""
    try:
        response = requests.get(url, timeout = 10)
        response.raise_for_status()
        with open(destination_path, 'wb') as file:
            file.write(response.content)
        return f"Successfully downloaded file to {destination_path}"
    except Exception as e:
        return f"DownloadError: {str(e)}"


@tool
def submit_answer(final_answer: str) -> str:
    """Submits the final answer and marks the task as complete."""
    return f"FINAL_ANSWER_SUBMITTED: {final_answer}"
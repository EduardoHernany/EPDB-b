import subprocess
from celery.utils.log import get_task_logger

# Get a logger for this module
logger = get_task_logger(__name__)

def execute_command(command, cwd=None, shell=False):
    """
    Executes a given command using subprocess and optionally allows execution in the shell.

    Args:
    command (list or str): The command to execute.
    cwd (str, optional): The working directory to execute the command.
    shell (bool, optional): Whether to execute the command in the shell.

    Returns:
    str: The stdout from the command if successful.

    Raises:
    RuntimeError: If the command execution fails.
    """
    try:
        if shell:
            if isinstance(command, list):
                command = ' '.join(command)  # Convert list to string if shell is True
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd, shell=shell)
        stdout, stderr = process.communicate()

        if process.returncode != 0:
            error_msg = f"Error executing {' '.join(command) if isinstance(command, list) else command}: {stderr.decode().strip()}"
            logger.error(error_msg)
            raise subprocess.CalledProcessError(returncode=process.returncode, cmd=command, output=stderr)

        return stdout.decode().strip()
    except subprocess.CalledProcessError as e:
        # Log the exception and re-raise it
        logger.exception("Subprocess execution failed")
        raise RuntimeError(f"Command execution failed: {e.output.decode().strip()}")

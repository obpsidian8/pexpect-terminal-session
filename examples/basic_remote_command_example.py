"""
Example showing how to:

1. SSH to a remote Linux host
2. Navigate to an application directory
3. Run commands
4. Validate command output
5. Remove a file
6. Verify the file was removed
7. Close the terminal session

Replace the example hostname, username, password,
directory names, and file names with values appropriate
for your environment.
"""

from terminal_session import TerminalSession, logger


def basic_remote_command_example():
    """
    Demonstrates basic remote shell automation using
    TerminalSession.

    This example:

    - Establishes an SSH connection
    - Authenticates to the remote host
    - Changes directories
    - Lists directory contents
    - Removes a file
    - Verifies the file was removed
    - Closes the session
    """

    logger.info("Starting process")

    session = TerminalSession(
        "ssh admin@example-host"
    )

    if "password:" in session.get_current_output().lower():

        result = session.send_command(
            "<PASSWORD>"
        )

        if ":~#" in result["output"]:
            logger.info(
                "Successfully logged in to the remote server."
            )

    logger.info(
        "Ready for next commands after successful login"
    )

    # Change to the application directory
    result = session.send_command(
        "cd /opt/example_application"
    )

    terminal_contents = result["output"]

    if "example_application#" in terminal_contents:
        logger.info(
            "Successfully changed directory."
        )

    # Remove previous terminal history
    session.flush_terminal()

    # List directory contents
    result = session.send_command(
        "ls -lh"
    )

    terminal_contents = result["output"]

    if "config.json" in terminal_contents:
        logger.info(
            "Successfully listed application directory contents."
        )

    session.flush_terminal()

    # Remove a temporary file
    session.send_command(
        "rm temp_file.txt"
    )

    # Remove traces of previous command output
    session.flush_terminal()

    # Verify the file was removed
    result = session.send_command(
        "ls -lh"
    )

    terminal_contents = result["output"]

    if "temp_file.txt" not in terminal_contents:
        logger.info(
            "Successfully removed temporary file."
        )
    else:
        logger.error(
            "Failed to remove temporary file."
        )

    session.flush_terminal()
    session.close()


if __name__ == "__main__":
    basic_remote_command_example()
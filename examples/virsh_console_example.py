from terminal_session import CommandType, TerminalSession, logger

def virsh_console_example():
    """
        Example showing how to:

        1. SSH to a Linux host
        2. List virtual machines with virsh
        3. Connect to a guest console
        4. Log into the guest operating system
        5. Run commands
        6. Exit the guest console
        7. Return to the host shell

        Replace the example hostnames, usernames, passwords,
        and VM names with values appropriate for your environment.
    """

    logger.info("Starting virsh console example")

    session = TerminalSession(
        "ssh username@example-host",
        timeout=5
    )

    if "password:" in session.get_current_output().lower():

        result = session.send_command(
            "example_password",
            timeout=3
        )

        if "Last login:" in result["output"]:
            logger.info(
                "Successfully logged in to the remote server."
            )

    logger.info(
        "Ready for next commands after successful login"
    )

    # Navigate to the VM image directory
    result = session.send_command(
        "cd /var/lib/libvirt/images/",
        token="images#",
        timeout=5
    )

    if result["matched"]:
        logger.info(
        "Successfully changed directory."
    )

    # List directory contents
    result = session.send_command(
        "ls -lh",
        timeout=5
    )

    if "lost+found" in result["output"]:
        logger.info(
            "Successfully listed directory contents."
        )

    session.flush_terminal()

    # List all virtual machines
    result = session.send_command(
        "virsh list --all",
        timeout=5
    )

    if "State" in result["output"]:
        logger.info(
            "Successfully listed all virtual machines."
        )

    session.flush_terminal()

    # Connect to a virtual machine console
    result = session.send_command(
        "virsh console example-vm",
        timeout=5
    )

    if "Escape character is" not in result["output"]:
        logger.error(
            "Failed to enter VM console."
        )
        return

    logger.info(
        "Successfully entered VM console."
    )

    # Do not flush while at a login prompt

    result = session.send_command(
        "\n",
        command_type=CommandType.RAW
    )

    terminal_contents = result["output"]

    if (
        "login:" not in terminal_contents
        and "admin@example-vm" not in terminal_contents
    ):
        logger.error(
            "Failed to reach VM login prompt."
        )
        return

    logger.info(
        "Successfully reached login prompt."
    )

    if "login:" in terminal_contents:

        result = session.send_command(
            "admin",
            timeout=5
        )

        terminal_contents = result["output"]

    if (
        "Password:" not in terminal_contents
        and "admin@example-vm" not in terminal_contents
    ):
        logger.error(
            "Failed to reach password prompt."
        )
        return

    if "Password:" in terminal_contents:

        result = session.send_command(
            "example_password",
            timeout=5
        )

        terminal_contents = result["output"]

    if "admin@example-vm" not in terminal_contents:
        logger.error(
            "Failed to log in to the VM."
        )
        return

    logger.info(
        "Successfully logged in to the VM."
    )

    session.flush_terminal()

    logger.info(
        f"Current terminal output: "
        f"{session.get_current_output()}"
    )

    # Run a command inside the VM
    result = session.send_command(
        "df -h",
        timeout=5
    )

    logger.info(result["output"])

    # Log out of the VM
    result = session.send_command(
        "exit",
        timeout=5
    )

    if "login:" not in result["output"]:
        logger.error(
            "Failed to log out of the VM."
        )
        return

    logger.info(
        "Successfully exited the VM session."
    )

    # Exit the virsh console (Ctrl+])
    result = session.send_command(
        "\x1d",
        command_type=CommandType.RAW,
        timeout=10
    )

    if "images#" not in result["output"]:
        logger.error(
            "Failed to exit the virsh console."
        )
        return

    logger.info(
        "Successfully exited the virsh console."
    )

    session.flush_terminal()
    session.close()

if __name__ == "__main__":
    virsh_console_example()
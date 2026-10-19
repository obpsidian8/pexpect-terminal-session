"""
Demonstrates validating terminal state transitions
using regular expressions.

Rather than checking if two strings exist somewhere
in the terminal history, a regex can verify that
one event occurred after another.

Example:

Password:
    ↓
Shell Prompt

This is generally more reliable than checking
for individual strings independently.
"""

import re
from terminal_session import TerminalSession, CommandType,logger

def regex_state_validation_example():
    """
    Demonstrates validating a login sequence
    using a regular expression.
    """

    session = TerminalSession(
        "ssh admin@example-host",
        timeout=5
    )

    result = session.send_command(
        "\n",
        command_type=CommandType.RAW,
        timeout=5
    )

    if re.search(
        r"Password:.*?[#$]",
        result["output"],
        re.DOTALL
    ):
        logger.info(
            "Successfully logged in."
        )
    else:
        logger.error(
            "Login sequence not detected."
        )

    session.close()


if __name__ == "__main__":
    regex_state_validation_example()
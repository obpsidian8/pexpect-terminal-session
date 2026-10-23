import csv
import logging
import re

import pexpect
from enum import Enum


logger = logging.getLogger("my_log")

# Create handler
c_handler = logging.StreamHandler()

# Create formatters and add it to handlers
c_format = logging.Formatter('%(asctime)s - %(name)s - %(lineno)d - %(levelname)s ------- %(message)s')
c_handler.setFormatter(c_format)

# Add handlers to the logger
logger.addHandler(c_handler)

logger.setLevel(logging.INFO)
class CommandType(Enum):
    NORMAL = "NORMAL"
    RAW = "RAW"
    CONTROL = "CONTROL"
class TerminalSession:
    FLUSH_TOKEN = "__PEXPECT_FLUSH_9f78a3c1__"
    PROMPT_TOKEN = "__THIS_TOKEN_WILL_NEVER_EXIST__"
    
    def __init__(self, initial_command: str,timeout: int=10) -> None:
        """
        Initialize the TerminalSession with an initial command and timeout.
        
        :param initial_command: The initial command used to spawn the terminal session.
        :param timeout: The timeout for expecting the prompt token. Defaults to 10.
        """
        self.child = self._spawn_child_terminal(initial_command, timeout)

    def _spawn_child_terminal(self, command: str, timeout: int) -> pexpect.spawn:
        """
        Spawn a child terminal with the specified command and timeout.\
        This function is a helper method used internally to spawn a child terminal and wait for the prompt token.
        
        :param command: The command to spawn the terminal with.
        :param timeout: The timeout for expecting the prompt token.
        :return: The spawned child terminal.
        :rtype: pexpect.spawn
        """
        logger.info(f"Spawning child terminal with command: {command}")
        child = pexpect.spawn(command, encoding='utf-8')
        try:
            child.expect(self.PROMPT_TOKEN, timeout=timeout)
        except pexpect.TIMEOUT as e:
            logger.info("Timeout waiting for PROMPT_TOKEN in spawned terminal:\n================================\n")
        except pexpect.EOF:
            logger.info("EOF encountered in spawned terminal.")
            raise

        logger.info("")    
        logger.info(f"Output Currently on Terminal after spawning command '{command}':\n[START]============================\n{child.before}\n[END]============================\n")
        return child

    def get_current_output(self) -> str:
        """
        Get the current output from the terminal session.
        This method retrieves the (currrent unconsumed) output that has been produced by the terminal session up to the current point in time.
        
        :param self: The instance of the TerminalSession class.
        :return: The current output from the terminal session.
        :rtype: str
        """
        logger.info("Getting current terminal output")

        try:
            self.child.expect(self.FLUSH_TOKEN, timeout=3)
            logger.info("Get output flush token received successfully.")
        except pexpect.TIMEOUT:
            logger.warning("Get output timed out while waiting for flush token.")

        current_terminal_output = self.child.before
        logger.info(f"\n[START(get_current_output)]============================\n{current_terminal_output}\n[END(get_current_output)]============================\n")
        return str(current_terminal_output)

    def send_command(self, command: str,token: str="",timeout: int=10, command_type: CommandType=CommandType.NORMAL) -> dict:
        """
        Docstring for send_command
        
        :param initial_command: The initial command used to spawn the terminal session.
        :param command: The command to send to the terminal.
        :param token: The token to expect in the output. Defaults to None.
        :param timeout: The timeout for expecting the token. Defaults to 10. If you think a longer or shorter timeout is needed for a 
            certain command, you can adjust this value accordingly.
        :param command_type: The type of command being sent. Can be NORMAL, RAW, or CONTROL. Defaults to NORMAL.

        :return: A dictionary containing the command sent and the output received. The dictionary has the following structure:
            {
                "command": <command_sent>,
                "output": <output_received>
            }

        This function send a commnand. It will then wait for the specified token to appear in the terminal output. 
        If the token is not found within the timeout period, a timeout will occur. 
        The output received up to that point will be captured and returned in the output dictionary.
        
        """
        logger.info("")
        logger.info(f"Sending command: {command}")
        # logger.info(f"Current Screen OutPut BEFORE sending command '{command}':\n[START]============================\n{self.get_current_output()}\n[END]============================\n")
        output_container = {
            "command": command,
            "output": "",
            "matched": False
        }
        if command_type == CommandType.RAW:
            self.child.send(command)
        elif command_type == CommandType.CONTROL:
            self.child.sendcontrol(command)
        else:
            self.child.sendline(command)
        
        try:
            if not token:
                token = self.PROMPT_TOKEN
            self.child.expect(token, timeout=timeout)
            logger.info(f"Token {token} found in command {command} output.")
            output_container["matched"] = True
        except pexpect.TIMEOUT as e:
            logger.info(f"Timeout waiting for token {token} in command {command}:\n\n")
            output_container["matched"] = False
        except pexpect.EOF:
            logger.info(f"EOF received while waiting for token {token} in command {command}.")
            output_container["matched"] = False
            raise
        finally:
            # If there is not match, the entire history of the command output will be captured in child.before. 
            # Child.before represents everything received since the last successful match.

            if token == self.PROMPT_TOKEN:
                output_container["output"] = str(self.child.before)
            else:
                output_container["output"] = str(self.child.before) + str(self.child.after)

            if self.FLUSH_TOKEN in command:
                output_container["output"] = "<FLUSHED>"
                logger.info(f"Output Currently on Terminal AFTER flushing:\n[START]============================\n{output_container['output']}\n[END]============================\n")
            else:
                logger.info("")    
                logger.info(f"Output Currently on Terminal AFTER sending command '{command}':\n[START]============================\n{output_container['output']}\n[END]============================\n")
        
        return output_container

    def flush_terminal(self) -> None:
        """
        Flush the terminal by sending a flush command and consuming the flush token. 
        This ensures that any previous output is cleared and will not interfere with subsequent commands.
        ** Only use this at a shell prompt. Do not use when at a username, password, or any other prompt.
        
        :param self: The instance of the TerminalSession class.
        """
        # send command "echo __PEXPECT_FLUSH_9f78a3c1__" with the same as expected token, so that the current terminal to this point is consumed
        logger.info("Flushing the terminal")
        self.send_command(command=self.FLUSH_TOKEN , token=self.FLUSH_TOKEN, timeout=5)
        # Do another expect to consume the flush token
        try:
            self.child.expect(self.FLUSH_TOKEN, timeout=5)
            logger.info("Flush token received successfully.")
        except pexpect.TIMEOUT:
            logger.warning("Second flush token not found. Flush may be incomplete.")
        except pexpect.EOF:
            logger.warning("Second flush token not found due to EOF. Flush may be incomplete.")
            raise 
        logger.info("Terminal flushed successfully. Output history will not show on new commands.")

    def close(self) -> None:
        """
        Close the terminal session.
        
        :param self: The instance of the TerminalSession class.
        """
        logger.info("Closing the terminal session")
        if self.child.isalive():
            self.child.close()
        logger.info("Terminal session closed")
# TerminalSession

A transcript-based wrapper around `pexpect` for automating interactive terminal sessions.

Unlike traditional `pexpect` scripts that rely heavily on matching shell prompts, `TerminalSession` focuses on collecting terminal output and validating state transitions using string matching and regular expressions.

This approach works particularly well for:

- SSH sessions
- Linux shells
- Interactive login prompts
- `virsh console` sessions
- Network device automation
- Cisco IOS-XR environments
- Install/reload workflows
- Interactive applications that do not have predictable prompts

---

# Features

- Simple terminal session abstraction
- Built on top of `pexpect`
- Transcript-based command execution
- Regex-friendly output validation
- Support for normal commands
- Support for raw character input
- Support for control characters (Ctrl+C, Ctrl+], etc.)
- Terminal flushing support
- Built-in logging
- Type-hinted API

---

# Installation

```bash
pip install pexpect
```

Clone the repository:

```bash
git clone https://github.com/<your-username>/terminal-session.git
cd terminal-session
```

---

# Quick Start

```python
from terminal_session import TerminalSession

session = TerminalSession("/bin/bash")

result = session.send_command("pwd")

print(result["output"])

session.close()
```

---

# Basic SSH Example

```python
from terminal_session import TerminalSession

session = TerminalSession(
    "ssh user@example.com"
)

if "password:" in session.get_current_output().lower():

    result = session.send_command("mypassword")

    print(result["output"])

session.close()
```

---

# Command Types

The framework supports three command types.

## NORMAL

Uses `sendline()`.

```python
session.send_command(
    "ls -lh"
)
```

Equivalent to:

```text
ls -lh<ENTER>
```

---

## RAW

Uses `send()`.

Useful for sending a single newline or other raw characters without automatically appending Enter.

```python
session.send_command(
    "\n",
    command_type=CommandType.RAW)
```

---

## CONTROL

Uses `sendcontrol()`.

Useful for sending control characters.

```python
session.send_command(
    "c",
    command_type=CommandType.CONTROL)
```

Equivalent to:

```text
Ctrl+C
```

---

# Return Value

`send_command()` returns a dictionary.

```python
{
    "command": "<command>",
    "output": "<terminal output>",
    "matched": True | False
}
```

Example:

```python
result = session.send_command(
    "show version",
    timeout=10)

print(result["matched"])
print(result["output"])
```

---

# Waiting For Specific Tokens

Instead of waiting for a timeout, you can wait for a specific piece of output.

```python
result = session.send_command(
    install_command,
    token=r"\[yes/no\]"
)

if result["matched"]:
    session.send_command("yes")
```

---

# Regex-Based Validation

One of the primary goals of this framework is validating state transitions instead of simply checking for individual strings.

Instead of:

```python
if "Password:" in output and "RP/" in output:
```

Use:

```python
import re

regex = re.compile(r'Password:[\s\S]*?RP/[^\r\n]+#')
if re.search(outpyt):
    print("Successfully returned to router prompt")
```

This verifies:

```text
Password prompt
        ↓
Routeer prompt
```

rather than simply checking if both strings exist somewhere in the terminal history.

---

# Working With virsh Console

Example

```python
session.send_command(
"virsh console myvm"
)

session.send_command(
    "\n",
    command_type=CommandType.RAW
)

session.send_command("root")
```

To exit a `virsh console` session:

```python
    session.send_command("]", command_type=CommandType.CONTROL)
```

Requirements:

- Linux host
- *VM/libvirt*- virsh
- Running guest VM

---

#Flushing The Terminal

The framework supports flushing previously collected terminal output.

```python
session.flush_terminal()
```

Example:

```python
session.send_command("ls -lh")

session.flush_terminal()

result = session.send_command("pwd")
```

### Warning

Only use `flush_terminal()` when the terminal is at a shell prompt.

Do **not** use it While sitting at:

- Username prompts
- Password prompts
- Confirmation prompts
- Login screens
- Any other interactive prompt

---

# Closing Sessions

Always close sessions when finished.

```python
session.close()
```

---

# Design Philosophy

Traditional `pexpect` usage often looks like:

```python
    child.sendline("show version")
    child.expect("#")
```

This framework instead encourages:

```python
    result = session.send_command(
    "show version"
)

terminal_output = result["output"]

# Validate state with regex
```

The focus is on:

- capturing terminal transcripts
- validating state transitions
- simplifying interactive workflows

---

# Requirements

- Python 3.10+
- pexpect

---

# License
MIT License
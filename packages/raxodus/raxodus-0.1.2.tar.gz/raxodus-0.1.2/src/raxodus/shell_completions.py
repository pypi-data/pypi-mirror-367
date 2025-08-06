"""Shell completion installation for raxodus."""

import os
from pathlib import Path

COMPLETION_SCRIPTS = {
    "bash": """
# raxodus bash completion
eval "$(_RAXODUS_COMPLETE=bash_source raxodus)"
""",
    "zsh": """
# raxodus zsh completion
eval "$(_RAXODUS_COMPLETE=zsh_source raxodus)"
""",
    "fish": """
# raxodus fish completion
_RAXODUS_COMPLETE=fish_source raxodus | source
""",
}


def get_shell_config_file(shell: str) -> Path:
    """Get the configuration file for the shell."""
    home = Path.home()

    if shell == "bash":
        bashrc = home / ".bashrc"
        bash_profile = home / ".bash_profile"
        return bashrc if bashrc.exists() else bash_profile
    elif shell == "zsh":
        return home / ".zshrc"
    elif shell == "fish":
        return home / ".config" / "fish" / "config.fish"
    else:
        raise ValueError(f"Unsupported shell: {shell}")


def install_completion(shell: str) -> tuple[bool, str]:
    """Install completion for the shell.

    Returns:
        (success, message)
    """
    if shell not in COMPLETION_SCRIPTS:
        return False, f"Shell '{shell}' is not supported. Supported shells: bash, zsh, fish"

    config_file = get_shell_config_file(shell)
    completion_script = COMPLETION_SCRIPTS[shell].strip()

    # Check if config file exists
    if not config_file.exists():
        config_file.touch()

    # Read existing config
    content = config_file.read_text()

    # Check if already installed
    if "raxodus" in content and "_RAXODUS_COMPLETE" in content:
        return False, f"Completion already installed in {config_file}"

    # Append completion script
    with open(config_file, "a") as f:
        f.write(f"\n{completion_script}\n")

    return True, f"Completion installed in {config_file}"


def detect_shell() -> str:
    """Detect the current shell."""
    shell_path = os.environ.get("SHELL", "")

    if "bash" in shell_path:
        return "bash"
    elif "zsh" in shell_path:
        return "zsh"
    elif "fish" in shell_path:
        return "fish"

    # Default to bash
    return "bash"

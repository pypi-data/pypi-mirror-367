# File: validators/pre_validator.py
# Description: Performs high-level pre-validation checks in the Python CLI
# before sending data to the backend API.

import toml
from pathlib import Path

# Define high-level constraints
MAX_TOML_SIZE_BYTES = 64 * 1024  # 64 KB
MAX_SCRIPT_SIZE_BYTES = 5 * 1024 * 1024 # 5 MB
REQUIRED_TOP_LEVEL_BLOCKS = {"agent", "network", "outputs"}

def pre_validate_toml(toml_string: str, base_path: str = "."):
    """
    Performs basic, high-level checks on the raw TOML string and its content.

    Args:
        toml_string: The raw string content of the elyzo.toml file.
        base_path: The root directory of the user's project, used to check for the entrypoint file.

    Returns:
        A list of error strings. The list is empty if all pre-checks pass.
    """
    errors = []

    # 1. Check the total size of the configuration file.
    if len(toml_string.encode('utf-8')) > MAX_TOML_SIZE_BYTES:
        errors.append(f"Configuration file size exceeds the maximum limit of {MAX_TOML_SIZE_BYTES / 1024} KB.")
        # If the file is too big, stop here to avoid parsing a huge file.
        return errors

    # 2. Check if the TOML is syntactically valid.
    try:
        parsed_toml = toml.loads(toml_string)
    except toml.TomlDecodeError as e:
        errors.append(f"Invalid TOML format: {e}")
        # If parsing fails, we can't perform any more checks.
        return errors

    # 3. Check for the presence of essential top-level blocks.
    missing_blocks = REQUIRED_TOP_LEVEL_BLOCKS - set(parsed_toml.keys())
    if missing_blocks:
        for block in missing_blocks:
            errors.append(f"Required top-level block '[{block}]' is missing.")

    # 4. Check the agent entrypoint file.
    agent_block = parsed_toml.get("agent", {})
    entrypoint = agent_block.get("entrypoint")

    if not entrypoint:
        errors.append("[agent.entrypoint] is a required field.")
    else:
        entrypoint_path = Path(base_path) / entrypoint
        # 4a. Check if the file exists.
        if not entrypoint_path.is_file():
            errors.append(f"Entrypoint file not found at the specified path: {entrypoint}")
        else:
            # 4b. Check if the file is too large.
            script_size = entrypoint_path.stat().st_size
            if script_size > MAX_SCRIPT_SIZE_BYTES:
                errors.append(
                    f"Agent script '{entrypoint}' is too large "
                    f"({script_size / 1024 / 1024:.2f} MB). "
                    f"The maximum size is {MAX_SCRIPT_SIZE_BYTES / 1024 / 1024} MB."
                )

    return errors

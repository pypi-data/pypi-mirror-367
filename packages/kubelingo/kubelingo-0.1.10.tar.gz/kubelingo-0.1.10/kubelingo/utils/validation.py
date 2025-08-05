import re
import shlex
try:
    import yaml
except ImportError:
    yaml = None
from typing import Dict, Any, List, Optional

# Attempt to import high-performance extensions from the Rust library
try:
    from kubelingo._native import commands_equivalent as rust_commands_equivalent
    from kubelingo._native import validate_yaml_structure as rust_validate_yaml_structure
except ImportError:
    rust_commands_equivalent = None
    rust_validate_yaml_structure = None
import os

# Allow disabling Rust-based validation via environment variable
RUST_VALIDATOR_ENABLED = os.getenv("KUBELINGO_DISABLE_RUST", "").lower() not in ("1", "true", "yes")


def commands_equivalent(cmd1: str, cmd2: str) -> bool:
    """
    Check if two kubectl commands are functionally equivalent.
    This function normalizes whitespace, handles aliases, is case-insensitive,
    and ignores the order of flags.
    """
    if rust_commands_equivalent and RUST_VALIDATOR_ENABLED:
        return rust_commands_equivalent(cmd1, cmd2)

    # Fallback to a more robust Python-based comparison if the Rust extension is not available.
    print("Warning: Rust extension not found or disabled. Falling back to enhanced Python command comparison.")

    def _normalize_command(cmd_str: str) -> (list, list):
        # 1. Lowercase and remove shell redirection
        cmd_str = cmd_str.lower().split(' > ')[0].strip()

        # 2. Handle common concatenated flags like -oyaml
        cmd_str = re.sub(r'(-o|-n)([a-z0-9-]+)', r'\1 \2', cmd_str)

        # 3. Tokenize using shlex to handle quotes
        try:
            parts = shlex.split(cmd_str)
        except ValueError:
            parts = cmd_str.split()  # Fallback for malformed commands

        # 4. Handle 'k' alias
        if parts and parts[0] == 'k':
            parts[0] = 'kubectl'

        # 5. Separate positional args from flags
        positional_args = []
        flags = []
        i = 0
        while i < len(parts):
            part = parts[i]
            if part.startswith('-'):
                # Handle --flag=value
                if '=' in part:
                    flags.append(part)
                    i += 1
                # Handle --flag value
                elif i + 1 < len(parts) and not parts[i+1].startswith('-'):
                    flags.append(f"{part} {parts[i+1]}")
                    i += 2
                # Handle boolean flag --flag
                else:
                    flags.append(part)
                    i += 1
            else:
                positional_args.append(part)
                i += 1

        flags.sort()
        return positional_args, flags

    cmd1_pos, cmd1_flags = _normalize_command(cmd1)
    cmd2_pos, cmd2_flags = _normalize_command(cmd2)

    return cmd1_pos == cmd2_pos and cmd1_flags == cmd2_flags

def validate_yaml_structure(yaml_content: str) -> Dict[str, Any]:
    """
    Validates YAML syntax and basic Kubernetes structure using the Rust implementation.

    This function checks for syntax errors and the presence of top-level
    'apiVersion', 'kind', and 'metadata' fields.

    Args:
        yaml_content: The YAML content as a string.

    Returns:
        A dictionary with validation results:
        {
            'valid': bool,
            'errors': List[str],
            'warnings': List[str],
            'parsed_yaml': Optional[Any]
        }
    """
    result = {
        'valid': False,
        'errors': [],
        'warnings': [],
        'parsed_yaml': None
    }

    # Use the high-performance Rust validator if available and enabled.
    if rust_validate_yaml_structure and RUST_VALIDATOR_ENABLED:
        is_valid, message = rust_validate_yaml_structure(yaml_content)
        if not is_valid:
            result['errors'].append(message)
        else:
            result['valid'] = True
    else:
        # Fallback to pure Python if the Rust extension is missing.
        warning_msg = "Warning: Rust extension not found. Using Python-based YAML validation."
        result['warnings'].append(warning_msg)
        # Also print a warning to stdout for visibility
        print(warning_msg)
        try:
            parsed = yaml.safe_load(yaml_content)
            if parsed is None:
                result['errors'].append("YAML content is empty or null.")
            elif not isinstance(parsed, dict):
                result['errors'].append("YAML is not a dictionary (mapping).")
            else:
                # Basic Kubernetes resource validation
                required_fields = ['apiVersion', 'kind', 'metadata']
                missing_fields = [field for field in required_fields if field not in parsed]
                if missing_fields:
                    result['errors'].extend([f"Missing required field: {field}" for field in missing_fields])
                else:
                    result['valid'] = True
        except yaml.YAMLError as e:
            result['errors'].append(f"YAML parsing error: {str(e)}")

    # Regardless of the validation method, try to parse and return the object
    # for further use by the caller.
    if yaml:
        try:
            result['parsed_yaml'] = yaml.safe_load(yaml_content)
        except yaml.YAMLError:
            # If parsing fails, parsed_yaml will remain None.
            pass

    return result

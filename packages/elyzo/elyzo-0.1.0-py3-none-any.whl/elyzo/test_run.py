# File: elyzo/test_run.py
# Description: Handles the logic for the 'test' command.

import os
from pathlib import Path
import sys
import requests
import toml
import base64
from elyzo.validator import pre_validate_toml # Import the pre-validator

# Use an environment variable for the API URL for flexibility
API_BASE_URL = os.environ.get("ELYZO_API_URL", "http://192.168.64.9:3000")
# API_BASE_URL = os.environ.get("ELYZO_API_URL", "https://api.elyzo.ai") 

CONFIG_FILENAME = "elyzo.toml"
MAX_INPUT_FILE_SIZE_BYTES = 10 * 1024 * 1024 # 10 MB limit for individual input files

def test_agent_run(api_key: str, input_args: list, output_path: str = None):
    """
    Orchestrates a dry-run of an agent by sending its code, config,
    and inputs to the backend API for immediate execution.

    Args:
        api_key: The authenticated developer's API key, e.g., "--api-key YOUR_API_KEY".
        input_args: A list of input arguments from the CLI, e.g., ["--input key1=value1", "--input key2=path/to/file.txt"].
        output_path: An optional path to a directory where output files will be saved, e.g., "--output /path/to/output".
    """
    print("Starting test run...")

    # 1. Read and pre-validate the TOML configuration
    try:
        config_path = Path.cwd() / CONFIG_FILENAME
        if not config_path.is_file():
            print(f"❌ Error: Your elyzo.toml file ('{CONFIG_FILENAME}') was not found in this directory.")
            sys.exit(1)
            
        toml_content = config_path.read_text()
        
        validation_errors = pre_validate_toml(toml_content, base_path=str(Path.cwd()))
        if validation_errors:
            print(f"❌ Validation failed for '{CONFIG_FILENAME}':")
            for error in validation_errors:
                print(f"   - {error}")
            sys.exit(1)
        
        print("✅ Local validation passed.")
        
        parsed_toml = toml.loads(toml_content)
        entrypoint = parsed_toml.get("agent", {}).get("entrypoint")
        if not entrypoint:
            print(f"❌ Error: [agent.entrypoint] is missing in your {CONFIG_FILENAME}.")
            sys.exit(1)
        
        agent_script_path = Path.cwd() / entrypoint
        agent_code_content = agent_script_path.read_text()

    except FileNotFoundError as e:
        print(f"❌ Error: Could not find a required file: {e.filename}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error reading project files: {e}")
        sys.exit(1)

    # 2. Process and validate the input arguments from the command line
    inputs_payload = {}
    provided_input_keys = set()
    defined_inputs = parsed_toml.get("inputs", {})
    
    for arg in input_args:
        if "=" not in arg:
            print(f"❌ Error: Invalid input format '{arg}'. Please use 'key=value'.")
            sys.exit(1)
        
        key, value = arg.split("=", 1)
        provided_input_keys.add(key)
        
        # --- REFACTORED VALIDATION LOGIC ---
        expected_type = defined_inputs.get(key, {}).get("type")
        
        if expected_type == "text":
            # If the TOML defines the input as text, treat the value as a literal string.
            input_content = value.encode('utf-8')
            input_name = key # Use the key as the "filename" for the API
            print(f"✅ Using text input for: {key}")
        else:
            # If the TOML defines a file type (e.g., .json), treat the value as a file path.
            file_path = Path(value)
            if not file_path.is_file():
                print(f"❌ Error: Input for '{key}' is defined as a file, but '{value}' is not a valid file path.")
                sys.exit(1)
            
            # Check the size of the input file before reading it.
            file_size = file_path.stat().st_size
            if file_size > MAX_INPUT_FILE_SIZE_BYTES:
                print(f"❌ Error: Input file '{value}' for '{key}' is too large "
                      f"({file_size / 1024 / 1024:.2f} MB). "
                      f"The maximum size is {MAX_INPUT_FILE_SIZE_BYTES / 1024 / 1024} MB.")
                sys.exit(1)

            if expected_type and not value.endswith(expected_type):
                print(f"❌ Error: Input file for '{key}' has the wrong extension. Expected '{expected_type}', but got '{file_path.suffix}'.")
                sys.exit(1)
            
            try:
                input_content = file_path.read_bytes()
                input_name = value # Use the actual filename for the API
                print(f"✅ Reading input file: {value}")
            except Exception as e:
                print(f"❌ Error reading input file '{value}': {e}")
                sys.exit(1)

        inputs_payload[key] = {
            "Name": input_name,
            "Content": base64.b64encode(input_content).decode('utf-8')
        }
    
    # 3. Check for missing required inputs and unexpected inputs
    missing_required_inputs = []
    defined_input_keys = set(defined_inputs.keys())

    for input_name, input_spec in defined_inputs.items():
        if input_spec.get("required") and input_name not in provided_input_keys:
            missing_required_inputs.append(input_name)
    
    if missing_required_inputs:
        print("❌ Error: Missing required inputs. Please provide them using the --input flag.")
        for missing in missing_required_inputs:
            print(f"   - Missing: {missing}")
        sys.exit(1)

    unexpected_inputs = provided_input_keys - defined_input_keys
    if unexpected_inputs:
        print("❌ Error: Unexpected inputs provided that are not defined in elyzo.toml.")
        for unexpected in unexpected_inputs:
            print(f"   - Unexpected: {unexpected}")
        sys.exit(1)

    # 4. Prepare and make the API call to the dry-run endpoint
    api_url = f"{API_BASE_URL}/run/dry-run"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "elyzo_toml": toml_content,
        "agent_code": agent_code_content,
        "inputs": inputs_payload
    }

    print(f"🚀 Sending test run for agent '{parsed_toml['agent']['name']}' to Elyzo...")
    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()

        # 5. Handle successful response from the runtime
        result = response.json()
        print("\n🎉 Test run completed successfully!")
        
        if result.get("stdout"):
            print("\n--- Agent STDOUT ---")
            print(result["stdout"].strip())
            print("--------------------")
        
        if result.get("stderr"):
            print("\n--- Agent STDERR ---")
            print(result["stderr"].strip())
            print("--------------------")


        # --- NEW: Handle and save output files ---
        if result.get("outputs"):
            # Determine the output directory
            if output_path:
                output_dir = Path(output_path)
            else:
                output_dir = Path.cwd() # Default to current directory

            try:
                # Create the directory if it doesn't exist
                output_dir.mkdir(parents=True, exist_ok=True)
                print(f"\n--- 💾 Saving Agent Outputs to '{output_dir.resolve()}' ---")
                
                for key, output_file in result["outputs"].items():
                    try:
                        filename = output_file["name"]
                        # Decode the Base64 content from the response
                        file_content = base64.b64decode(output_file["content"])
                        
                        save_path = output_dir / filename
                        
                        # Write the decoded bytes to the file
                        save_path.write_bytes(file_content)
                        print(f"  ✅ Saved: {filename}")
                    except Exception as e:
                        print(f"  ❌ FAILURE: Could not write file '{filename}': {e}")
                print("-------------------------------------------------")
            except Exception as e:
                print(f"❌ Error: Could not create or write to output directory '{output_dir}': {e}")
        # --- END NEW SECTION ---

    except requests.exceptions.HTTPError as e:
        print(f"\n❌ Test run failed (HTTP {e.response.status_code}):")
        try:
            error_details = e.response.json()
            print(f"   Error: {error_details.get('error')}")
            if error_details.get('details'):
                for detail in error_details['details']:
                    print(f"   - {detail}")
        except ValueError:
            print(f"   {e.response.text}")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Network error: Could not connect to the Elyzo API at {api_url}.")
        print(f"   Please check your network connection. Details: {e}")
        sys.exit(1)

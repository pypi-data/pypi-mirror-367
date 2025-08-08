import pytest
import toml
from pathlib import Path
from posit_keyring.token_file import write_token_to_file, TokenFileData

@pytest.fixture
def temp_token_file(tmp_path: Path) -> Path:
    """
    Provides a path to a temporary tokens.toml file for testing.
    The .ppm directory will be created by the write_token_to_file function.
    """
    test_dir = tmp_path / ".ppm" # Define the .ppm directory path
    return test_dir / "tokens.toml" # Return the full path to the tokens.toml file

def test_write_token_to_file_new_file(temp_token_file: Path):
    """
    Test case 1: File does not exist or is empty.
    Verifies that the file and its parent directory are created correctly.
    """
    # Ensure the token file and its parent directory do NOT exist initially
    # temp_token_file.parent is the .ppm directory
    assert not temp_token_file.exists()
    assert not temp_token_file.parent.exists() # Assert that .ppm doesn't exist yet

    write_token_to_file("http://localhost:4242", "new_token_123", "sso", token_file_path=temp_token_file)

    # After the function call, assert that they now exist
    assert temp_token_file.exists()
    assert temp_token_file.parent.exists()

    with open(temp_token_file, 'r') as f:
        data = toml.load(f)

    expected_data = {
        "connections": [
            {"address": "http://localhost:4242", "token": "new_token_123", "auth_type": "sso"}
        ]
    }
    assert data == expected_data

def test_write_token_to_file_update_existing_connection(temp_token_file: Path):
    """
    Test case 2: Update an existing connection.
    """
    # First, ensure the parent directory exists so we can create the initial file
    temp_token_file.parent.mkdir(exist_ok=True) # Use exist_ok=True to prevent error if already exists

    initial_data = {
        "connections": [
            {"address": "http://localhost:4242", "token": "initial_token", "auth_type": "sso"}
        ]
    }
    with open(temp_token_file, 'w') as f:
        toml.dump(initial_data, f)

    write_token_to_file("http://localhost:4242", "updated_token_456", "classic", token_file_path=temp_token_file)

    with open(temp_token_file, 'r') as f:
        data = toml.load(f)

    expected_data = {
        "connections": [
            {"address": "http://localhost:4242", "token": "updated_token_456", "auth_type": "classic"}
        ]
    }
    assert data == expected_data

def test_write_token_to_file_add_new_connection(temp_token_file: Path):
    """
    Test case 3: Add a new connection.
    """
    # Ensure parent directory exists for initial file creation
    temp_token_file.parent.mkdir(exist_ok=True)

    initial_data = {
        "connections": [
            {"address": "http://localhost:4242", "token": "existing_token", "auth_type": "sso"}
        ]
    }
    with open(temp_token_file, 'w') as f:
        toml.dump(initial_data, f)

    write_token_to_file("https://another.server.com", "another_token_789", "sso", token_file_path=temp_token_file)

    with open(temp_token_file, 'r') as f:
        data = toml.load(f)

    expected_connections = [
        {"address": "http://localhost:4242", "token": "existing_token", "auth_type": "sso"},
        {"address": "https://another.server.com", "token": "another_token_789", "auth_type": "sso"}
    ]
    assert sorted(data["connections"], key=lambda x: x['address']) == sorted(expected_connections, key=lambda x: x['address'])


def test_write_token_to_file_add_multiple_new_connections(temp_token_file: Path):
    """
    Test case 4: Add another new connection after previous additions.
    """
    # Ensure parent directory exists for initial file creation
    temp_token_file.parent.mkdir(exist_ok=True)

    initial_data = {
        "connections": [
            {"address": "http://localhost:4242", "token": "existing_token", "auth_type": "sso"}
        ]
    }
    with open(temp_token_file, 'w') as f:
        toml.dump(initial_data, f)

    write_token_to_file("https://another.server.com", "another_token_789", "sso", token_file_path=temp_token_file)
    write_token_to_file("https://yet.another.server.com", "yet_another_token_000", "classic", token_file_path=temp_token_file)

    with open(temp_token_file, 'r') as f:
        data = toml.load(f)

    expected_connections = [
        {"address": "http://localhost:4242", "token": "existing_token", "auth_type": "sso"},
        {"address": "https://another.server.com", "token": "another_token_789", "auth_type": "sso"},
        {"address": "https://yet.another.server.com", "token": "yet_another_token_000", "auth_type": "classic"}
    ]
    assert sorted(data["connections"], key=lambda x: x['address']) == sorted(expected_connections, key=lambda x: x['address'])


def test_write_token_to_file_corrupt_file_handling(temp_token_file: Path):
    """
    Test case for handling a corrupted TOML file.
    It should essentially overwrite it with the new data.
    """
    # Ensure parent directory exists for initial file creation
    temp_token_file.parent.mkdir(exist_ok=True)

    with open(temp_token_file, 'w') as f:
        f.write("[[connections]\naddress = \"corrupted\"\n token = \"invalid\"\n\nINVALID TOML HERE")

    write_token_to_file("http://localhost:4242", "new_token_for_corrupt", "sso", token_file_path=temp_token_file)

    with open(temp_token_file, 'r') as f:
        data = toml.load(f)

    expected_data = {
        "connections": [
            {"address": "http://localhost:4242", "token": "new_token_for_corrupt", "auth_type": "sso"}
        ]
    }
    assert data == expected_data
import os
import stat
from pathlib import Path

import toml


class AuthConnection:
    """Represents a single connection configuration."""
    def __init__(self, address: str, token: str, auth_type: str):
        self.address = address
        self.token = token
        self.auth_type = auth_type

    def to_dict(self):
        """Converts the connection object to a dictionary."""
        return {
            "address": self.address,
            "token": self.token,
            "auth_type": self.auth_type
        }

class TokenFileData:
    """Manages the data within the tokens.toml file."""
    def __init__(self, token_file_path: Path | None = None):
        if token_file_path is None:
            home_dir = Path.home()
            token_dir = home_dir / ".ppm"
            token_file_path = token_dir / "tokens.toml"
        self.token_file_path = token_file_path
        self.connections = []

        # Load connections only if the file exists and is not empty.
        if self.token_file_path.exists() and os.stat(self.token_file_path).st_size > 0:
            try:
                with open(self.token_file_path, 'r') as f:
                    data = toml.load(f)
                self.connections = [
                    AuthConnection(**conn_dict) for conn_dict in data.get("connections", [])
                ]
            except Exception as e:
                print(f"Warning: Unable to parse token file, it will be overwritten. Error: {e}")
                self.connections = []

    def add_connection(self, address: str, token: str, auth_type: str):
        """Adds a new connection object to the list."""
        self.connections.append(AuthConnection(address, token, auth_type))

    def find_connection(self, address: str) -> str | None:
        """Finds a token by its connection address."""
        for conn in self.connections:
            if conn.address == address:
                return conn.token
        return None

    def to_toml_dict(self):
        """Converts the entire data structure to a dictionary for TOML serialization."""
        return {"connections": [conn.to_dict() for conn in self.connections]}

def write_token_to_file(ppm_url: str, ppm_token: str, auth_type: str, token_file_path: Path | None = None) -> None:
    """
    Writes or updates a token in the specified TOML file.
    """
    if token_file_path is None:
        home_dir = Path.home()
        token_dir = home_dir / ".ppm"
        token_file = token_dir / "tokens.toml"
    else:
        token_file = token_file_path

    token_file.parent.mkdir(mode=0o700, parents=True, exist_ok=True)

    token_data = TokenFileData(token_file_path=token_file)

    connection_found = False
    for conn in token_data.connections:
        if conn.address == ppm_url:
            conn.token = ppm_token
            conn.auth_type = auth_type
            connection_found = True
            break

    if not connection_found:
        token_data.add_connection(ppm_url, ppm_token, auth_type)

    # Write the updated data back to the file.
    try:
        with open(token_file, 'w') as f:
            toml.dump(token_data.to_toml_dict(), f)
        os.chmod(token_file, stat.S_IRUSR | stat.S_IWUSR)
    except Exception as e:
        raise IOError(f"Unable to write token file: {e}") from e

    print(f"PPM token saved to {token_file}")

from pathlib import Path

def freeds_config_file_path() -> Path:
    return Path.home() / ".freeds"
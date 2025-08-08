import os
from pathlib import Path
from typing import Any, Optional

import yaml

import freeds.utils.log as log
from freeds.utils.boot import freeds_config_file_path

logger = log.setup_logging(__name__)


class ConfigFile:
    """Class to facade single config file from the source dirs "locals" or "configs"""

    def __init__(self, file_path: Path, data: Optional[dict[str, Any]] = None) -> None:
        self.source_file_path = file_path
        self.config_name = file_path.stem
        self.source = file_path.parent.name  # locals or configs
        self.data: Optional[dict[str, Any]] = data

    def load(self) -> None:
        if not self.source_file_path.exists():
            raise FileNotFoundError(f"Config file {self.source_file_path} does not exists.")
        with open(self.source_file_path, "r") as file:
            data: dict[str, Any] = yaml.safe_load(file)
            self.data = data
        self.validate()
        if self.data is None:
            raise ValueError(f"Config file malformed or empty (data is None) {self.source_file_path}")

    def validate(self, raise_for_error: bool = True) -> bool:
        """Check that format is valid, returns true if data is None."""
        message = None
        if self.data is None:
            return True

        if message is None and not self.data.get("config"):
            message = "The config has no 'config' root key."

        if raise_for_error and message:
            raise (ValueError(message))
        return message is None

    def set_config(self, data: dict[str, Any]) -> None:
        """Create a new "config" element with content from the provided data, {'config': data}"""
        self.data = {"config": data}

    def get_config(self) -> dict[str, Any]:
        """Get the content of the "config" element in the data"""
        if self.data is None:
            self.load()
        data: dict[str, Any] = self.data["config"]  # type: ignore[index]
        return data

    def write(self, file_path: Optional[Path] = None) -> Path:
        """Write config to a new location location or overwrite to source file if no location provided."""
        if self.data is None:
            raise ValueError("No config was loaded or provided. (self.data is None)")
        self.validate()
        target = file_path if file_path else self.source_file_path

        with open(target, "w") as file:
            yaml.dump(self.data, file, default_flow_style=False)

        return target

    @property
    def is_local(self) -> bool:
        return self.source == "locals"

    @property
    def is_config(self) -> bool:
        return self.source == "configs"


class ConfigSet:
    """Class for scanning multiple root config dirs concluding a single set of config files.
    Later scanned of same type overrides earlier.
    Locals always overrides configs of the same name."""

    def __init__(self) -> None:
        self.configs: dict[str, ConfigFile] = {}
        self.locals: dict[str, ConfigFile] = {}

        # for auditing/debugging:
        self.config_roots: list[Path] = []
        self.all_configs: list[ConfigFile] = []
        self.all_locals: list[ConfigFile] = []

    def add_config(self, config_file: ConfigFile) -> None:
        self.all_configs.append(config_file)
        self.configs[config_file.config_name] = config_file

    def add_local(self, config_file: ConfigFile) -> None:
        self.all_locals.append(config_file)
        self.locals[config_file.config_name] = config_file

    def list_files(self, root_dir: Path) -> list[Path]:
        result = list([f for f in (root_dir / "locals").iterdir()])
        result.extend(list([f for f in (root_dir / "configs").iterdir()]))
        return [file for file in result if file.suffix in {".yaml", ".yml"} and file.is_file()]

    def scan(self, config_root_path: Path) -> None:
        self.config_roots.append(config_root_path)
        for f in self.list_files(config_root_path):
            cfg = ConfigFile(f)
            if cfg.is_config:
                self.add_config(cfg)
            else:
                self.add_local(cfg)

    def config_set(self) -> dict[str, ConfigFile]:
        result = self.configs.copy()
        result.update(self.locals)
        return result


def freeds_root() -> Path:
    if "FREEDS_ROOT_PATH" in os.environ:
        return Path(os.environ["FREEDS_ROOT_PATH"])
    file_path = freeds_config_file_path()
    if not file_path.exists():
        raise FileNotFoundError("Root config file not found: {file_path}. Run freeds-setup.")
    config_file = ConfigFile(file_path=file_path)
    cfg = config_file.get_config()
    return Path(cfg["root"])


def freeds_config_set() -> ConfigSet:
    """Get the freeds config set (from config folder in the root freeds folder)."""
    cfg_dir = ConfigSet()
    cfg_dir.scan(freeds_root() / "config")
    return cfg_dir


def get_current_config_set() -> ConfigSet:
    """get all configured configs, which for now is only freeds"""
    return freeds_config_set()


def get_config(config_name: str) -> Optional[ConfigFile]:
    """Get config object for the config_name"""
    cfg_set = get_current_config_set().config_set()
    cfg = cfg_set.get(config_name)
    cfg.load()
    return cfg


def set_config(config_name: str, data: dict[str, Any]) -> None:
    """Set a config in the file, files are written to locals, the entire content is replaced."""
    file_path = freeds_root() / "config" / "locals" / (config_name + ".yaml")
    cfg_set = get_current_config_set()
    cfg: ConfigFile
    if config_name in cfg_set.config_set().keys():
        cfg = cfg_set.config_set()[config_name]
        cfg.set_config(data)
    else:
        cfg = ConfigFile(file_path=file_path, data=data)
    cfg.write(file_path=file_path)

if __name__ == '__main__':
    print(get_current_config_set())
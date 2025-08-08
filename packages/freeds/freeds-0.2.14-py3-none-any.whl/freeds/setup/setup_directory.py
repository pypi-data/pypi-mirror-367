from pathlib import Path
import sys
import git
import yaml

import freeds.setup.utils as utils
from freeds.utils.boot import freeds_config_file_path
import freeds.utils.log as log

logger = log.setup_logging(__name__)


def prompt_continue(user_dir: Path, this_dir: Path) -> bool:
    return utils.prompt_yesno(
        description=(
            f"A config file '.freeds' will be created in your user directory: {str(user_dir)}.\n"
            f"No other changes will be made outside the current folder: {str(this_dir)}."
        ),
        question="Shall we proceed",
    )


def prompt_overwrite_config_file(file: Path) -> bool:
    if not file.exists():
        return True
    return utils.prompt_yesno(
        description=f"The freeds config file already exists: {str(file)}.", question="Overwrite existing config"
    )


def setup_root_dir() -> bool:
    utils.log_header("Setting up the FreeDS root directory", "-")
    root_path = Path.cwd()

    if not prompt_continue(user_dir=Path.home(), this_dir=root_path):
        return False

    freeds_file_path = freeds_config_file_path()
    if prompt_overwrite_config_file(freeds_file_path):
        cfg = {"config": {"root": str(root_path)}}
        with open(freeds_file_path, "w") as f:
            yaml.dump(cfg, f, default_flow_style=False)
            logger.info(f"✅ Wrote config file: {freeds_file_path}")
    else:
        with open(freeds_file_path, "r") as file:
            config: dict[str, str] = yaml.safe_load(file)
            root_path = Path(config.get('config',{}).get('root'))
            if root_path is None:
                logger.error(f"❌ could not read config root from: {config}")
                return 1
            else:
                logger.info(f"✅ Loaded config file: {freeds_file_path}")

    logger.info(f"FreeDS root path: {root_path}")


    git_repos = {
        "freeds-config": "https://github.com/jens-koster/freeds-config.git",
        "the-free-data-stack": "https://github.com/jens-koster/the-free-data-stack.git",
        "freeds-lab-databrickish": "https://github.com/jens-koster/freeds-lab-databrickish.git",
    }

    tfds_repo_root = root_path / "the-free-data-stack"

    logger.info("Cloning missing git repos...")
    for name, url in git_repos.items():

        if (root_path / name).exists():
            logger.info(f"✅ Repo {name} already exists, skipping.")
            continue
        logger.info(f"Cloning repo: {url} into {name}...")
        logger.info(f"✅ Repo {name} cloned.")
        git.Repo.clone_from(url, name)

    logger.info("Creating directory structure")
    paths = [
        "config",
        "config/locals",
        "airflow",
        "airflow/logs",
        "postgres",
        "spark",
        "data/minio",
        "data/spark",
        "data/postgres",
        "data/local-pypi",
    ]
    for path in [(root_path / p) for p in paths]:
        logger.info(f"Creating {path}")
        path.mkdir(parents=True, exist_ok=True)

    # Airflow
    airflow_symlink_root = root_path / "airflow"
    airflow_target_root = tfds_repo_root / "airflow"
    utils.relink(symlink=airflow_symlink_root / "dags", target=airflow_target_root / "dags")
    utils.relink(symlink=airflow_symlink_root / "config", target=airflow_target_root / "config")
    utils.relink(symlink=airflow_symlink_root / "plugins", target=airflow_target_root / "plugins")

    # postgres
    utils.relink(symlink=root_path / "postgres" / "init", target=tfds_repo_root / "postgres" / "init")

    # spark
    spark_root = root_path / "spark"
    utils.relink(symlink=spark_root / "conf", target=tfds_repo_root / "spark" / "conf")
    utils.relink(symlink=spark_root / "jars", target=tfds_repo_root / "spark" / "jars")

    logger.info("Setting up config dir")
    config_path = root_path / "config"
    utils.relink(symlink=config_path / "configs", target=root_path / "freeds-config" / "configs")

    local_files = ["s3.yaml", "minio.yaml", "airflow.yaml"]

    for file in local_files:
        utils.soft_copy(
            source=config_path / "configs" / file,
            target=config_path / "locals" / file,
        )

    utils.log_header(title="🟢 Directory setup completed successfully 🌟", char=" ")
    return True


if __name__ == "__main__":
    setup_root_dir()

import typer

from freeds.cli.helpers.stackutils import get_current_stack_name, get_stack_names
from freeds.config import get_config, set_config

cfg_app = typer.Typer(help="Manage freeds stacks.")


@cfg_app.command()  # type: ignore
def ls() -> None:
    """List all stacks."""

    cfg = get_config("stacks")
    current_stack = get_current_stack_name()
    if current_stack is None:
        typer.echo("No current stack set,use 'freeds setstack <name>' to set one.")
    for stack in cfg.keys():
        if stack == current_stack:
            typer.echo(f"** stack: {stack} ** (current)")
        else:
            typer.echo(f"stack: {stack}")
        for service in cfg[stack].get("plugins", []):
            typer.echo(f"  - {service}")


@cfg_app.command()  # type: ignore
def set(
    stack: str = typer.Argument(..., help="Stack name to set as current"),
) -> None:
    """Set freeds to use the provided stack."""
    if stack not in get_stack_names():
        print(f"Error: Stack '{stack}' not found in config, use `freeds ls` to see available stacks.")

    config = {
        "annotation": "the current stack for freeds cli, use setstack to change it, editing here is fine too",
        "config": {"current_stack": stack},
    }
    set_config("currentstack", config)
    print(f"Current stack set to '{stack}'.")

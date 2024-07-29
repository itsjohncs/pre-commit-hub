from rich import print as rprint


def error(message: str) -> None:
    """Print an error message in red."""
    rprint(f"[bold red]error:[/bold red] {message}")


def warning(message: str) -> None:
    rprint(f"[yellow]warning:[/yellow] {message}")

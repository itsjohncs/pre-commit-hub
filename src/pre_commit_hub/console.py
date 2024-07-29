from rich import print as rprint


def error(message: str) -> None:
    """Print an error message in red."""
    rprint(f"[bold red]Error:[/bold red] {message}")

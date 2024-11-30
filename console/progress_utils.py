from time import sleep

from rich.console import Console
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)

console = Console()


def show_step_progress(description: str, action, *args):
    """
    Affiche une barre de progression avec un spinner pendant l'exécution d'une action.

    Args:
        description (str): La description de l'étape en cours.
        action (Callable): La fonction à exécuter.
        *args: Les arguments à passer à la fonction.

    Returns:
        Le résultat de la fonction `action`.
    """
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(complete_style="green"),
        TimeElapsedColumn(),
        console=console,
        transient=False,
    ) as progress:
        task = progress.add_task(description, total=1)
        result = action(*args)
        progress.update(task, completed=1, description=f"[green]✓ {description}")
        sleep(0.1)
    return result

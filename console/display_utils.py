from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

def display_metrics(total_cost: float, total_benefit: float, execution_time: float, total_memory_used: float):
    """Affiche les métriques globales."""
    metrics_table = Table(box=box.ROUNDED, expand=True)
    metrics_table.add_column("Métrique", style="cyan")
    metrics_table.add_column("Valeur", style="green", justify="right")

    metrics_table.add_row("Coût Total", f"{total_cost:.2f} €")
    metrics_table.add_row("Bénéfice Total", f"{total_benefit:.2f} €")
    metrics_table.add_row("Rendement", f"{(total_benefit / total_cost * 100):.2f}%")
    metrics_table.add_row("Temps d'exécution", f"{execution_time:.2f} secondes")
    metrics_table.add_row("Mémoire utilisée", f"{total_memory_used:.2f} MB")

    console.print(Panel(metrics_table, title="Métriques Globales", border_style="cyan"))


def create_best_actions_table(best_actions_data: list[dict]) -> Table:
    """Crée une table pour les actions sélectionnées."""
    best_table = Table(box=box.ROUNDED, expand=True)
    best_table.add_column("Action", style="cyan")
    best_table.add_column("Coût", justify="right", style="green")
    best_table.add_column("Bénéfice", justify="right", style="green")
    best_table.add_column("Rendement", justify="right", style="green")

    for action in best_actions_data:
        best_table.add_row(
            action['Action'],
            f"{action['Coût (€)']:.2f} €",
            f"{action['Bénéfice (€)']:.2f} €",
            f"{action['Bénéfice (%)']:.1f}%"
        )

    return best_table


def create_ignored_actions_table(ignored_actions_data: list[dict]) -> Table:
    """Crée une table pour les actions ignorées."""
    ignored_table = Table(box=box.ROUNDED, expand=True)
    ignored_table.add_column("Action", style="red")
    ignored_table.add_column("Raison", style="yellow")

    for action in ignored_actions_data:
        ignored_table.add_row(action['Action'], action['Raisons'])

    return ignored_table


def display_combined_tables(best_table: Table, ignored_table: Table):
    """Affiche les deux tables côte à côte."""
    container = Table.grid(expand=True)
    container.add_column("Left", justify="left", ratio=1)
    container.add_column("Right", justify="left", ratio=1)

    container.add_row(
        Panel(best_table, title="Actions Sélectionnées", border_style="cyan"),
        Panel(ignored_table, title="Actions Ignorées", border_style="red")
    )

    console.print("\n", container)


def display_results(best_actions_data, ignored_actions_data, total_cost, total_benefit, execution_time, total_memory_used):
    """Affiche les résultats dans la console."""
    console.print("\n[bold cyan]Résultats de l'analyse[/]")

    # Affiche les métriques globales
    display_metrics(total_cost, total_benefit, execution_time, total_memory_used)

    # Crée les tables des actions
    best_table = create_best_actions_table(best_actions_data)
    ignored_table = create_ignored_actions_table(ignored_actions_data)

    # Affiche les tables combinées
    display_combined_tables(best_table, ignored_table)

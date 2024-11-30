import sys
import time
import webbrowser
from typing import List, Tuple

from rich import box
from rich.align import Align
from rich.console import Console
from rich.panel import Panel

from action_loader import load_actions
from console.display_utils import display_results
from console.progress_utils import show_step_progress
from dashboard.app import create_dashboard
from models.action import Action

# Configuration de la console pour l'affichage
console = Console()

# ====================
# Fonctions de calcul des combinaisons
# ====================

def generate_combinations(actions: List[Action]) -> List[List[Action]]:
    """Génère toutes les combinaisons possibles d'actions en utilisant une approche itérative."""
    all_combinations = [[]]
    for action in actions:
        new_combinations = [combination + [action] for combination in all_combinations]
        all_combinations.extend(new_combinations)
    return all_combinations


def get_combinations_with_memory(actions: List[Action]) -> Tuple[List[List[Action]], float]:
    """Calcule les combinaisons et mesure leur empreinte mémoire en MB."""
    combinations = generate_combinations(actions)
    memory_size = sys.getsizeof(combinations) / (1024 * 1024)
    return combinations, memory_size

# ====================
# Fonctions d'optimisation
# ====================

def find_best_combination(actions: List[Action], max_budget: float) -> Tuple[List[Action], float, float, float]:
    """
    Recherche la combinaison optimale d'actions selon les critères suivants:
    - Respect du budget maximum
    - Maximisation du bénéfice total
    
    Retourne: (meilleure_combinaison, coût_total, bénéfice_total, mémoire_utilisée)
    """
    if not actions:
        return [], 0.0, 0.0, 0.0

    combinations, memory_used = get_combinations_with_memory(actions)
    best_combination = []
    best_benefit = 0
    best_cost = 0

    for combination in combinations:
        if Action.is_portfolio_within_budget(combination, max_budget):
            benefit = Action.total_portfolio_benefit(combination)
            cost = Action.total_portfolio_cost(combination)

            if benefit > best_benefit:
                best_combination = combination
                best_benefit = benefit
                best_cost = cost

    return best_combination, best_cost, best_benefit, memory_used

# ====================
# Fonctions de mesure de performance
# ====================

def measure_performance(actions_list: List[Action], max_budget: float) -> Tuple[List[int], List[float], List[float], float, float]:
    """
    Analyse les performances de l'algorithme en mesurant:
    - Le temps d'exécution pour différentes tailles d'entrée
    - L'utilisation de la mémoire
    """
    n_values = []
    times = []
    memories = []
    total_time = 0
    max_memory_used = 0

    for n in range(1, len(actions_list) + 1):
        current_actions = actions_list[:n]
        start_time = time.time()
        _, _, _, memory_used = find_best_combination(current_actions, max_budget)
        elapsed_time = time.time() - start_time

        n_values.append(n)
        times.append(elapsed_time)
        memories.append(memory_used)
        
        total_time += elapsed_time
        max_memory_used = max(max_memory_used, memory_used)

    return n_values, times, memories, total_time, max_memory_used

# ====================
# Fonctions d'affichage
# ====================

def print_header():
    """Affiche l'en-tête de l'application avec le style approprié."""
    title = Align.center(
        "[bold cyan]AlgoInvest&Trade[/]\n[white]Optimisation d'investissements par force brute[/]",
        vertical="middle"
    )
    console.print(Panel(title, box=box.ROUNDED, style="cyan", padding=(1, 2)))
    console.print("\n")

# ====================
# Fonction principale
# ====================

def main():
    """Point d'entrée principal du programme."""
    FILE_PATH = "data/actions.csv"
    MAX_BUDGET = 500

    console.clear()
    print_header()

    # Chargement et validation des données
    actions, invalid_actions, errors = show_step_progress(
        "Chargement des données",
        load_actions,
        FILE_PATH
    )

    if errors or not actions:
        console.print("\n[red]❌ Erreur lors du chargement des données :[/]")
        for error in errors:
            console.print(f"[red]  → {error}[/]")
        return

    # Recherche de la solution optimale
    best_actions, total_cost, total_benefit, _ = show_step_progress(
        "Recherche de la meilleure combinaison",
        find_best_combination,
        actions, MAX_BUDGET
    )

    # Analyse des performances
    n_values, times, memories, execution_time, total_memory_used = show_step_progress(
        "Analyse des performances",
        measure_performance,
        actions, MAX_BUDGET
    )

    # Préparation des données pour l'affichage
    ignored_actions_data = [{
        'Action': action.name,
        'Raisons': ', '.join(reasons)
    } for action, reasons in invalid_actions]

    best_actions_data = [{
        'Action': action.name,
        'Coût (€)': action.cost,
        'Bénéfice (€)': action.calculate_benefit(),
        'Bénéfice (%)': action.benefit_percent
    } for action in best_actions]

    # Affichage des résultats
    display_results(
        best_actions_data,
        ignored_actions_data,
        total_cost,
        total_benefit,
        execution_time,
        total_memory_used
    )

    # Lancement du dashboard
    console.print("\n[cyan]Lancement du dashboard...[/]")
    app = create_dashboard(
        best_actions_data,
        ignored_actions_data,
        total_cost,
        total_benefit,
        n_values,
        times,
        memories,
        execution_time,
        total_memory_used
    )

    webbrowser.open_new("http://127.0.0.1:8050/")
    console.print(Panel(
        "[bold green]Dashboard prêt ![/]\n"
        "[cyan]→ http://127.0.0.1:8050[/]\n"
        "[white]Appuyez sur Ctrl+C pour quitter le programme[/]",
        box=box.ROUNDED,
        title="Status",
        style="cyan"
    ))

    app.run(debug=True, use_reloader=False)

if __name__ == "__main__":
    main()

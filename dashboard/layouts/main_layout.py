
import dash_bootstrap_components as dbc
from dash import html


def create_main_layout(total_report, global_performance, best_actions_table,
                      ignored_actions_table, complexity_graphs, reports):
    """Crée le layout principal du dashboard."""
    layout = dbc.Container([
        html.H1("Dashboard d'optimisation par force brute", className="my-4"),
        total_report,
        html.H2("Performance globale de l'algorithme", className="my-4"),
        global_performance,
        html.H2("Actions ignorées", className="my-4"),
        ignored_actions_table,
        html.H2("Meilleure combinaison d'actions", className="my-4"),
        best_actions_table,
        html.H2("Complexité de l'algorithme", className="my-4"),
        complexity_graphs
    ], fluid=True)
    
    return layout
import dash_bootstrap_components as dbc
from dash import html


def create_temporal_report(execution_time: float):
    """Crée le rapport de complexité temporelle."""
    return dbc.CardBody([
        html.H4("Compte rendu de la complexité temporelle"),
        html.P([
            f"Pour analyser l'ensemble maximal de 20 actions, l'algorithme a nécessité environ {execution_time:.2f} secondes. ",
            "Le graphique de complexité temporelle montre une augmentation exponentielle du temps ",
            "d'exécution à mesure que le nombre d'actions augmente. Cette progression est particulièrement ",
            "visible à partir de 17-18 actions, où le temps de calcul commence à augmenter significativement. "
        ])
    ])


def create_spatial_report(total_memory_used: float):
    """Crée le rapport de complexité spatiale."""
    return dbc.CardBody([
        html.H4("Compte rendu de la complexité spatiale"),
        html.P([
            f"Le pic de mémoire maximale utilisé pour les 20 actions est de {total_memory_used:.2f} MB. ",
            "Le graphique montre une augmentation exponentielle de l'utilisation de la mémoire ",
            "à mesure que le nombre d'actions augmente. Cette croissance est due au nombre ",
            "de combinaisons possibles qui augmente exponentiellement avec chaque action supplémentaire, ",
            "nécessitant plus d'espace mémoire pour stocker toutes ces combinaisons."
        ])
    ])


def create_report_sections(execution_time: float, total_memory_used: float):
    """Crée les sections de rapport."""
    return [
        dbc.Card(
            create_temporal_report(execution_time),
            color="light",
            className="mb-4"
        ),
        dbc.Card(
            create_spatial_report(total_memory_used),
            color="light",
            className="mb-4"
        )
    ]
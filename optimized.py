# Importations
import os
import sys
import time
import webbrowser

import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objs as go
from dash import Dash, dash_table, dcc, html
from dash.dependencies import Input, Output, State
from InquirerPy import prompt

from models.action import Action

WALLET = 500
DATA_FOLDER = "data"

# Décisions d'achat de Sienna
SIENNA_DECISIONS = {
    "dataset_1.csv": {
        "total_cost": 498.76,
        "total_return": 196.61
    },
    "dataset_2.csv": {
        "total_cost": 489.24,
        "total_return": 193.78
    }
}


def load_actions(file_path: str) -> tuple[list[Action], list[Action], list[str]]:
    """Charge et valide les actions depuis un fichier CSV."""
    try:
        data = pd.read_csv(file_path, header=0)
        if data.shape[1] < 3:
            raise ValueError("Le fichier CSV doit contenir au moins trois colonnes : nom, coût, et bénéfice.")

        valid_actions = []
        invalid_actions = []
        errors = []
        
        for _, row in data.iterrows():
            try:
                name = row.iloc[0]
                cost = float(row.iloc[1])
                benefit_percent = float(str(row.iloc[2]).strip('%'))
                
                action = Action(name, cost, benefit_percent)
                if action.is_valid():
                    valid_actions.append(action)
                else:
                    invalid_actions.append(action)
                    errors.append(f"Action invalide {name}: {', '.join(action.get_invalid_reasons())}")
            
            except ValueError as e:
                errors.append(f"Erreur de conversion pour {name}: {e}")
                
        return valid_actions, invalid_actions, errors
    except Exception as e:
        return [], [], [f"Erreur lors du chargement du fichier: {str(e)}"]

def measure_performance(actions: list[Action], wallet: float):
    n_values = []
    cumulative_times = []
    memories = []
    total_cost = 0
    total_benefit = 0
    selected_actions = []
    cumulative_time = 0
    first_time = None

    for n in range(1, len(actions) + 1):
        current_action = actions[n-1]
        start_time = time.time()
        
        if total_cost + current_action.cost <= wallet:
            selected_actions.append(current_action)
            total_cost += current_action.cost
            total_benefit += current_action.benefit

        end_time = time.time()
        
        elapsed_time = (end_time - start_time) * 1000
        if first_time is None:
            first_time = elapsed_time
            cumulative_time = 0  
        else:
            cumulative_time += elapsed_time 
            
        memory_used = sum(sys.getsizeof(action) for action in selected_actions) / (1024 * 1024)
        
        n_values.append(n)
        cumulative_times.append(cumulative_time)
        memories.append(memory_used)

    return selected_actions, total_cost, total_benefit, cumulative_times, memories, n_values

def get_sienna_comparison(file_name: str, total_cost: float, total_benefit: float):
    """Calcule la comparaison avec les décisions de Sienna"""
    if file_name not in SIENNA_DECISIONS:
        return None
        
    sienna_data = SIENNA_DECISIONS[file_name]
    our_roi = (total_benefit / total_cost) * 100 if total_cost > 0 else 0
    sienna_roi = (sienna_data['total_return'] / sienna_data['total_cost']) * 100
    
    return {
        'cost_comparison': {
            'our_cost': total_cost,
            'sienna_cost': sienna_data['total_cost'],
            'difference': ((sienna_data['total_cost'] - total_cost) / sienna_data['total_cost']) * 100
        },
        'benefit_comparison': {
            'our_benefit': total_benefit,
            'sienna_benefit': sienna_data['total_return'],
            'difference': ((total_benefit - sienna_data['total_return']) / sienna_data['total_return']) * 100
        },
        'roi_comparison': {
            'our_roi': our_roi,
            'sienna_roi': sienna_roi,
            'difference': our_roi - sienna_roi
        }
    }

# Composants d'interface utilisateur
def create_data_controls(csv_files, selected_file):
    """Crée la section de contrôle des données"""
    return dbc.Row([
        # Sélection du Dataset
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.I(className="fas fa-database me-2"),
                    html.H5("Sélection du jeu de données", className="mb-0")
                ], className="bg-black text-white border-bottom-0 d-flex align-items-center"),
                dbc.CardBody([
                    dbc.Select(
                        id='file-selector',
                        options=[{'label': f, 'value': f} for f in csv_files],
                        value=selected_file,
                        className="mb-0"
                    )
                ], className="pt-2 pb-2")
            ], className="h-100 shadow-sm")
        ], width=6),
        
        # Contrôle du Budget
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.I(className="fas fa-euro-sign me-2"),
                    html.H5("Budget", className="mb-0")
                ], className="bg-black text-white border-bottom-0 d-flex align-items-center"),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            dbc.Input(
                                id='budget-input',
                                type='number',
                                value=WALLET,
                                min=0,
                                step=1
                            )
                        ], width=9),
                        dbc.Col([
                            dbc.Button(
                                "Valider",
                                id='validate-budget',
                                color="dark",
                                className="w-100"
                            )
                        ], width=3)
                    ], className="g-2 align-items-center")
                ], className="pt-2 pb-2")
            ], className="h-100 shadow-sm")
        ], width=6)
    ], className="mb-4")

def create_data_overview(valid_actions, invalid_actions, total_actions_count):
    """Crée la vue d'ensemble des données"""
    # Calcul des pourcentages pour le graphique en camembert
    valid_percentage = len(valid_actions) / total_actions_count * 100 if total_actions_count > 0 else 0
    invalid_percentage = len(invalid_actions) / total_actions_count * 100 if total_actions_count > 0 else 0

    # Graphique en camembert
    pie_chart_card = dbc.Card([
        dbc.CardBody([
            dcc.Graph(
                figure={
                    'data': [
                        go.Pie(
                            labels=['Valides', 'Invalides'],
                            values=[valid_percentage, invalid_percentage],
                            marker=dict(colors=['green', 'red']),
                            hole=.3
                        )
                    ],
                    'layout': go.Layout(
                        title='Répartition des actions',
                        showlegend=True
                    )
                }
            )
        ])
    ], className="h-100 shadow-sm")

    return dbc.Card([
        dbc.CardHeader([
            html.I(className="fas fa-binoculars me-2"),
            "Vue d'ensemble"
        ], className="bg-black text-white"),
        dbc.CardBody([
            # Statistiques principales
            dbc.Row([
                # Actions totales
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.Div([
                                html.I(className="fas fa-table me-2", style={'fontSize': '24px'}),
                                html.H4(f"{total_actions_count}", className="d-inline-block mb-0"),
                            ], className="d-flex align-items-center"),
                            html.P("Actions totales", className="text-muted mb-0 mt-2"),
                            html.Div([
                                html.I(
                                    className="fas fa-check-circle me-2" if valid_percentage >= 90 else
                                    "fas fa-exclamation-circle me-2" if valid_percentage >= 70 else
                                    "fas fa-times-circle me-2",
                                    style={'color': 'green' if valid_percentage >= 90 else
                                           'orange' if valid_percentage >= 70 else
                                           'red'}
                                ),
                                html.Small(
                                    "Qualité des données optimale" if valid_percentage >= 90 else
                                    "Qualité des données acceptable" if valid_percentage >= 70 else
                                    "Un nettoyage des données est recommandé",
                                    className="text-success" if valid_percentage >= 90 else
                                    "text-warning" if valid_percentage >= 70 else
                                    "text-danger"
                                )
                            ], style={"marginTop": "10px"}),
                        ]),
                    ]),
                ], width=4),

                # Actions valides
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.Div([
                                html.I(className="fas fa-check-circle me-2", style={'fontSize': '24px'}),
                                html.H4(f"{len(valid_actions)}", className="d-inline-block mb-0"),
                            ], className="d-flex align-items-center"),
                            html.P("Actions valides", className="text-muted mb-0 mt-2"),
                            html.Div([
                                html.Small(
                                    f"Taux de validité: {valid_percentage:.1f}%",
                                    className="text-success"
                                ),
                                dbc.Progress(
                                    value=valid_percentage,
                                    color="success",
                                    style={"height": "4px", "marginTop": "5px"}
                                )
                            ])
                        ]),
                    ]),
                ], width=4),

                # Actions invalides
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.Div([
                                html.I(className="fas fa-exclamation-circle me-2", style={'fontSize': '24px'}),
                                html.H4(f"{len(invalid_actions)}", className="d-inline-block mb-0"),
                            ], className="d-flex align-items-center"),
                            html.P("Actions invalides", className="text-muted mb-0 mt-2"),
                            html.Div([
                                html.Small(
                                    f"Taux d'invalidité: {invalid_percentage:.1f}%",
                                    className="text-danger"
                                ),
                                dbc.Progress(
                                    value=invalid_percentage,
                                    color="danger",
                                    style={"height": "4px", "marginTop": "5px"}
                                )
                            ])
                        ]),
                    ]),
                ], width=4),
            ], className="mb-4"),

            # Graphique en camembert et cards d'invalidité
            dbc.Row([
                dbc.Col([
                    pie_chart_card
                ], width=6),

                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.Div([
                                html.I(className="fas fa-times-circle me-2", style={'fontSize': '24px'}),
                                html.H4("Critères d'invalidité", className="d-inline-block mb-0"),
                            ], className="d-flex align-items-center"),
                            html.Ul([
                                html.Li("Le coût doit être positif"),
                                html.Li("Le bénéfice doit être positif"),
                                html.Li(f"Le coût ne doit pas dépasser le budget ({WALLET}€)"),
                            ], className="small text-muted mb-0")
                        ])
                    ], className="h-fit shadow-sm "),

                    dbc.Card([
                        dbc.CardBody([
                            html.Div([
                                html.I(className="fas fa-exclamation-triangle me-2", style={'fontSize': '24px'}),
                                html.H4("Raisons principales d'invalidité", className="d-inline-block mb-0"),
                            ], className="d-flex align-items-center"),
                            create_invalidity_reasons_summary(invalid_actions)
                        ])
                    ], className="h-fit shadow-sm")
                ], width=6, className="d-flex flex-column gap-4")
            ])
        ])
    ], className="h-100 shadow-sm")
def create_invalidity_reasons_summary(invalid_actions):
    """Crée un résumé des raisons d'invalidité les plus fréquentes"""
    # stock de toutes les raisons d'invalidité
    all_reasons = []
    for action in invalid_actions:
        all_reasons.extend(action.get_invalid_reasons())
    
    # Nbr d'occurrences de chaque raison
    reason_counts = {}
    for reason in all_reasons:
        reason_counts[reason] = reason_counts.get(reason, 0) + 1
    
    
    sorted_reasons = sorted(reason_counts.items(), key=lambda x: x[1], reverse=True)
    
    # Créer la liste des raisons avec leur fréquence
    return html.Ul([
        html.Li([
            f"{reason} ",
            html.Span(f"({count} occurrence{'s' if count > 1 else ''})", 
                     className="text-muted small")
        ]) for reason, count in sorted_reasons
    ], className="small mb-0")

def create_metrics_cards(valid_actions):
    """Crée les cartes d'analyse des coûts et bénéfices"""
    return dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.I(className="fas fa-balance-scale-left me-2"),
                    "Analyse des Coûts"
                ], className="bg-black text-white"),
                dbc.CardBody([
                    create_metric_row(
                        values=[
                            min([a.cost for a in valid_actions]),
                            max([a.cost for a in valid_actions]),
                            sum([a.cost for a in valid_actions])/len(valid_actions)
                        ],
                        labels=["Coût minimum", "Coût maximum", "Coût moyen"],
                        icon="fas fa-euro-sign",
                        format_str="{:.2f}€"
                    )
                ])
            ], className="h-100 shadow-sm")
        ], width=6),
        
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.I(className="fas fa-chart-line me-2"),
                    "Analyse des Bénéfices"
                ], className="bg-black text-white"),
                dbc.CardBody([
                    create_metric_row(
                        values=[
                            min([a.benefit_percent for a in valid_actions]),
                            max([a.benefit_percent for a in valid_actions]),
                            sum([a.benefit_percent for a in valid_actions])/len(valid_actions)
                        ],
                        labels=["Rendement minimum", "Rendement maximum", "Rendement moyen"],
                        icon="fas fa-percent",
                        format_str="{:.1f}%"
                    )
                ])
            ], className="h-100 shadow-sm")
        ], width=6)
    ])
def create_metric_row(values, labels, icon, format_str):
    """Crée une ligne de métriques sous forme de cartes sans en-tête"""
    return dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.I(className=f"{icon} me-2"),
                        html.H5(format_str.format(value), className="d-inline-block mb-0"),
                    ], className="d-flex align-items-center"),
                    html.P(label, className="text-muted mb-0 mt-2")
                ])
            ], className="h-100 shadow-sm")
        ]) for value, label in zip(values, labels)
    ])

def create_performance_card(title, value, description, icon, color, progress_value=None):
    """Crée une carte de performance avec une barre de progression et un texte en petit format"""
    return dbc.Card([
        dbc.CardBody([
            html.Div([
                html.I(className=f"{icon} me-2", style={'fontSize': '24px'}),
                html.H4(value, className="d-inline-block mb-0"),
            ], className="d-flex align-items-center"),
            html.P(title, className="text-muted mb-0 mt-2"),
            html.Div([
                html.Small(description, className=f"text-{color}"),
                dbc.Progress(
                    value=max(min(progress_value, 100), 5) if progress_value is not None else 0,
                    className="mt-2",
                    color=color,
                    style={"height": "4px"}
                ) if progress_value is not None else None
            ])
        ])
    ], className="h-100 shadow-sm")
    # Composants de visualisation
def create_cost_benefit_chart(selected_actions):
    """Crée le graphique coût-bénéfice"""
    return dbc.Card([
        dbc.CardHeader([
            html.I(className="fas fa-chart-bar me-2"),
            "Analyse Coût/Bénéfice"
        ], className="bg-black text-white"),
        dbc.CardBody([
            dcc.Graph(
                figure={
                    'data': [
                        go.Bar(
                            name='Coût',
                            x=[a.name for a in selected_actions],
                            y=[a.cost for a in selected_actions],
                            marker_color='red'
                        ),
                        go.Bar(
                            name='Bénéfice',
                            x=[a.name for a in selected_actions],
                            y=[a.benefit for a in selected_actions],
                            marker_color='green'
                        )
                    ],
                    'layout': go.Layout(
                        title='Coût et bénéfice des actions sélectionnées',
                        barmode='group',
                        xaxis={'title': 'Actions'},
                        yaxis={'title': 'Valeur (€)'},
                        plot_bgcolor='white',
                        paper_bgcolor='white',
                        height=400
                    )
                }
            )
        ])
    ])


def create_sienna_comparison_section(sienna_metrics):
    """Crée la section de comparaison avec Sienna"""
    return dbc.Card([
        dbc.CardHeader([
            html.I(className="fas fa-balance-scale me-2"),
            "Comparaison avec Sienna"
        ], className="bg-black text-white d-flex align-items-center"),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([create_comparison_card("Coût Total", sienna_metrics['cost_comparison'], True)], width=4),
                dbc.Col([create_comparison_card("Bénéfice Total", sienna_metrics['benefit_comparison'])], width=4),
                dbc.Col([create_comparison_card("ROI", sienna_metrics['roi_comparison'], value_suffix="%")], width=4)
            ])
        ])
    ], className="shadow mb-4")

def create_comparison_card(title, comparison_data, is_cost=False, value_suffix="€"):
    """Crée une carte de comparaison individuelle avec style amélioré et alignement à gauche"""
    our_value = comparison_data['our_cost' if is_cost else 'our_benefit' if 'our_benefit' in comparison_data else 'our_roi']
    sienna_value = comparison_data['sienna_cost' if is_cost else 'sienna_benefit' if 'sienna_benefit' in comparison_data else 'sienna_roi']
    
    # Calcul du pourcentage de différence
    difference = ((our_value - sienna_value) / sienna_value) * 100
    

    arrow_direction = "up" if our_value > sienna_value else "down"
    arrow_color = "red" if (is_cost and arrow_direction == "up") or (not is_cost and arrow_direction == "down") else "green"
    

    absolute_diff = abs(our_value - sienna_value)
    

    icon_class = "fas fa-coins" if is_cost else "fas fa-chart-line" if 'our_benefit' in comparison_data else "fas fa-percent"
    
    return dbc.Card([
        dbc.CardBody([

            html.Div([
                html.I(className=f"{icon_class} me-2"),
                html.H4(title, className="mb-0")
            ], className="d-flex align-items-center mb-3"),
            

            html.Div([

                html.Div([
                    html.Div("Algorithme", className="text-muted mb-1", 
                            style={'fontSize': '0.9rem'}),
                    html.Div(
                        f"{our_value:.2f}{value_suffix}",
                        className="fw-bold",
                        style={'fontSize': '1.2rem'}
                    )
                ], style={
                    'width': '50%',
                    'borderRight': '1px solid #dee2e6',
                    'paddingRight': '15px'
                }),
                
                # Sienna
                html.Div([
                    html.Div("Sienna", className="text-muted mb-1",
                            style={'fontSize': '0.9rem'}),
                    html.Div(
                        f"{sienna_value:.2f}{value_suffix}",
                        className="fw-bold",
                        style={'fontSize': '1.2rem'}
                    )
                ], style={
                    'width': '50%',
                    'paddingLeft': '15px',
                    
                })
            ], className="d-flex justify-content-between align-items-center mb-3"),
            

            html.Hr(className="my-2"),
            html.Div([
                html.I(
                    className=f"fas fa-arrow-{arrow_direction} me-2",
                    style={'color': arrow_color}
                ),
                html.Span(
                    [
                        f"{absolute_diff:.2f}{value_suffix}",
                        html.Span(
                            f" ({'+' if difference > 0 else ''}{difference:.1f}%)",
                            className="ms-1"
                        )
                    ],
                    style={'color': arrow_color, 'fontWeight': 'bold'}
                )
            ])
            
        ], className="p-3")
    ], className="h-100 shadow-sm")

def create_data_tables(selected_actions, invalid_actions):
    """Crée les tableaux d'actions"""
    return dbc.Row([
        dbc.Col([
            create_selected_actions_table(selected_actions)
        ], md=6),
        dbc.Col([
            create_invalid_actions_table(invalid_actions)
        ], md=6)
    ], className="mb-4")

def create_selected_actions_table(selected_actions):
    """Crée le tableau des actions sélectionnées"""
    return dbc.Card([
        dbc.CardHeader([
            html.I(className="fas fa-check-circle me-2"),
            "Actions sélectionnées"
        ], className="bg-black text-white"),
        dbc.CardBody([
            dash_table.DataTable(
                id='selected-actions-table',
                columns=[
                    {'name': 'Nom', 'id': 'name'},
                    {'name': 'Coût (€)', 'id': 'cost'},
                    {'name': 'Bénéfice (€)', 'id': 'benefit'},
                    {'name': 'Rendement (%)', 'id': 'benefit_percent'}
                ],
                data=[{
                    'name': a.name,
                    'cost': f"{a.cost:.2f}",
                    'benefit': f"{a.benefit:.2f}",
                    'benefit_percent': f"{a.benefit_percent:.2f}"
                } for a in selected_actions],
                style_table={'maxHeight': '400px', 'overflowY': 'auto'},
                style_cell={'textAlign': 'left', 'padding': '10px'},
                style_header={
                    'backgroundColor': 'rgb(230, 230, 230)',
                    'fontWeight': 'bold'
                }
            )
        ])
    ])

def create_invalid_actions_table(invalid_actions):
    """Crée le tableau des actions invalides"""
    return dbc.Card([
        dbc.CardHeader([
            html.I(className="fas fa-exclamation-circle me-2"),
            "Actions invalides"
        ], className="bg-black text-white"),
        dbc.CardBody([
            dash_table.DataTable(
                id='invalid-actions-table',
                columns=[
                    {'name': 'Nom', 'id': 'name'},
                    {'name': 'Raisons', 'id': 'reasons'}
                ],
                data=[{
                    'name': action.name,
                    'reasons': ', '.join(action.get_invalid_reasons())
                } for action in invalid_actions],
                style_table={'maxHeight': '400px', 'overflowY': 'auto'},
                style_cell={'textAlign': 'left', 'padding': '10px'},
                style_header={
                    'backgroundColor': 'rgb(230, 230, 230)',
                    'fontWeight': 'bold'
                }
            )
        ])
    ])

def create_complexity_section(times, memories, n_vals, selected_actions):
    """Crée la section de complexité avec une nouvelle organisation des cartes"""
    return dbc.Card([
        dbc.CardHeader([
            html.I(className="fas fa-cogs me-2"),
            "Complexité de l'algorithme"
        ], className="bg-black text-white"),
        dbc.CardBody([

            dbc.Row([

                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.I(className="fas fa-clock me-2"),
                            "Complexité Temporelle",
                            html.Span("O(n)", className="ms-auto")
                        ], className="bg-black text-white d-flex align-items-center justify-content-between"),
                        dbc.CardBody([
                            dcc.Graph(
                                figure=create_complexity_figure(
                                    n_vals[:len(selected_actions)],
                                    times[:len(selected_actions)],
                                    "Temps d'exécution cumulé (ms)",
                                    "blue"
                                )
                            ),
                            html.P([
                                "Ce graphique illustre le temps d'exécution cumulé de notre algorithme Greedy en fonction du nombre d'actions. ",
                                "La croissance linéaire O(n) démontre l'efficacité de notre approche, avec un temps de calcul qui augmente ",
                                "proportionnellement au nombre d'actions analysées."
                            ])
                        ], className="h-100")
                    ], className="mb-4 shadow-sm h-100")
                ], md=6),
                

                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.I(className="fas fa-memory me-2"),
                            "Complexité Spatiale",
                            html.Span("O(n)", className="ms-auto")
                        ], className="bg-black text-white d-flex align-items-center justify-content-between"),
                        dbc.CardBody([
                            dcc.Graph(
                                figure=create_complexity_figure(
                                    n_vals[:len(selected_actions)],
                                    memories[:len(selected_actions)],
                                    "Mémoire utilisée (MB)",
                                    "green"
                                )
                            ),
                            html.P([
                                "Le graphique montre l'utilisation mémoire linéaire de notre algorithme Greedy. ",
                                "L'espace mémoire utilisé croît de manière linéaire (O(n)) avec le nombre d'actions, ",
                                "permettant une gestion efficace des ressources système."
                            ])
                        ], className="h-100")
                    ], className="mb-4 shadow-sm h-100")
                ], md=6)
            ], className="mb-4"),
            

            dbc.Card([
                dbc.CardHeader([
                    html.I(className="fas fa-code-branch me-2"),
                    "Solutions envisagées"
                ], className="bg-black text-white"),
                dbc.CardBody([
                    html.P([
                        "Avant d'opter pour l'algorithme Greedy, nous avons exploré plusieurs approches algorithmiques, ",
                        "chacune présentant ses avantages et limitations :"
                    ]),
                    html.Ul([
                        html.Li([
                            html.Strong("Force brute (Complexités - Temps : O(2ⁿ), Espace : O(2ⁿ)) : "), 
                            "Cette approche teste toutes les combinaisons possibles d'actions. Bien qu'elle garantisse la solution optimale, "
                            "elle devient rapidement impraticable. Pour 30 actions, il faudrait évaluer plus d'un milliard de combinaisons, "
                            "nécessitant un temps de calcul excessif et une importante quantité de mémoire pour stocker toutes les combinaisons."
                        ]),
                        html.Li([
                            html.Strong("Récursivité (Complexités - Temps : O(2ⁿ), Espace : O(2ⁿ)) : "), 
                            "Cette méthode divise le problème en sous-problèmes mais souffre aussi d'une croissance exponentielle. "
                            "Elle présente des risques d'erreurs techniques liées à la mémoire (dépassement de la capacité de stockage temporaire du programme) "
                            "pour les grands ensembles de données."
                        ]),
                        html.Li([
                            html.Strong("Programmation dynamique (Complexités - Temps : O(n×W), Espace : O(n×W)) : "), 
                            "Cette stratégie utilise une matrice 2D pour mémoriser les calculs intermédiaires. Pour un budget W de 500€ et 40 actions, "
                            "elle nécessiterait une matrice de 20 000 cellules. Bien qu'elle garantisse une solution optimale, sa consommation mémoire "
                            "devient problématique pour de grands ensembles de données ou des budgets élevés."
                        ])
                    ])
                ], className="h-100")
            ], className="mb-4 shadow-sm h-100"),
            

            dbc.Card([
                dbc.CardHeader([
                    html.I(className="fas fa-lightbulb me-2"),
                    "Pourquoi avoir choisi la stratégie Greedy ?"
                ], className="bg-black text-white"),
                dbc.CardBody([
                    html.P([
                        "Après avoir analysé ces différentes approches, nous avons opté pour l'algorithme Greedy pour les raisons suivantes :"
                    ]),
                    html.Ul([
                        html.Li([
                            html.Strong("Efficacité : "), 
                            "Complexité linéaire O(n) en temps et en espace, permettant de traiter rapidement de grands volumes de données "
                            "sans compromettre les performances du système."
                        ]),
                        html.Li([
                            html.Strong("Simplicité : "), 
                            "Implementation simple et maintenable, facilitant les futures évolutions et la correction d'erreurs."
                        ]),
                        html.Li([
                            html.Strong("Scalabilité : "), 
                            "Parfaitement adapté au traitement de grands ensembles de données, contrairement aux autres approches qui deviennent "
                            "rapidement limitées par leur consommation de ressources."
                        ])
                    ]),
                    html.P([
                        "Bien que l'algorithme Greedy ne garantisse pas toujours la solution optimale absolue, il offre un excellent compromis "
                        "entre qualité de la solution et performances. Dans notre contexte d'optimisation financière, les solutions trouvées sont "
                        "généralement très proches de l'optimal, avec l'avantage d'être calculées instantanément."
                    ]),
                    html.P([
                        "Pour plus d'informations sur les algorithmes Greedy  : ",

                        html.A("Introduction aux Algorithmes Greedy",

                              href="https://www.geeksforgeeks.org/greedy-algorithms/", 
                              target="_blank")
                    ])
                ], className="h-100")
            ], className="mb-4 shadow-sm h-100")
        ])
    ], className="mb-4 shadow-sm")



def create_complexity_figure(x_vals, y_vals, name, color):
    """Crée une figure de complexité"""
    return {
        'data': [
            go.Scatter(
                x=x_vals,
                y=y_vals,
                mode='lines+markers',
                name=name,
                line=dict(color=color)
            )
        ],
        'layout': go.Layout(
            xaxis={'title': "Nombre d'actions"},
            yaxis={'title': name},
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(color='black')
        )
    }
# Initialisation de l'application
app = Dash(__name__, 
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css'
    ]
)

# Chargement initial des données
csv_files = [f for f in os.listdir(DATA_FOLDER) if f.endswith(".csv")]
if not csv_files:
    print("Aucun fichier CSV trouvé dans le dossier 'data'.")
    exit()

# Sélection initiale du fichier
questions = [
    {
        "type": "list",
        "name": "selected_file",
        "message": "Choisissez un fichier CSV pour l'analyse :",
        "choices": csv_files,
    }
]
selected_file = prompt(questions)["selected_file"]
file_path = os.path.join(DATA_FOLDER, selected_file)

# Chargement initial des actions
valid_actions, invalid_actions, load_errors = load_actions(file_path)
total_actions_count = len(valid_actions) + len(invalid_actions)

if load_errors:
    for error in load_errors:
        print(error)
    if not valid_actions:
        print("Aucune action valide trouvée.")
        exit()

# Tri initial des actions valides
valid_actions.sort(key=lambda x: x.ratio, reverse=True)

def create_main_layout():
    """Crée le layout principal de l'application"""
    return dbc.Container([

        html.H1("Dashboard d'optimisation par algorithme Greedy", className="text-dark mb-4"),
        

        create_data_controls(csv_files, selected_file),
        

        dbc.Card([
            dbc.CardHeader([
                html.I(className="fas fa-search me-2"),
                html.Div(id='dataset-title', children=f"Exploration des Données - {selected_file}")
            ], className="bg-black text-white d-flex align-items-center border-bottom-0"),
            dbc.CardBody([
                html.Div(id='data-exploration-content')
            ])
        ], className="mb-4"),
        

        dbc.Card([
            dbc.CardHeader([
                html.I(className="fas fa-chart-pie me-2"),  
                "Compte rendu global"
            ], className="bg-black text-white d-flex align-items-center border-bottom-0"),            
            dbc.CardBody([
                html.Div(id='summary-content')
            ])
        ], className="mb-4"),
        

        html.Div(id='cost-benefit-section', className="mb-4"),
        

        html.Div(id='tables-section'),
        

        html.Div(id='complexity-section')
        
    ], fluid=True, className="bg-light")


@app.callback(
    [Output('dataset-title', 'children'),
     Output('data-exploration-content', 'children'),
     Output('summary-content', 'children'),
     Output('cost-benefit-section', 'children'),
     Output('tables-section', 'children'),
     Output('complexity-section', 'children')],
    [Input('file-selector', 'value'),
     Input('validate-budget', 'n_clicks')],
    [State('budget-input', 'value')]
)
def update_dashboard(selected_file, n_clicks, budget):
    """Met à jour l'ensemble du dashboard"""
    if budget is None:
        budget = WALLET
    
    # Chargement des données
    file_path = os.path.join(DATA_FOLDER, selected_file)
    valid_actions, invalid_actions, _ = load_actions(file_path)
    total_actions_count = len(valid_actions) + len(invalid_actions)
    
    # Tri et mesures de performance
    valid_actions.sort(key=lambda x: x.ratio, reverse=True)
    selected, total_cost, total_benefit, times, memories, n_vals = measure_performance(valid_actions, budget)
    
    # Titre du dataset
    dataset_title = f"Exploration des Données - {selected_file}"
    
    # Contenu de l'exploration
    exploration_content = dbc.Row([
        dbc.Col([
            create_data_overview(valid_actions, invalid_actions, total_actions_count)
        ], width=12, className="mb-4"),
        create_metrics_cards(valid_actions)
    ])
    

    rendement = (total_benefit/total_cost*100 if total_cost > 0 else 0)
    utilisation_budget = (total_cost / budget) * 100
    

    performance_overview = dbc.Card([
        dbc.CardHeader([
            html.I(className="fas fa-robot me-2"), 
            "Résultats de l'algorithme"
        ], className="bg-black text-white d-flex align-items-center"),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    create_performance_card(
                        "Coût Total",
                        f"{total_cost:.2f}€",
                        f"Utilisation: {utilisation_budget:.1f}% du budget",
                        "fas fa-euro-sign",
                        "success" if utilisation_budget <= 100 else "danger",
                        utilisation_budget
                    )
                ], width=4),
                dbc.Col([
                    create_performance_card(
                        "Bénéfice Total",
                        f"{total_benefit:.2f}€",
                        f"ROI: {rendement:.1f}%",
                        "fas fa-chart-line",
                        "info",
                        rendement
                    )
                ], width=4),
                dbc.Col([
                    create_performance_card(
                        "Temps d'Exécution",
                        f"{times[-1]:.2f} ms",
                        "Performance optimale" if times[-1] < 1000 else "Performance à optimiser",
                        "fas fa-clock",
                        "success" if times[-1] < 1000 else "warning",
                        times[-1] / 10
                    )
                ], width=4)
            ], className="g-4") 
        ], className="p-3") 
    ], className="shadow mb-4") 
    
    summary_content = [performance_overview] 
    
   
    sienna_metrics = get_sienna_comparison(selected_file, total_cost, total_benefit)
    if sienna_metrics:
        summary_content.append(create_sienna_comparison_section(sienna_metrics))
    
   
    cost_benefit_content = create_cost_benefit_chart(selected)
    tables_content = create_data_tables(selected, invalid_actions)
    complexity_content = create_complexity_section(times, memories, n_vals, selected)
    
    return (
        dataset_title,
        exploration_content,
        summary_content,
        cost_benefit_content,
        tables_content,
        complexity_content
    )


if __name__ == '__main__':
    app.layout = create_main_layout()
    webbrowser.open("http://127.0.0.1:8050/")
    app.run_server(debug=True, use_reloader=False)
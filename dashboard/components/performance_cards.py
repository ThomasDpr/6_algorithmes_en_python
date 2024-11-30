import dash_bootstrap_components as dbc
from dash import html


def create_card_with_black_header(title, value, icon_class, measure_unit="", measure_type=""):
    """Crée une carte avec un en-tête noir, une icône FontAwesome à côté du titre, et un corps blanc."""
    return dbc.Card(
        [
            dbc.CardHeader(
                html.Div(
                    [
                        html.I(className=f"{icon_class} me-2"),  
                        html.H5(title, className="text-white mb-0 d-inline-block")
                    ],
                    className="d-flex align-items-center"  
                ),
                className="bg-black text-white border-bottom-0 d-flex align-items-center",
                style={'fontSize': '1.25rem'}  
            ),
            dbc.CardBody(
                [
                    html.H4(f"{value}{measure_unit}", className="card-title"),
                    html.Span(measure_type, className="card-text")
                    
                ],
                className="bg-white"  
            ),
        ],
        className="h-100 shadow-sm"  
    )


def create_total_report(total_cost: float, total_benefit: float) -> dbc.Row:
    return dbc.Row(
        [
            dbc.Col(
                create_card_with_black_header("Coût Total", f"{total_cost:.2f}", "fas fa-money-bill-wave", "€"),
                width=4,
            ),
            dbc.Col(
                create_card_with_black_header("Bénéfice Total", f"{total_benefit:.2f}", "fas fa-hand-holding-usd", "€"),
                width=4,
            ),
            dbc.Col(
                create_card_with_black_header("Rendement", f"{(total_benefit / total_cost * 100):.2f}", "fas fa-percentage", "%"),
                width=4,
            ),
        ],
        className="mb-4",
    )


def create_global_performance(execution_time: float, total_memory_used: float) -> dbc.Row:
    return dbc.Row(
        [
            dbc.Col(
                create_card_with_black_header("Temps d'exécution", f"{execution_time:.2f}", "fas fa-stopwatch", "s"),
                width=6,
            ),
            dbc.Col(
                create_card_with_black_header("Mémoire utilisée", f"{total_memory_used:.2f}", "fas fa-memory", "MB"),
                width=6,
            ),
        ],
        className="mb-4",
    )
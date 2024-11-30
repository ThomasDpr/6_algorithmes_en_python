import dash_bootstrap_components as dbc
from dash import Dash

from .components.action_tables import create_actions_tables
from .components.complexity_graphs import create_complexity_graphs
from .components.performance_cards import create_global_performance, create_total_report
from .components.report_sections import create_report_sections
from .layouts.main_layout import create_main_layout


def create_dashboard(best_actions_data: list, ignored_actions_data: list,
                    total_cost: float, total_benefit: float,
                    n_values: list, times: list, memories: list,
                    execution_time: float, total_memory_used: float) -> Dash:
    
    app = Dash(__name__, 
        external_stylesheets=[
            dbc.themes.BOOTSTRAP,
            'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css'
        ]
    )    

    # Je récupère le temps d'exécution pour 20 actions (dernière valeur de times)
    final_execution_time = times[-1] if times else 0
    
    total_report = create_total_report(total_cost, total_benefit)
    global_performance = create_global_performance(execution_time, total_memory_used)
    
    best_table, ignored_table = create_actions_tables(
        best_actions_data, 
        ignored_actions_data
    )
    
    time_graph, memory_graph = create_complexity_graphs(
        n_values, times, memories, execution_time
    )
    
    report_cards = create_report_sections(final_execution_time, total_memory_used)
    
    complexity_section = dbc.Row([
        dbc.Col([
            time_graph,
            report_cards[0]
        ], width=6),
        dbc.Col([
            memory_graph,
            report_cards[1]
        ], width=6)
    ], className="mb-4")
    
    app.layout = create_main_layout(
        total_report=total_report,
        global_performance=global_performance,
        best_actions_table=best_table,
        ignored_actions_table=ignored_table,
        complexity_graphs=complexity_section,
        reports=report_cards
    )
    
    return app
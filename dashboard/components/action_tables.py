import dash_bootstrap_components as dbc
from dash import dash_table


def create_actions_tables(best_actions_data: list, ignored_actions_data: list) -> tuple:
    best_actions_table = dash_table.DataTable(
        id='best-actions-table',
        columns=[
            {'name': 'Action', 'id': 'Action'},
            {'name': 'Coût (€)', 'id': 'Coût (€)'},
            {'name': 'Bénéfice (€)', 'id': 'Bénéfice (€)'},
            {'name': 'Bénéfice (%)', 'id': 'Bénéfice (%)'}
        ],
        data=best_actions_data,
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'left', 'padding': '5px'},
        style_header={
            'backgroundColor': 'rgb(230, 230, 230)',
            'fontWeight': 'bold'
        },
        style_as_list_view=True,
    )

    ignored_actions_table = dash_table.DataTable(
        id='ignored-actions-table',
        columns=[
            {'name': 'Action', 'id': 'Action'},
            {'name': 'Raisons', 'id': 'Raisons'}
        ],
        data=ignored_actions_data,
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'left', 'padding': '5px'},
        style_header={
            'backgroundColor': 'rgb(230, 230, 230)',
            'fontWeight': 'bold'
        },
        style_as_list_view=True,
    )
    
    return best_actions_table, ignored_actions_table

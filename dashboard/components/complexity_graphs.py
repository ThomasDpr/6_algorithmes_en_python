import dash_bootstrap_components as dbc
import plotly.graph_objs as go
from dash import dcc, html


def create_complexity_graphs(n_values: list, times: list, memories: list, execution_time: float) -> tuple:
    time_graph = dcc.Graph(
        id='time-complexity-graph',
        figure={
            'data': [
                go.Scatter(
                    x=n_values,
                    y=times,
                    mode='lines+markers',
                    name='Temps d\'exécution (s)',
                    line=dict(color='rgb(0, 0, 255)'),
                    marker=dict(
                        color='rgb(0, 0, 255)',
                        line=dict(color='white')
                    ),
                    hoverinfo='text',
                    text=[f'<b>Actions</b>: {x}<br><b>Temps</b>: {y:.6f} s' for x, y in zip(n_values, times)],
                    fill='tozeroy',
                    fillcolor='rgba(0, 0, 255, 0.1)'
                )
            ],
            'layout': go.Layout(
                title=dict(text='Complexité Temporelle'),
                xaxis=dict(
                    title='Nombre d\'actions',
                    gridcolor='rgba(128, 128, 128, 0.2)',
                    showline=True,
                    linecolor='black',
                    zeroline=True,
                    zerolinecolor='black'
                ),
                yaxis=dict(
                    title='Temps d\'exécution (s)',
                    gridcolor='rgba(128, 128, 128, 0.2)',
                    showline=True,
                    linecolor='black',
                    zeroline=True,
                    zerolinecolor='black'
                ),
                plot_bgcolor='white',
                paper_bgcolor='white',
                hovermode='x unified',
                hoverlabel=dict(bgcolor='white', font_size=14, font_family="Arial"),
                showlegend=True,
                legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
                margin=dict(l=80, r=30, t=100, b=80)
            )
        }
    )

    memory_graph = dcc.Graph(
        id='spatial-complexity-graph',
        figure={
            'data': [
                go.Scatter(
                    x=n_values,
                    y=memories,
                    mode='lines+markers',
                    name='Mémoire utilisée (MB)',
                    line=dict(color='rgb(0, 128, 0)'),
                    marker=dict(
                        color='rgb(0, 128, 0)',
                        line=dict(color='white')
                    ),
                    hoverinfo='text',
                    text=[f'<b>Actions</b>: {x}<br><b>Mémoire</b>: {y:.6f} MB' for x, y in zip(n_values, memories)],
                    fill='tozeroy',
                    fillcolor='rgba(0, 128, 0, 0.1)'
                )
            ],
            'layout': go.Layout(
                title=dict(text='Complexité Spatiale'),
                xaxis=dict(
                    title='Nombre d\'actions',
                    gridcolor='rgba(128, 128, 128, 0.2)',
                    showline=True,
                    linecolor='black',
                    zeroline=True,
                    zerolinecolor='black'
                ),
                yaxis=dict(
                    title='Mémoire utilisée (MB)',
                    gridcolor='rgba(128, 128, 128, 0.2)',
                    showline=True,
                    linecolor='black',
                    zeroline=True,
                    zerolinecolor='black'
                ),
                plot_bgcolor='white',
                paper_bgcolor='white',
                hovermode='x unified',
                hoverlabel=dict(bgcolor='white', font_size=14, font_family="Arial"),
                showlegend=True,
                legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
                margin=dict(l=80, r=30, t=100, b=80)
            )
        }
    )
    
    return time_graph, memory_graph
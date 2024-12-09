import dash
from dash import html, dcc, dash_table, Output, Input,State
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from pages.navbar import NAVBAR
import pandas as pd

dash.register_page(__name__,path='/page2',title="Plotly deep learning app",description="Deep learning simplified")

# Layout principal
layout = dmc.MantineProvider(
    html.Div([
        dcc.Location(id='url', refresh=True),
        html.Div(
            children=[
                html.Div("DATA"),
                html.Div("ANALYSIS"),
                
                dash_table.DataTable(
                    id='data-table2',
                    columns=[],  # Les colonnes seront mises à jour dynamiquement
                    data=[]      # Les données seront mises à jour dynamiquement
                ),
            ],
            className="content-pages",
        ),
        NAVBAR
    ])
)

@dash.callback(
    [Output('data-table2', 'data'),
     Output('data-table2', 'columns')],
    [Input('shared-array', 'data')]
)
def update_table(data):
    if data is not None:
        df = pd.DataFrame(data)
        return df.to_dict('records'), [{"name": col, "id": col} for col in df.columns]
    else:
        return [], []
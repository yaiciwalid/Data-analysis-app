import dash
import dash_bootstrap_components as dbc
from dash import html, _dash_renderer, dcc
import os

_dash_renderer._set_react_version("18.2.0")


app = dash.Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.BOOTSTRAP],
                prevent_initial_callbacks = True, suppress_callback_exceptions=True)


server = app.server


app.layout = html.Div(children=[
    dcc.Store(id='shared-array',data=[],storage_type='session'),
    dcc.Store(id='shared-array-columns-type',data=[],storage_type='session'),
    dcc.Store(id='shared-prediction-variable',data="",storage_type='session'),

    dash.page_container  
    
])

if __name__ == "__main__":
    app.run_server(debug=True)

import dash
from dash import html, dcc, Input, Output, State
import pandas as pd
import dash_mantine_components as dmc
from pages.navbar import NAVBAR
import numpy as np
from utils.transformation import *
from utils.const import *
from utils.calculation import *
import numpy as np
from dash_iconify import DashIconify
import pandas.api.types as ptypes





dash.register_page(__name__, path='/outlayer', title="Data analysis", description="Data analysis plateforme")

layout = dmc.MantineProvider(
    [
        html.Div([
            dcc.Location(id='url', refresh=True),  
            dcc.Store(id="outlayer-labels", data=None),
            dmc.Modal(

                title="Alerte",
                id="alert-modal",
                children=[
                    "Error occured."
                ],
                opened=False,  
            ),
            html.Div([
                html.Div("OUTLAYERS DETECTION", className="page-title"),
                html.Div([
                    dmc.Select(
                        id="method-select",
                        label="Choose the method:",
                        data=[
                            {"value": "DBSCAN", "label": "DBSCAN"},
                            {"value": "option2", "label": "Coming soon"},
                        ],
                        value="DBSCAN",
                        style={"margin-right":"40px", "margin-left":"10px"}
                    ),
                    html.Div(id="method-parameters", children=[
                        dmc.Select(
                            id="metric-select",
                            label="Choose the metric:",
                            data=DISTANCES,
                            value="euclidean",
                            style={"margin-right":"10px"}
                        ),
                        dmc.NumberInput(
                            id="eps-input",
                            label="Epsilon",  
                            placeholder="Enter epsilon",  
                            value=1.0,  
                        ),
                        
                        dmc.NumberInput(
                            id="min_samples-input",
                            label="Min Samples",
                            placeholder="Enter min samples",
                            value=5,
                            style={"margin-left":"10px"}
                        ),
                        html.Button(
                                    [DashIconify(icon="formkit:submit", width=24, height=24, style={"margin-right": "10px"}),
                                        "Detect Outlayers"],
                                    n_clicks=0,
                                    id="detect-outlayers-btn",
                                    style={"margin-right": "40px","margin-left": "40px",
                                           "marginTop":"20px",
                                           "width": "300px"},
                                    className="standard-btn"
                                )
                        ],
                        style={"display":"flex","flexDirection":"row", "justifyContent":"center", 
                                }
                    ),
                ], style={"display":"flex","flexDirection":"row", "justifyContent":"center", 
                          "padding": "10px 0", "border": "2px solid #000000", "width": "98%"}),
                html.Div(id="outlayer-body", children=[],style={
                        "maxWidth": "100%","padding": "10px 0", "width": "98%"})
                
        ],className="content-pages",
        ),
        NAVBAR  
        ])
    ]
)

@dash.callback(
    [Output("outlayer-body", "children"),
     Output('outlayer-labels', 'data'),
     Output("alert-modal", "opened", allow_duplicate=True),
     Output("alert-modal","children", allow_duplicate=True),],
    Input("detect-outlayers-btn", "n_clicks"),
    [State("shared-array", "data"),
     State("shared-prediction-variable", "data"),
    State("eps-input", "value"),
    State("min_samples-input", "value"),
    State("metric-select", "value"),
    ],
    prevent_initial_call=True)
def detect_outlayers(n_clicks, data, prediction_var, eps, min_samples, metric):
    df = pd.DataFrame(data)
    if n_clicks > 0:
        if df.isnull().any(axis=1).sum() > 0:
            return [], None, True, "DBSCAN doesnt support  missing values."
        else:
            for col in df.columns:
                if not ptypes.is_numeric_dtype(df[col]) and col != prediction_var:
                    return [], None, True, "DBSCAN doesnt support non-numeric values (except for the prediction variable)."

        labels = outlayers_dbscan_detection(df, prediction_var, eps, min_samples, metric)
        outlayer_tab = create_table(df[labels == -1], id="outlayer-table")
        nb_outlayers = np.sum(labels == -1)
        card1 = dmc.Card(children=update_card("Number of outlayers", str(nb_outlayers)), 
                                className="page-card", shadow="sm", padding="md", style={"margin":"20px 0px"})
        btn = html.Button(
            [DashIconify(icon="material-symbols:delete", width=24, height=24, style={"margin-right": "10px"}),
                "Delete outlayers"],
                id="delete-outlayers-btn",
                n_clicks=0,
                className="standard-btn",
                style={"margin-left": "auto", "width": "300px"}  
            )
        if nb_outlayers > 0:
            return [html.Div([card1, btn],
                             style={"display":"flex","flex-direction":"row", "align-items": "center", "padding-right": "20px"}), 
                    html.Div(children=[outlayer_tab], style={"overflowX": "auto"})], labels, False, []
        else:
            return [card1],[], False, []
    return dash.no_update

@dash.callback(
    [Output("outlayer-body", "children", allow_duplicate=True),
    Output('shared-array', 'data', allow_duplicate=True),],
    Input("delete-outlayers-btn", "n_clicks"),
    [State("shared-array", "data"),
     State("outlayer-labels", "data"),
    ],
    prevent_initial_call=True)
def delete_outlayers(n_clicks, data, outlayer_table):
    try:
        if n_clicks > 0:
            df = pd.DataFrame(data)
            outlayer_table = np.array(outlayer_table)
            df = df[outlayer_table == 0]
            
            card1 = dmc.Card(children=update_card("Number of outlayers", "0"), 
                                    className="page-card", shadow="sm", padding="md", style={"margin":"20px 0px"})
            return [card1], df.to_dict("records")
        return dash.no_update
    except Exception as e:
        return dash.no_update


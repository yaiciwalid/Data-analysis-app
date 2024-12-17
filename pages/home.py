import dash
from dash import html, dcc, Output, Input,State
import dash_mantine_components as dmc
import pandas as pd
import pandas.api.types as ptypes
import base64
import io
import os
from utils.const import *
from utils.transformation import get_csv_files

dash.register_page(__name__,path='/',title="Data analysis",description="Data analysis plateforme")


layout = dmc.MantineProvider(
    html.Div(
        id="app",
        children=[
            dcc.Location(id='url', refresh=True),
            html.Div(
                id="home",
                className="background",
                children=[
                    html.Div(className="overlay"),
                    html.Div(
                        className="text-section",
                        children=[
                            html.Div(
                                children=[
                                    html.Div("DATA"),
                                    html.Div("ANALYSIS"),
                                ],
                                className="title",
                            ),
                            html.Div(
                                children=[
                                    html.Ul(
                                        children=[
                                            html.Li("Transform and prepare data for machine learning algorithms"),
                                            html.Li("Univariate and bivariate analysis"),
                                            html.Li("Classification, clustering and regression algorithms"),
                                        ],
                                        className="description-list",
                                    )
                                ],
                                className="description",
                            ),
                            html.Div(
                                children=[
                                    dmc.Select(
                                        id="dropdown-dataset",
                                        label=dmc.Text("Choose a pre-loaded Dataset:", style={"fontSize": "1.2rem", "fontWeight": "bold"}),
                                        data=None,
                                        labelProps={"style": {"fontSize": "16px"}} 
                                    ),
                                    html.Div("OR", className="title-2"),
                                    html.Div(children=[
                                        dcc.Upload(
                                            ['Drag and Drop or ', html.A('Select a File')],
                                            className="dash-upload",
                                            id="dash-upload-btn",
                                        ),
                                        dmc.Switch(
                                            label="Use first row as header",
                                            onLabel="ON",
                                            offLabel="OFF",
                                            size="lg",
                                            color="teal",
                                            id="switch-header",
                                            className="mantine-switch",
                                        ),
                                    ], id="upload-container"),
                                    html.Button(
                                        "Upload File",
                                        id="confirm-upload",
                                        className="confirm-upload",
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )
)

@dash.callback(
    Output("dropdown-dataset", "data"),
    Input("url", "pathname"),
)
def update(pathname):
    if pathname=="/":
        return get_csv_files(DATASET_FOLDER)

@dash.callback(
    Output("dash-upload-btn", "children"),  
    Input("dash-upload-btn", "filename")  
)
def update_upload_text(filename):
    if filename:
        return f"File Selected: {filename[:15]}"
    else:
        return ['Drag and Drop or ', html.A('Select a File')]  

@dash.callback(
    [Output('shared-array', 'data'),
     Output('shared-array-columns-type', 'data'),
     Output('shared-prediction-variable', 'data'),
     Output('url', 'href')],
    Input("confirm-upload","n_clicks"),
    [State("dash-upload-btn", "contents"),
    State("dash-upload-btn", "filename"),
    State("dropdown-dataset", "value"),
    State("switch-header","checked")]
)
def redirect(n_clicks,contents,filename,drop_down_dataset,checked):
    try:
        if n_clicks and n_clicks > 0:
            if drop_down_dataset is not None:
                file_path = os.path.join(DATASET_FOLDER, drop_down_dataset)
                if file_path.endswith('.csv'):
                    df = pd.read_csv(file_path)
                elif file_path.endswith('.xlsx'):
                    df = pd.read_excel(file_path)
                else:
                    return dash.no_update ,dash.no_update, dash.no_update, dash.no_update
            elif contents is not None:
                _, content_string = contents.split(',')
                decoded = base64.b64decode(content_string)
                if filename.endswith('.csv'):
                    df = pd.read_csv(io.StringIO(decoded.decode('utf-8')), header=0 if checked else None)
                elif filename.endswith('.xlsx'):
                    df = pd.read_excel(io.BytesIO(decoded), header=0 if checked else None)
                else:
                    return dash.no_update ,dash.no_update, dash.no_update, dash.no_update
            col_types ={}
            for col in df.columns:
                if ptypes.is_integer_dtype(df[col]):
                    col_types[col]=DISCRET
                elif ptypes.is_float_dtype(df[col]):
                    col_types[col]=CONTINUOUS
                else:
                    col_types[col]=NOMINAL 
            df_dict = df.to_dict('records')
            prediction_var = df.columns[-1]
            return df_dict, col_types, prediction_var, '/overview'            
        else: 
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update
    except:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update
    

import dash
from dash import html, dcc, dash_table, Input, Output, State, ALL
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from pages.navbar import NAVBAR
import pandas as pd
import pandas.api.types as ptypes
from utils.transformation import update_card, create_colummns_array, create_edit_pop_up
import dash.exceptions
import json
from sklearn.preprocessing import LabelEncoder, OneHotEncoder

from utils.const import *


dash.register_page(__name__,path='/transform',title="Data analysis",description="Data analysis plateforme")

POP_UP = html.Div(
        id="popup-container",
        style={
            "display": "none",  
            "position": "fixed",
            "top": 0,
            "left": 0,
            "width": "100vw",
            "height": "100vh",
            "backgroundColor": "rgba(0, 0, 0, 0.5)",  
            "zIndex": 1000,  
        },
        children=[
            html.Div(
                id="pop-up-edit-column",
                style={
                    "position": "absolute",
                    "top": "50%",
                    "left": "50%",
                    "transform": "translate(-50%, -50%)",
                    "backgroundColor": "white",
                    "padding": "30px",
                    "borderRadius": "10px",
                    "boxShadow": "0px 4px 6px rgba(0, 0, 0, 0.5)",
                    "zIndex": 1100,
                    "font-size": "1rem",
                },
                children=[
                    html.Div(
                    style={"display": "flex", "justifyContent": "space-between", "alignItems": "center"},
                    children=[
                        html.H2("Edit Column", style={"margin": "0"}),
                        html.Button("\u2715", id="close-popup-btn", style={"background": "none", "border": "none", "fontSize": "20px", "cursor": "pointer"}),
                    ]),
                    html.Label("Column Name:", style={"marginTop": "15px","marginRight": "5px"}),
                    html.Label("Column Name", id="old-name-column", style={"marginTop": "10px", "color":"#002a5c", "font-weight":"bold"}),
                    dcc.Input(id="column-name-input", type="text", placeholder="Enter new column name", style={"width": "100%", "marginTop": "15px", "marginBottom": "15px"}),

                    dmc.RadioGroup(
                        id="normalization-radio-group",
                        label="Normalization:",
                        value="z-normalization",
                        children=[
                            dmc.Radio(label="Z-Normalization", value=Z_NORMALIZATION),
                            dmc.Radio(label="Min-Max Normalization", value=MIN_MAX_NORMALIZATION),
                            dmc.Radio(label="No Normalization", value=NO_NORMALIZATION),
                        ],
                    ),
                    dmc.RadioGroup(
                        id="encoding-radio-group",
                        label="Encoding:",
                        value=NO_ENCODING,
                        children=[],
                    ),

                    dmc.Select(
                        id="variable-type-dropdown",
                        label="Variable Type:",
                        value="",
                        data=[],
                        style={"marginTop": "15px"},
                    ),

                    html.Button("Confirm", id="confirm-edit-column-btn", 
                                style={
                                        "marginTop": "20px", 
                                        "width": "30%",
                                        "marginLeft": "35%"
                    })
                ],
            ),
        ],
    )

layout = dmc.MantineProvider(
    html.Div([
        dcc.Location(id='url', refresh=True),
        dcc.Store(id="transform-columns-df"),
        html.Div(
            children=[
                POP_UP,
                html.Div("GLOBAL TRANSFORMATION", className="page-title"),
                html.Div(
                    children=[
                        html.Div(
                            children=[
                                dmc.Card(
                                    id="kpi-nb-rows",
                                    className="page-card",  
                                    children=[
                                        dmc.Text("Number of rows", size="sm"),
                                        dmc.Title("0", order=2),
                                    ],
                                    shadow="sm",
                                    padding="md",
                                ),
                                dmc.Card(
                                    id="kpi-nb-incomplete-individual",
                                    className="page-card", 
                                    children=[
                                        dmc.Text("Incomplete Individuals", size="sm"),
                                        dmc.Title("0", order=2),
                                    ],
                                    shadow="sm",
                                    padding="md",
                                ),
                                dmc.RadioGroup(
                                    id="radiobox-process-missing-values",
                                    value="delete", 
                                    className="page-radio-group",
                                    children=[
                                        dmc.Radio(label="Delete incomplete individuals", value="delete"),
                                        dmc.Radio(label="fill in incomplete individuals", value="fill"),
                                    ],
                                    size="md",  
                                ),
                                dmc.Select(
                                    id="dropdown-process-missing-values",
                                    label="Method to complete missing values:",
                                    value="Mean/Mod",  
                                    data=[
                                        {"value": "Mean/Mod", "label": "Mean:Mod"},
                                        {"value": "option2", "label": "Coming soon"},
                                    ],
                                    className="page-select",  
                                ),
                            ], id="row-1",style={"display":"flex","flex-direction":"row"}
                        ),
                        html.Div(
                            children=[
                                dmc.Card(
                                    id="kpi-nb-columns",
                                    className="page-card",  
                                    children=[
                                        dmc.Text("Number of columns", size="sm"),
                                        dmc.Title("0", order=2),
                                    ],
                                    shadow="sm",
                                    padding="md",
                                ),
                                dmc.Card(
                                    id="kpi-incomplete-column",
                                    className="page-card",  
                                    children=[
                                        dmc.Text("Incomplete columns", size="sm"),
                                        dmc.Title("0", order=2),
                                    ],
                                    shadow="sm",
                                    padding="md",
                                ),
                                dmc.Select(
                                    id="dropdown-class-var",
                                    label="Choose the prediction variable:",
                                    data=None,
                                    className="page-select",  
                                ),
                                html.Button(
                                    [DashIconify(icon="formkit:submit", width=24, height=24, style={"margin-right": "10px"}),
                                        "Submit modification"],
                                    n_clicks=0,
                                    id="apply-transformation-btn",
                                    className="standard-btn"
                                ),
                            ], id="row-2", style={"display":"flex","flex-direction":"row"}
                        ),
                    ], id="page-container-1",  
                    style={"display":"flex","flex-direction":"column"},
                ),
                html.Div(
                    html.Table(id="transform-table",
                               children=[
                                ],
                                
                               
                    )
                ),
            ],
            className="content-pages",
        ),
        NAVBAR
    ])
)


@dash.callback(
    [Output('dropdown-class-var', 'data', allow_duplicate=True),
     Output('dropdown-class-var', 'value', allow_duplicate=True),
     Output('kpi-nb-incomplete-individual','children'),
     Output('kpi-incomplete-column','children'),
     Output('kpi-nb-rows','children',allow_duplicate=True),
     Output('kpi-nb-columns','children',allow_duplicate=True),
     Output("transform-table",'children'),
     Output("transform-columns-df",'data')],
    [Input('url', 'pathname')],
    [State('shared-array', 'data'),
     State('shared-prediction-variable', 'data'),
     State('shared-array-columns-type','data')],
    prevent_initial_call=True
)
def update(pathname, shared_array, predict_var, columns_type):
    if pathname=="/transform":
        try:
            df = pd.DataFrame(shared_array)
            nb_null_rows = df.isnull().any(axis=1).sum()
            nb_null_col = df.isnull().any(axis=0).sum()
            nb_rows, nb_columns = df.shape
            card1=update_card("Incomplete Individuals", str(nb_null_rows))
            card2=update_card("Incomplete columns", str(nb_null_col))
            card3=update_card("Number of rows", str(nb_rows))
            card4=update_card("Number of columns", str(nb_columns))
            array, df_tranformation_tab = create_colummns_array(df,columns_type)
    
            return [{'label': col, 'value': col} for col in df.columns], predict_var, card1, card2, card3, card4, array, df_tranformation_tab.to_dict('records')
        except:
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
    return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update



@dash.callback(
    [Output('shared-array', 'data',allow_duplicate=True ),
     Output('shared-prediction-variable', 'data',allow_duplicate=True ),
     Output('kpi-nb-incomplete-individual','children',allow_duplicate=True),
     Output('kpi-incomplete-column','children',allow_duplicate=True),
     Output('kpi-nb-rows','children',allow_duplicate=True),
     Output('kpi-nb-columns','children',allow_duplicate=True),
     Output('apply-transformation-btn','n_clicks',allow_duplicate=True),
     Output("transform-table",'children', allow_duplicate=True),
     Output("transform-columns-df",'data', allow_duplicate=True),
    ],
    [Input('apply-transformation-btn','n_clicks')],
    [State('shared-array', 'data'),
     State('radiobox-process-missing-values','value'),
     State('dropdown-process-missing-values','value'),
     State('dropdown-class-var','value'),
     State('shared-array-columns-type','data')
    ], prevent_initial_call=True
)
def apply_transformation(n_clicks, shared_array,radiobox_process_missing, dropdown_process_missing, dropdown_class_var, columns_type):
    if n_clicks>0:
        try:
            df = pd.DataFrame(shared_array)
            if radiobox_process_missing=="delete":
                df = df.dropna()
            else:
                for column in df.columns:
                    if ptypes.is_integer_dtype(df[column]) or ptypes.is_float_dtype(df[column]):  
                        df[column] = df[column].fillna(round(df[column].mean(),2))
                    else:  
                        df[column] = df[column].fillna(df[column].mode()[0])
            nb_rows, nb_columns = df.shape
            card1=update_card("Incomplete Individuals", "0")
            card2=update_card("Incomplete columns", "0")
            card3=update_card("Number of rows", str(nb_rows))
            card4=update_card("Number of columns", str(nb_columns))
            array, df_tranformation_tab = create_colummns_array(df,columns_type)

            return df.to_dict('records'),dropdown_class_var, card1, card2, card3, card4, 0, array, df_tranformation_tab.to_dict('records')
        except:
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, 0, dash.no_update, dash.no_update
    else:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
    

@dash.callback(
    [Output('transform-table', 'children', allow_duplicate=True),
     Output('popup-container','style'),
     Output('pop-up-edit-column','children')],  
    [Input({'type': 'edit-column-btn', 'index': ALL}, 'n_clicks')],  
    [State('transform-columns-df', 'data')],  
    prevent_initial_call=True
)
def edit(n_clicks, transform_columns_df):
    if not any(n_clicks):  
        raise dash.exceptions.PreventUpdate
    style = {
            "display": "block",  
            "position": "fixed",
            "top": 0,
            "left": 0,
            "width": "100vw",
            "height": "100vh",
            "backgroundColor": "rgba(0, 0, 0, 0.5)",
            "zIndex": 1000,
        } 
    triggered_id_dict = dash.callback_context.triggered_id  
    if triggered_id_dict:
        try:
            if triggered_id_dict['type'] == 'edit-column-btn':
                clicked_index = triggered_id_dict['index']
                df = pd.DataFrame(transform_columns_df)
                selected_row = df.iloc[clicked_index]
                return dash.no_update, style, create_edit_pop_up(selected_row)
        except json.JSONDecodeError:
            return dash.no_update, dash.no_update, dash.no_update
    
    return dash.no_update, dash.no_update, dash.no_update


@dash.callback(
    [Output('transform-table', 'children', allow_duplicate=True),
     Output('kpi-nb-incomplete-individual','children',allow_duplicate=True),
     Output('kpi-incomplete-column','children',allow_duplicate=True),
     Output('kpi-nb-rows','children',allow_duplicate=True),
     Output('kpi-nb-columns','children',allow_duplicate=True),
     Output('dropdown-class-var', 'value', allow_duplicate=True),
     Output('transform-columns-df', 'data', allow_duplicate=True),
     Output('shared-array', 'data', allow_duplicate=True),
     Output('shared-array-columns-type','data', allow_duplicate=True),
     Output('shared-prediction-variable', 'data', allow_duplicate=True)],  
    [Input({'type': 'delete-column-btn', 'index': ALL}, 'n_clicks')],  
    [State('transform-columns-df', 'data'),
     State('shared-array', 'data'),
     State('shared-array-columns-type','data'),
     State('shared-prediction-variable', 'data')],  
    prevent_initial_call=True
)
def delete(n_clicks, transform_columns_df, data, columns_type, prediction_var):
    if not any(n_clicks):  
        raise dash.exceptions.PreventUpdate
    
    triggered_id_dict = dash.callback_context.triggered_id  
    if triggered_id_dict:
        try:
            if triggered_id_dict['type'] == 'delete-column-btn':
                clicked_index = triggered_id_dict['index']
                transform_df = pd.DataFrame(transform_columns_df)
                df=pd.DataFrame(data)
                selected_row = transform_df.iloc[clicked_index]
                df = df.drop(selected_row[COLUMN_NAME],axis=1)
                transform_df = transform_df.drop(clicked_index)
                columns_type.pop(selected_row[COLUMN_NAME])
                if prediction_var==selected_row[COLUMN_NAME]:
                    if df.shape[1]>=1:
                        prediction_var=df.columns[-1]
                    else:
                        prediction_var=""
                nb_null_rows = df.isnull().any(axis=1).sum()
                nb_null_col = df.isnull().any(axis=0).sum()
                nb_rows, nb_columns = df.shape
                card1=update_card("Incomplete Individuals", str(nb_null_rows))
                card2=update_card("Incomplete columns", str(nb_null_col))
                card3=update_card("Number of rows", str(nb_rows))
                card4=update_card("Number of columns", str(nb_columns))
                array, df_tranformation_tab = create_colummns_array(df,columns_type)
                
                return array, card1, card2, card3, card4, prediction_var, df_tranformation_tab.to_dict('records'), df.to_dict('records'), columns_type, prediction_var
            
        except json.JSONDecodeError:
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
    
    return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update


@dash.callback(
    Output('popup-container','style', allow_duplicate=True),  
    [Input('close-popup-btn', 'n_clicks')],  
    prevent_initial_call=True
)
def edit(n_clicks):
    if n_clicks and n_clicks>0:  
        return {'display':"none"}
    
    return dash.no_update


@dash.callback(
    [Output('shared-array','data', allow_duplicate=True), 
     Output('transform-columns-df','data', allow_duplicate=True),
     Output('shared-array-columns-type','data', allow_duplicate=True),
     Output('transform-table','children', allow_duplicate=True),
     Output('popup-container','style', allow_duplicate=True),
     Output('dropdown-class-var','data', allow_duplicate=True)],
    [Input('confirm-edit-column-btn', 'n_clicks'),],
     [State('shared-array','data'),
      State('old-name-column','children'),
      State('shared-array-columns-type','data'),
      State('column-name-input', 'value'),
      State('normalization-radio-group','value'),
      State('encoding-radio-group','value'),
      State('variable-type-dropdown','value')],  
    prevent_initial_call=True
)
def confirm_edit(n_clicks, data, old_name_column, columns_type, column_name_input, normalization_radio_group, encoding_radio_group, variable_type_dropdown):
    try:
        if n_clicks and n_clicks>0:  
            df = pd.DataFrame(data)
            old_name = old_name_column
            
            if normalization_radio_group == MIN_MAX_NORMALIZATION:
                if df[old_name].max() != df[old_name].min():
                    df[old_name] = round((df[old_name] - df[old_name].min()) / (df[old_name].max() - df[old_name].min()),2)

            elif normalization_radio_group == Z_NORMALIZATION:
                if df[old_name].std() != 0:
                    df[old_name] = round((df[old_name] - df[old_name].mean()) / df[old_name].std(),2)
            elif encoding_radio_group == LABEL_ENCODING:
                label_encoder = LabelEncoder()
                df[old_name] = label_encoder.fit_transform(df[old_name])
            elif encoding_radio_group == ONE_HOT_ENCODING:
                encoder = OneHotEncoder(sparse_output=False)
                encoded_array = encoder.fit_transform(df[[old_name]])
                df_encoded = pd.DataFrame(encoded_array, columns=encoder.get_feature_names_out([old_name]))
                for col in df_encoded.columns:
                    columns_type[col]=NOMINAL
                df = pd.concat([df, df_encoded], axis=1)

            else:
                columns_type[old_name]=variable_type_dropdown
                if  column_name_input is not None and column_name_input.strip() != "":
                    df=df.rename(columns={old_name:column_name_input})
                    columns_type.pop(old_name)
                    columns_type[column_name_input]=variable_type_dropdown

            df = df.sort_index(axis=1)
            array, df_tranformation_tab = create_colummns_array(df,columns_type) 

            return df.to_dict('records'),  df_tranformation_tab.to_dict('records'), columns_type, array, {'display':"none"},[{'label': col, 'value': col} for col in df.columns]
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
    except:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
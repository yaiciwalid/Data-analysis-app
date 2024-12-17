from dash import html, dcc
import dash_mantine_components as dmc
from dash_iconify import DashIconify
import pandas as pd
from utils.const import *

def update_card(title, value):

    return [
            dmc.Text(title, size="sm"),
            dmc.Title(str(value), order=2),
        ]

def generate_table_rows(data):
    tr = []
    for index, row in data.iterrows():
        td = []
        for val in row.values:
            td.append(html.Td(val))
        td.append(
            html.Td(
                [
                    html.Button(
                        [DashIconify(icon="clarity:pop-out-line", width=24, height=24, style={"margin-right": "10px"}),
                        "Edit"],
                        n_clicks=0,
                        id={"type": "edit-column-btn", "index": index}, className="edit-column-btn"
                    ),
                    html.Button(
                        [DashIconify(icon="typcn:delete", width=24, height=24, style={"margin-right": "10px"}),
                        "Delete"],
                        n_clicks=0,
                        id={"type": "delete-column-btn", "index": index}, style={"margin-left":"10px"}, className="delete-column-btn"
                    )
                ]
            )
            
        )
        
        tr.append(html.Tr(td))
    return tr

def create_colummns_array(df, columns_type):
    data = []
    for col in df.columns:
        row = []
        row.extend([col,columns_type[col],df[col].nunique(),int(df[col].isnull().sum())])
        if columns_type[col]==CONTINUOUS or columns_type[col]==DISCRET:
            row.append(round(df[col].mean(),2))
        else:
            row.append(df[col].mode()[0])
        data.append(row)
    df_result = pd.DataFrame(data, columns=[COLUMN_NAME,TYPE,NB_DISTINCT_VALUES,NB_MISSING_VALUES,MEAN_MOD])
    children = [
                html.Thead(html.Tr([
                    html.Th("Column"),
                    html.Th("Type"),
                    html.Th("Nb distinct values"),
                    html.Th("Nb missing values"),
                    html.Th("Mean/Mod"),
                    html.Th("Edit")
                ])),
                html.Tbody(generate_table_rows(df_result))
    ]
    return children, df_result


def create_edit_pop_up(df):
    column_name = df[COLUMN_NAME]
    column_type = df[TYPE]
    type_choice = [
        {"value": DISCRET, "label": DISCRET},
        {"value": CONTINUOUS, "label": CONTINUOUS},
        {"value": NOMINAL, "label": NOMINAL},
        {"value": ORDINAL, "label": ORDINAL},
    ]
    normalization_choice = [
                dmc.Radio(label="No Normalization", value=NO_NORMALIZATION),
                dmc.Radio(label="Z-Normalization", value=Z_NORMALIZATION),
                dmc.Radio(label="Min-Max Normalization", value=MIN_MAX_NORMALIZATION),
            ]
    if column_type == ORDINAL or column_type == NOMINAL:
        type_choice = [
            {"value": NOMINAL, "label": NOMINAL},
            {"value": ORDINAL, "label": ORDINAL},
        ]
        normalization_choice = [
                dmc.Radio(label="No Normalization", value=NO_NORMALIZATION),
            ]
 
    return [
        html.Div(
        style={"display": "flex", "justifyContent": "space-between", "alignItems": "center"},
        children=[
            html.H2("Edit Column", style={"margin": "0"}),
            html.Button("\u2715", id="close-popup-btn", style={"background": "none", "border": "none", "fontSize": "20px", "cursor": "pointer"}),
        ]),
        html.Label("Column Name:", style={"marginTop": "15px","marginRight": "5px"}),
        html.Label(column_name, id="old-name-column",style={"marginTop": "10px", "color":"#002a5c", "font-weight":"bold"}),
        dcc.Input(id="column-name-input", type="text", placeholder="Enter new column name", style={"width": "100%", "marginTop": "15px", "marginBottom": "15px"}),

        dmc.RadioGroup(
            id="normalization-radio-group",
            label="Normalization:",
            value=NO_NORMALIZATION,
            children=normalization_choice,
        ),

        dmc.Select(
            id="variable-type-dropdown",
            label="Variable Type:",
            value=column_type,
            data=type_choice,
            style={"marginTop": "15px"},
        ),

        html.Button("Confirm", id="confirm-edit-column-btn", 
                    style={
                            "marginTop": "20px", 
                            "width": "30%",
                            "marginLeft": "35%"
        })
    ]
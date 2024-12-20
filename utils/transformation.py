from dash import html, dcc, dash_table
import dash_mantine_components as dmc
from dash_iconify import DashIconify
import pandas as pd
from utils.const import *
import os
import plotly.graph_objs as go
import plotly.express as px




def get_csv_files(folder):
    try:
        files = [
            f for f in os.listdir(folder)
            if os.path.isfile(os.path.join(folder, f)) and f.endswith('.csv') or f.endswith('.xlsx')
        ]
        return [{"label": file, "value": file} for file in files]
    except Exception as e:
        print(f"Error reading dataset folder: {e}")
        return []
    
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
    encoding_choice = [
        dmc.Radio(label="No encoding", value=NO_ENCODING),
    ]

    if column_type == ORDINAL or column_type == NOMINAL:
        type_choice = [
            {"value": NOMINAL, "label": NOMINAL},
            {"value": ORDINAL, "label": ORDINAL},
        ]
        normalization_choice = [
                dmc.Radio(label="No Normalization", value=NO_NORMALIZATION),
            ]
        encoding_choice = [
            dmc.Radio(label="No encoding", value=NO_ENCODING),
            dmc.Radio(label="One-hot encoding", value=ONE_HOT_ENCODING),
            dmc.Radio(label="Label encoding", value=LABEL_ENCODING),
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

        dmc.RadioGroup(
            id="encoding-radio-group",
            label="Encoding:",
            value=NO_ENCODING,
            children=encoding_choice,
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


def create_2d_plot(df, x, y, color) :
    fig = px.scatter(
        df, x=x, y=y,color=color,
    )
    fig.update_layout(plot_bgcolor='white')

    return dcc.Graph(figure=fig, style={"width": "100%"})

def create_heatmap(df, columns_type):
    cols = [col for col in columns_type.keys() if columns_type[col] in {CONTINUOUS, DISCRET}]
    df_filtered = df[cols]
    correlation_matrix = df_filtered.corr().round(2)
    num_cols = len(correlation_matrix.columns)
    plot_size = min(1500,max(400, num_cols * 50))
    fig = px.imshow(
        correlation_matrix,
        text_auto=True,               
        color_continuous_scale='Viridis',  
        title='Heatmap of Correlations'
    )
    fig.update_layout(
        width=plot_size,
        height=plot_size,
        title_font_size=20
    )
    return dcc.Graph(figure=fig)

def create_categorial_bar_plot(contingency_table, var1, var2):

    fig = px.bar(contingency_table, 
             x=var1, 
             y='count',  
             color=var2,  
             labels={'Variable1': 'Catégories de Variable1', 'count': 'count', 'Variable2': 'Catégories de Variable2'},
             text='count',
            )  
    fig.update_layout(plot_bgcolor='white')
    return dcc.Graph(figure=fig, style={"width": "100%"})

def create_table(contingency_table, id=""):


    return dash_table.DataTable(
        id=id,
        columns=[{'name': col, 'id': col} for col in contingency_table.columns],
        data=contingency_table.to_dict('records'),
        style_cell={'textAlign': 'center'},
        style_as_list_view=True,
        style_data={
            'color': 'black',
            'backgroundColor': 'white',
            'border': 'none',  
        },
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(13, 110, 253,0.05)',  
            }
        ],
        style_header={
            'backgroundColor': 'rgb(0, 51, 102)',  
            'color': 'white',                      
            'fontWeight': 'bold',
            'fontSize': '1rem',
            'border': 'none'                   
        }
    )

def create_mixed_var_box_plot(df,qualitative_var,quantitative_var):
    fig = px.box(df, x=qualitative_var, y=quantitative_var, color=qualitative_var, points="all")
    fig.update_layout(plot_bgcolor='white')

    return dcc.Graph(figure=fig, style={"width": "100%"})
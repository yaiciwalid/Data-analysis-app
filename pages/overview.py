import dash
from dash import html, dcc, dash_table, Input, Output, State
import pandas as pd
import dash_mantine_components as dmc
from pages.navbar import NAVBAR
import pandasql as ps
from dash_iconify import DashIconify
import dash_bootstrap_components as dbc



dash.register_page(__name__, path='/overview', title="Data analysis", description="Data analysis plateforme")

layout = dmc.MantineProvider(
    [dmc.Modal(
        title="Alerte",
        id="alert-modal",
        children=[
            "Error occured."
        ],
        opened=False,  
    ),
    html.Div([
        dcc.Store(id="local-array"),
        dcc.Location(id='url', refresh=True),  
        html.Div(
            children=[
                html.Div("DATA OVERVIEW", className="page-title"),
                dcc.Textarea(
                    id="sql-input",
                    placeholder="Write your SQL query here (ex: SELECT * FROM df WHERE age > 30). Use df as name of your table",
                    style={
                        "width": "98%",
                        "height": "150px",
                        "fontFamily": "monospace",
                        "fontSize": "1rm",
                        "marginBottom": "10px",
                        "border": "2px solid black",  
                        "borderRadius": "5px",
                    },
                ),
                html.Div([
                    html.Button(
                        [DashIconify(icon="mingcute:download-fill", width=24, height=24, style={"margin-right": "10px"}),
                         "Download CSV"],
                        id="download-button",
                        n_clicks=0,
                        className="standard-btn",
                        style={"margin-right": "auto"}  
                    ),
                    html.Button(
                        [DashIconify(icon="ix:reset", width=24, height=24, style={"margin-right": "10px"}),
                         "Reset"],
                        id="reset-query",
                        n_clicks=0,
                        className="standard-btn"
                    ),
                    html.Button(
                        [DashIconify(icon="mdi:sql-query", width=24, height=24, style={"margin-right": "10px"}),
                         "Execute Query"],
                        id="execute-query",
                        n_clicks=0,
                        className="standard-btn"
                    ),
                ], style={"display":"flex","flex-direction":"row", "align-items": "center", "padding-right": "20px"}),
                
                dash_table.DataTable(
                    id='data-table',
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
                    },
                    columns=[],  
                    data=[],
                    filter_action="native",
                    sort_action="native",
                    sort_mode='multi',
                    selected_rows=[],
                    page_action='native',
                    page_current=0,
                    page_size=15,      
                ),
                dcc.Download(id="download-dataframe-csv"),  
            ],
            className="content-pages",
        ),
        NAVBAR  
    ])]
)



@dash.callback(
    [Output('data-table', 'data'),
     Output('data-table', 'columns'),
     Output('local-array', 'data'),
     Output('reset-query', 'n_clicks')],
    [Input('url', 'pathname'),
     Input('reset-query', 'n_clicks')],
     [State('shared-array', 'data'),]
)
def update_table(pathname, n_clicks, data):
    if pathname=="/overview":
        if data is not None or n_clicks>0:
            try:
                df = pd.DataFrame(data)
                return df.to_dict('records'),[{"name": col, "id": col, "type": "numeric" if pd.api.types.is_numeric_dtype(df[col]) else "text"} for col in df.columns], data, 0
            except:
                return dash.no_update, dash.no_update, dash.no_update, 0
        else:
            return [], [],[], 0
    return dash.no_update, dash.no_update, dash.no_update, dash.no_update
    
@dash.callback(
    [Output('data-table', 'data',allow_duplicate=True),
     Output('data-table', 'columns',allow_duplicate=True),
     Output('local-array', 'data',allow_duplicate=True),
     Output("alert-modal", "opened"),
     Output("alert-modal","children"),
     Output('execute-query', 'n_clicks')],
    [Input('execute-query', 'n_clicks')],
     [State('shared-array', 'data'),
      State('sql-input','value')],prevent_initial_call=True
)
def execute_query(n_clicks, data,query):
    if data is not None and n_clicks>0:
        try:
            df = pd.DataFrame(data)
            result_df = ps.sqldf(query, {"df":df})
            return result_df.to_dict("records"), [{"name": col, "id": col} for col in result_df.columns], result_df.to_dict("records"), False, [], 0
        except:
            return dash.no_update, dash.no_update, dash.no_update, True, ["Error occured when executing SQL query, retry"], 0
    else:
        return [], [],[], True, ["No Data available, re-upload dataset"], 0
    
@dash.callback(
    [Output("download-dataframe-csv", "data"),
     Output("download-button", "n_clicks")],
    Input("download-button", "n_clicks"),
    State("data-table", "data"),
    prevent_initial_call=True
)
def download_csv(n_clicks, table_data):
    if table_data and n_clicks>0:
        
        df = pd.DataFrame(table_data)
        
        return dcc.send_data_frame(df.to_csv, "query_results.csv", index=False), 0
    return None, 0
    



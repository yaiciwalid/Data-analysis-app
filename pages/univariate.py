import dash
from dash import html, dcc, dash_table, Input, Output, State
import pandas as pd
import dash_mantine_components as dmc
from pages.navbar import NAVBAR
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from utils.transformation import update_card
from utils.const import *
from utils.calculation import *



dash.register_page(__name__, path='/univariate', title="Data analysis", description="Data analysis plateforme")

layout = dmc.MantineProvider(
    [
        html.Div([
            dcc.Location(id='url', refresh=True),  
            html.Div([
                html.Div("UNIVARIATE ANALYSIS", className="page-title"),
                html.Div([
                    html.Div([
                        dmc.Card(
                            id="kpi-nb-incomplete-individual2",
                            className="page-card", 
                            children=[
                                dmc.Text("Incomplete Individuals", size="sm"),
                                dmc.Title("0", order=2),
                            ],
                            shadow="sm",
                            padding="md",
                        ),
                        dmc.Card(
                            id="kpi-Mean-Mod",
                            className="page-card", 
                            children=[
                                dmc.Text("Mean", size="sm"),
                                dmc.Title("0", order=2),
                            ],
                            shadow="sm",
                            padding="md",
                        ),
                        dmc.Card(
                            id="kpi-Variance-Entropy",
                            className="page-card", 
                            children=[
                                dmc.Text("Variance", size="sm"),
                                dmc.Title("0", order=2),
                            ],
                            shadow="sm",
                            padding="md",
                        ),
                        dmc.Card(
                            id="kpi-Std-GeniIndex",
                            className="page-card", 
                            children=[
                                dmc.Text("Standard Deviation", size="sm"),
                                dmc.Title("0", order=2),
                            ],
                            shadow="sm",
                            padding="md",
                        ),
                    ],style={"display":"flex","flex-direction":"row", "flex-grow": "1", "padding": "10px 0"}
                    ),
                    html.Div([
                        dmc.Select(
                            id="dropdown-variable",
                            label="Choose the variable:",
                            data=None,
                            style={"margin-right":"40px"}
                        ),
                        html.Div([
                            html.Label("Number of partitions:", style={"font-weight":"bold","margin": "15 5px", "padding-bottom": "10px"}),
                            dcc.Slider(
                                1, 
                                10, 
                                step=1, 
                                value=5,
                                id="slider-partitions",
                            ),
                        ],
                        style = {"flex-grow": "1"} 
                        )
                    ], style={"display":"flex","flex-direction":"row", "padding": "10px 0"}
                    )
                ]
                ,style={"display": "flex","flex-direction": "column","justify-content": "center", 
                        "border": "2px solid #000000", "padding": "20px", "width": "98%"}
                ),
                html.Div([
                    dcc.Graph(
                            id='histogram',
                            figure={
                                'data': [
                                    go.Histogram(
                                        x=[],               
                                        nbinsx=10,            
                                        marker=dict(color='blue')  
                                    )
                                ],
                                'layout': go.Layout(
                                    title="Frequency histogram",
                                    xaxis=dict(title="Values"),  
                                    yaxis=dict(title="Frequency"),  
                                )
                            }
                    ),
                    dcc.Graph(
                        id='cumulative-frequency-curve',
                        figure={
                            'data': [],
                            'layout': go.Layout(
                                title="Cumulative frequency curve",
                                xaxis=dict(title="Values"),
                                yaxis=dict(title="Cumulative frequency"),
                            )
                        }
                    ),
                    html.Div(children = [
                        dash_table.DataTable(
                            id='box-plot-table',
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
                        html.Div(id="box-plot-div", children=[
                            dcc.Graph(
                                id='box-plot',
                                figure={
                                    'data': [],
                                    'layout': go.Layout(
                                        title="Box Plot",
                                        yaxis=dict(title="Valeurs"),
                                    )
                                }
                            ),
                        ]),
                        
                    ],style={"display": "flex","flex-direction": "row","justify-content": "center", 
                         "padding-top": "20px", "width": "98%", "align-items": "center"}),
                ])
                
        ],className="content-pages",
        ),
        NAVBAR  
        ])
    ]
)

@dash.callback(
    Output("dropdown-variable", "data"),
    Input('url', 'pathname'),
    State('shared-array', 'data'),
)
def update_dropdown(pathname, data):
    try:
        if pathname=="/univariate":
            df=pd.DataFrame(data)
            columns = []
            for cl in df.columns:
                columns.append({"label":cl, "value":cl})
            return columns
    except:
        return dash.no_update

    

@dash.callback(
    [Output("kpi-nb-incomplete-individual2", "children"),
     Output('kpi-Mean-Mod' , 'children'),
     Output('kpi-Variance-Entropy' , 'children'),
     Output('kpi-Std-GeniIndex' , 'children'),
     Output('histogram', 'figure'),
     Output('cumulative-frequency-curve', 'figure'),
     Output('box-plot-div', 'children'),
     Output('box-plot-table', 'data'),
     Output('box-plot-table', 'columns'),],
    [Input('dropdown-variable', 'value'),
     Input('slider-partitions', 'value'),],
    [State('shared-array', 'data'),
     State('shared-array-columns-type','data'),],
)
def load_content(value, nb_partitions, data, columns_type):
    
    try:
        if value is not None:
            df=pd.DataFrame(data)
            hist_data=df[value].tolist()
            

            sorted_data = np.sort(df[value].tolist())
            cumulative_freq = np.arange(1, len(sorted_data) + 1) / len(sorted_data)  

            if columns_type[value]==CONTINUOUS or columns_type[value]==DISCRET:
                  
                if columns_type[value]==CONTINUOUS:
                    bin_min = min(hist_data)-0.1
                    bin_max = max(hist_data)+0.1
                    print(bin_min,bin_max)
                    bin_size = (bin_max - bin_min) / nb_partitions  
                else:
                    bin_min =None
                    bin_max = None
                    bin_size = 1
                nb_null_rows = df[value].isna().sum()
                mean_card_name = "Mean"
                mean = round(df[value].mean(),2)
                variance_card_name = "Variance"
                variance = round(df[value].var(),2)
                std_card_name = "Standard Deviation"
                std = round(df[value].std(),2)
                q1 = round(df[value].quantile(0.25),2) 
                q3 = round(df[value].quantile(0.75),2)
                minimum = round(df[value].min(),2)
                maximum = round(df[value].max(),2)
                median = round(df[value].median(),2)
                x_binz = dict(
                    start=bin_min,
                    end=bin_max,    
                    size=bin_size   
                )
            else:
                nb_null_rows = 0
                mean_card_name = "Mode"
                mean = df[value].mode()[0]
                variance_card_name = "Entropy"
                variance = round(calculate_entropy(df[value]),2)
                std_card_name = "Gini Index"
                std = round(calculate_gini_index(df[value]),2)
                x_binz = {}
        else:
            hist_data = []
            bin_min = 0
            bin_max = 0
            bin_size = 0
            sorted_data = []
            cumulative_freq = []
            nb_null_rows = 0
            mean_card_name = "Mean"
            mean = 0
            variance_card_name = "Variance"
            variance = 0
            std_card_name = "Standard Deviation"
            std = 0
            q1 = 0
            q3 = 0
            minimum = 0
            maximum = 0
            median = 0
            x_binz = {}
        
        card1=update_card("Incomplete Individuals", str(nb_null_rows))
        card2=update_card(mean_card_name, str(mean))
        card3=update_card(variance_card_name, str(variance))
        card4=update_card(std_card_name, str(std))
        
        histogram = go.Histogram(
            x=hist_data,               
            xbins=x_binz,
            texttemplate="%{y}", textfont_size=20  
        )
        hist_figure = {
            'data': [histogram],
            'layout': go.Layout(
                title="Frequency Histogram",
                xaxis=dict(title='Values', showgrid=False),
                yaxis=dict(title='Frequency', showgrid=False, showticklabels=False),
                plot_bgcolor='white', 
                
                bargap=0.1  
            ),
        }
        
        cumulative_curve = go.Scatter(
            x=sorted_data,  
            y=cumulative_freq,  
            line_shape='spline',
            mode='lines',  
            name='Cumulative Frequency Curve',
            line=dict(color='blue')  
        )
        cumulative_figure = {
            'data': [cumulative_curve],
            'layout': go.Layout(
                xaxis=dict(title='Values', showgrid=False),
                yaxis=dict(title='Cumulative Frequency'),
                template="plotly_white"
            )
        }

        if value is not None and (columns_type[value]==NOMINAL or columns_type[value]==ORDINAL):
            box_div = []
            box_tab = []
            box_tab_column_name = []
        else:
            dd = pd.DataFrame(hist_data, columns=[value])
            box_plot = px.box(dd, y=value, points="all")
            box_plot_figure = box_plot.update_layout(
                title=dict(
                    text="Boxplot",
                    x=0.5,
                    font=dict(size=20, color="white"),
                ),
                plot_bgcolor="white",  # Supprimer la grille
                font_color="white"     # Couleur des textes
            )
            box_div = [dcc.Graph(id='box-plot', figure=box_plot_figure)]

            box_tab = [{"Metric": "Mean", "Value": mean},
                        {"Metric": "Variance", "Value": variance},
                        {"Metric": "Standard Deviation", "Value": std},
                        {"Metric": "Median", "Value": median},
                        {"Metric": "Q1", "Value": q1},
                        {"Metric": "Q3", "Value": q3},
                        {"Metric": "Min", "Value": minimum},
                        {"Metric": "Max", "Value": maximum},
                        ]
            box_tab_column_name = [{"name":"Metric","id":"Metric"},{"name":"Value","id":"Value"}]



        return card1, card2, card3, card4 , hist_figure, cumulative_figure, box_div, box_tab, box_tab_column_name
    except:
        return dash.no_update  
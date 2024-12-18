import dash
from dash import html, dcc, dash_table, Input, Output, State
import pandas as pd
import dash_mantine_components as dmc
from pages.navbar import NAVBAR
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from utils.transformation import *
from utils.const import *
from utils.calculation import *
from scipy.stats import pearsonr,chi2_contingency, f_oneway





dash.register_page(__name__, path='/bivariate', title="Data analysis", description="Data analysis plateforme")

layout = dmc.MantineProvider(
    [
        html.Div([
            dcc.Location(id='url', refresh=True),  
            html.Div([
                html.Div("BIVARIATE ANALYSIS", className="page-title"),
                html.Div(id="bivariate-head",
                         children=[
                            html.Div(id="bivariate-kpis",children=[
                                
                            ], style={"display":"flex","flexDirection":"row", "justifyContent":"center", 
                                    "padding": "10px 0"}
                            ),
                            html.Div(children=[
                                dmc.Select(
                                        id="dropdown-variable-1",
                                        label="Choose the variable:",
                                        data=None,
                                        className="page-select",  
                                ),
                                dmc.Select(
                                        id="dropdown-variable-2",
                                        label="Choose the variable:",
                                        data=None,
                                        className="page-select",  

                                ),
                            ], style={"display":"flex","flexDirection":"row", "justifyContent":"center", 
                                    "padding": "10px 0"}
                            )
                        ], style={"border": "2px solid #000000", "padding": "20px", "width": "98%"}
                    ),
                    html.Div(id="bivariate-plots",children=[
                        
                    ], style={"display":"flex","flexDirection":"column", "alignItems":"center", "padding": "20px", "width": "98%"})
                
            ],className="content-pages",
            ),
            NAVBAR  
        ])
    ]
)

@dash.callback(
    [Output("dropdown-variable-1", "data"),
     Output("dropdown-variable-2", "data")],
    Input("url", "pathname"),
    State('shared-array', 'data'),
    prevent_initial_call=True)
def update(pathname, data):
    if pathname=="/bivariate":
        df = pd.DataFrame(data)
        columns = []
        for cl in df.columns:
            columns.append({"label":cl, "value":cl})
        return columns, columns
    else:
        return dash.no_update, dash.no_update
    
@dash.callback(
    [Output("bivariate-kpis", "children"),
     Output("bivariate-plots", "children")],
    Input("dropdown-variable-1", "value"),
    Input("dropdown-variable-2", "value"),
    [State('shared-array', 'data'),
    State("shared-array-columns-type", "data"),
    State("shared-prediction-variable", "data")],
    prevent_initial_call=True)
def update_kpis(var1, var2, data, columns_type, prediction_variable):
    try:
        if var1 is not None and var2 is not None:
            df = pd.DataFrame(data)
            if ((columns_type[var1] in {CONTINUOUS,DISCRET}) and 
            (columns_type[var2] in {CONTINUOUS,DISCRET})):
                r, p_value = pearsonr(df[var1], df[var2])
                cov = np.cov(df[var1], df[var2])[0,1]
                card1 = dmc.Card(children=update_card("Covariance", str(round(cov,4))), 
                                className="page-card", shadow="sm", padding="md")
                card2 = dmc.Card(children=update_card("Correlation", str(round(r,4))), 
                                className="page-card", shadow="sm", padding="md")
                card3 = dmc.Card(children=update_card("P-value", str(round(p_value,4))), 
                                className="page-card", shadow="sm", padding="md")
                if columns_type[prediction_variable] in {CONTINUOUS,DISCRET}:
                    color = None
                else:
                    color = prediction_variable
                plot_points = create_2d_plot(df, var1, var2, color)
                plot_hot_map_correlation = create_heatmap(df, columns_type)
                return [card1, card2, card3], [plot_points, plot_hot_map_correlation]
            
            elif ((columns_type[var1] in {NOMINAL,ORDINAL}) and 
            (columns_type[var2] in {NOMINAL,ORDINAL})):
                if df[var2].nunique() > df[var1].nunique():
                    var3 = var2
                    var2 = var1
                    var1 = var3
                contingency_table = pd.crosstab(df[var1], df[var2])
                chi2, p_value, dof, expected = chi2_contingency(contingency_table)
                n = contingency_table.to_numpy().sum()
                phi2 = chi2 / n
                r, c = contingency_table.shape
                cramers_v = np.sqrt(phi2 / min(r - 1, c - 1))
                card1 = dmc.Card(children=update_card("chi2 test", str(round(chi2,4))), 
                                className="page-card", shadow="sm", padding="md")
                card2 = dmc.Card(children=update_card("p-value", str(round(p_value,4))), 
                                className="page-card", shadow="sm", padding="md")
                card3 = dmc.Card(children=update_card("phi2", str(round(phi2,4))), 
                                className="page-card", shadow="sm", padding="md")
                card4 = dmc.Card(children=update_card("cramers v", str(round(cramers_v,4))), 
                                className="page-card", shadow="sm", padding="md")
                
                contingency_table_reset = contingency_table.reset_index().melt(id_vars=[var1], var_name=var2, value_name='count')

                bar_plot = create_categorial_bar_plot(contingency_table_reset, var1, var2)
                contingency_table_plot = create_table(contingency_table_reset)
                return [card1, card2, card3, card4], [bar_plot,contingency_table_plot]

            else:
                if columns_type[var1] in {NOMINAL,ORDINAL}:
                    qualitative_var= var1
                    quantitative_var = var2
                else:
                    qualitative_var= var2
                    quantitative_var = var1
                
                stats_by_group = df.groupby(qualitative_var)[quantitative_var].agg(
                    mean='mean',
                    variance='var',
                    std='std',
                    min='min',
                    max='max'
                ).reset_index().round(2)
                stats_tab = create_table(stats_by_group)
                                
                groupes = [df[df[qualitative_var] == g][quantitative_var] for g in df[qualitative_var].unique()]

                anova_result = f_oneway(*groupes)

                card1 = dmc.Card(children=update_card("Anova F-statistic", str(round(anova_result.statistic,4))), 
                                className="page-card", shadow="sm", padding="md")
                card2 = dmc.Card(children=update_card("p-value", str(round(anova_result.pvalue,4))), 
                                className="page-card", shadow="sm", padding="md")
                box_plot = create_mixed_var_box_plot(df, qualitative_var, quantitative_var)
                return [card1, card2], [box_plot, stats_tab]
        else:
            return [], []
    except:
        return [], []
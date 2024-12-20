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
import dash_bootstrap_components as dbc
from groq import Groq
from utils.chatbot_functions import response
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("API_KEY")
client = Groq(
    api_key=api_key,
)



dash.register_page(__name__, path='/chatbot', title="Data analysis", description="Data analysis plateforme")



def textbox(text, box="AI", name="Philippe"):
    style = {
        "max-width": "90%",
        "width": "max-content",
        "padding": "5px 10px",
        "border-radius": 25,
        "margin-bottom": 20,
    }

    if box == "user":
        style["margin-left"] = "auto"
        style["margin-right"] = 0

        return dbc.Card(text, style=style, body=True, color="primary", inverse=True)

    elif box == "AI":
        style["margin-left"] = 0
        style["margin-right"] = "auto"
        

        thumbnail = DashIconify(icon="bxs:bot", width=30, height=30, style={"margin-right": "10px"})
        textbox = dbc.Card( dbc.CardBody(dcc.Markdown(text)), style=style, body=True, color="light", inverse=False, className="markdown")

        return html.Div([thumbnail, textbox])

    else:
        raise ValueError("Incorrect option for `box`.")


description = """
Philippe is the principal architect at a condo-development firm in Paris. He lives with his girlfriend of five years in a 2-bedroom condo, with a small dog named Coco. Since the pandemic, his firm has seen a  significant drop in condo requests. As such, he’s been spending less time designing and more time on cooking,  his favorite hobby. He loves to cook international foods, venturing beyond French cuisine. But, he is eager  to get back to architecture and combine his hobby with his occupation. That’s why he’s looking to create a  new design for the kitchens in the company’s current inventory. Can you give him advice on how to do that?
"""
conversation = html.Div(
    html.Div(id="display-conversation"),
    style={
        "overflow-y": "auto",
        "display": "flex",
        "height": "calc(90vh - 132px)",
        "flex-direction": "column-reverse",
    },
)

controls = dbc.InputGroup(
    children=[
        dbc.Input(id="user-input", placeholder="Write to the chatbot...", type="text"),
        dbc.Button("Submit", id="submit")
    ]
)


layout = dmc.MantineProvider(
    [
        html.Div([
            dcc.Location(id='url', refresh=True), 

 
            html.Div([
                html.Div([
                    html.Div("CHATBOT ANALYSER", className="page-title", style={"textAlign":"center"}),
                    html.Hr(),
                    dcc.Store(id="store-conversation", data="Hello, Im a data analyser bot. How can I help you?<split>", storage_type="session"),
                    conversation,
                    controls,
                    dbc.Spinner(html.Div(id="loading-component")),
                ], style={"margin-left": "10%", "margin-right": "10%"},
                    
                )
                
            ],className="content-pages",
            ),
            NAVBAR  
        ])
    ]
)

@dash.callback(
    Output("display-conversation", "children"), [Input("store-conversation", "data")]
)
def update_display(chat_history):
    return [
        textbox(x, box="user") if i % 2 == 1 else textbox(x, box="AI")
        for i, x in enumerate(chat_history.split("<split>")[:-1])
    ]


@dash.callback(
    Output("user-input", "value"),
    [Input("submit", "n_clicks"), Input("user-input", "n_submit")],
)
def clear_input(n_clicks, n_submit):
    return ""


@dash.callback(
    [Output("store-conversation", "data"), Output("loading-component", "children")],
    [Input("submit", "n_clicks"), Input("user-input", "n_submit")],
    [State("user-input", "value"), State("store-conversation", "data"), State('shared-array', 'data'),
     State('shared-array-columns-type', 'data'), State('shared-dataset-name', 'data')],
)
def run_chatbot(n_clicks, n_submit, user_input, chat_history, data, columns_categories, dataset_name):
    if n_clicks == 0 and n_submit is None:
        return "", None

    if user_input is None or user_input == "":
        return chat_history, None

    columns_categories = list(columns_categories.values())
    df= pd.DataFrame(data)
    columns_names = df.columns.tolist()
    columns_types=df.dtypes.tolist()
    data_set_shape= df.shape
    rep = response(client, df, user_input, dataset_name, data_set_shape,columns_names, columns_types, columns_categories)
    chat_history += f"{user_input}<split>{rep}<split>"
    return chat_history, None


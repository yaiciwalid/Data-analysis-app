# navbar.py
from dash import html, dcc
import dash_bootstrap_components as dbc
from dash_iconify import DashIconify

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "width": "18%",
    "background-color": "#002a5c",
    "display": "flex",
    "flex-direction": "column",
    "justify-content": "flex-start",
    "align-items": "flex-start",
    "padding": "2rem 1rem",
    "height": "100vh",  
    "overflow-y": "auto",  
    "overflow-x": "hidden",  
}



NAVBAR = html.Div(
    [
        dcc.Location(id='url', refresh=True),  

        dbc.Nav(
            [
                dbc.NavItem(
                    dbc.NavLink(
                        [
                            DashIconify(icon="material-symbols:home", width=20, height=20, style={"margin-right": "10px"}),
                            "Back home"
                        ],
                        href="/",
                        id="home-link",
                        active="exact",
                        
                    )
                ),
                html.P('DATA TRANSFORMATION',className = "sidebar_subtitle"),

                dbc.NavItem(
                    dbc.NavLink(
                        [
                            DashIconify(icon="grommet-icons:overview", width=20, height=20, style={"margin-right": "10px"}),
                            "Overview"
                        ],
                        href="/overview",
                        id="oevrview-link",
                        active="exact",
                        
                    )
                ),
                dbc.NavItem(
                    dbc.NavLink(
                        [
                            DashIconify(icon="carbon:transform-instructions", width=20, height=20, style={"margin-right": "10px"}),
                            "Global Transormation"
                        ],
                        href="/transform",
                        id="transform-link",
                        active="exact",
                    )
                ),
                dbc.NavItem(
                    dbc.NavLink(
                        [
                            DashIconify(icon="icon-park-solid:reverse-operation-out", width=20, height=20, style={"margin-right": "10px"}),
                            "Outlayer processing"
                        ],
                        href="/outlayer",
                        id="outlayer-link",
                        active="exact",
                    )
                ),
                html.P('DATA ANALYSIS',className = "sidebar_subtitle"),
                dbc.NavItem(
                    dbc.NavLink(
                        [
                            DashIconify(icon="uis:analysis", width=20, height=20, style={"margin-right": "10px"}),
                            "Univariate analysis"
                        ],
                        href="/univariate",
                        id="univariate-link",
                        active="exact",
                    )
                ),
                dbc.NavItem(
                    dbc.NavLink(
                        [
                            DashIconify(icon="streamline:money-graph-analytics-business-product-graph-data-chart-analysis", width=20, height=20, style={"margin-right": "10px"}),
                            "Bivariate analysis"
                        ],
                        href="/bivariate",
                        id="bivariate-link",
                        active="exact",
                    )
                ),
                dbc.NavItem(
                    dbc.NavLink(
                        [
                            DashIconify(icon="tabler:message-chatbot", width=20, height=20, style={"margin-right": "10px"}),
                            "Chatbot analysis"
                        ],
                        href="/chatbot",
                        id="chatbot-link",
                        active="exact",
                        
                    )
                ),
                html.P('MACHINE LEARNING',className = "sidebar_subtitle"),
                dbc.NavItem(
                    dbc.NavLink(
                        [
                            DashIconify(icon="bx:data", width=20, height=20, style={"margin-right": "10px"}),
                            "Training dataset"
                        ],
                        href="/page-3",
                        id="page-3-link",
                        active="exact",
                    )
                ),
                dbc.NavItem(
                    dbc.NavLink(
                        [
                            DashIconify(icon="oui:ml-classification-job", width=20, height=20, style={"margin-right": "10px"}),
                            "Classification"
                        ],
                        href="/page-7",
                        id="page-7-link",
                        active="exact",
                    )
                ),
                dbc.NavItem(
                    dbc.NavLink(
                        [
                            DashIconify(icon="vaadin:cluster", width=20, height=20, style={"margin-right": "10px"}),
                            "Clustering"
                        ],
                        href="/page-8",
                        id="page-8-link",
                        active="exact",
                    )
                ),
                dbc.NavItem(
                    dbc.NavLink(
                        [
                            DashIconify(icon="carbon:chart-logistic-regression", width=20, height=20, style={"margin-right": "10px"}),
                            "Regression"
                        ],
                        href="/page-9",
                        id="page-9-link",
                        active="exact",
                    )
                ),
            ],
            vertical=True,
            pills=True,
            className="nav-pills"
        ),
    ],
    style=SIDEBAR_STYLE,
)

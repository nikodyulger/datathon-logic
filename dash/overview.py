import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, callback, State
import plotly.express as px
import pandas as pd
import datetime as dt

# Importamos datos
df_items = pd.read_csv("../Clean Data/clean_items.csv", parse_dates=["date"])

cities = sorted(df_items[df_items['state'].notna()]['state'].unique().tolist())


@callback(Output("orders", "children"),
          Output("benefits", "children"),
          Output("qtty", "children"),
          Output("clients", "children"),
          Output("trend_graph", "figure"),
          Output("qtty_graph", "figure"),
          Output("cat_graph", "figure"),
          Output("map_graph", "figure"),
          Input("date_picker0", "start_date"),
          Input("date_picker0", "end_date"),
          Input("province0", "value"))
def update_orders(start, end, provinces):
    """Filtramos los datos segun los parametros introducidos en los filtros"""
    if not provinces:
        dff = df_items.loc[(df_items["date"] >= start)
                           & (df_items["date"] <= end)]
    else:
        dff = df_items.loc[(df_items["date"] >= start) & (
            df_items["date"] <= end) & (df_items["state"].isin(provinces))]
    return [
        # Estadísticas numéricas formateadas
        f'{dff["num_order"].nunique():n}',
        f'{dff["price"].sum() - dff["base_cost"].sum():.9n} €',
        f'{dff["qty_ordered"].sum():n}',
        f'{dff["customer_id"].nunique():n}',

        # Gráficas
        # Tendencia
        px.bar(dff.groupby("date", as_index=False).agg({"num_order": "nunique"}), x="date", y="num_order",
               labels={"date": "Fecha", "num_order": "Cantidad de pedidos"}),
        # Ranking productos
        px.bar(dff.groupby("name", as_index=False).agg({"qty_ordered": "sum"}).sort_values("qty_ordered", ascending=False).head(15)[::-1],
               y="name", x="qty_ordered", orientation='h', color="qty_ordered", text="qty_ordered", labels={"name": "Producto", "qty_ordered": "Cantidad vendida"})
        .update_traces(textfont_size=14, textposition='outside', cliponaxis=False),
        # Categorías
        px.pie(dff.groupby("analytic_category", as_index=False).agg({"qty_ordered": "sum"}), names="analytic_category", values="qty_ordered", hole=0.4,
               labels={"analytic_category": "Categoría", "qty_ordered": "Cantidad vendida"})
        .update_traces(textposition='inside', textinfo='percent+label'),
        # Mapa de "calor"
        px.scatter_mapbox(dff.groupby(by=["lat", "lon", "city"], as_index=False).agg({"qty_ordered": "sum"}), lat="lat", lon="lon",
                          color="qty_ordered", size="qty_ordered", size_max=15, zoom=3, labels={"qty_ordered": "Cantidad vendida"}, hover_name="city", mapbox_style="carto-positron", color_continuous_scale="Bluered")
    ]


@callback(
    Output("collapse0", "is_open"),
    Output("collapse-button0", "children"),
    [Input("collapse-button0", "n_clicks")],
    [State("collapse0", "is_open")],
)
def toggle_collapse(n, is_open):
    """Funcion para ocultar/mostrar la barra de filtros"""
    options = ["Mostrar filtros", "Ocultar filtros"]
    if n:
        return not is_open, options[0 if is_open else 1]
    return is_open, "Mostrar filtros"


@callback(
    Output("date_picker0", "start_date"),
    Output("date_picker0", "end_date"),
    Output("province0", "value"),
    [Input("reset-button1", "n_clicks")],
)
def reset_filter(n):
    """Funcion para limpiar los filtros"""
    return [dt.date(2017, 1, 1),
            dt.date(2018, 12, 31),
            [], ]


def get_layout():
    """Funcion que define el esqueleto de la pagina de Overview"""
    return dbc.Container([
        ############################################################ Filters ################################################################
        html.Br(),
        html.Br(),
        html.Br(),
        dbc.Row(
            dbc.Col(
                [dbc.Button(
                    "Mostrar filtros",
                    id="collapse-button0",
                    color="primary",
                    class_name="mx-3",
                    n_clicks=0,
                ),
                    dbc.Button(
                    "Resetear filtros",
                    id="reset-button1",
                    color="primary",
                    class_name="mx-3",
                    n_clicks=0)
                ], class_name="col-12 text-center"
            ),
        ),
        html.Br(),
        dbc.Collapse(
            [dbc.Row([
                dbc.Col([
                    html.Div([
                        html.H6("Rango de fechas"),
                        dcc.DatePickerRange(start_date=dt.date(2017, 1, 1), end_date=dt.date(2018, 12, 31),
                                            min_date_allowed=dt.date(2017, 1, 1), max_date_allowed=dt.date(2018, 12, 31),
                                            display_format="MMM Do, YY", start_date_placeholder_text="MMM Do, YY",
                                            end_date_placeholder_text="MMM Do, YY", id="date_picker0"),
                    ]),
                ], class_name="col-12 col-sm-6 col-md-6 col-lg-6 mb-3 text-center"),
                dbc.Col([
                    html.Div([
                        html.H6("Regiones"),
                        dcc.Dropdown(options=cities,
                                     id='province0', multi=True),
                    ]),
                ], class_name="col-12 col-sm-6 col-md-6 col-lg-6 mb-3 text-center")
            ], class_name="bg-white"),
                html.Hr()],
            id="collapse0",
            is_open=False,
        ),
        ############################################################ Stats #################################################################
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H2(id="orders", children=dbc.Spinner(
                            color="primary")),
                        html.P("Pedidos realizados", className="card-text")
                    ], class_name="text-center")
                ]),
            ], class_name="col-12 col-sm-12 col-md-6 col-lg-3 mb-3"),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H2(id="benefits", children=dbc.Spinner(
                            color="primary")),
                        html.P("Beneficios totales", className="card-text")
                    ], class_name="text-center")
                ]),
            ], class_name="col-12 col-sm-12 col-md-6 col-lg-3 mb-3"),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H2(id="qtty", children=dbc.Spinner(
                            color="primary")),
                        html.P("Productos vendidos", className="card-text")
                    ], class_name="text-center")
                ]),
            ], class_name="col-12 col-sm-12 col-md-6 col-lg-3 mb-3"),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H2(id="clients", children=dbc.Spinner(
                            color="primary")),
                        html.P("Clientes", className="card-text")
                    ], class_name="text-center")
                ])
            ], class_name="col-12 col-sm-12 col-md-6 col-lg-3 mb-3"),
        ]),
        ################################################################ Graphs ####################################################################
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5("Tendencia", className="card-title"),
                        dcc.Graph(id="trend_graph")
                    ])
                ])
            ], class_name="col-lg-12 mb-3"),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5("Mapa", className="card-title"),
                        dcc.Graph(id="map_graph")
                    ])
                ])
            ], class_name="col-md-12 col-lg-6 mb-3"),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5(["Categorías ",
                                 html.I(className="bi bi-info-circle",
                                        id="cat-help"),
                                 dbc.Tooltip(
                                    "Se muestran las categorías en base a la cantidad de productos vendidos",
                                    target="cat-help",
                                 ), ], className="card-title"),
                        dcc.Graph(id="cat_graph")
                    ])
                ])
            ], class_name="col-md-12 col-lg-6 mb-3"),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5("Productos más vendidos",
                                className="card-title"),
                        dcc.Graph(id="qtty_graph"),
                    ])
                ])
            ], class_name="col-lg-12 mb-3"),
        ]),
        html.Br(),
        html.Br()
    ], fluid=True)

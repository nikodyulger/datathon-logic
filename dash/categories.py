import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, State, callback
import plotly.express as px
import pandas as pd
import datetime as dt
import locale

# Importamos datos y los tranformamos
df_items = pd.read_csv("../Clean Data/clean_items.csv", parse_dates=["date"])
df_items["benefit"] = (df_items["price"] -
                       df_items["base_cost"]) * df_items["qty_ordered"]
cities_all = sorted(
    df_items[df_items['state'].notna()]['state'].unique().tolist())
categories_all = sorted(df_items['analytic_category'].unique().tolist())


@callback(Output("mean_price", "children"),
          Output("benefits_cat", "children"),
          Output("sold_products", "children"),
          Output("clients_cat", "children"),
          Output("most_sold_brand", "figure"),
          Output("greatest_benefit_brand", "figure"),
          Output("cat_graph_cat", "figure"),
          Input("date_picker", "start_date"),
          Input("date_picker", "end_date"),
          Input("category", "value"),
          Input("province", "value"))
def update_orders(start, end, categories, provinces):
    """Funcion para filtrar los datos segun los parametros de entrada de los filtros"""
    # Dependiendo de los parametros realizamos una u otra accion
    if not provinces and not categories:
        dff = df_items.loc[(df_items["date"] >= start)
                           & (df_items["date"] <= end)]
    elif not provinces and categories:
        dff = df_items.loc[(df_items["date"] >= start) & (df_items["date"] <= end) & (
            df_items["analytic_category"].isin(categories))]
    elif not categories:
        dff = df_items.loc[(df_items["date"] >= start) & (
            df_items["date"] <= end) & (df_items["state"].isin(provinces))]
    else:
        dff = df_items.loc[(df_items["date"] >= start) & (df_items["date"] <= end) & (
            df_items["state"].isin(provinces)) & (df_items["analytic_category"].isin(categories))]

    # Aplicamos los filtros
    dff2 = dff.groupby(['marca_value', 'analytic_category'], as_index=False).agg(
        {"qty_ordered": "sum", "benefit": "sum"})

    return [
        # Estadísticas numericas
        f'{locale.format_string("%.2f", dff["price"].mean() if dff["price"].mean() > 0 else 0, grouping=True)} €',
        f'{locale.format_string("%.2f", dff["benefit"].sum(), grouping=True)} €',
        f'{dff["product_id"].nunique():n}',
        f'{dff["customer_id"].nunique():n}',

        # Graficas
        # Marcas más vendidas
        px.treemap(dff2[(dff2["qty_ordered"] > 0)].sort_values("qty_ordered", ascending=False).groupby('analytic_category').head(20),
                   path=[px.Constant("Vista general"), "analytic_category", "marca_value"], values="qty_ordered", labels={"marca_value": "Marca", "analytic_category": "Categoría", "qty_ordered": "Cantidad"},
                   color="qty_ordered", color_continuous_scale="ice"),
        # Marcas que mas beneficio generan
        px.sunburst(dff2[(dff2["benefit"] > 0)].sort_values("benefit", ascending=False).groupby('analytic_category').head(10),
                    path=["analytic_category", "marca_value"], values="benefit", labels={"marca_value": "Marca", "analytic_category": "Categoría", "benefit": "Beneficio"},
                    color="benefit", color_continuous_scale="ice"),
        # Ventas por categorías
        px.histogram(data_frame=dff, nbins=24, x="date", y="qty_ordered", color="analytic_category",
                     labels={"date": "Fecha", "analytic_category": "Categoría", "qty_ordered": "Cantidad"})
            .update_yaxes(title_text='Nº productos')
    ]


@callback(
    Output("collapse2", "is_open"),
    Output("collapse-button2", "children"),
    [Input("collapse-button2", "n_clicks")],
    [State("collapse2", "is_open")],
)
def toggle_collapse(n, is_open):
    """Funcion para ocultar/mostrar la barra de filtros"""
    options = ["Mostrar filtros", "Ocultar filtros"]
    if n:
        return not is_open, options[0 if is_open else 1]
    return is_open, "Mostrar filtros"


@callback(
    Output("date_picker", "start_date"),
    Output("date_picker", "end_date"),
    Output("category", "value"),
    Output("province", "value"),
    [Input("reset-button2", "n_clicks")],
)
def reset_filter(n):
    """Funcion para limpiar los filtros"""
    return [dt.date(2017, 1, 1),
            dt.date(2018, 12, 31),
            [],
            [], ]


def get_layout():
    """Funcion que define el esqueleto de la pagina de Categories"""
    return dbc.Container([
        ############################################################ Filters ############################################################
        html.Br(),
        html.Br(),
        html.Br(),
        dbc.Row(
            dbc.Col(
                [dbc.Button(
                    "Mostrar filtros",
                    id="collapse-button2",
                    color="primary",
                    class_name="mx-3",
                    n_clicks=0,
                ),
                    dbc.Button(
                    "Resetear filtros",
                    id="reset-button2",
                    color="primary",
                    class_name="mx-3",
                    n_clicks=0)
                ], class_name="col-12 text-center"
            ),
        ),
        html.Br(),
        dbc.Collapse([
            dbc.Container([], class_name="m-2"),
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.H6("Rango de fechas"),
                        dcc.DatePickerRange(start_date=dt.date(2017, 1, 1), end_date=dt.date(2018, 12, 31),
                                            min_date_allowed=dt.date(2017, 1, 1), max_date_allowed=dt.date(2018, 12, 31),
                                            display_format="MMM Do, YY", start_date_placeholder_text="MMM Do, YY",
                                            end_date_placeholder_text="MMM Do, YY", id="date_picker"),
                    ]),
                ], class_name="col-12 col-sm-6 col-md-6 col-lg-4 mt-3 text-center"),
                dbc.Col([
                    html.Div([
                        html.H6("Categorías"),
                        dcc.Dropdown(options=categories_all,
                                     id='category', multi=True),
                    ]),
                ], class_name="col-12 col-sm-6 col-md-6 col-lg-4 mt-3 text-center"),
                dbc.Col([
                    html.Div([
                        html.H6("Regiones"),
                        dcc.Dropdown(options=cities_all,
                                     id='province', multi=True),
                    ]),
                ], class_name="col-12 col-sm-6 col-md-6 col-lg-4 mt-3 text-center"),
            ], class_name="bg-white"),
            html.Hr(),
        ], id="collapse2", is_open=False),
        ######################################################################### Stats #########################################################
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H2(id="clients_cat", children=dbc.Spinner()),
                        html.P("Clientes", className="card-text")
                    ], class_name="text-center")
                ])
            ], class_name="col-sm-12 col-md-6 col-lg-3 mb-3"),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H2(id="sold_products", children=dbc.Spinner()),
                        html.P("Productos vendidos", className="card-text")
                    ], class_name="text-center")
                ]),
            ], class_name="col-sm-12 col-md-6 col-lg-3 mb-3"),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H2(id="mean_price", children=dbc.Spinner()),
                        html.P("Precio medio", className="card-text")
                    ], class_name="text-center")
                ]),
            ], class_name="col-12 col-sm-12 col-md-6 col-lg-3 mb-3"),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H2(id="benefits_cat", children=dbc.Spinner()),
                        html.P("Beneficios totales", className="card-text")
                    ], class_name="text-center")
                ]),
            ], class_name="col-12 col-sm-12 col-md-6 col-lg-3 mb-3"),
        ]),
        ######################################################################### Graphs #########################################################
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5([
                            "Marcas más vendidas ",
                            html.I(className="bi bi-info-circle",
                                   id="marcas_help1"),
                            dbc.Tooltip(
                                "Solo se muestran las 20 marcas que más cantidad venden por cada una de las categorias",
                                target="marcas_help1",
                            ),
                        ], className="card-title"),
                        dcc.Graph(id="most_sold_brand")
                    ])
                ])
            ], class_name="col-md-12 col-lg-6 mb-3"),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5([
                            "Marcas con más beneficio ",
                            html.I(className="bi bi-info-circle",
                                   id="marcas_help2"),
                            dbc.Tooltip(
                                "Solo se muestran las 10 marcas que más beneficio generan por cada una de las categorias",
                                target="marcas_help2",
                            ),
                        ], className="card-title"),
                        dcc.Graph(id="greatest_benefit_brand")
                    ])
                ])
            ], class_name="col-md-12 col-lg-6 mb-3"),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5("Productos vendidos", className="card-title"),
                        dcc.Graph(id="cat_graph_cat")
                    ])
                ])
            ], class_name="col-lg-12 mb-3")
        ]),
        html.Br(),
        html.Br()
    ], fluid=True)

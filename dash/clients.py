import dash_bootstrap_components as dbc
from dash import dash_table, html, dcc, Input, Output, callback, State
import plotly.express as px
import pandas as pd
import datetime as dt
import locale

# Importamos datos y los tranformamos
df_items = pd.read_csv("../Clean Data/clean_items.csv", parse_dates=["date"])
dff = df_items.groupby(['customer_id', 'num_order', 'analytic_category'],
                       as_index=False).agg({'qty_ordered': 'sum', 'price': 'sum'})
dff = dff.groupby(['customer_id', 'num_order'], as_index=False).agg(
    {'qty_ordered': 'sum', 'price': 'sum', 'analytic_category': 'count'})
dff = dff.groupby(['customer_id'], as_index=False).agg(
    {'num_order': 'count', 'qty_ordered': 'sum', 'price': 'sum'})
dff['price'].round(decimals=2)

categories = sorted(df_items['analytic_category'].unique().tolist())


@callback(Output("n_clients", "children"),
          Output("cat_order", "children"),
          Output("qty_order", "children"),
          Output("cost_order", "children"),
          Output("more_orders", "figure"),
          Output("more_money", "figure"),
          Output("datatable-interactivity", "data"),
          Input("date_picker3", "start_date"),
          Input("date_picker3", "end_date"),
          Input("categories3", "value"),
          Input("orders_count", "value"),
          Input("total_price", "value"))
def update_orders(start, end, categories, orders, prices):
    """Funcion para filtrar los datos segun los parametros de entrada de los filtros"""
    global dff
    if not categories:
        dff = df_items.loc[(df_items["date"] >= start)
                           & (df_items["date"] <= end)]
    else:
        dff = df_items.loc[(df_items["date"] >= start) & (df_items["date"] <= end) & (
            df_items["analytic_category"].isin(categories))]

    # Aplicamos los filtros
    dff = dff.groupby(['customer_id', 'num_order', 'analytic_category'],
                      as_index=False).agg({'qty_ordered': 'sum', 'price': 'sum'})
    dff = dff.groupby(['customer_id', 'num_order'], as_index=False).agg(
        {'qty_ordered': 'sum', 'price': 'sum', 'analytic_category': 'count'})
    dff = dff.groupby(['customer_id'], as_index=False).agg(
        {'num_order': 'count', 'qty_ordered': 'sum', 'price': 'sum', 'analytic_category': 'mean'})

    dff = dff.loc[(dff["num_order"] >= orders[0]) & (dff["num_order"] <= orders[1]) & (
        dff["price"] >= prices[0]) & (dff["price"] <= prices[1])]
    dff['price'].round(decimals=2)
    dff_shortened_customer = dff.copy()
    dff_shortened_customer["customer_id"] = dff_shortened_customer["customer_id"].apply(
        lambda x: x[:6])

    return [
        # Estadísticas numéricas
        f'{dff["customer_id"].count():n}',
        f'{dff["analytic_category"].mean() if dff["analytic_category"].mean() > 0 else 0:.0f}',
        f'{dff["qty_ordered"].mean() if dff["qty_ordered"].mean() > 0 else 0:.0f}',
        f'{locale.format_string("%.0f", dff["price"].mean() if dff["price"].mean() > 0 else 0, grouping=True)} €',
        # Gráficas
        # Ranking de clientes con más pedidos
        px.bar(dff_shortened_customer.sort_values(by='num_order').tail(10),
               y="customer_id", x="num_order", orientation='h', color="num_order", text="num_order", color_continuous_scale="Sunset", labels={"customer_id": "Cliente", "num_order": "Nº de pedidos"})
        .update_traces(textfont_size=14, textposition='outside', cliponaxis=False),
        # Ranking de clientes con mayor desembolso
        px.bar_polar(dff_shortened_customer.sort_values(by='price').tail(10),
                     theta="customer_id", r="price", color="price", labels={"customer_id": "Cliente", "price": "Dinero gastado (€)"}, color_continuous_scale="aggrnyl"),
        # Datos tabla interactiva
        dff.to_dict('records')]


@callback(
    Output("collapse", "is_open"),
    Output("collapse-button", "children"),
    [Input("collapse-button", "n_clicks")],
    [State("collapse", "is_open")],
)
def toggle_collapse(n, is_open):
    """Funcion para ocultar/mostrar la barra de filtros"""
    options = ["Mostrar filtros", "Ocultar filtros"]
    if n:
        return not is_open, options[0 if is_open else 1]
    return is_open, "Mostrar filtros"


@callback(
    Output("date_picker3", "start_date"),
    Output("date_picker3", "end_date"),
    Output("categories3", "value"),
    Output("orders_count", "value"),
    Output("total_price", "value"),
    [Input("reset-button3", "n_clicks")],
)
def reset_filter(n):
    """Funcion para limpiar los filtros"""
    aux = df_items.groupby(['customer_id', 'num_order', 'analytic_category'], as_index=False).agg(
        {'qty_ordered': 'sum', 'price': 'sum'})
    aux = aux.groupby(['customer_id', 'num_order'], as_index=False).agg(
        {'qty_ordered': 'sum', 'price': 'sum', 'analytic_category': 'count'})
    dff = aux.groupby(['customer_id'], as_index=False).agg(
        {'num_order': 'count', 'qty_ordered': 'sum', 'price': 'sum'})
    dff['price'].round(decimals=2)
    return [dt.date(2017, 1, 1),
            dt.date(2018, 12, 31),
            [],
            [dff["num_order"].min(), dff["num_order"].max()],
            [dff["price"].min(), dff["price"].max()]]


def get_layout():
    """Funcion que define el esqueleto de la pagina de Clients"""
    return dbc.Container([
        ############################################################ Filters ############################################################
        html.Br(),
        html.Br(),
        html.Br(),
        dbc.Row(
            dbc.Col(
                [dbc.Button(
                    "Mostrar filtros",
                    id="collapse-button",
                    color="primary",
                    class_name="mx-3",
                    n_clicks=0,
                ),
                    dbc.Button(
                    "Resetear filtros",
                    id="reset-button3",
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
                                            end_date_placeholder_text="MMM Do, YY", id="date_picker3"),
                    ]),
                ], class_name="col-12 col-sm-6 col-md-6 col-lg-6 mb-3 text-center"),
                dbc.Col([
                    html.Div([
                        html.H6("Categoría"),
                        dcc.Dropdown(options=categories,
                                     id='categories3', multi=True),
                    ]),
                ], class_name="col-12 col-sm-6 col-md-6 col-lg-6 mb-3 text-center"),
                dbc.Col([
                    html.Div([
                        html.H6("Nº pedidos realizados"),
                        dcc.RangeSlider(dff["num_order"].min(), dff["num_order"].max(), value=[
                                        dff["num_order"].min(), dff["num_order"].max()], id="orders_count"),
                    ]),
                ], class_name="col-12 col-sm-6 col-md-6 col-lg-6 mb-3 text-center"),
                dbc.Col([
                    html.Div([
                        html.H6("Dinero gastado (€)"),
                        dcc.RangeSlider(dff["price"].min(), dff["price"].max(), value=[
                                        dff["price"].min(), dff["price"].max()], id="total_price"),
                    ]),
                ], class_name="col-12 col-sm-6 col-md-6 col-lg-6 mb-3 text-center"),
                dbc.Col([
                    html.Div([

                    ]),
                ], class_name="col-12 mb-3 text-center")
            ], class_name="bg-white"),
                html.Hr()],
            id="collapse",
            is_open=False,
        ),
        ########################################################### Stats ##################################################################
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H2(id="n_clients", children=dbc.Spinner(
                            color="primary")),
                        html.P("Clientes", className="card-text")
                    ], class_name="text-center")
                ]),
            ], class_name="col-12 col-sm-12 col-md-6 col-lg-3 mb-3"),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H2(id="cat_order", children=dbc.Spinner(
                            color="primary")),
                        html.P("Media de categorias por pedido",
                               className="card-text")
                    ], class_name="text-center")
                ]),
            ], class_name="col-12 col-sm-12 col-md-6 col-lg-3 mb-3"),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H2(id="qty_order", children=dbc.Spinner(
                            color="primary")),
                        html.P("Media de productos por pedido",
                               className="card-text")
                    ], class_name="text-center")
                ]),
            ], class_name="col-12 col-sm-12 col-md-6 col-lg-3 mb-3"),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H2(id="cost_order",
                                children=dbc.Spinner(color="primary")),
                        html.P("Media de gasto por pedido",
                               className="card-text")
                    ], class_name="text-center")
                ])
            ], class_name="col-12 col-sm-12 col-md-6 col-lg-3 mb-3"),
        ]),
        ########################################################### Graphs ##################################################################
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5("Pedidos realizados", className="card-title"),
                        dcc.Graph(id="more_orders"),
                    ])
                ])
            ], class_name="col-mg-12 col-lg-6 mb-3"),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5("Dinero gastado", className="card-title"),
                        dcc.Graph(id="more_money"),
                    ])
                ])
            ], class_name="col-mg-12 col-lg-6 mb-3"),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5([
                            "Tabla resumen  ",
                            html.I(className="bi bi-info-circle",
                                   id="table-help"),
                            dbc.Tooltip(
                                "Esta tabla muestra todos los usuarios con sus estadísticas. "
                                "Puedes filtrar por los diferentes campos usando comprobaciones como '> 10' y pulsando Intro",
                                target="table-help",
                            ),
                        ], className="card-title"),
                        dash_table.DataTable(
                            id='datatable-interactivity',
                            columns=[
                                {"name": i, "id": i, "deletable": False, "selectable": False} for i in dff.columns
                            ],
                            data=dff.to_dict('records'),
                            editable=False,
                            filter_action="native",
                            sort_action="native",
                            sort_mode="multi",
                            row_deletable=False,
                            selected_columns=[],
                            selected_rows=[],
                            page_action="native",
                            page_current=0,
                            page_size=10,
                        ), ])
                ])
            ], class_name="col-12 mb-3"),
        ]),
        html.Br(),
        html.Br()
    ], fluid=True)

from http import client
import locale
import dash_bootstrap_components as dbc
from dash import Dash, html, dcc, Input, Output
import overview
import categories
import clients

locale.setlocale(locale.LC_ALL, '')

# Definimos la aplicacion
app = Dash(__name__, external_stylesheets=[dbc.themes.CERULEAN, dbc.icons.BOOTSTRAP], suppress_callback_exceptions=True,
           meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}, ],)

app.title = "Datathon-Log(ic)"

# Layout de la barra de navegación
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink(
            [html.I(className="bi bi-house-fill"), " Vista general"], href="/")),
        dbc.NavItem(dbc.NavLink(
            [html.I(className="bi bi-tag-fill"), " Categorías"], href="/categories")),
        dbc.NavItem(dbc.NavLink(
            [html.I(className="bi bi-people-fill"), " Clientes"], href="/clients")),
        dbc.NavItem(dbc.NavLink([html.I(className="bi bi-github"), " Github"],
                                href="https://github.com/nikodyulger/datathon-logic", external_link=True, target="_blank")),
    ],
    brand="MiFarma Dashboard",
    brand_href="/",
    color="primary",
    dark=True,
    fluid=True,
    class_name="fixed-top"
)

app.layout = app.layout = html.Div([
    navbar,
    dcc.Location("url"),
    html.Div(id='page-content')
])


@app.callback(Output("page-content", "children"), Input("url", "pathname"))
def create_layout(pathname):
    """Funcion para el manejo de las URLs"""
    if pathname == '/categories':
        return categories.get_layout()
    elif pathname == '/clients':
        return clients.get_layout()
    else:
        return overview.get_layout()


if __name__ == '__main__':
    app.run_server(debug=True)

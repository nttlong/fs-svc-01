import sys
import pathlib
sys.path.append(pathlib.Path(__file__).parent.parent.__str__())
import dash
import dash_bootstrap_components as dbc
from dash import Dash, dcc, html, Input, Output
from cy_ui.main_page import get_header
app = dash.Dash(external_stylesheets=[dbc.themes.DARKLY],url_base_pathname='/godash/')
from dash import Dash, html
header = get_header(app)
app.layout = html.Div(
    [header, html.Div(id='app-page-content')]
)


if __name__ == "__main__":
    # Only for debugging while developing
    app.run_server(host="0.0.0.0", debug=True, port=8081)
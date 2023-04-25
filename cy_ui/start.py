import sys
import pathlib
sys.path.append(pathlib.Path(__file__).parent.parent.__str__())
import dash
import dash_bootstrap_components as dbc
from dash import Dash, dcc, html, Input, Output
from cy_ui.main_page import get_header
import dash_uploader as du
app = dash.Dash(external_stylesheets=[dbc.themes.DARKLY],url_base_pathname='/godash/',use_pages=True)

from dash import Dash, html
header = get_header(app)
du.configure_upload(app, r"/home/vmadmin/python/v6/file-service-02/background_service_files/file")
app.layout = html.Div(
    [header, dash.page_container]
)


if __name__ == "__main__":
    # Only for debugging while developing
    app.run_server(host="0.0.0.0", debug=True, port=8081)
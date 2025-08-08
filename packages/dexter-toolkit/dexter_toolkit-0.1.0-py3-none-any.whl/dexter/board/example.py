from jupyter_dash import JupyterDash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

# Create a JupyterDash app
app = JupyterDash(__name__)

app.layout = html.Div([
    html.H1('Dash App with IPython Terminal'),
    dcc.Input(id='input', value='initial value', type='text'),
    html.Div(id='output')
])

@app.callback(
    Output('output', 'children'),
    [Input('input', 'value')]
)
def update_output(value):
    return f'You entered: {value}'

app.run_server(mode='inline')

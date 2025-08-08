import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, State
import subprocess
import threading

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Layout of the Dash app
app.layout = dbc.Container([
    dbc.Row(dbc.Col(html.H1("IPython Terminal in Dash App"), className="text-center")),
    dbc.Row(dbc.Col(dcc.Textarea(id='terminal-output', style={'width': '100%', 'height': '400px'}))),
    dbc.Row([
        dbc.Col(dcc.Input(id='terminal-input', type='text', style={'width': '100%'})),
        dbc.Col(dbc.Button('Run', id='run-button', color='primary'), width='auto')
    ])
])

# Function to start IPython terminal in a separate thread
def start_ipython_terminal(queue):
    console = subprocess.Popen(['jupyter-console'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    while True:
        output = console.stdout.readline()
        if output:
            queue.append(output)

# Callback to handle terminal input and output
@app.callback(
    Output('terminal-output', 'value'),
    Input('run-button', 'n_clicks'),
    State('terminal-input', 'value'),
    State('terminal-output', 'value'),
    prevent_initial_call=True
)
def run_command(n_clicks, command, current_output):
    if n_clicks:
        console.stdin.write(command + '\n')
        console.stdin.flush()
        return current_output + '\n' + '>>> ' + command + '\n' + console.stdout.readline()
    return current_output

# Start IPython terminal
console = subprocess.Popen(['jupyter-console'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
output_queue = []
thread = threading.Thread(target=start_ipython_terminal, args=(output_queue,))
thread.start()

if __name__ == '__main__':
    app.run_server(debug=True)

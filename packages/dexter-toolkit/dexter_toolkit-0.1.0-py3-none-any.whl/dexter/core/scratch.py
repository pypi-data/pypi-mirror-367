import dash
from dash import html, dcc, Input, Output
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import plotly.express as px

# Simulated data for demonstration
np.random.seed(42)
dates = pd.date_range(start="2023-01-01", periods=120, freq="D")
revenue = np.random.gamma(shape=9, scale=100, size=120).cumsum()
inventory_data = pd.DataFrame({
    "Date": dates,
    "Revenue": revenue,
    "Inventory": np.random.choice([100, 150, 200, 250], size=120),
    "Days to Sell": np.random.choice([10, 15, 20, 25], size=120)
})

# Calculate KPIs
average_days_to_sell = inventory_data["Days to Sell"].mean()
inventory_turnover_rate = len(inventory_data) / inventory_data["Inventory"].mean()

# Plotting
fig_revenue = px.line(inventory_data, x="Date", y="Revenue", title="Revenue Over Time")
fig_stock_levels = px.bar(inventory_data[-10:], x="Date", y="Inventory", title="Current Stock Levels")
fig_turnover = go.Figure(go.Indicator(
    mode="gauge+number",
    value=inventory_turnover_rate,
    title={'text': "Inventory Turnover Rate"},
    domain={'x': [0, 1], 'y': [0, 1]}
))
fig_days_to_sell = px.histogram(inventory_data, x="Days to Sell", nbins=15, title="Average Days to Sell Inventory")

app = dash.Dash(__name__)

app.layout = html.Div([
    html.Div([
        html.Button("Refresh", id="refresh-button"),
        html.Button("Export Data", id="export-data-button")
    ], style={'padding': 10}),

    dcc.Tabs(id="tabs", value='tab-1', children=[
        dcc.Tab(label='Revenue', value='tab-1'),
        dcc.Tab(label='Inventory Levels', value='tab-2'),
        dcc.Tab(label='Performance Metrics', value='tab-3'),
    ]),
    html.Div(id='tabs-content')
])

@app.callback(Output('tabs-content', 'children'),
              Input('tabs', 'value'))
def render_content(tab):
    if tab == 'tab-1':
        return html.Div([
            dcc.Graph(figure=fig_revenue)
        ])
    elif tab == 'tab-2':
        return html.Div([
            dcc.Graph(figure=fig_stock_levels)
        ])
    elif tab == 'tab-3':
        return html.Div([
            dcc.Graph(figure=fig_turnover),
            dcc.Graph(figure=fig_days_to_sell)
        ])

if __name__ == '__main__':
    app.run_server(debug=True)

import numpy as np
import pandas as pd
import dash
from dash import dcc, html, dash_table
import plotly.express as px


class Invento:
    def __init__(self, df:pd.DataFrame):
        self.df = df
        self.bar = self.setup_bar()
        self.app = self.setup_app()


    def setup_app(self):
        app = dash.Dash(__name__)

        # App layout
        app.layout = html.Div(children=[
            html.Div(children=[
                html.H1("DataFrame Display"),
                dash_table.DataTable(
                    id='table',
                    columns=[{"name": i, "id": i} for i in self.df.columns],
                    data=self.df.to_dict('records'),
                    style_cell={'textAlign': 'left'}
                )], style={"display":"inline-block"}),
            html.Div(children=[
                html.H2("Stock per Product"),
                dcc.Graph(figure=self.bar)
            ], style={'width':'500px',      'display':'inline-block', 'margin':'5px'})
        ])
        
        return app
    
    def setup_bar(self):
        fig = px.bar(inv_df, x='name', y='stock', title='Stock per Product', color="name")
        return fig

if __name__ == "__main__":
    inv_df = pd.read_csv("Large_Simple_Inventory.csv")

    new_stock = np.random.normal(inv_df["stock"].mean(), inv_df["stock"].std(), inv_df.shape[0])
    inv_df["stock"] = new_stock

    inv = Invento(inv_df)

    inv.app.run_server(debug=True)




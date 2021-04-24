import dash_html_components as html
import pandas as pd
import dash_core_components as dcc
import plotly.graph_objs as go
from scipy.optimize import curve_fit
from sigfig import round
import dash
import dash_table
import scipy.integrate as integrate
import os
import fnmatch


def func(x, a, b):
    return a * x ** b


layout = None
port = 8050
for filename in os.listdir('.'):
    if fnmatch.fnmatch(filename, 'data*.csv'):
        df = pd.read_csv(filename)
        xdata = df.supply
        ydata = df.price
        popt, pcov = curve_fit(func, xdata, ydata)

        l = []
        for i in range(10000, 101000, 1000):
            l.append(
                {'supply': i, 'price': int(func(i, *popt)),
                 'total': int(integrate.quad(func, 0, i, args=(popt[0], popt[1]))[0])})

        df = pd.DataFrame(l)

        a = float(df.price[df.supply == 10000])
        b = float(df.price[df.supply == 20000])

        result = integrate.quad(func, 10000, 100000, args=(popt[0], popt[1]))[0]

        external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

        app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

        fig_one = go.Figure(go.Scatter(x=df.supply, y=df.price), layout={
            'title': 'price (DAI) vs supply (ARRAY)'
        })

        fig_two = go.Figure(go.Scatter(x=df.supply, y=df.total), layout={
            'title': 'price (DAI) vs supply (ARRAY)'
        })

        app.layout = html.Div(children=[

            html.H6(children=f'adjusted formula: y = {round(float(popt[0]), 4)} * x ** {round(float(popt[1]), 4)}'),
            html.H6(children=f'price increases  by {b / a:.3f} for every doubling of supply'),
            html.H6(children=f'max. market cap (100k supply) = ${result:,.0f} DAI'),

            dcc.Graph(
                id='price',

                figure=fig_one,
                style={'title': 'price vs supply'}

            ),

            dcc.Graph(
                id='total',

                figure=fig_two,
                style={'title': 'total vs supply'}

            ),

            dash_table.DataTable(
                id='table',
                columns=[{"name": i, "id": i} for i in df.columns],
                data=df.to_dict('records'), style_cell_conditional=[
                    {'if': {'column_id': 'supply'},
                     'width': '100'},
                    {'if': {'column_id': 'price'},
                     'width': '100'}
                ], style_table={'width': '50%'})
        ],
        )
        port = port + 1
        app.run_server(debug=True, port=port)

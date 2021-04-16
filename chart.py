import dash_html_components as html
import pandas as pd
import dash_core_components as dcc
import plotly.graph_objs as go
from scipy.optimize import curve_fit
from sigfig import round
import dash
import dash_table
import scipy.integrate as integrate


def func(x, a, b):
    return a * x ** b


m = 7.550247718452775e-06
exp = 1.6000026000026

df = pd.read_csv('data.csv')
xdata = df.supply
ydata = df.price
popt, pcov = curve_fit(func, xdata, ydata)

l = []
for i in range(10000, 101000, 1000):
    l.append({'supply': i, 'price': int(func(i, *popt))})

df = pd.DataFrame(l)

a = float(df.price[df.supply == 10000])
b = float(df.price[df.supply == 20000])

result = integrate.quad(func, 10000, 100000, args=(popt[0], popt[1]))[0]

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

fig = go.Figure(go.Scatter(x=df.supply, y=df.price), layout={
    'title': 'price (DAI) vs supply (ARRAY)'
})

app.layout = html.Div(children=[

    html.H6(children=f'input formula: y = {round(m, 4)} * x ** {round(exp, 4)}'),
    html.H6(children=f'adjusted formula: y = {round(float(popt[0]), 4)} * x ** {round(float(popt[1]), 4)}'),
    html.H6(children=f'price increases  by {b / a:.3f} for every doubling of supply'),
    html.H6(children=f'max. market cap (100k supply) = ${result:,.0f} DAI'),

    dcc.Graph(
        id='example-graph',

        figure=fig,
        style={'title': 'price vs supply'}

    ),

    dash_table.DataTable(
        id='table',
        columns=[{"name": i, "id": i} for i in df.columns],
        data=df.to_dict('records'), style_cell_conditional=[
            {'if': {'column_id': 'supply'},
             'width': '130px'},
            {'if': {'column_id': 'price'},
             'width': '130px'}
        ])
], style={'width': '25%'}
)

if __name__ == '__main__':

    app.run_server(debug=True)

import dash
import dash_html_components as html
import pandas as pd
import dash_core_components as dcc
import plotly.graph_objs as go


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

df = pd.read_csv('../plot/data.csv')

fig = go.Figure(go.Scatter(x=df['supply'], y=df['price'], line_shape='spline'))
app.layout = html.Div(children=[
    dcc.Graph(
        id='example-graph',
        figure=fig
    )
], style={ "height" :'10vh' ,'width': '40vh'}
)

if __name__ == '__main__':
    app.run_server(debug=True)

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

from weather_service.db_utils import get_historical_data, get_realtime_data

app = dash.Dash(__name__)

def plot_data(data):
    # Create a line chart using the data
    # You can use any plotting library of your choice, such as Plotly or Matplotlib
    # Here's an example using Plotly:
    fig = px.line(data, x='date', y='value')
    return dcc.Graph(figure=fig)

@app.callback(Output('historical-chart', 'children'), [Input('refresh-button', 'n_clicks')])
def update_historical_chart(n_clicks):
    # Retrieve historical data from the database using db_utils.py
    historical_data = get_historical_data()
    return plot_data(historical_data)

@app.callback(Output('realtime-chart', 'children'), [Input('refresh-button', 'n_clicks')])
def update_realtime_chart(n_clicks):
    # Retrieve realtime data from the database using db_utils.py
    realtime_data = get_realtime_data()
    return plot_data(realtime_data)

def combine_charts():
    # Retrieve both historical and realtime data
    historical_data = get_historical_data()
    realtime_data = get_realtime_data()

    # Combine the data into a single dataframe or plot
    combined_data = pd.concat([historical_data, realtime_data])

    return plot_data(combined_data)

app.layout = html.Div([
    html.H1("Weather Data Processing"),
    html.Button('Refresh Data', id='refresh-button', n_clicks=0),
    html.Div(id='historical-chart'),
    html.Div(id='realtime-chart'),
    html.Div(combine_charts())
])

if __name__ == '__main__':
    app.run_server(debug=True)
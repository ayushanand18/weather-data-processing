import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

from weather_service.db_utils import get_historical_data, get_realtime_data

app = dash.Dash(
    __name__,
    requests_pathname_prefix='/statistics/'
)

def plot_data(data, col):
    fig = px.bar(data, x='dt', y=col, color='city', barmode='group',
             title='Temperature vs Date for Different Cities',
             labels={'temp': 'Temperature', 'dt': 'Date'})
    
    return dcc.Graph(figure=fig)

@app.callback(Output('historical-chart', 'children'), [Input('refresh-button', 'n_clicks')])
def update_historical_chart(n_clicks):
    # Retrieve historical data from the database using db_utils.py
    historical_data = pd.DataFrame(eval(get_historical_data()))
    return plot_data(historical_data)

@app.callback(Output('realtime-chart', 'children'), [Input('refresh-button', 'n_clicks')])
def update_realtime_chart(n_clicks):
    # Retrieve realtime data from the database using db_utils.py
    realtime_data = pd.DataFrame(eval(get_realtime_data()))
    realtime_data['dt'] = realtime_data['dt'].astype('category')
    return plot_data(realtime_data, 'temp')

def plot_realtime_data():
    realtime_data = pd.DataFrame(eval(get_realtime_data()))
    realtime_data['dt'] = realtime_data['dt'].astype('category')

    return plot_data(realtime_data, 'temp')

def plot_historical_data():
    data = get_historical_data()
    df = pd.DataFrame(eval(data))
    return [html.Div([
        html.H2("Temperature vs Time"),
        plot_data(df, 'temp')
    ])]

app.layout = html.Div([
    html.H1("Weather Data Historical and Realtime"),
    html.Button('Refresh Data', id='refresh-button', n_clicks=0),
    html.Div(id='realtime-chart', title="Realtime Weather Data", children=plot_realtime_data()),
    # html.Div(id='historical-chart', children=plot_historical_data()),
])

if __name__ == '__main__':
    app.run_server(debug=True)
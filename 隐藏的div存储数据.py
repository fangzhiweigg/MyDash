import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd

app = dash.Dash('隐藏的div', external_stylesheets=['assets/bWLwgP.css'])


global_df = pd.read_excel('合并_1218_1755.xlsx')

app.layout = html.Div([
    dcc.Graph(id='graph'),
    html.Table(id='table'),
    dcc.Dropdown(id='dropdown'),
    # Hidden div inside the app that stores the intermediate value
    html.Div(id='intermediate-value', style={'display': 'none'})
])


@app.callback(Output('intermediate-value', 'children'), [Input('dropdown', 'value')])
def clean_data(value):

     # some expensive clean data step
     cleaned_df = value

     # more generally, this line would be
     # json.dumps(cleaned_df)
     return cleaned_df.to_json(date_format='iso', orient='split')


@app.callback(Output('graph', 'figure'), [Input('intermediate-value', 'children')])
def update_graph(jsonified_cleaned_data):

    # more generally, this line would be
    # json.loads(jsonified_cleaned_data)
    dff = pd.read_json(jsonified_cleaned_data, orient='split')

    figure = (dff)
    return figure


# @app.callback(Output('table', 'children'), [Input('intermediate-value', 'children')])
# def update_table(jsonified_cleaned_data):
#     dff = pd.read_json(jsonified_cleaned_data, orient='split')
#     table = create_table(dff)
#     return table
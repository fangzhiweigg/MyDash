import dash
import base64, io, datetime
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Output, Input, State
from dash.exceptions import PreventUpdate
import dash_table

import pandas as pd

app = dash.Dash(__name__, external_stylesheets=['assets/bWLwgP.css'])

app.layout = html.Div([
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        multiple=True
    ),
    html.H4('store_in'),
    dcc.Store(id='local', storage_type='session'),
    html.H4('store_out'),
    html.Table([
        html.Tbody([
            html.Tr([
                    html.Td(id='local-clicks', persistence=True)
                ])
        ])
    ])

])


def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    return df.to_json()


@app.callback(Output('local', 'data'),
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename'),
               State('upload-data', 'last_modified')])
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children

# 展示当前store中的数据 在刷新后消失
@app.callback(Output('local-clicks', 'children'),
              [Input('local', 'modified_timestamp')],
              [State('local', 'data')])
def on_data(ts, data):
    if ts is None:
        raise PreventUpdate
    return data


# @app.callback(Output)




if __name__ == '__main__':
    app.run_server(debug=False, port=8077, threaded=True)
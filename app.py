import os
import io
import base64
import datetime, time
import json
import re

import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input, State
from dash.exceptions import PreventUpdate

import pandas as pd

app = dash.Dash(__name__, external_stylesheets=['assets/bWLwgP.css', 'assets/myown.css'])

app.layout = html.Div([
    # html.H3('日常数据', id='title', className='container'),
    html.Div(id='row_1',
             style={'display': 'flex'},
             children=[
                 html.Div(id='上传数据',
                          className='left_bar',
                          children=[
                              html.Div(id='数据上传区域',
                                       children=[
                                           html.H5('数据源'),
                                           dcc.Upload(
                                               id='stock_file',
                                               children=html.Div([
                                                   html.A('选择库存文件')]),
                                               className='my_upload',
                                               multiple=False),
                                           dcc.Upload(
                                               id='daily_file',
                                               children=html.Div([
                                                   html.A('选择日常数据文件')]),
                                               className='my_upload',
                                               multiple=False),
                                           dcc.Upload(
                                               id='property_file',
                                               children=html.Div([
                                                   html.A('选择产品属性文件')]),
                                               className='my_upload',
                                               multiple=False
                                           ),
                                       ]),
                              html.Div(id='数据存储区域',
                                       children=[
                                           html.H5('数据仓'),
                                           dcc.Store(id='daily_file_store', storage_type='local', data='waiting file'),
                                           dcc.Store(id='daily_filename_store', storage_type='local',
                                                     data='waiting filename'),
                                           html.Tbody([
                                               html.Th('文件内容'),
                                               html.Th('文件名'),
                                               html.Tr([
                                                   html.Td(id='daily_file_td'),
                                                   html.Td(id='daily_filename_td')
                                               ])
                                           ]),
                                       ]),
                          ]),
                 html.Div(id='聚合数据展示区域',
                          className='top_bar',
                          children=[
                              html.Div(id='daily_graph_ploy'),
                              html.H5('聚合数据区域'),
                              html.P('数据汇总、完成度等等')
                          ]),
             ]),
    html.Div(id='row_2',
             className='content_page',
             children=[
                 html.Div(id='ASIN选择',
                          style={'position': 'fixed', 'left': '3%', 'top': '40%'},
                          children=[
                              html.Div(
                                  children=[
                                      dcc.Dropdown(id='select_asin', style={'width': '150px'}),
                                      dcc.Dropdown(id='select_sub_asin', style={'width': '150px'})],
                                  ),
                          ]),
                 html.H5('类目数据展示'),
                 html.Div(id='产品数据展示区域',
                          children=[
                              html.Div(id='daily_graph_category'),

                              html.P('数据汇总')
                          ]),
                 html.H5('父ASIN级别的数据'),
                 html.Div(id='asin数据展示区域',
                          children=[
                              html.Div(id='daily_graph_asin'),

                          ]),
                 html.Div(id='子asin详细数据展示区域',
                          className='columns',
                          children=[
                              html.Div(id='daily_graph_sub_asin'),

                          ]),
                 html.H5('子asin级别的数据'),
             ]),
        ])


def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # 上传csv文件
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
            return df.to_json(),filename
        elif 'xls' in filename:
            # 上传xlsx文件
            df = pd.read_excel(io.BytesIO(decoded))
            return df.to_json(), filename
    except Exception as e:
        print(e)
        return json.dumps({'error': '请选择csv或xlsx文件'}), 'no file'


@app.callback([Output('daily_file_store', 'data'),
               Output('daily_filename_store', 'data')],
              [Input('daily_file', 'contents')],
              [State('daily_file', 'filename'),
               State('daily_file', 'last_modified'),
              State('daily_file_store', 'data'),
              State('daily_filename_store', 'data')])
def update_output(list_of_contents, list_of_names, list_of_dates, store_file, store_name):
    if list_of_contents is not None:
        # children = [
        #     parse_contents(c, n, d) for c, n, d in
        #     zip(list_of_contents, list_of_names, list_of_dates)]
        children = parse_contents(list_of_contents, list_of_names, list_of_dates)
    else:
        children = store_file, store_name
    return children


@app.callback([Output('daily_file_td', 'children'),
              Output('daily_filename_td', 'children')],
              [Input('daily_file_store', 'modified_timestamp')],
              [State('daily_file_store', 'data'),
               State('daily_filename_store', 'data'),
              ])
def get_td(mt, file_data, filename):
    if not mt:
        return 'filedata...', 'filename...'
    else:
        return file_data[:15], filename


@app.callback(Output('select_asin', 'options'),
              [Input('daily_file_store', 'modified_timestamp')],
              [State('daily_file_store', 'data')])
def get_asin(mt, file_data):
    if not mt:
        return [{'label': 'none', 'value': 'none'}]
    else:
        df = pd.DataFrame(json.loads(file_data))
        asin_list = df['asin'].unique()
        result = [{'label': i, 'value': i} for i in asin_list]
        return result


@app.callback(Output('select_sub_asin', 'options'),
              [Input('daily_file_store', 'modified_timestamp'),
               Input('select_asin', 'value')],
              [State('daily_file_store', 'data')])
def get_sub_asin(mt, asin, file_data):
    if not (mt and asin):
        return [{'label': 'none', 'value': 'none'}]
    else:
        df = pd.DataFrame(json.loads(file_data))
        print(df.columns)
        sub_asin_list = list(df[df['asin'] == asin]['sub_asin'].unique())
        print(asin, sub_asin_list)
        result = [{'label': i, 'value': i} for i in sub_asin_list]
        return result


def get_pivot(data_info):
    def get_num(strr):
        if isinstance(strr,int) or isinstance(strr, float):
            return float(strr)
        strr = str(strr)
        if re.search('￥', strr):
            try:
                strr = float(strr.strip('￥').replace(",", ''))
                return strr
            except Exception as e:
                print(e)

        if re.search(r'US', strr):
            try:
                strr = float(strr.strip('US$').replace(",", ''))
                return strr
            except Exception as e:
                print(e)
        return strr
    # print(data_info.head())
    mode_list = data_info.columns   # '已订购商品销售额'
    if '已订购商品销售额' in mode_list:
        data_info['已订购商品销售额'] = data_info['已订购商品销售额'].apply(get_num)
    if '买家访问次数' in mode_list:
        data_info['买家访问次数'] = data_info['买家访问次数'].apply(lambda x: int(str(x).replace(',', '')))
    if '订单商品数量转化率' in mode_list:
        data_info['订单商品数量转化率'] = data_info['订单商品数量转化率'].apply(lambda x: float(str(x).strip('%')) * 0.01)

    if 'date' in mode_list:
        try:
            data_info['date'] = data_info['date'].apply(lambda x: time.strftime('%Y-%m-%d', time.localtime(x/1000)))
        except:
            pass

    data_pivot = pd.pivot_table(data=data_info, columns=['asin', 'sub_asin'],
                                index=['date'],
                                values=['买家访问次数', '订单商品数量转化率', '已订购商品数量', '已订购商品销售额'])

    return data_pivot


@app.callback(Output('daily_graph_sub_asin', 'children'),
              [Input('daily_file_store', 'modified_timestamp'),
              Input('select_sub_asin', 'value')],
              [State('daily_file_store', 'data')])
def get_graph_sub_asin(mt, sub_asin, data):
    if not (mt and sub_asin):
        raise PreventUpdate
    df = pd.DataFrame(json.loads(data))
    print(df.columns)
    data_pivot = get_pivot(df)
    print(data_pivot.columns.levels[0].to_list())
    if sub_asin not in data_pivot.columns.levels[2].to_list():
        raise PreventUpdate
    mode_list = data_pivot.columns.levels[0].to_list()
    print("mode_list:", mode_list)
    df = data_pivot.xs(sub_asin, level=2, axis=1, drop_level=False)
    out_dict = {}
    for each in mode_list:
        out_dict[each] = list(df[each].to_dict('list').values())[0]
        # print(out_dict)

    figures = [
        dcc.Graph(
            figure=dict(
                data=[dict(x=list(data_pivot.index),
                           y=out_dict.get(i),
                           name=i,
                           type='bar')],
                layout=dict(
                    title=i,
                    showlegend=True,
                    # margin={'l':30, 'r':30},
                    showdata=True,
                    padding={'l':5, 'r':5},
                    # margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                    legend={'x': 0, 'y': 1},
                    hover=[i],
                    hovermode='closest'
                    )
                ),
            className='six columns',
            # style={
            #     'border-width': '3px',
            #     'border': 'dimgray',
            #     'border-style': 'solid',
            # }
            ) for i in out_dict.keys()]

    return figures


if __name__ == '__main__':
    app.run_server(debug=True, port=8077)
import datetime, time
import json
import re
import plotly.graph_objects as go
import dateutil

import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input, State
from dash.exceptions import PreventUpdate
import plotly.express as px
import numpy as np
import pandas as pd
from asin_dict import asin_pic_dict

data = pd.read_excel(r'E:\产品开发\商品推广自动投放报告.xls')

data['销量'] = data['7天总销售量(#)']
data['销售额'] = data['7天总销售额(￥)']
data_info = data[['广告组名称', '广告活动名称','投放','客户搜索词','展现量','点击量','销量','销售额','花费']]

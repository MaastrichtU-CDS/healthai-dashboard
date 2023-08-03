# -*- coding: utf-8 -*-

"""
TNM statistics
"""
import os
import logging

import pandas as pd
import plotly.express as px

from dash import dcc
from dash import html

from app import app

logging.basicConfig(
    filename='record.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(message)s',
    datefmt='%d-%b-%y %H:%M:%S'
)

df = pd.read_csv('data/lung_reduced.csv')
df['date_of_diagnosis'] = pd.to_datetime(df['date_of_diagnosis'])
df['date_of_fu'] = pd.to_datetime(df['date_of_fu'])
df['days'] = df['date_of_fu'] - df['date_of_diagnosis']


# ------------------------------------------------------------------------------
# Statistics page layout
# ------------------------------------------------------------------------------
layout = html.Div([
    html.H1('Statistics'),
    html.Hr(),
    html.P(),
    html.Div([
        dcc.Graph(
            id='figure1',
            figure = px.histogram(df, x='centre')
        ),
    ],
    style={
        'width': '49%', 'display': 'inline-block', 'vertical-align': 'middle'
    }),
    html.Div([
        dcc.Graph(
            id='figure1',
            figure=px.histogram(df, x='centre', color='stage')
        ),
    ],
    style={
        'width': '49%', 'display': 'inline-block', 'vertical-align': 'middle'
    }),
    html.Div([
        dcc.Graph(
            id='figure1',
            figure=px.histogram(df, x='centre', color='vital_status')
        ),
    ],
    style={
        'width': '49%', 'display': 'inline-block', 'vertical-align': 'middle'
    }),
    html.Div([
        dcc.Graph(
            id='figure1',
            figure=px.histogram(df, x='days', color='centre')
        ),
    ],
    style={
        'width': '49%', 'display': 'inline-block', 'vertical-align': 'middle'
    }),
    html.P()
])


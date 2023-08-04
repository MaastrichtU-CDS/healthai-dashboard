# -*- coding: utf-8 -*-

"""
TNM statistics
"""
import os
import re
import logging

import numpy as np
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


# ------------------------------------------------------------------------------
# Get data
# ------------------------------------------------------------------------------
# Read data
df = pd.read_csv('data/lung_reduced.csv')
df['date_of_diagnosis'] = pd.to_datetime(df['date_of_diagnosis'])
df['date_of_fu'] = pd.to_datetime(df['date_of_fu'])
df['days'] = df.apply(
    lambda x: (x['date_of_fu'] - x['date_of_diagnosis']).days, axis=1
)

# Patients per centre
dfg1 = df.groupby('centre')['id'].nunique().reset_index()

# Patients per centre per stage
dfg2 = df.groupby(['centre', 'stage'])['id'].nunique().reset_index()

# Patients per centre per vital status
dfg3 = df.groupby(['centre', 'vital_status'])['id'].nunique().reset_index()

# Interval between diagnosis and follow up
bins = [0, 3*31, 6*31, 9*31, 12*31, 15*31, 18*31, 21*31, 24*30, np.Inf]
df['days'] = pd.cut(df['days'], bins)
dfg4 = df.groupby(['centre', 'days'])['id'].nunique().reset_index()
dfg4['days'] = dfg4['days'].apply(lambda x: x.right)


# ------------------------------------------------------------------------------
# Statistics page layout
# ------------------------------------------------------------------------------
layout = html.Div([
    html.H1('Statistics'),
    html.Hr(),
    html.P(),
    html.Div([
        dcc.Graph(
            figure = px.bar(dfg1, x='centre', y='id')
        ),
    ],
    style={
        'width': '49%', 'display': 'inline-block', 'vertical-align': 'middle'
    }),
    html.Div([
        dcc.Graph(
            figure=px.bar(dfg2, x='centre', y='id', color='stage')
        ),
    ],
    style={
        'width': '49%', 'display': 'inline-block', 'vertical-align': 'middle'
    }),
    html.Div([
        dcc.Graph(
            figure=px.bar(dfg3, x='centre', y='id', color='vital_status')
        ),
    ],
    style={
        'width': '49%', 'display': 'inline-block', 'vertical-align': 'middle'
    }),
    html.Div([
        dcc.Graph(
            figure=px.bar(dfg4, x='days', y='id', color='centre')
        ),
    ],
    style={
        'width': '49%', 'display': 'inline-block', 'vertical-align': 'middle'
    }),
    html.P()
])


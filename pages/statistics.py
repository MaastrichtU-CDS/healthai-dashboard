# -*- coding: utf-8 -*-

"""
TNM statistics
"""
import os
import time

import numpy as np
import pandas as pd
import plotly.express as px

from dash import dcc
from dash import html
from vantage6.client import Client

from app import app
from pages import config


# ------------------------------------------------------------------------------
# Get data
# ------------------------------------------------------------------------------
# Initialize the vantage6 client object, and run the authentication
client = Client(
    config.server_url, config.server_port, config.server_api, verbose=True
)
client.authenticate(config.username, config.password)
client.setup_encryption(None)

# Run vantage6 task that retrieves the statistics
input_ = {
    'method': 'master',
    'master': True,
    'kwargs': {'org_ids': [7, 8]},
}

task = client.task.create(
    collaboration=2,
    organizations=[7, 8],
    name='v6-nids-py',
    image='aiaragomes/v6-nids-py:latest',
    description='get patients per centre',
    input=input_,
    data_format='json'
)

task_info = client.task.get(task['id'], include_results=True)
while not task_info.get('complete'):
    task_info = client.task.get(task['id'], include_results=True)
    time.sleep(3)

result_info = client.result.list(task=task_info['id'])
results = result_info['data'][0]['result']

# Read data
df = pd.read_csv('data/lung_reduced.csv')
df['date_of_diagnosis'] = pd.to_datetime(df['date_of_diagnosis'])
df['date_of_fu'] = pd.to_datetime(df['date_of_fu'])
df['days'] = df.apply(
    lambda x: (x['date_of_fu'] - x['date_of_diagnosis']).days, axis=1
)

# Patients per centre
dfg1 = pd.DataFrame({
    'id': [result['nids'] for result in results],
    'centre': [result['organisation'] for result in results]
})

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


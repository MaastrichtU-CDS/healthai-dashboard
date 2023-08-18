# -*- coding: utf-8 -*-

"""
TNM patient similarity
"""
import time

import pandas as pd
import plotly.express as px

from dash import dcc
from dash import html
from dash.dependencies import Input
from dash.dependencies import Output
from vantage6.client import Client

from pages import config
from app import app


# ------------------------------------------------------------------------------
# Get clusters with federated kmeans
# ------------------------------------------------------------------------------
# Initialize the vantage6 client object, and run the authentication
client = Client(
    config.server_url, config.server_port, config.server_api, verbose=True
)
client.authenticate(config.username, config.password)
client.setup_encryption(None)

# Run vantage6 task that retrieves cluster centroids
input_ = {
    'method': 'master',
    'master': True,
    'kwargs': {
        'org_ids': [7, 8],
        'k': 4,
        'epsilon': 0.05,
        'max_iter': 5,
        'columns': ['t', 'n', 'm']
    }
}

task = client.task.create(
    collaboration=2,
    organizations=[7, 8],
    name='v6-kmeans-py',
    image='aiaragomes/v6-kmeans-py:latest',
    description='run kmeans',
    input=input_,
    data_format='json'
)

task_info = client.task.get(task['id'], include_results=True)
while not task_info.get('complete'):
    task_info = client.task.get(task['id'], include_results=True)
    time.sleep(3)

result_info = client.result.list(task=task_info['id'])
centroids = result_info['data'][0]['result']['centroids']
# centroids = [[1, 0, 0], [2, 1, 0], [3, 2, 0], [4, 3, 1]]


# ------------------------------------------------------------------------------
# Get averaged survival profiles for the clusters
# ------------------------------------------------------------------------------
# TODO: compute survival profiles, for that we need another v6
#  algorithm that takes the centroids as input and sends tasks to get
#  the average survival profile for the clusters


# ------------------------------------------------------------------------------
# Patient similarity page layout
# ------------------------------------------------------------------------------
layout = html.Div([
    html.H1('Patient similarity'),
    html.Hr(),
    html.P(),
    html.H4('Patient diagnosed with:'),
    html.Div(
        dcc.Dropdown(
            options=[
                'T0', 'T1', 'T1a', 'T1b', 'T1c', 'T2', 'T2a', 'T2b',
                'T3', 'T3a', 'T4'
            ],
            placeholder='T stage',
            id='input-tstage'
        ),
        style={
            'width': '15%', 'display': 'inline-block',
            'vertical-align': 'middle'
        }
    ),
    html.Div(
        dcc.Dropdown(
            options=[
                'N0', 'N1', 'N2', 'N2b', 'N2c', 'N3'
            ],
            placeholder='N stage',
            id='input-nstage'
        ),
        style={
            'width': '15%', 'display': 'inline-block',
            'vertical-align': 'middle'
        }
    ),
    html.Div(
        dcc.Dropdown(
            options=[
                'M0', 'M1', 'M1a', 'M1b', 'M1c'
            ],
            placeholder='M stage',
            id='input-mstage'
        ),
        style={
            'width': '15%', 'display': 'inline-block',
            'vertical-align': 'middle'
        }
    ),
    html.P(),
    html.P(),
    html.Div(id='output-survival-profile'),
    html.P()
])


# ------------------------------------------------------------------------------
# Callbacks
# ------------------------------------------------------------------------------
@app.callback(
    Output('output-survival-profile', 'children'),
    [Input('input-tstage', 'value'),
     Input('input-nstage', 'value'),
     Input('input-mstage', 'value')]
)
def survival_profile(t, n, m):
    if t and n and m:
        # TODO: convert from categorical to numerical TNM
        # TODO: get closest cluster
        # TODO: plot survival profile for the closest cluster

        # Output for UI
        return html.Div([
            html.H4('Survival profile for similar patients:'),
            dcc.Graph(
                figure=px.line(
                    x=list(range(15)), y=list(range(15))
                ),
                id='output-survival-profile'
            ),
        ],
            style={
                'width': '50%', 'display': 'inline-block',
                'vertical-align': 'middle'
            }
        )
    else:
        return html.Plaintext('')

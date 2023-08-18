# -*- coding: utf-8 -*-

"""
TNM patient similarity
"""
import time

import pandas as pd
import plotly.express as px

from dash import dcc
from dash import html
from vantage6.client import Client

from pages import config


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


# ------------------------------------------------------------------------------
# Patient similarity page layout
# ------------------------------------------------------------------------------
layout = html.Div([
    html.H1('Patient similarity'),
    html.Hr()
])

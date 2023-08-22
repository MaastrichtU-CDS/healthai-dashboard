# -*- coding: utf-8 -*-

"""
TNM patient similarity
"""
import os
import time
import json

import numpy as np
import pandas as pd
import plotly.express as px

from dash import dcc
from dash import html
from dash.dependencies import Input
from dash.dependencies import Output
from scipy.spatial import distance
from vantage6.client import Client

from pages import config
from app import app


# ------------------------------------------------------------------------------
# Get clusters and survival profiles
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
        'columns': ['t_num', 'n_num', 'm_num']
    }
}

task = client.task.create(
    collaboration=2,
    organizations=[7, 8],
    name='v6-healthai-paient-similarity-py',
    image='aiaragomes/v6-healthai-paient-similarity-py:latest',
    description='run tnm patient similarity',
    input=input_,
    data_format='json'
)

task_info = client.task.get(task['id'], include_results=True)
while not task_info.get('complete'):
    task_info = client.task.get(task['id'], include_results=True)
    time.sleep(3)

result_info = client.result.list(task=task_info['id'])
centroids = result_info['data'][0]['result']['centroids']
profiles = result_info['data'][0]['result']['profiles']


# ------------------------------------------------------------------------------
# TNM common data model
# ------------------------------------------------------------------------------
input_path = os.path.join(os.getcwd(), 'input')
cdm_file = os.path.join(input_path, 'cdm.json')
cdm = json.load(open(cdm_file))

t_values = cdm['t']['values']
t_nvalues = list(range(len(t_values)))

n_values = cdm['n']['values']
n_nvalues = list(range(len(n_values)))

m_values = cdm['m']['values']
m_nvalues = list(range(len(m_values)))


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
            options=cdm['t']['values'],
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
            options=cdm['n']['values'],
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
            options=cdm['m']['values'],
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
        # Convert from categorical to numerical TNM
        t_idx = np.where(np.array(t_values) == t)[0][0]
        t = t_nvalues[t_idx]

        n_idx = np.where(np.array(n_values) == n)[0][0]
        n = n_nvalues[n_idx]

        m_idx = np.where(np.array(m_values) == m)[0][0]
        m = m_nvalues[m_idx]

        # Get closest cluster
        xi = [t, n, m]
        distances = [distance.euclidean(xi, xj) for xj in centroids]
        idx = np.argmin(distances)

        # Survival profile for the closest cluster
        dfp = pd.DataFrame({
            'survival rate': profiles[idx],
            'survival days': list(range(0, 730, 30))
        })

        # Output for UI
        return html.Div([
            html.H4('Survival profile for similar patients:'),
            dcc.Graph(
                figure=px.line(
                    dfp, x='survival days', y='survival rate'
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

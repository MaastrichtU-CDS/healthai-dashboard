# -*- coding: utf-8 -*-

"""
TNM statistics
"""
import time

import pandas as pd
import plotly.express as px

from dash import dcc
from dash import html
from vantage6.client import Client

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
cutoff = 730
delta = 30
input_ = {
    'method': 'master',
    'master': True,
    'kwargs': {
        'org_ids': [7, 8],
        'cutoff': cutoff,
        'delta': delta
    }
}

task = client.task.create(
    collaboration=2,
    organizations=[7, 8],
    name='v6-healthai-dashboard-py',
    image='aiaragomes/v6-healthai-dashboard-py:latest',
    description='get tnm statistics',
    input=input_,
    data_format='json'
)

task_info = client.task.get(task['id'], include_results=True)
while not task_info.get('complete'):
    task_info = client.task.get(task['id'], include_results=True)
    time.sleep(3)

result_info = client.result.list(task=task_info['id'])
results = result_info['data'][0]['result']

# Patients per centre
dfg1 = pd.DataFrame({
    'patients': [result['nids'] for result in results],
    'centre': [result['organisation'] for result in results]
})

# Patients per centre per stage
dfg2 = pd.DataFrame()
for result in results:
    tmp = pd.DataFrame(result['stages'])
    tmp['centre'] = result['organisation']
    dfg2 = dfg2.append(tmp)
dfg2.rename(columns={'id': 'patients'}, inplace=True)

# Patients per centre per vital status
dfg3 = pd.DataFrame()
for result in results:
    tmp = pd.DataFrame(result['vital_status'])
    tmp['centre'] = result['organisation']
    dfg3 = dfg3.append(tmp)
dfg3.rename(
    columns={'id': 'patients', 'vital_status': 'vital status'}, inplace=True
)

# Survival rate profile per centre
dfg4 = pd.DataFrame()
for result in results:
    tmp = pd.DataFrame({
        'survival rate': result['survival'],
        'survival days': list(range(0, cutoff, delta))
    })
    tmp['centre'] = result['organisation']
    dfg4 = dfg4.append(tmp)


# ------------------------------------------------------------------------------
# Statistics page layout
# ------------------------------------------------------------------------------
layout = html.Div([
    html.H1('Statistics'),
    html.Hr(),
    html.P(),
    html.Div([
        dcc.Graph(
            figure=px.bar(dfg1, x='centre', y='patients')
        ),
    ],
        style={
            'width': '49%', 'display': 'inline-block',
            'vertical-align': 'middle'
        }
    ),
    html.Div([
        dcc.Graph(
            figure=px.bar(dfg2, x='centre', y='patients', color='stage')
        ),
    ],
        style={
            'width': '49%', 'display': 'inline-block',
            'vertical-align': 'middle'
        }
    ),
    html.Div([
        dcc.Graph(
            figure=px.bar(dfg3, x='centre', y='patients', color='vital status')
        ),
    ],
        style={
            'width': '49%', 'display': 'inline-block',
            'vertical-align': 'middle'
        }
    ),
    html.Div([
        dcc.Graph(
            figure=px.line(
                dfg4, x='survival days', y='survival rate', color='centre'
            )
        ),
    ],
        style={
            'width': '49%', 'display': 'inline-block',
            'vertical-align': 'middle'
        }
    ),
    html.P()
])

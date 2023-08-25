# -*- coding: utf-8 -*-

"""
TNM statistics
"""
import time

import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc

from dash import dcc
from dash import html
from dash.dependencies import Input
from dash.dependencies import Output
from dateutil import parser
from vantage6.client import Client

from pages import config
from app import app


# ------------------------------------------------------------------------------
# Global variables
# ------------------------------------------------------------------------------
client = None
task = None
start = None


# ------------------------------------------------------------------------------
# Statistics page layout
# ------------------------------------------------------------------------------
layout = html.Div([
    html.H1('Statistics'),
    html.Hr(),
    html.P(),
    dbc.Button('Send task', id='send-stats-task', n_clicks=0),
    dcc.Loading(
        id='loading-statistics-task', type='default',
        children=html.Div(id='output-statistics-task')
    ),
    html.P(),
    dcc.Loading(
        id='loading-statistics-results', type='default',
        children=html.Div(id='output-statistics')
    ),
    html.P()
])


# ------------------------------------------------------------------------------
# Callbacks
# ------------------------------------------------------------------------------
@app.callback(
    Output('output-statistics-task', 'children'),
    [Input('send-stats-task', 'n_clicks')]
)
def send_statistics_task(n_clicks):
    global client
    global task
    global start

    if n_clicks > 0:
        # Initialize the vantage6 client object, and run the authentication
        client = Client(
            config.server_url, config.server_port, config.server_api,
            verbose=True
        )
        client.authenticate(config.username, config.password)
        client.setup_encryption(None)

        # Input for task that retrieves the statistics
        input_ = {
            'method': 'master',
            'master': True,
            'kwargs': {
                'org_ids': config.org_ids,
                'cutoff': config.cutoff,
                'delta': config.delta
            }
        }

        # Create task to compute statistics
        start = time.time()
        task = client.task.create(
            collaboration=config.collaboration,
            organizations=config.org_ids,
            name='v6-healthai-dashboard-py',
            image='ghcr.io/maastrichtu-cds/v6-healthai-dashboard-py:latest',
            description='get tnm statistics',
            input=input_,
            data_format='json'
        )

        # Output for UI
        if task:
            return html.Div([
                html.Plaintext('Task was created, waiting for results...'),
                html.P(),
                dbc.Button('Get results', id='get-results2', n_clicks=0),
            ])
        else:
            return html.Div(
                html.Plaintext('Something went wrong...')
            )
    else:
        return html.Plaintext('')


@app.callback(
    Output('output-statistics', 'children'),
    [Input('get-results2', 'n_clicks')]
)
def get_statistics(n_clicks):
    global client
    global task
    global start

    if n_clicks > 0:
        # Get results
        task_info = client.task.get(task['id'], include_results=True)
        results = None
        if task_info.get('complete'):
            result_info = client.result.list(task=task_info['id'])
            results = result_info['data'][0]['result']
            end = result_info['data'][0]['finished_at']
            duration = round((parser.parse(end).timestamp() - start), 3)

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
                columns={'id': 'patients', 'vital_status': 'vital status'},
                inplace=True
            )

            # Survival rate profile per centre
            dfg4 = pd.DataFrame()
            for result in results:
                tmp = pd.DataFrame({
                    'survival rate': result['survival'],
                    'survival days': list(range(0, config.cutoff, config.delta))
                })
                tmp['centre'] = result['organisation']
                dfg4 = dfg4.append(tmp)

        # Output for UI
        if results:
            return html.Div([
                html.Plaintext(f'Analysis completed in {duration} seconds'),
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
                        figure=px.bar(dfg2, x='centre', y='patients',
                                      color='stage')
                    ),
                ],
                    style={
                        'width': '49%', 'display': 'inline-block',
                        'vertical-align': 'middle'
                    }
                ),
                html.Div([
                    dcc.Graph(
                        figure=px.bar(dfg3, x='centre', y='patients',
                                      color='vital status')
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
                            dfg4, x='survival days', y='survival rate',
                            range_y=[0, 1], color='centre'
                        )
                    ),
                ],
                    style={
                        'width': '49%', 'display': 'inline-block',
                        'vertical-align': 'middle'
                    }
                )
            ])
        else:
            return html.Div(
                html.Plaintext('Still waiting for results, try again later...')
            )
    else:
        return html.Plaintext('')

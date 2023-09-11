# -*- coding: utf-8 -*-

"""
TNM patient survival
"""
import os
import re
import time
import json

import numpy as np
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

from dash import dcc
from dash import html
from dash.dependencies import Input
from dash.dependencies import Output
from dateutil import parser
from vantage6.client import Client
from sklearn.linear_model import LogisticRegression

from pages import config
from app import app


# ------------------------------------------------------------------------------
# Global variables
# ------------------------------------------------------------------------------
client = None
task = None
start = None
model = None
accuracy = None


# ------------------------------------------------------------------------------
# TNM common data model
# ------------------------------------------------------------------------------
input_path = os.path.join(os.getcwd(), 'input')
cdm_file = os.path.join(input_path, 'cdm.json')
cdm = json.load(open(cdm_file))


# ------------------------------------------------------------------------------
# Patient survival page layout
# ------------------------------------------------------------------------------
layout = html.Div([
    html.H1('Patient survival'),
    html.Hr(),
    html.P(),
    dbc.Button('Send task', id='send-task3', n_clicks=0),
    dcc.Loading(
        id='loading-survival-task', type='default',
        children=html.Div(id='output-send-task3')
    ),
    html.P(),
    dcc.Loading(
        id='loading-survival-results', type='default',
        children=html.Div(id='output-survival-results')
    ),
    html.P(),
    html.H4('Patient diagnosed with:'),
    html.Div(
        dcc.Dropdown(
            options=cdm['t']['values'],
            placeholder='T stage',
            id='input-tstage3'
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
            id='input-nstage3'
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
            id='input-mstage3'
        ),
        style={
            'width': '15%', 'display': 'inline-block',
            'vertical-align': 'middle'
        }
    ),
    html.P(),
    html.P(),
    html.Div(id='output-2years-survival'),
    html.P()
])


# ------------------------------------------------------------------------------
# Callbacks
# ------------------------------------------------------------------------------
@app.callback(
    Output('output-send-task3', 'children'),
    [Input('send-task3', 'n_clicks')]
)
def send_survival_analysis_task(n_clicks):
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
        client.setup_encryption(config.privkey_path)

        # Vantage6 task that runs NSCLC 2-years survival
        input_ = {
            'method': 'master',
            'master': True,
            'kwargs': {
                'org_ids': config.org_ids,
                'max_iter': config.max_iter_survival,
            }
        }

        start = time.time()
        task = client.task.create(
            collaboration=config.collaboration,
            organizations=config.org_ids,
            name='v6-healthai-survival-analysis-py',
            image=config.image_surv,
            description='run nsclc survival analysis',
            input=input_,
            data_format='json'
        )

        # Output for UI
        if task:
            return html.Div([
                html.Plaintext('Task was created, waiting for results...'),
                html.P(),
                dbc.Button('Get results', id='get-results3', n_clicks=0),
            ])
        else:
            return html.Div(
                html.Plaintext('Something went wrong...')
            )
    else:
        return html.Plaintext('')


@app.callback(
    Output('output-survival-results', 'children'),
    [Input('get-results3', 'n_clicks')]
)
def get_survival_analysis_results(n_clicks):
    global client
    global task
    global start
    global model
    global accuracy

    if n_clicks > 0:
        # Get results for survival analysis
        task_info = client.task.get(task['id'], include_results=True)
        if task_info.get('complete'):
            result_info = client.result.list(task=task_info['id'])
            model = result_info['data'][0]['result']['model']
            accuracy = result_info['data'][0]['result']['accuracy']
            end = result_info['data'][0]['finished_at']
            duration = round((parser.parse(end).timestamp() - start)/60., 3)

        # Output for UI
        if model:
            return html.Div([
                html.Plaintext(f'Analysis completed in {duration} minutes'),
            ])
        else:
            return html.Div(
                html.Plaintext('Still waiting for results, try again later...')
            )
    else:
        return html.Plaintext('')


@app.callback(
    Output('output-2years-survival', 'children'),
    [Input('input-tstage3', 'value'),
     Input('input-nstage3', 'value'),
     Input('input-mstage3', 'value')]
)
def survival_analysis(t, n, m):
    global model
    global accuracy

    if t and n and m:
        # Convert from categorical to numerical TNM
        t = re.compile(r'\d').findall(t)
        t = int(t[0]) if len(t) != 0 else -1
        n = re.compile(r'\d').findall(n)
        n = int(n[0]) if len(n) != 0 else -1
        m = re.compile(r'\d').findall(m)
        m = int(m[0]) if len(m) != 0 else -1

        # Get prediction based on model
        X = np.array([[t, n, m]])
        vital_status = model.predict(X)
        survival_prob = model.predict_proba(X)
        classes = model.classes_

        # Format for table
        prob = survival_prob[0][np.where(classes == vital_status)[0][0]]*100.
        prob_txt = f'{round(prob, 2)}%'
        accuracy_txt = f'{round(accuracy, 2)}'

        table = go.Figure(data=[
            go.Table(
                header=dict(values=['Vital status', 'Probability', 'Accuracy']),
                cells=dict(values=[[vital_status], [prob_txt], [accuracy_txt]])
            )
        ])

        # Output for UI
        return html.Div([
            html.H4('Patient 2-years survival prediction:'),
            dcc.Graph(figure=table)
        ],
            style={
                'width': '50%', 'display': 'inline-block',
                'vertical-align': 'middle'
            }
        )
    else:
        return html.Plaintext('')

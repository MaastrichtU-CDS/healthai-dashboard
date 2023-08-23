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
import dash_bootstrap_components as dbc

from dash import dcc
from dash import html
from dash.dependencies import Input
from dash.dependencies import Output
from scipy.spatial import distance
from vantage6.client import Client

from pages import config
from app import app


# ------------------------------------------------------------------------------
# Global variables
# ------------------------------------------------------------------------------
centroids = None
profiles = None
# TODO: profiles do not seem to match centroids
# centroids = [
#     [3.9734848484848486, 3.951515151515151, 2.2867424242424246],
#     [9.14757505144243, 1.140516195849175, 0.7739054004333429],
#     [3.3931351078167116, 0.4987196765498654, 0.1549444070080861],
#     [9.392801977139328, 4.488018006090295, 2.363321417538285]
# ]
# profiles = [
#     [0.9838709677419355, 0.9032258064516129, 0.7419354838709677, 0.6666666666666666, 0.6075268817204301, 0.5483870967741935, 0.46774193548387094, 0.40860215053763443, 0.3333333333333333, 0.3064516129032258, 0.26344086021505375, 0.24193548387096775, 0.23118279569892472, 0.20967741935483872, 0.1989247311827957, 0.1774193548387097, 0.16666666666666666, 0.16129032258064516, 0.16129032258064516, 0.14516129032258066, 0.14516129032258066, 0.12903225806451613, 0.12903225806451613, 0.12365591397849462, 0.11827956989247312],
#     [0.9965753424657534, 0.9606164383561644, 0.8476027397260274, 0.7363013698630136, 0.6541095890410958, 0.565068493150685, 0.4657534246575342, 0.3972602739726027, 0.3561643835616438, 0.3013698630136986, 0.2756849315068493, 0.2585616438356164, 0.2363013698630137, 0.2226027397260274, 0.2071917808219178, 0.19006849315068494, 0.1832191780821918, 0.1643835616438356, 0.15753424657534246, 0.14383561643835616, 0.13013698630136986, 0.1232876712328767, 0.11986301369863013, 0.11301369863013698, 0.10616438356164383],
#     [1.0, 0.9642184557438794, 0.8041431261770244, 0.6290018832391714, 0.5555555555555556, 0.4651600753295669, 0.3728813559322034, 0.3352165725047081, 0.2975517890772128, 0.2730696798493409, 0.263653483992467, 0.2523540489642185, 0.2391713747645951, 0.224105461393597, 0.2184557438794727, 0.21468926553672316, 0.20527306967984935, 0.19397363465160075, 0.17890772128060264, 0.1713747645951036, 0.16760828625235405, 0.1544256120527307, 0.14500941619585686, 0.1374764595103578, 0.12994350282485875],
#     [0.9882352941176471, 0.8647058823529412, 0.6941176470588235, 0.6441176470588236, 0.5764705882352941, 0.5205882352941177, 0.4294117647058823, 0.36470588235294116, 0.3235294117647059, 0.27647058823529413, 0.24411764705882352, 0.22647058823529412, 0.20588235294117646, 0.18823529411764706, 0.18529411764705883, 0.17647058823529413, 0.16176470588235295, 0.15294117647058825, 0.15294117647058825, 0.1411764705882353, 0.12941176470588237, 0.12352941176470589, 0.11176470588235295, 0.10294117647058823, 0.09117647058823529]
# ]


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
    dbc.Button('Run analysis', id='similarity-analysis', n_clicks=0),
    dcc.Loading(
        id='loading-similarity', type='default',
        children=html.Div(id='output-similarity')
    ),
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
    Output('output-similarity', 'children'),
    [Input('similarity-analysis', 'n_clicks')]
)
def run_federated_similarity_analysis(n_clicks):
    global centroids
    global profiles

    if n_clicks > 0:
        # Initialize the vantage6 client object, and run the authentication
        start = time.time()
        client = Client(
            config.server_url, config.server_port, config.server_api,
            verbose=True
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
        duration = time.time() - start

        # Output for UI
        if centroids and profiles:
            return html.Div([
                html.Plaintext(f'Analysis completed in {duration} seconds.'),
            ])
        else:
            return html.Div(
                html.Plaintext('Something went wrong...')
            )
    else:
        return html.Plaintext('')


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
                )
            ),
        ],
            style={
                'width': '50%', 'display': 'inline-block',
                'vertical-align': 'middle'
            }
        )
    else:
        return html.Plaintext('')

# -*- coding: utf-8 -*-

"""
HealthAI home page
"""

from dash import html


# ------------------------------------------------------------------------------
# Homepage layout
# ------------------------------------------------------------------------------
layout = html.Div([
    html.H1('Home'),
    html.Hr(),
    html.P('HealthAI dashboard for TNM analysis')
])

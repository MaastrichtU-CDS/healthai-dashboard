# -*- coding: utf-8 -*-

"""
TNM statistics
"""
import os
import logging

import pandas as pd

from dash import dcc
from dash import html
from dash import dash_table
from dash.dependencies import Input
from dash.dependencies import Output
from dash.dependencies import State

from app import app

logging.basicConfig(
    filename='record.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(message)s',
    datefmt='%d-%b-%y %H:%M:%S'
)


# ------------------------------------------------------------------------------
# Statistics page layout
# ------------------------------------------------------------------------------
layout = html.Div([
    html.H1('Statistics'),
    html.Hr()
])


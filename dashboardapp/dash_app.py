#!/usr/bin/env python

"""
A dashboard application that displays data from a PostgreSQL database

Chris Francis, chrisfrancischris@gmail.com
"""

from flask import Flask, render_template, request, Response, redirect, url_for
import psycopg2
import os
import plotly.graph_objs as go
import plotly
from plotly.colors import qualitative as colors
import json
import pandas as pd

app = Flask(__name__, template_folder='templates')


def get_db_connection():
    """
    Create and return a new connection to the database

    Returns:
        conn: psycopg2.extensions.connection, connection to the database
    """
    conn: psycopg2.connection = psycopg2.connect(
        host=os.environ['POSTGRES_HOST'],
        port=os.environ['POSTGRES_PORT'],
        database=os.environ['POSTGRES_DB'],
        user=os.environ['POSTGRES_USER'],
        password=os.environ['POSTGRES_PASSWORD']
    )
    return conn


def get_df(table_name: str):
    """
    Select all rows from the table and return as a dataframe

    Arguments:
        table_name: str, name of the table to select from

    Returns:
        df: pandas.DataFrame, dataframe of the table
    """
    conn: psycopg2.connection = get_db_connection()
    cur: psycopg2.cursor = conn.cursor()
    cur.execute('SELECT * FROM "{}" ORDER BY time'.format(table_name))
    rows: list[tuple] = cur.fetchall()
    df: pd.DataFrame = pd.DataFrame(rows, columns=['time', 'value'])
    cur.close()
    conn.close()
    return df


def create_fig(df: pd.DataFrame, title: str, yaxis_title: str, color: str):
    """
    Create and return a plotly figure of the dataframe

    Arguments:
        df: pandas.DataFrame, dataframe to plot
        title: str, title of the plot
        yaxis_title: str, title of the y-axis
        color: str, color of the line

    Returns:
        fig: plotly.graph_objs._figure.Figure, plotly figure of the dataframe
    """
    fig: go._figure.Figure = go.Figure()
    fig.add_trace(go.Scatter(x=df['time'], y=df['value'], mode='lines',
                             name=title, line_color=color))
    fig.update_layout(title=title, xaxis_title='Time',
                      yaxis_title=yaxis_title,
                      margin=dict(l=0, r=0, b=35, t=60))
    # Add range slider and selector buttons
    fig.update_xaxes(
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=list([
                dict(count=4, label="4 hours",
                     step="hour", stepmode="backward"),
                dict(count=2, label="2 hours",
                     step="hour", stepmode="backward"),
                dict(count=1, label="1 hour",
                     step="hour", stepmode="backward"),
                dict(count=30, label="30 min",
                     step="minute", stepmode="backward"),
                dict(step="all")
            ])
        )
    )
    return fig


def create_json(table_name: str, title: str, color: str):
    """
    Encode the plotly figure of a table as json and return it

    Arguments:
        table_name: str, name of the table
        title: str, title of the plot
        color: str, color of the line

    Returns:
        graph_json: str, json encoded plotly figure
    """
    df: pd.DataFrame = get_df(table_name)
    fig: go._figure.Figure = create_fig(df, title + " vs time", title, color)
    graph_json: str = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graph_json


def create_response(table_name: str, filename: str):
    """
    Create and return a table as a csv file response

    Arguments:
        table_name: str, name of the table
        filename: str, name of the csv file

    Returns:
        Response: flask.wrappers.Response, csv file response
    """
    df: pd.DataFrame = get_df(table_name)
    return Response(
        df.to_csv(index=False),
        mimetype="text/csv",
        headers={"Content-disposition":
                 "attachment; filename={}.csv".format(filename)}
    )


@app.route('/')
def index():
    """
    Render the index.html template with the plotly figures of the tables

    Returns:
        render_template: flask.templating.render_template, rendered html 
                         template
    """
    table_names: list[str] = ['CM_HAM_DO_AI1/Temp_value',
                              'CM_HAM_PH_AI1/pH_value',
                              'CM_PID_DO/Process_DO',
                              'CM_PRESSURE/Output']
    titles: list[str] = ['Temperature (Celsius)', 'pH',
                         'Distilled Oxygen (%)', 'Pressure (psi)']
    graph_json_list: list[str] = []

    for table_name, title in zip(table_names, titles):
        graph_json_list.append(create_json(table_name, title,
                                           colors.Plotly[titles.index(title)]))

    return render_template('index.html', graph_json_list=graph_json_list)


@app.route('/', methods=['POST'])
def download():
    """
    Handle the requests from the download buttons and return the csv response

    Returns:
        flask.wrappers.Response, csv file response or redirect response to 
        index.html
    """
    if request.method == 'POST':
        if 'download1' in request.form:
            return create_response('CM_HAM_DO_AI1/Temp_value', 'temperature')
        elif 'download2' in request.form:
            return create_response('CM_HAM_PH_AI1/pH_value', 'ph')
        elif 'download3' in request.form:
            return create_response('CM_PID_DO/Process_DO', 'distilled_oxygen')
        elif 'download4' in request.form:
            return create_response('CM_PRESSURE/Output', 'pressure')
    else:
        return redirect(url_for('/'))


@app.route('/refresh', methods=['GET', 'POST'])
def refresh():
    """
    Handle the requests from the refresh buttons and return the json encoded 
    plotly figure

    Returns:
        str or flask.wrappers.Response, json encoded plotly figure or redirect
        response to index.html
    """
    if request.method == 'POST':
        if 'id' in request.form:
            id: str = request.form['id']
            if id == '1':
                return create_json('CM_HAM_DO_AI1/Temp_value', 'Temperature (Celsius)',
                                   colors.Plotly[int(id)])
            elif id == '2':
                return create_json('CM_HAM_PH_AI1/pH_value', 'pH',
                                   colors.Plotly[int(id)])
            elif id == '3':
                return create_json('CM_PID_DO/Process_DO', 'Distilled Oxygen (%)',
                                   colors.Plotly[int(id)])
            elif id == '4':
                return create_json('CM_PRESSURE/Output', 'Pressure (psi)',
                                   colors.Plotly[int(id)])
    else:
        return redirect(url_for('/'))


def run_app():
    """
    Run the flask app
    """
    app.run(host='0.0.0.0', port=8888)


if __name__ == '__main__':
    """
    Run the flask app
    """
    app.run(host='0.0.0.0', port=8888)
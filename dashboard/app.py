# TODO
#
# - Make particulate matter chart optional
# - Use this container to store data: https://dash.plotly.com/dash-core-components/store
# 


# --------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------ IMPORTS
# Plotly imports
import dash
from dash.dependencies import Output, Input
import dash_core_components as dcc
import dash_html_components as html
import plotly
import plotly.graph_objs as go

# Python imports
import random
from collections import deque
import time
from datetime import datetime

# Other imports
import pandas as pd # import to fix bug in plotly

# --------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------- APP INITIALIZATION
app = dash.Dash(
	__name__,
	meta_tags=[{"name": "viewport", "content": "width=device-width"}]
	)

# --------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------- SENSOR INITIALIZATION
start_time = datetime.now()

# BME280 weather sensor
from bme280 import BME280
try:
	from smbus2 import SMBus
except ImportError:
	from smbus import SMBus
bus    = SMBus(1)
bme280 = BME280(i2c_dev=bus)

# LTR559 light sensor
try:
    from ltr559 import LTR559
    ltr559 = LTR559()
except ImportError:
    import ltr559

# MICS6814 gas sensor
from enviroplus import gas

# PMS5003 particulate matter sensor 
from pms5003 import PMS5003, ReadTimeoutError
pms5003 = PMS5003()
time.sleep(5.0)

# --------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------- PARAMETERS
# Frequency at which to retrieve sensor values
frequency = 20 # seconds

# Number of data points to store
num_points = 4320 # 24hrs @ 20 sec / point

# --------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------ DATA INITIALIZATION
X             = deque(maxlen=num_points)

cpu_temps     = deque(maxlen=5)
Y_temperature = {'title': 'Temperature',
				 'units': 'C',
				 'values': {'Temperature':     deque(maxlen=num_points)}}
Y_humidity    = {'title': 'Humidity',
				 'units': '%',
				 'values': {'Humidity':        deque(maxlen=num_points)}}
Y_pressure    = {'title': 'Pressure',
				 'units': 'mBar',
				 'values': {'Pressure':        deque(maxlen=num_points)}}
Y_light       = {'title': 'Light',
				 'units': 'Lux',
				 'values': {'Light':           deque(maxlen=num_points)}}
Y_gas_red_nh3 = {'title': 'Reducing and NH3 gases',
				 'units': 'kΩ',
				 'values': {'RED':             deque(maxlen=num_points),
				 			'NH3':             deque(maxlen=num_points)}}
Y_gas_oxi     = {'title': 'Oxidising gases',
				 'units': 'kΩ',
				 'values': {'OX':              deque(maxlen=num_points)}}
Y_pms_small   = {'title': 'Particulate matters (small)',
				 'units': 'per 0.1L of air',
				 'values': {'0.3 - 0.5 um':    deque(maxlen=num_points),
							'0.5 - 1.0 um':    deque(maxlen=num_points)}}
Y_pms_large   = {'title': 'Particulate matters (large)',
				 'units': 'per 0.1L of air',
				 'values': {'1.0 - 2.5  um':   deque(maxlen=num_points),
							'2.5 - 5.0  um':   deque(maxlen=num_points),
							'5.0 - 10.0 um':   deque(maxlen=num_points),
							'>10.0 um':        deque(maxlen=num_points)}}


# --------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------- LAYOUT
app.layout = html.Div([
	html.Div([
        html.Div([
            html.Div([
                html.H3("Joost's Air Quality Dashboard", style={"margin-bottom": "0px"}),
                html.H5("Wouldn't cha know it.", style={"margin-top": "0px"}),
                html.Div(id='reset', style={'display': 'none'}),
                html.Button('Reset', id='button'),
                html.Div(id='counter')]
            )],
            className="one-half column",
            id="title",
        )],
	    id="header",
	    className="row flex-display",
	    style={"margin-bottom": "25px"},
	),
    html.Div([
	    html.Div(
	        [dcc.Graph(id='graph-temperature', animate=True)],
	        className="chart_container six columns",
	    ),
	    html.Div(
	        [dcc.Graph(id='graph-humidity', animate=True)],
	        className="chart_container six columns",
	    )],
		className="row flex-display",
    ),

    html.Div([
	    html.Div(
	        [dcc.Graph(id='graph-pressure', animate=True)],
	        className="chart_container six columns",
	    ),
	    html.Div(
	        [dcc.Graph(id='graph-light', animate=True)],
	        className="chart_container six columns",
	    )],
		className="row flex-display",
    ),

    html.Div([
	    html.Div(
	        [dcc.Graph(id='graph-gases-red-nh3', animate=True)],
	        className="chart_container six columns",
	    ),
	    html.Div(
	        [dcc.Graph(id='graph-gases-ox', animate=True)],
	        className="chart_container six columns",
	    )],
		className="row flex-display",
    ),

    html.Div([
	    html.Div(
	        [dcc.Graph(id='graph-particulates-small', animate=True)],
	        className="chart_container six columns",
	    ),
	    html.Div(
	        [dcc.Graph(id='graph-particulates-large', animate=True)],
	        className="chart_container six columns",
	    )],
		className="row flex-display",
    ),

	dcc.Interval(id='graph-update', interval=frequency*1000),

], id="mainContainer", style={"display": "flex", "flex-direction": "column"})

# --------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------- UTILITY FUNCTIONS
def unpack_values(Y):
	unpacked = []
	for name, values in Y['values'].items():
		for y in values:
			if y is not None:
				unpacked.append(y)
	return unpacked

# --------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------- RESET BUTTON
@app.callback(Output('reset', 'children'),
			  [Input('button', 'n_clicks')])
def reset_data(n_clicks):
	# On page reloads, n_clicks will be None
	if n_clicks is not None:
		X.clear()
		Y_temperature['values']['Temperature'].clear()
		Y_humidity['values']['Humidity'].clear()
		Y_pressure['values']['Pressure'].clear()
		Y_light['values']['Light'].clear()
		Y_gas_red_nh3['values']['RED'].clear()
		Y_gas_red_nh3['values']['NH3'].clear()
		Y_gas_oxi['values']['OX'].clear()
		Y_pms_small['values']['0.3 - 0.5 um'].clear()
		Y_pms_small['values']['0.5 - 1.0 um'].clear()
		Y_pms_large['values']['1.0 - 2.5  um'].clear()
		Y_pms_large['values']['2.5 - 5.0  um'].clear()
		Y_pms_large['values']['5.0 - 10.0 um'].clear()
		Y_pms_large['values']['>10.0 um'].clear()
	return ''

# --------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------ CHART UPDATES
def create_scatter(X, name, values):
	return plotly.graph_objs.Scatter(
				x           = list(X),
				y           = list(values),
				name        = name,
				mode        = 'lines',
				connectgaps = False,
				)

def update_graph(X, Y):
	chart = {'data': [create_scatter(X, name, values) for name, values in Y['values'].items()]}
	Y_all = unpack_values(Y)
	if (len(X) > 0) and (len(Y_all) > 0):
		chart['layout'] = go.Layout(title=Y['title'],
									yaxis_title=Y['units'],
									xaxis=dict(range=[min(X),     max(X)]),
									yaxis=dict(range=[min(Y_all), max(Y_all)]))
	return chart

# Time axis
@app.callback(Output('counter', 'children'),
			  [Input('graph-update', 'n_intervals')])
def update_time(input_data):
	X.append(datetime.now())
	return 'Most recent update: {}'.format(X[-1])
	
# Temperature
def get_cpu_temperature():
	with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
		temp = f.read()
		temp = int(temp) / 1000.0
	return temp

@app.callback(Output('graph-temperature', 'figure'),
			  [Input('graph-update', 'n_intervals')])
def update_graph_temperature(input_data):
	try:
		factor       = 2.25
		cpu_temps.append(get_cpu_temperature())
		avg_cpu_temp = sum(cpu_temps) / float(len(cpu_temps))
		raw_temp     = bme280.get_temperature()
		value        = raw_temp - ((avg_cpu_temp - raw_temp) / factor)
	except:
		value = None
	Y_temperature['values']['Temperature'].append(value)
	return update_graph(X, Y_temperature)

# Humidity
@app.callback(Output('graph-humidity', 'figure'),
			  [Input('graph-update', 'n_intervals')])
def update_graph_temperature(input_data):
	try:
		value = bme280.get_humidity()
	except:
		value = None
	Y_humidity['values']['Humidity'].append(value)
	return update_graph(X, Y_humidity)

# Pressure
@app.callback(Output('graph-pressure', 'figure'),
			  [Input('graph-update', 'n_intervals')])
def update_graph_temperature(input_data):
	try:
		value = bme280.get_pressure()
	except:
		value = None
	Y_pressure['values']['Pressure'].append(value)
	return update_graph(X, Y_pressure)

# Light
@app.callback(Output('graph-light', 'figure'),
			  [Input('graph-update', 'n_intervals')])
def update_graph_temperature(input_data):
	try:
		value = ltr559.get_lux()
	except:
		value = None
	Y_light['values']['Light'].append(value)
	return update_graph(X, Y_light)

# Gases
@app.callback([Output('graph-gases-red-nh3', 'figure'),
	           Output('graph-gases-ox', 'figure')],
			  [Input('graph-update', 'n_intervals')])
def update_graph_gases(input_data):
	try:
		gases = gas.read_all()
		value_red = gases.reducing / 1000
		value_nh3 = gases.nh3 / 1000
		value_oxi = gases.oxidising / 1000
	except:
		value_red = None
		value_nh3 = None
		value_oxi = None
	Y_gas_red_nh3['values']['RED'].append(value_red)
	Y_gas_red_nh3['values']['NH3'].append(value_nh3)
	Y_gas_oxi['values']['OX'].append(value_oxi)
	return (update_graph(X, Y_gas_red_nh3), update_graph(X, Y_gas_oxi))

# Particulate matter
@app.callback([Output('graph-particulates-small', 'figure'),
			   Output('graph-particulates-large', 'figure')],
			  [Input('graph-update', 'n_intervals')])
def update_graph_particulates(input_data):
	try:
		particles = pms5003.read()
		pm100 = particles.pm_per_1l_air(10.0)
		pm50  = particles.pm_per_1l_air(5.0) - pm100
		pm25  = particles.pm_per_1l_air(2.5) - pm100 - pm50
		pm10  = particles.pm_per_1l_air(1.0) - pm100 - pm50 - pm25
		pm5   = particles.pm_per_1l_air(0.5) - pm100 - pm50 - pm25 - pm10
		pm3   = particles.pm_per_1l_air(0.3) - pm100 - pm50 - pm25 - pm10 - pm5
	except:
		pm100 = None
		pm50  = None
		pm25  = None
		pm10  = None
		pm5   = None
		pm3   = None
	Y_pms_small['values']['0.3 - 0.5 um'].append(pm3)
	Y_pms_small['values']['0.5 - 1.0 um'].append(pm5)
	Y_pms_large['values']['1.0 - 2.5  um'].append(pm10)
	Y_pms_large['values']['2.5 - 5.0  um'].append(pm25)
	Y_pms_large['values']['5.0 - 10.0 um'].append(pm50)
	Y_pms_large['values']['>10.0 um'].append(pm100)
	return (update_graph(X, Y_pms_small), update_graph(X, Y_pms_large))

# --------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------- APP LAUNCH
if __name__ == '__main__':
	app.run_server(host='0.0.0.0', port=8080 ,debug=True)


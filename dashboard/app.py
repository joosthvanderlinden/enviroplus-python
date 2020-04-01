# TODO
#
# - Come up with some interesting numbers to display, perhaps based on experiments?
#	- Inspiration: https://dash-gallery.plotly.host/Portal/
#   - Main example: https://github.com/plotly/dash-sample-apps/tree/master/apps/dash-oil-and-gas
#
# - Make particulate matter chart optional
#
# - Add layout for different lines,
# 	- Examples: https://plotly.com/python/line-charts/

# --------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------- PARAMETERS

# Frequency at which to retrieve sensor values
frequency  = 10 # seconds

# Number of data points to store
num_points = 8640 # 24hrs @ 10 sec / point

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
# ------------------------------------------------------------------------------ DATA INITIALIZATION
X             = deque(maxlen=num_points)

Y_temperature = {'title': 'Temperature',
				 'units': 'C',
				 'values': {'Temperature': deque(maxlen=num_points)}}
Y_humidity    = {'title': 'Humidity',
				 'units': '%',
				 'values': {'Humidity':    deque(maxlen=num_points)}}
Y_pressure    = {'title': 'Pressure',
				 'units': 'mBar',
				 'values': {'Pressure':    deque(maxlen=num_points)}}
Y_light       = {'title': 'Light',
				 'units': 'Lux',
				 'values': {'Light':       deque(maxlen=num_points)}}
Y_gas         = {'title': 'Gases',
				 'units': 'kΩ',
				 'values': {'OX*10':       deque(maxlen=num_points),
				 			'RED':         deque(maxlen=num_points),
				 			'NH3':         deque(maxlen=num_points)}}
Y_pms         = {'title': 'Particulate matters',
				 'units': '/100cl',
				 'values': {'>0.3um':      deque(maxlen=num_points),
							'>0.5um':      deque(maxlen=num_points),
							'>1.0um':      deque(maxlen=num_points),
							'>2.5um':      deque(maxlen=num_points),
							'>5.0um':      deque(maxlen=num_points),
							'>10.0um':     deque(maxlen=num_points)}}

# --------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------- LAYOUT
app.layout = html.Div([
	html.Div([
        html.Div(
            [
                # html.Img(
                #     src=app.get_asset_url("dash-logo.png"),
                #     id="plotly-image",
                #     style={
                #         "height": "60px",
                #         "width": "auto",
                #         "margin-bottom": "25px",
                #     },
                # )
            ],
            className="one-third column",
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.H3(
                            "Air Quality Dashboard",
                            style={"margin-bottom": "0px"},
                        ),
                        html.H5(
                            "Wouldn't cha know it.", 
                            style={"margin-top": "0px"}
                        ),
                    ]
                )
            ],
            className="one-half column",
            id="title",
        ),
        html.Div(
            [
                # html.A(
                #     html.Button("Learn More", id="learn-more-button"),
                #     href="https://plot.ly/dash/pricing/",
                # )
            ],
            className="one-third column",
            id="button",
        )],
	    id="header",
	    className="row flex-display",
	    style={"margin-bottom": "25px"},
	),

	# html.Div([
	#     html.Div([
 #            html.H3(
 #                "Air Quality Dashboard",
 #                style={"margin-bottom": "0px"},
 #            ),
 #            html.H5(
 #                "Wouldn't cha know it", 
 #                style={"margin-top": "0px"}
 #            )],
	#         className="one-half column",
	#         id="title",
	#     ),
	#     html.Div(id='counter')
	#     ], 
	#     id="header",
	# 	className="row flex-display",
	# 	style={"margin-bottom": "10px"},
 #    ),

	html.Div(id='counter'),
	# html.Div([
	# 	html.Div(
 #            [html.H6(id="number-temperature-text"), html.P("Temperature")],
 #            id="number-temperature",
 #            className="number_container",
 #        ),
 #        html.Div(
 #            [html.H6(id="number-humidity-text"), html.P("Humidity")],
 #            id="number-humidity",
 #            className="number_container",
 #        ),
 #        html.Div(
 #            [html.H6(id="number-pressure-text"), html.P("Pressure")],
 #            id="number-pressure",
 #            className="number_container",
 #        ),
 #        html.Div(
 #            [html.H6(id="number-light-text"), html.P("Light")],
 #            id="number-light",
 #            className="number_container",
 #        ),
 #        html.Div(
 #            [html.H6(id="number-oxi-text"), html.P("Oxidising")],
 #            id="number-oxi",
 #            className="number_container",
 #        ),
 #        html.Div(
 #            [html.H6(id="number-red-text"), html.P("Reducing")],
 #            id="number-red",
 #            className="number_container",
 #        ),
 #        html.Div(
 #            [html.H6(id="number-nh3-text"), html.P("NH3")],
 #            id="number-nh3",
 #            className="number_container",
 #        ),
 #        html.Div(
 #            [html.H6(id="number-pm03-text"), html.P(">0.3um")],
 #            id="number-pm03",
 #            className="number_container",
 #        ),
 #        html.Div(
 #            [html.H6(id="number-pm05-text"), html.P(">0.5um")],
 #            id="number-pm05",
 #            className="number_container",
 #        ),
 #        html.Div(
 #            [html.H6(id="number-pm10-text"), html.P(">1.0um")],
 #            id="number-pm10",
 #            className="number_container",
 #        ),
 #        html.Div(
 #            [html.H6(id="number-pm25-text"), html.P(">2.5um")],
 #            id="number-pm25",
 #            className="number_container",
 #        ),
 #        html.Div(
 #            [html.H6(id="number-pm50-text"), html.P(">5.0um")],
 #            id="number-pm50",
 #            className="number_container",
 #        ),
 #        html.Div(
 #            [html.H6(id="number-pm100-text"), html.P(">10.0um")],
 #            id="number-pm100",
 #            className="number_container",
 #        )], 
 #    	id="number-header", 
 #    	className="row container-display"
 #    ),

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
	        [dcc.Graph(id='graph-gases', animate=True)],
	        className="chart_container six columns",
	    ),
	    html.Div(
	        [dcc.Graph(id='graph-particulates', animate=True)],
	        className="chart_container six columns",
	    )],
		className="row flex-display",
    ),

	dcc.Interval(id='graph-update', interval=frequency*1000),

], id="mainContainer", style={"display": "flex", "flex-direction": "column"})

# --------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------- UTILITY FUNCTIONS
def unpack_values(Y):
	Y_all = []
	for name, values in Y['values'].items():
		for y in values:
			if y is not None:
				Y_all.append(y)
	return Y_all

def round_values(Y):
	rounded = []
	for name, values in Y['values'].items():
		v = values[-1]
		if v is None:
			rounded.append('')
		else:
			rounded.append(round(v, 1))
	return tuple(rounded)

# --------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------ CHART UPDATES
def create_scatter(X, name, values):
	return plotly.graph_objs.Scatter(
				x           = list(X),
				y           = list(values),
				name        = name,
				mode        = 'lines',
				connectgaps = False,
				line_shape  = 'hv' 
				)

def update_graph(X, Y):
	chart = {'data': [create_scatter(X, name, values) for name, values in Y['values'].items()]}
	Y_all = unpack_values(Y)
	if (len(X) > 0) and (len(Y_all) > 0):
		chart['layout'] = go.Layout(title=Y['title'],
									yaxis_title=Y['units'],
									xaxis=dict(range=[min(X),     max(X)]),
									yaxis=dict(range=[min(Y_all), max(Y_all)]))
	return (chart,)# + round_values(Y) # (chart,) creates single-item tuple

# Time axis
@app.callback(Output('counter', 'children'),
			  [Input('graph-update', 'n_intervals')])
def update_time(input_data):
	X.append(datetime.now())
	return 'Most recent update: {}'.format(X[-1])
	
# Temperature
@app.callback([Output('graph-temperature', 'figure'),
	 		   # Output('number-temperature-text', 'children')
	 		   ],
			  [Input('graph-update', 'n_intervals')])
def update_graph_temperature(input_data):
	try:
		value = bme280.get_temperature()
	except:
		value = None
	Y_temperature['values']['Temperature'].append(value)
	return update_graph(X, Y_temperature)

# Humidity
@app.callback([Output('graph-humidity', 'figure'),
	 		   # Output('number-humidity-text', 'children')
	 		   ],
			  [Input('graph-update', 'n_intervals')])
def update_graph_temperature(input_data):
	try:
		value = bme280.get_humidity()
	except:
		value = None
	Y_humidity['values']['Humidity'].append(value)
	return update_graph(X, Y_humidity)

# Pressure
@app.callback([Output('graph-pressure', 'figure'),
	 		   # Output('number-pressure-text', 'children')
	 		   ],
			  [Input('graph-update', 'n_intervals')])
def update_graph_temperature(input_data):
	try:
		value = bme280.get_pressure()
	except:
		value = None
	Y_pressure['values']['Pressure'].append(value)
	return update_graph(X, Y_pressure)

# Light
@app.callback([Output('graph-light', 'figure'),
	 		   # Output('number-light-text', 'children')
	 		   ],
			  [Input('graph-update', 'n_intervals')])
def update_graph_temperature(input_data):
	try:
		value = ltr559.get_lux()
	except:
		value = None
	Y_light['values']['Light'].append(value)
	return update_graph(X, Y_light)

# Gases
@app.callback([Output('graph-gases', 'figure'),
	 		   # Output('number-oxi-text', 'children'),
	 		   # Output('number-red-text', 'children'),
	 		   # Output('number-nh3-text', 'children')
	 		   ],
			  [Input('graph-update', 'n_intervals')])
def update_graph_gases(input_data):
	try:
		gases = gas.read_all()
		value_oxi = gases.oxidising / 100 # adjusted to fit chart better
		value_red = gases.reducing / 1000
		value_nh3 = gases.nh3 / 1000
	except:
		value_oxi = None
		value_red = None
		value_nh3 = None
	Y_gas['values']['Oxidising'].append(value_oxi)
	Y_gas['values']['Reducing'].append(value_red)
	Y_gas['values']['NH3'].append(value_nh3)
	return update_graph(X, Y_gas)

# Particulate matter
@app.callback([Output('graph-particulates', 'figure'),
	 		   # Output('number-pm03-text', 'children'),
	 		   # Output('number-pm05-text', 'children'),
	 		   # Output('number-pm10-text', 'children'),
	 		   # Output('number-pm25-text', 'children'),
	 		   # Output('number-pm50-text', 'children'),
	 		   # Output('number-pm100-text', 'children')
	 		   ],
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
	Y_pms['values']['>0.3um'].append(pm3)
	Y_pms['values']['>0.5um'].append(pm5)
	Y_pms['values']['>1.0um'].append(pm10)
	Y_pms['values']['>2.5um'].append(pm25)
	Y_pms['values']['>5.0um'].append(pm50)
	Y_pms['values']['>10.0um'].append(pm100)
	return update_graph(X, Y_pms)

# --------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------- APP LAUNCH
if __name__ == '__main__':
	app.run_server(host='0.0.0.0', port=8080 ,debug=True)


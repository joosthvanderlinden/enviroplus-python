# TODO
# - Add other charts to app.layout
# 	- 3x2 grid of:
#		- Temperature
#		- Humidity
#		- Pressure
#		- Light
#		- Gases (OX, RED, NH3)
#		- Particulates (>0.3um, >0.5um, >1.0um, >2.5um, >5.0um, >10.0um)
#
# - Come up with some interesting numbers to display, perhaps based on experiments?
#	- Inspiration: https://dash-gallery.plotly.host/Portal/
#   - Main example: https://github.com/plotly/dash-sample-apps/tree/master/apps/dash-oil-and-gas
#	
# - Load all the data in app.callback, as in https://github.com/nophead/EnviroPlusWeb/blob/master/app.py
# 	- Wrap chart update in seperate function but create a seperate callback for every chart
#   - Come up with a way to show multiple lines in one chart (for gases and PMs)
#   - Basics: https://dash.plotly.com/getting-started-part-2
#
# - Make particulate matter chart optional
#
# - Add layout for different lines,
# 	- Examples: https://plotly.com/python/line-charts/

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
X             = deque(maxlen=20)
Y_temperature = ('Temperature', deque(maxlen=20))
Y_humidity    = ('Humidity', deque(maxlen=20))
Y_pressure    = ('Pressure', deque(maxlen=20))
Y_light       = ('Light', deque(maxlen=20))
Y_gas_oxi     = ('Oxidising', deque(maxlen=20))
Y_gas_red     = ('Reducing', deque(maxlen=20))
Y_gas_nh3     = ('NH3', deque(maxlen=20))
Y_pm_03       = ('>0.3um', deque(maxlen=20))
Y_pm_05       = ('>0.5um', deque(maxlen=20))
Y_pm_10       = ('>1.0um', deque(maxlen=20))
Y_pm_25       = ('>2.5um', deque(maxlen=20))
Y_pm_50       = ('>5.0um', deque(maxlen=20))
Y_pm_100      = ('>10.0um', deque(maxlen=20))

# --------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------- LAYOUT
app.layout = html.Div(children=[
	html.Div([
	    html.Div([
            html.H3(
                "Air Quality Dashboard",
                style={"margin-bottom": "0px"},
            )],
	        className="one-half column",
	        id="title",
	    )], 
	    id="header",
		className="row flex-display",
		style={"margin-bottom": "25px"},
    ),

	html.Div(id='counter'),
	html.Div([
		html.Div(
            [html.H6(id="number-temperature-text"), html.P("Temperature")],
            id="number-temperature",
            className="mini-container",
        ),
        html.Div(
            [html.H6(id="number-humidity-text"), html.P("Humidity")],
            id="number-humidity",
            className="mini-container",
        ),
        html.Div(
            [html.H6(id="number-pressure-text"), html.P("Pressure")],
            id="number-pressure",
            className="mini-container",
        ),
        html.Div(
            [html.H6(id="number-light-text"), html.P("Light")],
            id="number-light",
            className="mini-container",
        ),
        html.Div(
            [html.H6(id="number-oxi-text"), html.P("Oxidising")],
            id="number-oxi",
            className="mini-container",
        ),
        html.Div(
            [html.H6(id="number-red-text"), html.P("Reducing")],
            id="number-red",
            className="mini-container",
        ),
        html.Div(
            [html.H6(id="number-nh3-text"), html.P("NH3")],
            id="number-nh3",
            className="mini-container",
        ),
        html.Div(
            [html.H6(id="number-pm03-text"), html.P(">0.3um")],
            id="number-pm03",
            className="mini-container",
        ),
        html.Div(
            [html.H6(id="number-pm05-text"), html.P(">0.5um")],
            id="number-pm05",
            className="mini-container",
        ),
        html.Div(
            [html.H6(id="number-pm10-text"), html.P(">1.0um")],
            id="number-pm10",
            className="mini-container",
        ),
        html.Div(
            [html.H6(id="number-pm25-text"), html.P(">2.5um")],
            id="number-pm25",
            className="mini-container",
        ),
        html.Div(
            [html.H6(id="number-pm50-text"), html.P(">5.0um")],
            id="number-pm50",
            className="mini-container",
        ),
        html.Div(
            [html.H6(id="number-pm100-text"), html.P(">10.0um")],
            id="number-pm100",
            className="mini-container",
        )], 
    	id="number-header", 
    	className="row container-display"
    ),

    html.Div([
	    html.Div(
	        [dcc.Graph(id='graph-temperature', animate=True)],
	        className="pretty_container six columns",
	    ),
	    html.Div(
	        [dcc.Graph(id='graph-humidity', animate=True)],
	        className="pretty_container six columns",
	    )],
		className="row flex-display",
    ),

    html.Div([
	    html.Div(
	        [dcc.Graph(id='graph-pressure', animate=True)],
	        className="pretty_container six columns",
	    ),
	    html.Div(
	        [dcc.Graph(id='graph-light', animate=True)],
	        className="pretty_container six columns",
	    )],
		className="row flex-display",
    ),

    html.Div([
	    html.Div(
	        [dcc.Graph(id='graph-gases', animate=True)],
	        className="pretty_container six columns",
	    ),
	    html.Div(
	        [dcc.Graph(id='graph-particulates', animate=True)],
	        className="pretty_container six columns",
	    )],
		className="row flex-display",
    ),

	dcc.Interval(id='graph-update', interval=5*1000), # update every 5 seconds

], id="mainContainer", style={"display": "flex", "flex-direction": "column"})

# --------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------- UTILITY FUNCTIONS
def unpack_arrays(Ys):
	Y_all = []
	for Y in Ys:
		for y in Y[1]:
			if y is not None:
				Y_all.append(y)
	return Y_all

def round_values(Ys):
	values = []
	for Y in Ys:
		v = Y[1][-1]
		if v is None:
			values.append('')
		else:
			values.append(round(v, 1))
	return tuple(values)

# --------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------ CHART UPDATES
def create_scatter(X, Y):
	return plotly.graph_objs.Scatter(
				x           = list(X),
				y           = list(Y[1]),
				name        = Y[0],
				mode        = 'lines+markers',
				connectgaps = False
				)

def update_graph(X, Ys):
	chart = {'data': [create_scatter(X, Y) for Y in Ys]}
	Y_all = unpack_arrays(Ys)
	if (len(X) > 0) and (len(Y_all) > 0):
		chart['layout'] = go.Layout(xaxis=dict(range=[min(X),     max(X)]),
									yaxis=dict(range=[min(Y_all), max(Y_all)]))
	return tuple(chart) + round_values(Ys)

# Time axis
@app.callback(Output('counter', 'children'),
			  [Input('graph-update', 'n_intervals')])
def update_time(input_data):
	if len(X) == 0:
		X.append(1)
	else:
		X.append(X[-1]+1)
	return 'Most recent update: {}'.format(X[-1])
	
# Temperature
@app.callback([Output('graph-temperature', 'figure'),
	 		   Output('number-temperature-text', 'children')],
			  [Input('graph-update', 'n_intervals')])
def update_graph_temperature(input_data):
	try:
		value = bme280.get_temperature()
	except:
		value = None
	Y_temperature[1].append(value)
	return update_graph(X, [Y_temperature])

# Humidity
@app.callback([Output('graph-humidity', 'figure'),
	 		   Output('number-humidity-text', 'children')],
			  [Input('graph-update', 'n_intervals')])
def update_graph_temperature(input_data):
	try:
		value = bme280.get_humidity()
	except:
		value = None
	Y_humidity[1].append(value)
	return update_graph(X, [Y_humidity])

# Pressure
@app.callback([Output('graph-pressure', 'figure'),
	 		   Output('number-pressure-text', 'children')],
			  [Input('graph-update', 'n_intervals')])
def update_graph_temperature(input_data):
	try:
		value = bme280.get_pressure()
	except:
		value = None
	Y_pressure[1].append(value)
	return update_graph(X, [Y_pressure])

# Light
@app.callback([Output('graph-light', 'figure'),
	 		   Output('number-light-text', 'children')],
			  [Input('graph-update', 'n_intervals')])
def update_graph_temperature(input_data):
	try:
		value = ltr559.get_lux()
	except:
		value = None
	Y_light[1].append(value)
	return update_graph(X, [Y_light])

# Gases
@app.callback([Output('graph-gases', 'figure'),
	 		   Output('number-oxi-text', 'children'),
	 		   Output('number-red-text', 'children'),
	 		   Output('number-nh3-text', 'children')],
			  [Input('graph-update', 'n_intervals')])
def update_graph_gases(input_data):
	try:
		gases = gas.read_all()
		value_oxi = gases.oxidising / 1000
		value_red = gases.reducing / 1000
		value_nh3 = gases.nh3 / 1000
	except:
		value_oxi = None
		value_red = None
		value_nh3 = None
	Y_gas_oxi[1].append(value_oxi)
	Y_gas_red[1].append(value_red)
	Y_gas_nh3[1].append(value_nh3)
	return update_graph(X, [Y_gas_oxi, Y_gas_red, Y_gas_nh3])

# Particulate matter
@app.callback([Output('graph-particulates', 'figure'),
	 		   Output('number-pm03-text', 'children'),
	 		   Output('number-pm05-text', 'children'),
	 		   Output('number-pm10-text', 'children'),
	 		   Output('number-pm25-text', 'children'),
	 		   Output('number-pm50-text', 'children'),
	 		   Output('number-pm100-text', 'children')],
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
	Y_pm_03[1].append(pm3)
	Y_pm_05[1].append(pm5)
	Y_pm_10[1].append(pm10)
	Y_pm_25[1].append(pm25)
	Y_pm_50[1].append(pm50)
	Y_pm_100[1].append(pm100)
	return update_graph(X, [Y_pm_03, Y_pm_05, Y_pm_10, Y_pm_25, Y_pm_50, Y_pm_100])

# --------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------- APP LAUNCH
if __name__ == '__main__':
	app.run_server(host='0.0.0.0', port=8080 ,debug=True)


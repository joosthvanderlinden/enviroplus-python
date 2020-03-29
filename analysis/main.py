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
Y_temperature = deque(maxlen=20)
Y_humidity    = deque(maxlen=20)
Y_pressure    = deque(maxlen=20)
Y_light       = deque(maxlen=20)
Y_gas_oxi     = deque(maxlen=20)
Y_gas_red     = deque(maxlen=20)
Y_gas_nh3     = deque(maxlen=20)
Y_pm_03       = deque(maxlen=20)
Y_pm_05       = deque(maxlen=20)
Y_pm_10       = deque(maxlen=20)
Y_pm_25       = deque(maxlen=20)
Y_pm_50       = deque(maxlen=20)
Y_pm_100      = deque(maxlen=20)

# --------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------- LAYOUT
header_text = '''
## Air Quality Dashboard
A [plotly dash](https://dash.plotly.com/) for the output of the 
[Enviro+](https://shop.pimoroni.com/products/enviro?variant=31155658457171) air quality sensor 
board and [PMS5003](https://shop.pimoroni.com/products/pms5003-particulate-matter-sensor-with-cable) 
particulate matter sensor, connected to a [Raspberry Pi](https://www.raspberrypi.org/).
'''

app = dash.Dash(__name__)
app.layout = html.Div(children=[
	dcc.Markdown(children=header_text),
	html.Div(id='counter'),

	dcc.Graph(id='graph-temperature', animate=True),
	dcc.Graph(id='graph-humidity', animate=True),
	dcc.Graph(id='graph-pressure', animate=True),
	dcc.Graph(id='graph-light', animate=True),
	dcc.Graph(id='graph-gases', animate=True),
	dcc.Graph(id='graph-particulates', animate=True),

	dcc.Interval(id='graph-update', interval=5*1000), # update every 5 seconds
])

# --------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------- UTILITY FUNCTIONS
def unpack_arrays(Ys):
	Y_all = []
	for Y in Ys:
		for y in Y:
			if y is not None:
				Y_all.append(y)
	return Y_all

# --------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------ CHART UPDATES
def create_scatter(X,Y):
	return plotly.graph_objs.Scatter(
				x           = list(X),
				y           = list(Y),
				name        = 'Scatter',
				mode        = 'lines+markers',
				connectgaps = False
				)

def update_graph(X, Ys):
	chart = {'data': [create_scatter(X, Y) for Y in Ys]}
	Y_all = unpack_arrays(Ys)
	if (len(X) > 0) and (len(Y_all) > 0):
		chart['layout'] = go.Layout(xaxis=dict(range=[min(X),     max(X)]),
									yaxis=dict(range=[min(Y_all), max(Y_all)]))
	return chart

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
@app.callback(Output('graph-temperature', 'figure'),
			  [Input('graph-update', 'n_intervals')])
def update_graph_temperature(input_data):
	try:
		Y_temperature.append(bme280.get_temperature())
	except:
		Y_temperature.append(None)
	return update_graph(X, [Y_temperature])

# Humidity
@app.callback(Output('graph-humidity', 'figure'),
			  [Input('graph-update', 'n_intervals')])
def update_graph_temperature(input_data):
	try:
		Y_humidity.append(bme280.get_humidity())
	except:
		Y_humidity.append(None)
	return update_graph(X, [Y_humidity])

# Pressure
@app.callback(Output('graph-pressure', 'figure'),
			  [Input('graph-update', 'n_intervals')])
def update_graph_temperature(input_data):
	try:
		Y_pressure.append(bme280.get_pressure())
	except:
		Y_pressure.append(None)
	return update_graph(X, [Y_pressure])

# Light
@app.callback(Output('graph-light', 'figure'),
			  [Input('graph-update', 'n_intervals')])
def update_graph_temperature(input_data):
	try:
		Y_light.append(ltr559.get_lux())
	except:
		Y_light.append(None)
	return update_graph(X, [Y_light])

# Gases
@app.callback(Output('graph-gases', 'figure'),
			  [Input('graph-update', 'n_intervals')])
def update_graph_gases(input_data):
	try:
		gases = gas.read_all()
		Y_gas_oxi.append(gases.oxidising / 1000)
		Y_gas_red.append(gases.reducing / 1000)
		Y_gas_nh3.append(gases.nh3 / 1000)
	except:
		Y_gas_oxi.append(None)
		Y_gas_red.append(None)
		Y_gas_nh3.append(None)
	return update_graph(X, [Y_gas_oxi, Y_gas_red, Y_gas_nh3])

# Particulate matter
@app.callback(Output('graph-particulates', 'figure'),
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
		Y_pm_03.append(pm3)
		Y_pm_05.append(pm5)
		Y_pm_10.append(pm10)
		Y_pm_25.append(pm25)
		Y_pm_50.append(pm50)
		Y_pm_100.append(pm100)
	except:
		Y_pm_03.append(None)
		Y_pm_05.append(None)
		Y_pm_10.append(None)
		Y_pm_25.append(None)
		Y_pm_50.append(None)
		Y_pm_100.append(None)
	return update_graph(X, [Y_pm_03, Y_pm_05, Y_pm_10, Y_pm_25, Y_pm_50, Y_pm_100])

# --------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------- APP LAUNCH
if __name__ == '__main__':
	app.run_server(host='0.0.0.0', port=8080 ,debug=True)


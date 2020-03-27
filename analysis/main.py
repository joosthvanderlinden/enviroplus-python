# TODO
# - Add other charts to app.layout
# 	- 3x2 grid of:
#		- Temperature
#		- Humidity
#		- Pressure
#		- Light
#		- Gasses (OX, RED, NH3)
#		- Particulates (>0.3um, >0.5um, >1.0um, >2.5um, >5.0um, >10.0um)
#
# - Come up with some interesting numbers to display, perhaps based on experiments?
#	- Inspiration: https://dash-gallery.plotly.host/Portal/
#	
# - Load all the data in app.callback, as in https://github.com/nophead/EnviroPlusWeb/blob/master/app.py
# 	- Wrap chart update in seperate function but create a seperate callback for every chart
#   - Come up with a way to show multiple lines in one chart (for gasses and PMs)
#   - Basics: https://dash.plotly.com/getting-started-part-2
#
# - Make particulate matter chart optional

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
import pandas

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
# --------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------ DATA INITIALIZATION
X = deque(maxlen=20)
X.append(1)

Y_temperature = deque(maxlen=20)
Y_temperature.append(25)

Y_humidity = deque(maxlen=20)
Y_humidity.append(25)

Y_pressure = deque(maxlen=20)
Y_pressure.append(25)

Y_light = deque(maxlen=20)
Y_light.append(25)

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

	dcc.Graph(id='graph-temperature', animate=True),
	dcc.Graph(id='graph-humidity', animate=True),
	dcc.Graph(id='graph-pressure', animate=True),
	dcc.Graph(id='graph-light', animate=True),
	# dcc.Graph(id='graph-gasses', animate=True),
	# dcc.Graph(id='graph-particulates', animate=True),

	dcc.Interval(id='graph-update', interval=5*1000), # update every 5 seconds
])

# --------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------ CHART UPDATES
def update_graph(X, Y):
	data = plotly.graph_objs.Scatter(
			x=list(X),
			y=list(Y),
			name='Scatter',
			mode='lines+markers'
			)

	return {'data': [data],'layout' : go.Layout(xaxis=dict(range=[min(X),max(X)]),
												yaxis=dict(range=[min(Y),max(Y)]),)}

# Time axis
@app.callback(None,
			  [Input('graph-update', 'n_intervals')])
def update_time(input_data):
	X.append(X[-1]+1)
	
# Temperature
@app.callback(Output('graph-temperature', 'figure'),
			  [Input('graph-update', 'n_intervals')])
def update_graph_temperature(input_data):
	Y_temperature.append(bme280.get_temperature())
	return update_graph(X, Y_temperature)

# Humidity
@app.callback(Output('graph-humidity', 'figure'),
			  [Input('graph-update', 'n_intervals')])
def update_graph_temperature(input_data):
	Y_humidity.append(bme280.get_humidity())
	return update_graph(X, Y_humidity)

# Pressure
@app.callback(Output('graph-pressure', 'figure'),
			  [Input('graph-update', 'n_intervals')])
def update_graph_temperature(input_data):
	Y_pressure.append(bme280.get_pressure())
	return update_graph(X, Y_pressure)

# Light
@app.callback(Output('graph-temperature', 'figure'),
			  [Input('graph-light', 'n_intervals')])
def update_graph_temperature(input_data):
	Y_light.append(ltr559.get_lux())
	return update_graph(X, Y_light)


# --------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------- APP LAUNCH
if __name__ == '__main__':
	app.run_server(host='0.0.0.0', port=8080 ,debug=True)

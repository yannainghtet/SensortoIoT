from flask import Flask, render_template, request, redirect, make_response, Response
import random
import json
from random import random
from flask_sqlalchemy import SQLAlchemy
from time import sleep
import os
import logging
from turbo_flask import Turbo
import threading
from datetime import datetime
from pytz import timezone
import time

app = Flask(__name__)
temperature = 0
humidity = 0
turbocount = 0
glcount = 0

turbo = Turbo(app)

#Starting page
@app.route('/')
def index():
  return render_template('index.html')

@app.route('/submit', methods=['GET','POST'])
def submit():
  name= request.form['name']
  email=request.form['email']
  return redirect('/log_Data')


@app.route('/log_Data', methods=['GET','POST'])
def log_Data():
    global temperature
    global humidity
    global time

    if request.method == 'POST':
        #app.logger.info(request.form)
        temperature = request.form.get('temp')
        print(temperature)
        humidity = request.form.get('hum')
        print(humidity)
        #return "data logged"
    return render_template('base.html', temperature=temperature, humidity=humidity,time=time)
    
    
@app.route('/data', methods=["GET", "POST"])
def data():    
    if request.method == 'GET':
        Temperature = temperature
        Humidity = humidity	
        data = [time() * 1000, Temperature, Humidity]

        response = make_response(json.dumps(data))

        response.content_type = 'application/json'

        return response    

@app.route('/temp-data')
def temp_data():
    def generate_temp_data():
        while True:
            json_data = json.dumps(
                {'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'value': temperature})
            yield f"data:{json_data}\n\n"
            time.sleep(1)

    return Response(generate_temp_data(), mimetype='text/event-stream')     

@app.route('/hum-data')
def hum_data():
    def generate_hum_data():
        while True:
            json_data = json.dumps(
                {'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'value': humidity})
            yield f"data:{json_data}\n\n"
            time.sleep(1)

    return Response(generate_hum_data(), mimetype='text/event-stream')     



#-----------------------------------------------------------------------

@app.context_processor
def injectSensorData():

    global temperature
    global humidity

        
    return dict(
    temperature = temperature,
    humidity = humidity,
    )

#----------------------------------------------------------------------------

#------------------------------------------------------------------------------
# Background updater thread that runs before 1st client connects
@app.before_first_request
def before_first_request():
    threading.Thread(target=update_sensor_data).start()

def update_sensor_data():
    with app.app_context():    
        while True:
            sleep(4)
            turbo.push(turbo.replace(render_template('base.html'), 'base'))
            
#-----------------------------------------------------------------------

if __name__ == '__main__':
    port = os.environ.get("PORT", 5000)# Get port number of env at runtime, else use default port 5000
    app.run(debug=True, host='0.0.0.0', port=port)  # 0.0.0.0 port forwarding resolves the host IP address at runtime

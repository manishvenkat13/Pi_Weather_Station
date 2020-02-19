from flask import Flask, request, render_template
from sendEmail import send_email
from weather import get_timestamp
from sense_hat import SenseHat
import os
import csv


app = Flask(__name__)


def get_csv_data():
    """Open the daily csv log and return the content"""
    csv_list = []
    day = get_timestamp().split()[0]
    csv_path = os.path.join(os.path.dirname(__file__) + '/logs/', day + '.csv')
    # csv_path = '/home/pi/Pi_Weather_Station/src/logs/' + day + '.csv'
    with open(csv_path, 'r') as csv_file:
        # content = f.read()
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            # print(row)
            csv_list.append(row)
    return csv_list

# print(get_csv_data())

def get_dark_sky():
    """Read the most recent dark sky log and return a list of the stats"""
    csv_content = get_csv_data()
    most_recent = csv_content[-1]
    dark_sky_string = most_recent[9]
    dark_sky_list = dark_sky_string.strip('][').split(', ')
    ds_temp = dark_sky_list[0]
    ds_cond = dark_sky_list[1].strip("'")
    ds_fore = dark_sky_list[2].strip("'")
    return [ds_temp, ds_cond, ds_fore]

# print(get_dark_sky())

def get_gov_aqi():
    """Read the most recent aqi log and return the stats"""
    csv_content = get_csv_data()
    most_recent = csv_content[-1]
    aqi_string = most_recent[10]
    aqi_list = aqi_string.strip('][').split(', ')
    aqi = aqi_list[0]
    air_cond = aqi_list[1].strip("'")
    return [aqi, air_cond]

# print(get_gov_aqi())


@app.route('/')
def index():
    sense = SenseHat()
    sense.clear()

    acceleration = sense.get_accelerometer_raw()
    celsius      = round(sense.get_temperature(), 1)
    kwargs = dict(
        celsius     = celsius,
        fahrenheit  = round(1.8 * celsius + 32, 1),
        humidity    = round(sense.get_humidity(), 1),
        pressure    = round(sense.get_pressure(), 1),
        x = round(acceleration['x'], 2),
        y = round(acceleration['y'], 2),
        z = round(acceleration['z'], 2),
    )
    aqi = get_gov_aqi()
    dark_sky = get_dark_sky()
    return render_template('weather.html', **kwargs, aqi=aqi, dark_sky=dark_sky)


@app.route('/alerts/', methods=['POST', 'GET'])
def alerts():
    if request.method == 'POST':
        e_subject = request.form['subject']
        e_message = request.form['message']
        send_email(e_subject, e_message)
    return render_template('alerts.html')


@app.route('/logs/')
def logs_web():
    day = get_timestamp().split()[0]
    csv_path = os.path.join(os.path.dirname(__file__) + '/logs/', day + '.csv')
    with open(csv_path, 'r') as f:
        content = f.read()
    return render_template('logs.html', content=content)


while __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

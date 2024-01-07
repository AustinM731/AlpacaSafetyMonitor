from datetime import datetime
from flask import Flask, jsonify, render_template
from flask_cors import CORS
from pymongo import MongoClient
from pytz import timezone
import config_secrets as secrets
import board
import graphs
import threading
import time
import psycopg2
from adafruit_bme280 import basic as adafruit_bme280
from adafruit_mlx90614 import MLX90614
from gpiozero import InputDevice


app = Flask(__name__)
CORS(app)

# db_config = {
#     "dbname": secrets.postgres_db_name,
#     "user": secrets.postgres_db_user,
#     "password": secrets.postgres_db_password,
#     "host": secrets.postgres_db_host,
#     "port": secrets.postgres_db_port
# }

def get_mongo_client():
    hosts = ','.join(secrets.mongodb_host)
    uri = f"mongodb://{secrets.mongodb_user}:{secrets.mongodb_password}@{hosts}/{secrets.mongodb_dbname}?authSource=admin&replicaSet={secrets.mongodb_replicaset}"
    client = MongoClient(uri)
    return client

i2c = board.I2C()
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)
mlx90614 = MLX90614(i2c)
rain_sensor = InputDevice(17, pull_up=True)

polling_interval = 5
latest_sensor_data = {}
safe = False
cloudy_condition_duration = 3000
unsafe_cloudy_condition_duration = 5*60

# def insert_into_db(data):
#     """ Insert sensor data into the database """
#     conn = None
#     try:
#         conn = psycopg2.connect(**db_config)
#         cur = conn.cursor()
#         query = """
#         INSERT INTO sensor_data (timestamp, ambient_temp, pressure, humidity, sky_temp, cloudiness, rain, safe)
#         VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
#         """
#         cur.execute(query, data)
#         conn.commit()
#         cur.close()
#     except (Exception, psycopg2.DatabaseError) as error:
#         print(error)
#     finally:
#         if conn is not None:
#             conn.close()

def insert_into_db(data):
    """ Insert sensor data into MongoDB """
    client = None
    try:
        client = get_mongo_client()
        db = client[secrets.mongodb_dbname]
        collection = db[secrets.mongodb_collection]

        # Data conversion to dictionary (if not already in that format)
        data_dict = {
            "timestamp": data[0],
            "ambient_temp": data[1],
            "pressure": data[2],
            "humidity": data[3],
            "sky_temp": data[4],
            "cloudiness": data[5],
            "rain": data[6],
            "safe": data[7]
        }

        # Inserting data into MongoDB
        collection.insert_one(data_dict)
    except Exception as error:
        print(error)
    finally:
        if client is not None:
            client.close()

def celsius_to_fahrenheit(celsius):
    return (celsius * 9 / 5) + 32

def hpa_to_inhg(hpa):
    return hpa * 0.02953

def determine_cloudiness(ambient_temp_f, sky_temp_f):
    temp_diff = abs(ambient_temp_f - sky_temp_f)
    if temp_diff < 10:
        return "Heavy Clouds"
    elif temp_diff < 25:
        return "Clouds"
    elif temp_diff < 30:
        return "Light Clouds"
    else:
        return "Clear"
    
def is_cloudy_condition(cloudiness):
    return cloudiness in ["Light Clouds", "Clouds", "Heavy Clouds"]
    
def determine_safety(sensor_data):
    global cloudy_condition_duration, safe

    if is_cloudy_condition(sensor_data.get("cloudiness", "")):
        cloudy_condition_duration += polling_interval
    else:
        cloudy_condition_duration = 0

    if cloudy_condition_duration >= unsafe_cloudy_condition_duration or sensor_data.get("rain", False):
        safe = False
    else:
        safe = True

    
def poll_sensors():
    global latest_sensor_data
    while True:
        ambient_temp_f = celsius_to_fahrenheit(bme280.temperature)
        pressure_inhg = hpa_to_inhg(bme280.pressure)
        humidity = bme280.humidity
        sky_temp_f = celsius_to_fahrenheit(mlx90614.object_temperature)
        cloudiness = determine_cloudiness(ambient_temp_f, sky_temp_f)
        rain = rain_sensor.is_active

        latest_sensor_data = {
            "ambient_temperature_f": ambient_temp_f,
            "pressure_inhg": pressure_inhg,
            "humidity": humidity,
            "sky_temperature_f": sky_temp_f,
            "cloudiness": cloudiness,
            "rain": rain
        }
        
        determine_safety(latest_sensor_data)

        # current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        eastern = timezone('US/Eastern')
        current_time = datetime.now(eastern)
        db_data = (
            current_time,
            ambient_temp_f,
            pressure_inhg,
            humidity,
            sky_temp_f,
            cloudiness,
            rain,
            safe
        )

        insert_into_db(db_data)
        time.sleep(polling_interval)

sensor_polling_thread = threading.Thread(target=poll_sensors, daemon=True)
sensor_polling_thread.start()

def generate_graphs():
    while True:
        graphs.generate_all_graphs(secrets.observer_latitude, secrets.observer_longitude)
        time.sleep(300)

graph_generation_thread = threading.Thread(target=generate_graphs, daemon=True)
graph_generation_thread.start()

@app.route('/')
def home():
    return render_template('frontend.html')

@app.route('/data')
def get_data():
    return jsonify(latest_sensor_data)

@app.route('/is_safe')
def is_safe():
    return jsonify(safe)

if __name__ == '__main__':
    app.run(host='0.0.0.0')

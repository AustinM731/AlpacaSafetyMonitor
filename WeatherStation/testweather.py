from flask import Flask, jsonify
from flask_cors import CORS
import config_secrets as secrets
import graphs
import threading
import time
import random
import psycopg2


app = Flask(__name__)
CORS(app)

db_config = {
    "dbname": secrets.postgres_db_name,
    "user": secrets.postgres_db_user,
    "password": secrets.postgres_db_password,
    "host": secrets.postgres_db_host,
    "port": secrets.postgres_db_port
}

polling_interval = 30
latest_sensor_data = {}
safe = True
cloudy_condition_duration = 0
unsafe_cloudy_condition_duration = 10*60

def insert_into_db(data):
    """ Insert sensor data into the database """
    conn = None
    try:
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()
        query = """
        INSERT INTO sensor_data (timestamp, ambient_temp, pressure, humidity, sky_temp, cloudiness, rain, safe)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cur.execute(query, data)
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

def generate_fake_sensor_data():
    """ Generate fake data for testing """
    ambient_temp_f = random.uniform(50, 60)  # Fake temperature in Fahrenheit
    pressure_inhg = random.uniform(28, 32)    # Fake pressure in inHg
    humidity = random.uniform(0, 100)         # Fake humidity in percent
    sky_temp_f = random.uniform(0, 45)       # Fake sky temperature in Fahrenheit
    rain = random.choice([True, False])       # Randomly choose rain status
    return ambient_temp_f, pressure_inhg, humidity, sky_temp_f, rain

def determine_cloudiness(ambient_temp, sky_temp):
    temp_diff = abs(ambient_temp - sky_temp)
    if temp_diff < 10:
        return "Heavy Clouds"
    elif temp_diff < 25:
        return "Clouds"
    elif temp_diff < 30:
        return "Light Clouds"
    else:
        return "Clear"

def is_cloudy_condition(cloudiness):
    return cloudiness in ["Clouds", "Heavy Clouds"]

def determine_safety(sensor_data):
    global cloudy_condition_duration, safe

    if is_cloudy_condition(sensor_data.get("cloudiness", "")):
        cloudy_condition_duration += polling_interval
    else:
        cloudy_condition_duration = 0

    if cloudy_condition_duration >= unsafe_cloudy_condition_duration:
        safe = False

    if sensor_data.get("rain", True):
        safe = False

    else:
        safe = True
    
def poll_sensors():
    global latest_sensor_data
    while True:
        ambient_temp_f, pressure_inhg, humidity, sky_temp_f, rain = generate_fake_sensor_data()
        cloudiness = determine_cloudiness(ambient_temp_f, sky_temp_f)

        latest_sensor_data = {
            "ambient_temperature_f": ambient_temp_f,
            "pressure_inhg": pressure_inhg,
            "humidity": humidity,
            "sky_temperature_f": sky_temp_f,
            "cloudiness": cloudiness,
            "rain": rain
        }
        
        determine_safety(latest_sensor_data)

        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
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

@app.route('/data')
def get_data():
    return jsonify(latest_sensor_data)

@app.route('/is_safe')
def is_safe():
    return jsonify(safe)

if __name__ == '__main__':
    app.run(debug=True)

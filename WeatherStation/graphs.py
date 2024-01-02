import ephem
import datetime
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patches as mpatches
import os
import psycopg2
import config_secrets as secrets
from sqlalchemy import create_engine

# Database connection parameters
db_config = {
    "dbname": secrets.postgres_db_name,
    "user": secrets.postgres_db_user,
    "password": secrets.postgres_db_password,
    "host": secrets.postgres_db_host,
    "port": secrets.postgres_db_port
}

def generate_clouds_graph(df, ax):
    ax.plot(df['timestamp'], df['ambient_temp'], label='Ambient Temperature')
    ax.plot(df['timestamp'], df['sky_temp'], label='Sky Temperature', color='lightblue')

    # Heavy Clouds
    ax.fill_between(df['timestamp'], df['ambient_temp'], df['ambient_temp'] - 10, 
                    color='gray', alpha=0.5)
    heavy_cloud_patch = mpatches.Patch(color='gray', alpha=0.5, label='Heavy Clouds')

    # General Clouds
    ax.fill_between(df['timestamp'], df['ambient_temp'], df['ambient_temp'] - 25, 
                    color='gray', alpha=0.3)
    cloud_patch = mpatches.Patch(color='gray', alpha=0.3, label='Clouds')

    # Light Clouds
    ax.fill_between(df['timestamp'], df['ambient_temp'], df['ambient_temp'] - 30, 
                    color='gray', alpha=0.1)
    light_cloud_patch = mpatches.Patch(color='gray', alpha=0.1, label='Light Clouds')

    # Adjusting legend to include new cloud types
    legend = ax.legend(handles=[*ax.get_legend_handles_labels()[0], heavy_cloud_patch, cloud_patch, light_cloud_patch], 
                       loc='upper center', bbox_to_anchor=(0.5, -0.1), 
                       fancybox=True, shadow=True, ncol=3)
    legend.get_frame().set_alpha(0.5)

    ax.set_ylabel('Temperature F')
    ax.set_title('Clouds Graph')


def generate_humidity_graph(df, ax):
    ax.plot(df['timestamp'], df['humidity'], label='Humidity', color='green')
    ax.set_ylabel('Humidity (%)')
    ax.set_title('Humidity Graph')
    legend = ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1))
    legend.get_frame().set_alpha(0.5)

def generate_air_pressure_graph(df, ax):
    ax.plot(df['timestamp'], df['pressure'], label='Air Pressure', color='purple')
    ax.set_ylabel('Pressure (inHg)')
    ax.set_title('Air Pressure Graph')
    legend = ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1))
    legend.get_frame().set_alpha(0.5)

def generate_boolean_graph(df, ax):
    df['safe_numeric'] = df['safe'].astype(int)
    df['rain_numeric'] = df['rain'].astype(int)
    ax.plot(df['timestamp'], df['safe_numeric'], label='Safe', color='green', marker='o')
    ax.plot(df['timestamp'], df['rain_numeric'], label='Rain', color='blue', marker='o')
    ax.set_ylabel('Status (0=False, 1=True)')
    ax.set_title('Safe and Rain Status')
    ax.set_yticks([0, 1])
    ax.set_yticklabels(['False', 'True'])
    legend = ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1))
    legend.get_frame().set_alpha(0.5)
    
# def plot_sun_moon_positions(observer_latitude, observer_longitude, ax):
#     observer = ephem.Observer()
#     observer.lat = str(observer_latitude)
#     observer.lon = str(observer_longitude)

#     start_date = datetime.datetime.now()
#     end_date = start_date + datetime.timedelta(days=2)
#     date_range = pd.date_range(start=start_date, end=end_date, freq='10T')  # data every 10 minutes

#     sun_altitudes = []
#     moon_altitudes = []

#     for single_date in date_range:
#         observer.date = single_date

#         sun = ephem.Sun(observer)
#         moon = ephem.Moon(observer)
        
#         sun.compute(observer)
#         moon.compute(observer)
        
#         sun_altitudes.append(float(sun.alt))
#         moon_altitudes.append(float(moon.alt))

#     ax.plot(date_range, sun_altitudes, label='Sun Altitude')
#     ax.plot(date_range, moon_altitudes, label='Moon Altitude')
#     ax.fill_between(date_range, 0, sun_altitudes, alpha=0.1, color='yellow')
#     ax.fill_between(date_range, 0, moon_altitudes, alpha=0.1, color='blue')
#     ax.set_ylabel('Altitude (radians)')
#     ax.set_title('Sun and Moon Altitude')
#     ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1))
#     ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
#     ax.xaxis.set_major_locator(mdates.HourLocator(interval=12))


db_engine = create_engine(f'postgresql://{db_config["user"]}:{db_config["password"]}@{db_config["host"]}/{db_config["dbname"]}')

def generate_all_graphs(observer_latitude, observer_longitude):
    with db_engine.connect() as conn:
        query = "SELECT timestamp, ambient_temp, sky_temp, humidity, pressure, rain, safe FROM sensor_data"
        df = pd.read_sql(query, conn)

    fig, axs = plt.subplots(4, 1, figsize=(15, 20))

    generate_clouds_graph(df, axs[0])
    generate_humidity_graph(df, axs[1])
    generate_air_pressure_graph(df, axs[2])
    generate_boolean_graph(df, axs[3])
    # plot_sun_moon_positions(observer_latitude, observer_longitude, axs[4])

    plt.tight_layout()
    current_script_path = os.path.dirname(os.path.abspath(__file__))
    static_dir_path = os.path.join(current_script_path, 'static')
    graph_path = os.path.join(static_dir_path, 'graphs.png')
    fig.savefig(graph_path, transparent=True)
    plt.close(fig)

generate_all_graphs(secrets.observer_latitude, secrets.observer_longitude)


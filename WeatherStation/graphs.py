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

def set_plot_style(ax):
    # Set the style for each plot
    ax.spines['bottom'].set_color('white')
    ax.spines['top'].set_color('white')
    ax.spines['left'].set_color('white')
    ax.spines['right'].set_color('white')
    ax.xaxis.label.set_color('white')
    ax.yaxis.label.set_color('white')
    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')
    ax.title.set_color('white')
    for line in ax.get_legend().get_lines():
        line.set_color('white')

def generate_clouds_graph(df, ax):
    ax.plot(df['timestamp'], df['ambient_temp'], label='Ambient Temperature', color='orange')
    ax.plot(df['timestamp'], df['sky_temp'], label='Sky Temperature', color='cyan')

    # Adjusted cloud colors for dark mode
    ax.fill_between(df['timestamp'], df['ambient_temp'], df['ambient_temp'] - 10, 
                    color='deepskyblue', alpha=0.5)
    ax.fill_between(df['timestamp'], df['ambient_temp'], df['ambient_temp'] - 25, 
                    color='dodgerblue', alpha=0.3)
    ax.fill_between(df['timestamp'], df['ambient_temp'], df['ambient_temp'] - 30, 
                    color='lightblue', alpha=0.1)

    set_plot_style(ax)
    ax.set_ylabel('Temperature F')
    ax.set_title('Clouds Graph')

def generate_humidity_graph(df, ax):
    ax.plot(df['timestamp'], df['humidity'], label='Humidity', color='limegreen')

    set_plot_style(ax)
    ax.set_ylabel('Humidity (%)')
    ax.set_title('Humidity Graph')

def generate_air_pressure_graph(df, ax):
    ax.plot(df['timestamp'], df['pressure'], label='Air Pressure', color='fuchsia')

    set_plot_style(ax)
    ax.set_ylabel('Pressure (inHg)')
    ax.set_title('Air Pressure Graph')

def generate_boolean_graph(df, ax):
    df['safe_numeric'] = df['safe'].astype(int)
    df['rain_numeric'] = df['rain'].astype(int)
    ax.plot(df['timestamp'], df['safe_numeric'], label='Safe', color='lime', marker='o')
    ax.plot(df['timestamp'], df['rain_numeric'], label='Rain', color='aqua', marker='o')

    set_plot_style(ax)
    ax.set_ylabel('Status (0=False, 1=True)')
    ax.set_title('Safe and Rain Status')
    ax.set_yticks([0, 1])
    ax.set_yticklabels(['False', 'True'])

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

    plt.tight_layout()
    current_script_path = os.path.dirname(os.path.abspath(__file__))
    static_dir_path = os.path.join(current_script_path, 'static')
    graph_path = os.path.join(static_dir_path, 'graphs.png')
    fig.savefig(graph_path, transparent=True)
    plt.close(fig)

generate_all_graphs(secrets.observer_latitude, secrets.observer_longitude)

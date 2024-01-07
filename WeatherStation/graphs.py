import datetime
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patches as mpatches
import os
import config_secrets as secrets
from pymongo import MongoClient
from datetime import datetime, timedelta
from pytz import timezone

def get_mongo_client():
    hosts = ','.join(secrets.mongodb_host)
    uri = f"mongodb://{secrets.mongodb_user}:{secrets.mongodb_password}@{hosts}/{secrets.mongodb_dbname}?authSource=admin&replicaSet={secrets.mongodb_replicaset}"
    client = MongoClient(uri)
    return client

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

    # Style the legend
    legend = ax.get_legend()
    if legend:
        legend.get_frame().set_alpha(0.5)
        # Set text color in the legend to white
        for text in legend.get_texts():
            text.set_color('white')

def generate_clouds_graph(df, ax):
    ax.plot(df['timestamp'], df['ambient_temp'], label='Ambient Temperature', color='orange')
    ax.plot(df['timestamp'], df['sky_temp'], label='Sky Temperature', color='cyan')

    # Adjusted cloud colors for dark mode
    ax.fill_between(df['timestamp'], df['ambient_temp'], df['ambient_temp'] - 10, 
                    color='deepskyblue', alpha=0.5)
    heavy_cloud_patch = mpatches.Patch(color='deepskyblue', alpha=0.5, label='Heavy Clouds')

    ax.fill_between(df['timestamp'], df['ambient_temp'], df['ambient_temp'] - 25, 
                    color='dodgerblue', alpha=0.3)
    cloud_patch = mpatches.Patch(color='dodgerblue', alpha=0.3, label='Clouds')

    ax.fill_between(df['timestamp'], df['ambient_temp'], df['ambient_temp'] - 30, 
                    color='lightblue', alpha=0.1)
    light_cloud_patch = mpatches.Patch(color='lightblue', alpha=0.1, label='Light Clouds')

    # Create the legend with adjusted patches
    legend = ax.legend(handles=[*ax.get_legend_handles_labels()[0], heavy_cloud_patch, cloud_patch, light_cloud_patch], 
                       loc='upper center', bbox_to_anchor=(0.5, -0.1), 
                       fancybox=True, shadow=True, ncol=3)

    set_plot_style(ax)
    ax.set_ylabel('Temperature F')
    ax.set_title('Clouds')

def generate_humidity_graph(df, ax):
    ax.plot(df['timestamp'], df['humidity'], label='Humidity', color='limegreen')
    ax.set_ylabel('Humidity (%)')
    ax.set_title('Humidity')
    legend = ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1))
    set_plot_style(ax)

def generate_air_pressure_graph(df, ax):
    ax.plot(df['timestamp'], df['pressure'], label='Air Pressure', color='fuchsia')
    ax.set_ylabel('Pressure (inHg)')
    ax.set_title('Air Pressure')
    legend = ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1))
    set_plot_style(ax)

def generate_boolean_graph(df, ax):
    df['safe_numeric'] = df['safe'].astype(int)
    df['rain_numeric'] = df['rain'].astype(int)
    ax.plot(df['timestamp'], df['safe_numeric'], label='Safe', color='lime', marker='o')
    ax.plot(df['timestamp'], df['rain_numeric'], label='Rain', color='aqua', marker='o')
    ax.set_ylabel('Status (0=False, 1=True)')
    ax.set_title('Safe and Rain Status')
    ax.set_yticks([0, 1])
    ax.set_yticklabels(['False', 'True'])
    legend = ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1))
    set_plot_style(ax)


def generate_all_graphs(observer_latitude, observer_longitude):
    try:
        client = get_mongo_client()
        db = client[secrets.mongodb_dbname]
        collection = db[secrets.mongodb_collection]
        eastern = timezone('US/Eastern')
        time_threshold = datetime.now(eastern) - timedelta(hours=48)
        query = {"timestamp": {"$gt": time_threshold}}
        cursor = collection.find(query)
        df = pd.DataFrame(list(cursor))

        fig, axs = plt.subplots(4, 1, figsize=(15, 20))

        try:
            generate_clouds_graph(df, axs[0])
        except Exception as e:
            print(f"Error generating clouds graph: {e}")

        try:
            generate_humidity_graph(df, axs[1])
        except Exception as e:
            print(f"Error generating humidity graph: {e}")

        try:
            generate_air_pressure_graph(df, axs[2])
        except Exception as e:
            print(f"Error generating air pressure graph: {e}")

        try:
            generate_boolean_graph(df, axs[3])
        except Exception as e:
            print(f"Error generating boolean graph: {e}")

        plt.tight_layout()
        current_script_path = os.path.dirname(os.path.abspath(__file__))
        static_dir_path = os.path.join(current_script_path, 'static')
        graph_path = os.path.join(static_dir_path, 'graphs.png')
        fig.savefig(graph_path, transparent=True)
        plt.close(fig)

    except Exception as e:
        print(f"Error in generate_all_graphs: {e}")

generate_all_graphs(secrets.observer_latitude, secrets.observer_longitude)


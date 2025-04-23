import pandas as pd
import mysql.connector
# import env
import numpy as np
import re
import time
import os
from sharepointetl import load_env_vars, get_access_token, get_site_id, download_directory, download_file, delete_files_in_directory
import pandas as pd
import warnings
from datetime import datetime, timedelta
import requests
import glob
from bluebook_etl import ETL_Bluebook

HOST = os.getenv("HOST")
DBUSER = os.getenv("DBUSER")
DBNAME = os.getenv("DBNAME")
PASSWORD = os.getenv("PASSWORD")

conn = mysql.connector.connect(
    user=DBUSER,
    password=PASSWORD,
    host=HOST,
    database=DBNAME
)

cursor = conn.cursor()

def run_bluebook_menu():
    # ------------- Loadings vars
    print('Loading vars')
    env_vars = load_env_vars()
    access_token = get_access_token(env_vars)
    site_id = get_site_id(access_token, env_vars["site_name"])
    run_func = ETL_Bluebook

    base_path = env_vars['base_path']
        
    if datetime.now().month <10:
        bluebook_folder = f"{datetime.now().year}/0{datetime.now().month}/{datetime.now().day-1}"
    else:
        bluebook_folder = f"{datetime.now().year}/{datetime.now().month}/{datetime.now().day-1}"
        
    bluebook_path = os.path.join(base_path, bluebook_folder)
    bluebook_path = os.path.normpath(bluebook_path)

    print(f'File path {bluebook_path}')
    directory_path = remote_path = bluebook_path

    # ----------------- DOWNLOADING
    print('Starting Function')
    local_directory = env_vars['LOCAL_DIRECTORY']
    print(f'Loaded directory {local_directory}')

    downloaded = False
    try:
        print('Starting download')
        download_directory(access_token, site_id, remote_path, local_directory)
        print(f'Downloaded file to {local_directory}')
        downloaded = True
    
    except Exception as e:
        print(f"Download error for {run_func.__name__}: {e}")

    if downloaded:
        # ------------ running ETL
        try:
            print('Running main function')

            #conn = mysql.connector.connect(
            #    user=env_vars.DBUSER,
            #    password=env_vars.PASSWORD,
            #    host=env_vars.HOST,
            #    database=env_vars.DBNAME
            #)

            #cursor = conn.cursor()

            run_func(conn, cursor).run()

        except Exception as e:
            print(f"Problem running {run_func.__name__}: {e}")
    else:
        print(f"Skipping {run_func.__name__} due to download failure.")

    # removing the files from the folders locally

    if os.path.exists(env_vars['LOCAL_DIRECTORY']):
        delete_files_in_directory(env_vars['local_directory'])
        print(f"Directory {env_vars['LOCAL_DIRECTORY']} deleted")
    else:
        print(f"Directory {env_vars['LOCAL_DIRECTORY']} does not exist to delete files.")

    

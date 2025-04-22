import requests
import os
# import env
# from dotenv import load_dotenv

def load_env_vars():
    # loading environment variables
    # load_dotenv("./cred.env")
    return {
        "tenant_id": os.getenv("TENANT_ID"),
        "client_id": os.getenv("CLIENT_ID"),
        "client_secret": os.getenv("CLIENT_SECRET"),
        "site_name": os.getenv("SITE_NAME"),
        "directory_path": os.getenv("DIRECTORY_PATH"),
        "base_path": os.getenv("BASE_PATH"),
        "HOST": os.getenv("HOST"),
        "DBNAME": os.getenv("DBNAME"),
        "DBUSER": os.getenv("DBUSER"),
        "PASSWORD": os.getenv("PASSWORD"),
        "LOCAL_DIRECTORY": os.getenv("LOCAL_DIRECTORY")
    }
    # return {
    #     "tenant_id": env.TENANT_ID,
    #     "client_id": env.CLIENT_ID,
    #     "client_secret": env.CLIENT_SECRET,
    #     "site_name": env.SITE_NAME,
    #     "directory_path": env.LOCAL_DIRECTORY,
    #     "base_path": env.BASE_PATH,
    #     "local_directory": env.LOCAL_DIRECTORY
    # }

def get_access_token(env_vars):
    #authenticating and getting access token
    print("Authenticating and getting access token...")
    auth_url = f"https://login.microsoftonline.com/{env_vars['tenant_id']}/oauth2/v2.0/token"
    payload = {
        "grant_type": "client_credentials",
        "client_id": env_vars['client_id'],
        "client_secret": env_vars['client_secret'],
        "scope": "https://graph.microsoft.com/.default"
    }

    response = requests.post(auth_url, data=payload)
    response.raise_for_status()
    print("Access token obtained successfully.")
    return response.json().get("access_token")

def get_site_id(access_token, site_name):
    #getting the side id for the given Sharepoint site
    print(f"Fetching site id for site: {site_name}...")
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(f"https://graph.microsoft.com/v1.0/sites/{site_name}", headers=headers)
    response.raise_for_status()
    site_id = response.json().get("id")
    return site_id

def list_files_in_directory(access_token, site_id, directory_path):
    # listing all the files in the directory
    headers = {"Authorization": f"Bearer {access_token}"}
    url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive/root:/{directory_path}:/children"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    files = response.json().get("value", [])
    return files

def download_file(access_token, site_id, file_path, local_file_name, local_directory):
    #downloading the file from Sharepoint
    headers = {"Authorization": f"Bearer {access_token}"}
    file_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive/root:/{file_path}:/content"
    response = requests.get(file_url, headers=headers)
    response.raise_for_status()

    #saving the file locally
    try:
        os.makedirs(local_directory, exist_ok=True) #creating the directory locally if it doesn't exist
    except OSError as e:
        print(f"Error creating directory {local_directory}: {e}")

    with open(local_file_name, "wb") as file:
        file.write(response.content)

def download_directory(access_token, site_id, directory_path, local_directory):
    # downloading all the files from the directory
    print(f"Creating local directory: {local_directory}...")

    try:
        os.makedirs(local_directory, exist_ok=True)  # Create the directory if it doesn't exist

    except OSError as e:
        print(f"Error creating directory {local_directory}: {e}")
        return

    files = list_files_in_directory(access_token, site_id, directory_path)
    for file in files:
        if file.get("file"):  # Ensure it is a file and not a folder
            file_name = file.get("name")
            file_path = f"{directory_path}/{file_name}"
            local_file_path = os.path.join(local_directory, file_name)
            download_file(access_token, site_id, file_path, local_file_path, local_directory)
    print(f"All files in the {directory_path} have been downloaded.")

def delete_files_in_directory(directory):
    # downloading all the files from the directory
    for file in os.listdir(directory):
        file_path = os.path.join(directory, file)
        try:
            os.remove(file_path)
        except OSError as e:
            pass
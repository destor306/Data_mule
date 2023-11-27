from ftplib import FTP
import os
import subprocess
import time
import logging
from playsound import playsound


beep1 = './assets/beep-01a.wav'
beep2 = './assets/beep-05.wav'
come_get_it = './assets/come_get_it.wav'
no_files = './assets/car_horn_x.wav'
good_to_go = './assets/toot2_x.wav'
# Function to play a sound


def play_notification_sound(sound_path):
    playsound(sound_path)


# Define the base directory for log files
log_base_directory = r'C:\Users\hyunj\OneDrive\Desktop\MVP'

# Initialize logging for the client
client_log_file = r'C:\Users\hyunj\OneDrive\Desktop\MVP\client.log'
logging.basicConfig(filename=client_log_file,
                    level=logging.INFO, format='%(asctime)s - %(message)s')


# Example FTP configurations (you can add more configurations)
ftp_configs = [
    {
        "network_name": 'Yoo',
        "ftp_server": '192.168.1.218',
        "username": 'ftp-user',
        "password": '1234',
        "local_directory": r'C:\Users\hyunj\OneDrive\Desktop\MVP'
    },
    {
        "network_name": 'Yoo',
        "ftp_server": '10.226.121.80',
        "username": 'ftp-user2',
        "password": '1234',
        "local_directory": r'C:\Users\hyunj\OneDrive\Desktop\MVP'
    },
    # Add more configurations as needed
]


def delete_files(ftp, file_list):
    for remote_filename in file_list:
        ftp.delete(remote_filename)
        print(f'Deleted {remote_filename} from the {ftp.host}')


def delete_local_files(local_directory):
    try:
        local_files = os.listdir(local_directory)
        for local_filename in local_files:
            local_filepath = os.path.join(local_directory, local_filename)
            file_extension = os.path.splitext(local_filename)[1]

            # Check if the file extension is not ".log" before deleting
            if file_extension != ".log":
                os.remove(local_filepath)
                print(f'Deleted local file: {local_filename}')
    except Exception as e:
        print(f"Error deleting local files: {str(e)}")


def is_connected_to_wifi_network(network_name):
    try:
        output = subprocess.check_output(
            ['netsh', 'wlan', 'show', 'interfaces']).decode('utf-8')
        return network_name in output
    except subprocess.CalledProcessError:
        return False


def download_files(ftp, username, local_directory, downloaded_files, log_file):
    file_list = ftp.nlst()

    # Create the local directory if it doesn't exist
    if not os.path.exists(local_directory):
        os.makedirs(local_directory)

    # Check if there are files to pick up (excluding .log files) before playing the sound
    if any(not file.endswith('.log') for file in file_list):
        play_notification_sound(come_get_it)

    for remote_filename in file_list:
        if remote_filename not in downloaded_files:
            # Check the file extension and skip downloading log files
            if not remote_filename.endswith('.log'):
                local_filepath = os.path.join(local_directory, remote_filename)
                with open(local_filepath, 'wb') as local_file:
                    ftp.retrbinary(f'RETR {remote_filename}', local_file.write)

                # Modify the log message to include source and filename
                log_message = f'From {username} {ftp.host} download {remote_filename} to Truck {local_filepath}'
                logging.info(log_message)

                print(f'Downloaded {remote_filename} to {local_filepath}')
                downloaded_files.append(remote_filename)  # Append to the list

    logging.shutdown()


def upload_files(ftp, local_directory, uploading_files):
    local_files = os.listdir(local_directory)

    # Check if there are files to upload before proceeding
    if local_files:
        for local_filename in local_files:
            if local_filename not in uploading_files:
                if not local_filename.endswith(".log"):
                    local_filepath = os.path.join(
                        local_directory, local_filename)
                    with open(local_filepath, 'rb') as local_file:
                        ftp.storbinary(f'STOR {local_filename}', local_file)

                    # Log the action on the client
                    log_message = f'From Truck {local_directory} upload {local_filename} to {ftp.host}'
                    logging.info(log_message)

                    print(f'Uploaded {local_filename} to the FTP server')
                    uploading_files.append(local_filename)
        logging.shutdown()

    else:
        print("No files to upload.")


def upload_log_files(ftp, local_directory):
    local_files = os.listdir(local_directory)

    if local_files:
        for local_filename in local_files:
            if local_filename.endswith(".log"):
                local_filepath = os.path.join(local_directory, local_filename)
                with open(local_filepath, 'rb') as local_file:
                    ftp.storbinary(f'STOR {local_filename}', local_file)

                # Log the action on the client
                log_message = f'From User {local_directory} upload {local_filename} to {ftp.host}'
                logging.info(log_message)

                print(f'Uploaded {local_filename} to the FTP server')
        logging.shutdown()
        play_notification_sound(good_to_go)
    else:
        print("No files to upload")


def connect_to_ftp_server(ftp_config):

    if is_connected_to_wifi_network(ftp_config["network_name"]):
        try:
            max_retries = 3
            retry_interval = 5

            retry_count = 0
            while retry_count < max_retries:
                try:
                    ftp = FTP()
                    ftp.connect(ftp_config["ftp_server"])
                    ftp.login(ftp_config["username"], ftp_config["password"])
                    print(
                        f'Truck arrived at {ftp_config["network_name"]} (FTP server)')

                    # Check for files to download
                    downloaded_files = []
                    print(f'Truck checking for files to pick up...')
                    download_files(
                        ftp, ftp_config["username"], ftp_config["local_directory"], downloaded_files, client_log_file)

                    if downloaded_files:
                        print(f'Truck found files to pick up!')
                        upload_log_files(ftp, ftp_config["local_directory"])

                    delete_files(ftp, downloaded_files)
                    ftp.quit()
                    break  # Break the loop if the connection and file check are successful
                except TimeoutError:
                    retry_count += 1
                    print(
                        f'Truck waiting at {ftp_config["network_name"]}... (Attempt {retry_count}/{max_retries})')
                    time.sleep(retry_interval)
            else:
                print(
                    f'Truck unable to connect to {ftp_config["network_name"]} after {max_retries} attempts. Moving on...')
                play_notification_sound(no_files)
                play_notification_sound(no_files)

        except Exception as e:
            print(
                f"Error with FTP server {ftp_config['network_name']}: {str(e)}")
    else:
        print(
            f'Truck not connected to {ftp_config["network_name"]}. Moving on...')


# Truck driver's routine
while True:
    files_downloaded = False  # Initialize a variable to track whether files are downloaded

    for ftp_config in ftp_configs:
        connect_to_ftp_server(ftp_config)

    # Truck driver takes a break before checking the next village
    time.sleep(5)


# End of the while loop

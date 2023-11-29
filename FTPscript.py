from ftplib import FTP
import os
import subprocess
import time
import logging
from playsound import playsound
import sqlite3
import math

beep1 = './assets/beep-01a.wav'
beep2 = './assets/beep-05.wav'
come_get_it = './assets/come_get_it.wav'
no_files = './assets/car_horn_x.wav'
good_to_go = './assets/toot2_x.wav'
# Function to play a sound
python_script_path = './status.py'


def play_notification_sound(sound_path):
    playsound(sound_path)


# Define the base directory for log files
log_base_directory = r'C:\Users\hyunj\OneDrive\Desktop\MVP'

# Initialize logging for the client
client_log_file = r'C:\Users\hyunj\OneDrive\Desktop\MVP\client.log'
logging.basicConfig(filename=client_log_file,
                    level=logging.INFO, format='%(asctime)s - %(message)s')
current_ftp_server = None

# Example FTP configurations (you can add more configurations)
ftp_configs = [
    {
        "network_name": 'Yoo',
        "ftp_server": '192.168.1.218',
        "username": 'villageA',
        "password": '1234',
        "local_directory": r'C:\Users\hyunj\OneDrive\Desktop\MVP'
    },
    {
        "network_name": 'Yoo',
        "ftp_server": '192.168.1.54',
        "username": 'villageB',
        "password": '1234',
        "local_directory": r'C:\Users\hyunj\OneDrive\Desktop\MVP'
    },
    # Add more configurations as needed
]


# def get_next_delivery():
#     conn = sqlite3.connect('file_delivery.db')
#     cursor = conn.cursor()

#     # Example query to get the next file to be delivered
#     cursor.execute(
#         "SELECT filename, SourceVillage, DestinationVillage FROM FileStatuses WHERE Status = 'In Transit (Yellow)' LIMIT 1;")
#     result = cursor.fetchone()

#     conn.close()
#     # Returns a tuple (filename, SourceVillage, DestinationVillage)
#     return result


# def mark_as_delivered(filename):
#     conn = sqlite3.connect('file_delivery.db')
#     cursor = conn.cursor()

#     # Example query to mark the file as delivered
#     cursor.execute(
#         "UPDATE FileStatuses SET Status = 'Delivered (Green)' WHERE filename = ?;", (filename,))

#     conn.commit()
#     conn.close()


def delete_files(ftp, downloaded_files, upload_files):
    print("######################## DELETING FILES ########################")
    for remote_filename in downloaded_files:
        print(remote_filename)
        if remote_filename not in upload_files:
            ftp.delete(remote_filename)
            print(f'Deleted {remote_filename} from the {ftp.host}')


def is_connected_to_wifi_network(network_name):
    try:
        output = subprocess.check_output(
            ['netsh', 'wlan', 'show', 'interfaces']).decode('utf-8')
        return network_name in output
    except subprocess.CalledProcessError:
        return False


def download_files(ftp, username, local_directory, downloaded_files, upload_files):
    file_list = ftp.nlst()

    # Create the local directory if it doesn't exist
    if not os.path.exists(local_directory):
        os.makedirs(local_directory)

    # Check if there are files to pick up (excluding .log files) before playing the sound
    if any(not file.endswith('.log') for file in file_list):
        play_notification_sound(come_get_it)

    upload_file_list = [item[0] for item in upload_files]
    for remote_filename in file_list:
        if remote_filename not in downloaded_files and remote_filename not in upload_file_list:
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


def get_file_size(filename):
    file_size_bytes = os.path.getsize(filename)
    file_size_mb = file_size_bytes / 1024 / 1024
    return math.ceil(file_size_mb)


def get_destination_village_from_db(dest_user):
    conn = sqlite3.connect('file_delivery.db')
    cursor = conn.cursor()

    cursor.execute(
        'SELECT Village FROM UserAccounts WHERE LOWER(Username) = ?', (dest_user.lower(),))
    result = cursor.fetchone()

    conn.close()

    if result:
        return result[0]
    else:
        return None


def upload_files_to_ftp(ftp, local_directory, upload_files, ftp_config, keep_files):
    local_files = os.listdir(local_directory)

    # Check if there are files to upload before proceeding
    if local_files:
        for local_filename in local_files:
            if local_filename not in upload_files:
                if not local_filename.endswith(".log"):
                    local_filepath = os.path.join(
                        local_directory, local_filename)
                    dest_user = local_filename.split("_")[1]
                    dest_user = dest_user.split(".")[0]
                    dest_village = get_destination_village_from_db(dest_user)

                    # Check if the file is meant for the current village
                    if dest_village == ftp_config["username"]:
                        with open(local_filepath, 'rb') as local_file:
                            ftp.storbinary(
                                f'STOR {local_filename}', local_file)

                        file_size = get_file_size(local_filepath)
                        # Log the action on the client
                        log_message = f'From Truck {local_directory} upload {local_filename} {file_size}MB to {ftp_config["username"]} {ftp.host}'
                        logging.info(log_message)

                        print(
                            f'Uploaded {local_filename} to the {ftp_config["username"]} {ftp_config["ftp_server"]}')
                        upload_files.append((local_filename, dest_village))
                    else:
                        keep_files.append(local_filename)
                        print(
                            f'File {local_filename} is not meant for {ftp_config["username"]}. Skipping upload.')

        logging.shutdown()
    else:
        print("No files to upload.")


def remove_files_local_directory(local_files, keep_files):
    for local_filename in local_files:
        if not local_filename.endswith(".log"):
            if local_filename not in keep_files:
                local_filepath = os.path.join(
                    r'C:\Users\hyunj\OneDrive\Desktop\MVP', local_filename)
                os.remove(local_filepath)


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

    else:
        print("No files to upload")


def connect_to_ftp_server(ftp, ftp_config, downloaded_files, upload_files, keep_files):
    global current_ftp_server
    # Initialize the list for local files
    local_files = [filename for filename in os.listdir(
        r'C:\Users\hyunj\OneDrive\Desktop\MVP') if not filename.endswith('.log')]

    if is_connected_to_wifi_network(ftp_config["network_name"]):
        # connected to village
        play_notification_sound(good_to_go)
        try:
            max_retries = 3
            retry_interval = 2

            retry_count = 1
            while retry_count < max_retries:
                try:
                    ftp.connect(ftp_config["ftp_server"])
                    ftp.login(ftp_config["username"], ftp_config["password"])
                    print(
                        f'Truck arrived at {ftp_config["username"]} {ftp_config["ftp_server"]}')

                    if current_ftp_server != ftp_config["ftp_server"]:
                        current_ftp_server = ftp_config["ftp_server"]
                        # Upload files to the FTP server
                        print(f"There are loads in Truck")

                        upload_files_to_ftp(
                            ftp, ftp_config["local_directory"], upload_files, ftp_config, keep_files)
                        upload_log_files(ftp, ftp_config["local_directory"])
                        remove_files_local_directory(local_files, keep_files)

                        print("Upload_files", upload_files)
                        print(
                            "################################ Truck Files deleted ############################################")
                        # Download files from the FTP server
                        print(
                            f'Truck checking for files to pick up at {ftp_config["username"]}')

                        download_files(
                            ftp, ftp_config["username"], ftp_config["local_directory"], downloaded_files, upload_files)

                        if downloaded_files:
                            print(f'Truck found files to pick up!')
                            upload_log_files(
                                ftp, ftp_config["local_directory"])

                        delete_files(ftp, downloaded_files, upload_files)
                        upload_files = []
                        current_ftp_server = ftp_config["ftp_server"]

                    print(
                        "#################################################################################################")

                    ftp.quit()
                    # current_ftp_server = None
                    play_notification_sound(no_files)
                    play_notification_sound(no_files)
                    break  # Break the loop if the connection and file check are successful
                except TimeoutError:
                    retry_count += 1
                    print(
                        f'Truck waiting at {ftp_config["username"]} { ftp_config["ftp_server"]}... (Attempt {retry_count}/{max_retries})')
                    time.sleep(retry_interval)
            else:
                print(
                    f'Truck unable to connect to {ftp_config["username"]} {ftp_config["ftp_server"]} after {max_retries} attempts. Moving on...')
                # current_ftp_server = None
                play_notification_sound(no_files)
                play_notification_sound(no_files)

        except Exception as e:
            print(
                f"Error with FTP server {ftp_config['username']}: {str(e)}")
    else:
        print(
            f'Truck not connected to {ftp_config["username"]}. Moving on...')


# Initialize the list to keep track of downloaded files
# Truck driver's routine
while True:
    for ftp_config in ftp_configs:
        downloaded_files = []

        upload_files = []
        keep_files = []

        ftp = FTP()  # Create a new FTP instance for each village
        connect_to_ftp_server(
            ftp, ftp_config, downloaded_files, upload_files, keep_files)
        # Run the status script to update FileStatuses
        subprocess.run(['python', python_script_path])
        # Truck driver takes a break before checking the next village
        time.sleep(20)


# End of the while loop

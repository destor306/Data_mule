from ftplib import FTP
import os
import subprocess
import time
import logging
from playsound import playsound
import sqlite3


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
        "ftp_server": '192.168.1.54',
        "username": 'ftp-villageA',
        "password": '1234',
        "local_directory": r'C:\Users\hyunj\OneDrive\Desktop\MVP'
    },
    # Add more configurations as needed
]


def get_next_delivery():
    conn = sqlite3.connect('file_delivery.db')
    cursor = conn.cursor()

    # Example query to get the next file to be delivered
    cursor.execute(
        "SELECT filename, SourceVillage, DestinationVillage FROM FileStatuses WHERE Status = 'In Transit (Yellow)' LIMIT 1;")
    result = cursor.fetchone()

    conn.close()
    # Returns a tuple (filename, SourceVillage, DestinationVillage)
    return result


def mark_as_delivered(filename):
    conn = sqlite3.connect('file_delivery.db')
    cursor = conn.cursor()

    # Example query to mark the file as delivered
    cursor.execute(
        "UPDATE FileStatuses SET Status = 'Delivered (Green)' WHERE filename = ?;", (filename,))

    conn.commit()
    conn.close()


def delete_files(ftp, downloaded_files, upload_files):
    print("######################## DELETING FILES ########################")
    for remote_filename in downloaded_files:
        print(remote_filename)
        if remote_filename not in upload_files:
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


def download_files(ftp, username, local_directory, downloaded_files, upload_files):
    file_list = ftp.nlst()

    # Create the local directory if it doesn't exist
    if not os.path.exists(local_directory):
        os.makedirs(local_directory)

    # Check if there are files to pick up (excluding .log files) before playing the sound
    if any(not file.endswith('.log') for file in file_list):
        play_notification_sound(come_get_it)

    for remote_filename in file_list:
        if remote_filename not in downloaded_files and remote_filename not in upload_files:
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


def upload_files_to_ftp(ftp, local_directory, upload_files, ftp_config):
    local_files = os.listdir(local_directory)

    # Check if there are files to upload before proceeding
    if local_files:
        for local_filename in local_files:
            if local_filename not in upload_files:
                if not local_filename.endswith(".log"):
                    local_filepath = os.path.join(
                        local_directory, local_filename)
                    with open(local_filepath, 'rb') as local_file:
                        ftp.storbinary(f'STOR {local_filename}', local_file)

                    # Log the action on the client
                    log_message = f'From Truck {local_directory} upload {local_filename} to {ftp_config["username"]} {ftp.host}'
                    logging.info(log_message)

                    print(
                        f'Uploaded {local_filename} to the {ftp_config["username"]} {ftp_config["ftp_server"]}')
                    upload_files.append(local_filename)
        logging.shutdown()

    else:
        print("No files to upload.")


def remove_files_local_directory(local_files):
    for local_filename in local_files:
        if not local_filename.endswith(".log"):
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
        # play_notification_sound(good_to_go)
    else:
        print("No files to upload")


def connect_to_ftp_server(ftp, ftp_config, downloaded_files, upload_files):
    # Initialize the list for local files
    local_files = [filename for filename in os.listdir(
        r'C:\Users\hyunj\OneDrive\Desktop\MVP') if not filename.endswith('.log')]

    if is_connected_to_wifi_network(ftp_config["network_name"]):
        try:
            max_retries = 3
            retry_interval = 5

            retry_count = 0
            while retry_count < max_retries:
                try:
                    ftp.connect(ftp_config["ftp_server"])
                    ftp.login(ftp_config["username"], ftp_config["password"])
                    print(
                        f'Truck arrived at {ftp_config["username"]} {ftp_config["ftp_server"]}')

                    if local_files:
                        print(f"There are loads in Truck")
                        # Upload files to the FTP server
                        upload_files_to_ftp(
                            ftp, ftp_config["local_directory"], upload_files, ftp_config)
                        upload_log_files(ftp, ftp_config["local_directory"])
                        remove_files_local_directory(local_files)
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
                        upload_log_files(ftp, ftp_config["local_directory"])

                    delete_files(ftp, downloaded_files, upload_files)
                    upload_files = []
                    print(
                        "#################################################################################################")

                    ftp.quit()
                    break  # Break the loop if the connection and file check are successful
                except TimeoutError:
                    retry_count += 1
                    print(
                        f'Truck waiting at {ftp_config["username"]} { ftp_config["ftp_server"]}... (Attempt {retry_count}/{max_retries})')
                    time.sleep(retry_interval)
            else:
                print(
                    f'Truck unable to connect to {ftp_config["username"]} {ftp_config["ftp_server"]} after {max_retries} attempts. Moving on...')
                play_notification_sound(no_files)
                play_notification_sound(no_files)

        except Exception as e:
            print(
                f"Error with FTP server {ftp_config['username']}: {str(e)}")
    else:
        print(
            f'Truck not connected to {ftp_config["username"]}. Moving on...')
    # Run the status script to update FileStatuses
    subprocess.run(['python', python_script_path])


# Initialize the list to keep track of downloaded files
# Truck driver's routine
while True:
    for ftp_config in ftp_configs:
        downloaded_files = []

        upload_files = []

        ftp = FTP()  # Create a new FTP instance for each village
        connect_to_ftp_server(ftp, ftp_config, downloaded_files, upload_files)

        # delivery_info = get_next_delivery()
        # if delivery_info:
        #     filename, source_village, destination_village = delivery_info
        #     print(
        #         f'Truck delivering {filename} from {source_village} to {destination_village}')

        #     try:
        #         # Perform FTP operations here (download, upload, etc.)
        #         # connect_to_ftp_server(ftp, ftp_config)

        #         # Mark the file as delivered in the database
        #         mark_as_delivered(filename)
        #     except Exception as e:
        #         print(f"Error with {str(e)}")
        # else:
        #     print("No more deliveries at the moment.")

    # Truck driver takes a break before checking the next village
    time.sleep(5)


# End of the while loop

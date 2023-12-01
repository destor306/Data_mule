import sqlite3
import os
import re
import time
import uuid

DATABASE_PATH = r'C:\Users\hyunj\OneDrive\Desktop\MVP\file-delivery.db'


# def create_tables():
#     conn = sqlite3.connect(DATABASE_PATH)
#     cursor = conn.cursor()
#     cursor.execute('DROP TABLE IF EXISTS FileStatuses')
#     cursor.execute('DROP TABLE IF EXISTS UserAccounts')

#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS UserAccounts (
#             id TEXT,
#             username TEXT ,
#             password TEXT,
#             phone TEXT,
#             village TEXT,
#             active INTEGER


#         )
#     ''')

#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS FileStatuses (
#             Filename TEXT PRIMARY KEY,
#             SourceVillage TEXT,
#             Sender TEXT,
#             DestinationVillage TEXT,
#             DestinationUser TEXT,
#             Status TEXT,
#             Sizeby_MB INTEGER  -- Add this column for file size
#         )
#     ''')
#     conn.commit()
#     conn.close()


def add_user_account(username, village):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    id = None

    password = None
    phone = None
    active = None

    cursor.execute('''
        INSERT OR REPLACE INTO UserAccounts (id, username, password, phone, village, active)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (id, username, password, phone, village, active))

    conn.commit()
    conn.close()


def get_users_in_village(village):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute(
        'SELECT username FROM UserAccounts WHERE Village = ?', (village,))
    users = cursor.fetchall()

    conn.close()
    return users


# class Truck:
#     def __init__(self):
#         self.village_users = {}

#     def receive_user_information(self, village, users):
#         self.village_users[village] = users

#     def update_user_information(self, village, users):
#         conn = sqlite3.connect(DATABASE_PATH)
#         cursor = conn.cursor()

#         # Update the user information in the village's database
#         for username in users:
#             cursor.execute('''
#                 INSERT OR REPLACE INTO UserAccounts (id, username, password, phone, address, active)
#                 VALUES (?, ?, ?, ?, ?, ?)
#             ''', (id, username, password, phone, village, active))

#         conn.commit()
#         conn.close()

#     def distribute_user_information(self):
#         for destination_village, users in self.village_users.items():
#             for source_village, source_users in self.village_users.items():
#                 if destination_village != source_village:
#                     # Distribute user information from source village to destination village
#                     self.update_user_information(
#                         destination_village, source_users)


def clear_table(table_name):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute(f'DELETE FROM {table_name}')

    conn.commit()
    conn.close()


def update_file_size(filename, file_size):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Update the FileStatuses table with the new file size
    cursor.execute('''
        UPDATE FileStatuses
        SET Sizeby_MB = ?
        WHERE LOWER(Filename) = LOWER(?)
    ''', (file_size, filename))

    conn.commit()
    conn.close()

# Function to get file statuses from the log file and update the database


# def update_truckDatabase(source_file, destination_file):
#     # Connect to source and destination databases
#     source_conn = sqlite3.connect(source_file)
#     destination_conn = sqlite3.connect(destination_file)

#     # Create cursors
#     source_cursor = source_conn.cursor()
#     destination_cursor = destination_conn.cursor()

#     try:
#         # Fetch data from the source database
#         source_cursor.execute("SELECT * FROM users")
#         data_to_copy = source_cursor.fetchall()

#         # Insert or replace data into the destination database
#         destination_cursor.executemany('''
#             INSERT OR REPLACE INTO UserAccounts (id, username, password, phone, village, active)
#             VALUES (
#                 COALESCE((SELECT id FROM UserAccounts WHERE username = ?), ?),
#                 ?,
#                 ?,
#                 ?,
#                 ?,
#                 ?
#             )
#         ''', [(row[1], str(uuid.uuid4()), row[1], row[2], row[3], row[4], row[5]) for row in data_to_copy])

#         # Commit changes
#         destination_conn.commit()

#     finally:
#         # Close connections
#         source_conn.close()
#         destination_conn.close()


# def update_file_statuses(log_file_path, directory_path):
#     conn = sqlite3.connect(DATABASE_PATH)
#     cursor = conn.cursor()

#     file_statuses = {}

#     def update_file_status(filename, source_village, sender, destination_user, status):
#         conn = sqlite3.connect(DATABASE_PATH)
#         cursor = conn.cursor()
#         print(destination_user)
#         # # Print the value of destination_user for debugging
#         # print(f"Destination User: {destination_user}")

#         # Query the UserAccounts table to get the destination village
#         cursor.execute('''
#             SELECT * FROM UserAccounts WHERE LOWER(username) = LOWER(?)
#         ''', (destination_user,))
#         result = cursor.fetchone()
#         # print(result)
#         destination_village = result[4]

#         # Check if the destination user exists in the UserAccounts table
#         if destination_village:
#             # Convert filenames and username to lowercase for case-insensitive comparison
#             filename_lower = filename.lower()
#             sender_lower = sender.lower()
#             source_info = f"from {source_village}"
#             status_message = f"{filename}: {source_info} {sender_lower} -> {destination_village} - {status} (Sender: {sender}, Receiver: {destination_user})"
#             # print(status_message)  # Print the status message

#             cursor.execute('''
#                 SELECT * FROM FileStatuses WHERE Filename = ?
#             ''', (filename_lower,))
#             existing_entry = cursor.fetchone()

#             if existing_entry:
#                 # Entry exists, update only the Status field
#                 cursor.execute('''
#                     UPDATE FileStatuses
#                     SET Status = ?
#                     WHERE Filename = ?
#                 ''', (status, filename_lower))
#             else:
#                 # Entry doesn't exist, insert a new row
#                 cursor.execute('''
#                     INSERT INTO FileStatuses (Filename, SourceVillage, Sender, DestinationVillage, DestinationUser, Status)
#                     VALUES (?, ?, ?, ?, ?, ?)
#                 ''', (filename_lower, source_village, sender, destination_village, destination_user, status))

#         else:
#             # Handle the case where the destination user is not found
#             print(
#                 f"Destination user '{destination_user}' not found in UserAccounts table.")
#         conn.commit()
#         conn.close()

#     def get_status(line):
#         if "download" in line:
#             return "In Transit (Yellow)"
#         elif "upload" in line:
#             return "Delivered (Green)"
#         else:
#             return "Other (Gray)"

#     with open(log_file_path, 'r') as log_file:
#         download_pattern = re.compile(
#             r"From (.+?) download (.+?) to Truck (.+)")
#         upload_pattern = re.compile(r"From (.+?) upload (.+?) to (.+)")
#         file_size_pattern = re.compile(r".+? (\d+)MB ")

#         source_user = None  # Variable to store the source user during processing

#         for line in log_file:
#             if ".log" in line:
#                 source_user_match = re.search(r"From (.+?) ", line)
#                 if source_user_match:
#                     source_user = source_user_match.group(1)
#                 continue

#             status = get_status(line)
#             download_match = download_pattern.search(line)
#             upload_match = upload_pattern.search(line)
#             size_match = file_size_pattern.search(line)

#             # update_file_status(filename, source_village, sender, destination_user, status):
#             if download_match:
#                 uploader, filename, destination = download_match.groups()

#                 # Split the filename by underscore and take the second part (receiver)
#                 sender = filename.split('_')[0]
#                 receiver = filename.split('_')[1]
#                 destination_village, destination_user = destination.split('_')
#                 destination_user = destination_user.split('.')[0]
#                 update_file_status(
#                     filename, uploader, sender, destination_user, status)
#             if upload_match:
#                 uploader, filename, destination = upload_match.groups()
#                 # print(uploader, filename, destination)
#                 # Split the filename by underscore and take the second part (receiver)
#                 sender = filename.split('_')[0]
#                 receiver = filename.split('_')[1]
#                 receiver = receiver.split('.')[0]

#                 update_file_status(
#                     filename, uploader, sender, receiver, status)
#             if size_match:
#                 file_size = size_match.group(1)
#                 update_file_size(filename, file_size)
#                 # Do something with the file size (e.g., update in the database)
#                 # print(f"File Size: {file_size} MB")
#     # List files in the directory
#     files_in_directory = [f for f in os.listdir(
#         directory_path) if os.path.isfile(os.path.join(directory_path, f))]

#     conn.commit()
#     conn.close()


# Example usage
def connect_to_db():
    conn = sqlite3.connect(DATABASE_PATH)


def create_users_table():
    conn = sqlite3.connect(DATABASE_PATH)
    # Create a table if it doesn't exist
    connect_to_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT,
            password TEXT,
            phone TEXT,
            village TEXT,
            active INTEGER
        )
    ''')

    # Create the friends table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS friends (
            user_id INTEGER,
            friend_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (friend_id) REFERENCES users (id),
            PRIMARY KEY (user_id, friend_id)
        )
    ''')

    conn.commit()
    conn.close()


create_users_table()
# Example usage
log_file_path = r'C:\Users\hyunj\OneDrive\Desktop\MVP\client.log'
directory_path = r'C:\Users\hyunj\OneDrive\Desktop\MVP'


# add_user_account("Ken", "ftp-villageB", "ken@email.com")


#  update_file_statuses(log_file_path, directory_path)


# Print File Statuses
# conn = sqlite3.connect(DATABASE_PATH)
# cursor = conn.cursor()
# cursor.execute('SELECT * FROM FileStatuses')
# file_statuses = cursor.fetchall()
# conn.close()

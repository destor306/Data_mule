import sqlite3
import os
import re
import time

DATABASE_PATH = 'file_delivery.db'


def create_tables():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS FileStatuses')
    cursor.execute('DROP TABLE IF EXISTS UserAccounts')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS UserAccounts (
            Username TEXT PRIMARY KEY,
            Village TEXT,
            Email TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS FileStatuses (
            Filename TEXT PRIMARY KEY,
            SourceVillage TEXT,
            Sender TEXT,
            DestinationVillage TEXT,
            DestinationUser TEXT,
            Status TEXT,
            Sizeby_MB INTEGER  -- Add this column for file size
        )
    ''')
    conn.commit()
    conn.close()


def add_user_account(username, village, email):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        INSERT OR REPLACE INTO UserAccounts (Username, Village, Email)
        VALUES (?, ?, ?)
    ''', (username, village, email))

    conn.commit()
    conn.close()


def get_users_in_village(village):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute(
        'SELECT Username, Email FROM UserAccounts WHERE Village = ?', (village,))
    users = cursor.fetchall()

    conn.close()
    return users


class Truck:
    def __init__(self):
        self.village_users = {}

    def receive_user_information(self, village, users):
        self.village_users[village] = users

    def update_user_information(self, village, users):
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        # Update the user information in the village's database
        for username, email in users:
            cursor.execute('''
                INSERT OR REPLACE INTO UserAccounts (Username, Village, Email)
                VALUES (?, ?, ?)
            ''', (username, village, email))

        conn.commit()
        conn.close()

    def distribute_user_information(self):
        for destination_village, users in self.village_users.items():
            for source_village, source_users in self.village_users.items():
                if destination_village != source_village:
                    # Distribute user information from source village to destination village
                    self.update_user_information(
                        destination_village, source_users)


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


def update_file_statuses(log_file_path, directory_path):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    file_statuses = {}

    def update_file_status(filename, source_village, sender, destination_user, status):
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        # # Print the value of destination_user for debugging
        # print(f"Destination User: {destination_user}")

        # Query the UserAccounts table to get the destination village
        cursor.execute('''
            SELECT * FROM UserAccounts WHERE LOWER(Username) = LOWER(?)
        ''', (destination_user,))
        result = cursor.fetchone()
        # print(result)
        destination_village = result[1]

        # Check if the destination user exists in the UserAccounts table
        if destination_village:
            # Convert filenames and username to lowercase for case-insensitive comparison
            filename_lower = filename.lower()
            sender_lower = sender.lower()
            source_info = f"from {source_village}"
            status_message = f"{filename}: {source_info} {sender_lower} -> {destination_village} - {status} (Sender: {sender}, Receiver: {destination_user})"
            print(status_message)  # Print the status message

            cursor.execute('''
                SELECT * FROM FileStatuses WHERE Filename = ?
            ''', (filename_lower,))
            existing_entry = cursor.fetchone()

            if existing_entry:
                # Entry exists, update only the Status field
                cursor.execute('''
                    UPDATE FileStatuses
                    SET Status = ?
                    WHERE Filename = ?
                ''', (status, filename_lower))
            else:
                # Entry doesn't exist, insert a new row
                cursor.execute('''
                    INSERT INTO FileStatuses (Filename, SourceVillage, Sender, DestinationVillage, DestinationUser, Status)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (filename_lower, source_village, sender, destination_village, destination_user, status))

        else:
            # Handle the case where the destination user is not found
            print(
                f"Destination user '{destination_user}' not found in UserAccounts table.")
        conn.commit()
        conn.close()

    def get_status(line):
        if "download" in line:
            return "In Transit (Yellow)"
        elif "upload" in line:
            return "Delivered (Green)"
        else:
            return "Other (Gray)"

    with open(log_file_path, 'r') as log_file:
        import re

        download_pattern = re.compile(
            r"From (.+?) (.+?) download (.+?) to Truck (.+)")
        upload_pattern = re.compile(
            r"From (.+?) upload (.+?) (\d+)MB to (.+?) (.+)")

        file_size_pattern = re.compile(r".+? (\d+)MB ")
        source_user = None  # Variable to store the source user during processing

        for line in log_file:
            if ".log" in line:
                source_user_match = re.search(r"From (.+?) ", line)
                if source_user_match:
                    source_user = source_user_match.group(1)
                continue

            status = get_status(line)
            download_match = download_pattern.search(line)
            upload_match = upload_pattern.search(line)
            size_match = file_size_pattern.search(line)

            # update_file_status(filename, source_village, sender, destination_user, status):
            if download_match:
                source, additional_info, filename, destination = download_match.groups()

                # Extract relevant information from the additional_info group
                sender = filename.split('_')[0]
                receiver = filename.split('_')[1]
                destination_village, destination_user = destination.split('_')
                destination_user = destination_user.split('.')[0]

                # Use source_user if it is not captured in the log message
                source_user = source_user or source

                update_file_status(
                    filename, source_user, sender, destination_user, status)
            if upload_match:
                source, filename, file_size, destination_info, destination = upload_match.groups()

                # Extract relevant information from the filename and destination_info groups
                sender = filename.split('_')[0]
                receiver = filename.split('_')[1]
                receiver = receiver.split('.')[0]

                # Use source_user if it is not captured in the log message
                source_user = source_user or source

                update_file_status(
                    filename, source_user, sender, receiver, status)
                update_file_size(filename, file_size)
            if size_match:
                file_size = size_match.group(1)
                update_file_size(filename, file_size)

                # Do something with the file size (e.g., update in the database)
                # print(f"File Size: {file_size} MB")
    # List files in the directory
    files_in_directory = [f for f in os.listdir(
        directory_path) if os.path.isfile(os.path.join(directory_path, f))]

    conn.commit()
    conn.close()


# Example usage

create_tables()

# Example usage
log_file_path = r'C:\Users\hyunj\OneDrive\Desktop\MVP\client.log'
directory_path = r'C:\Users\hyunj\OneDrive\Desktop\MVP'

# Village A adds new users
add_user_account("Alice", "villageB", "alice@email.com")
add_user_account("Bob", "villageB", "bob@email.com")

# Village B adds new users
add_user_account("Jason", "villageA", "jason@email.com")
add_user_account("Ellen", "villageA", "ellen@email.com")
add_user_account("Ace", "villageA", "ace@email.com")

add_user_account("Ken", "villageC", "ken@email.com")


update_file_statuses(log_file_path, directory_path)

# Print File Statuses
conn = sqlite3.connect(DATABASE_PATH)
cursor = conn.cursor()
cursor.execute('SELECT * FROM FileStatuses')
file_statuses = cursor.fetchall()
conn.close()

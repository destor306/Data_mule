import tkinter as tk
from tkinter import ttk, filedialog
import json
import hashlib
import os
import shutil
import sqlite3


class App:

    def load_login_info(self):
        self.connect_to_db()
        cursor = self.conn.cursor()
        cursor.execute("SELECT username, password FROM users")
        data = cursor.fetchall()
        print(data)
        login_info = {username: password for username, password in data}
        self.conn.commit()
        self.conn.close()
        return login_info

    def connect_to_db(self):
        self.conn = sqlite3.connect('user_info.db')

    def __init__(self, root):
        self.root = root
        self.root.title("File Storage App")
        self.connect_to_db()
        self.create_users_table()
        # Set the window size and center it
        window_width = 800
        window_height = 600
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x_coordinate = (screen_width - window_width) // 2
        y_coordinate = (screen_height - window_height) // 2

        self.root.geometry(
            f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")

        # Current user
        self.current_user = None

        # Load login information from the db file
        self.login_info = self.load_login_info()

        # Login Page
        self.login_frame = ttk.Frame(self.root, padding="10")
        self.create_login_page()

        # Registration Page
        self.registration_frame = ttk.Frame(self.root, padding="10")
        self.create_registration_page()

        # Dropbox-like Page
        self.dropbox_frame = ttk.Frame(self.root, padding="10")
        self.create_dropbox_page()

        # Load friend list from the JSON file
        self.friend_list = self.load_friend_list()

        # Load uploaded files from the JSON file
        self.uploaded_files = self.load_uploaded_files()

        # Friend List Page
        self.friend_list_frame = ttk.Frame(self.root, padding="10")
        self.create_friend_list_page()

        # Download Files Page
        self.download_files_frame = ttk.Frame(self.root, padding="10")
        self.create_download_files_page()

        # Initially, show the login page
        self.show_login_page()

    def create_users_table(self):
        # Create a table if it doesn't exist
        self.connect_to_db()
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password TEXT,
                phone TEXT,
                address TEXT
            )
        ''')
        self.conn.commit()
        self.conn.close()

    def create_login_page(self):
        self.login_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        self.welcome_label_login = ttk.Label(
            self.login_frame, text="Welcome to Data Depot", font=("Helvetica", 16))
        self.username_label = ttk.Label(self.login_frame, text="Username:")
        self.password_label = ttk.Label(self.login_frame, text="Password:")
        self.username_entry = ttk.Entry(self.login_frame)
        self.password_entry = ttk.Entry(self.login_frame, show="*")
        self.login_button = ttk.Button(
            self.login_frame, text="Login", command=self.login)
        self.create_account_button = ttk.Button(
            self.login_frame, text="Create Account", command=self.show_registration_page)

        self.login_frame.columnconfigure(1, weight=1)
        for i in range(5):
            self.login_frame.rowconfigure(i, weight=1)

        padding_x = 40
        padding_y = 5

        self.welcome_label_login.grid(row=0, column=0, columnspan=2, pady=(
            0, padding_y), padx=padding_x, sticky=tk.W + tk.E)
        self.username_label.grid(
            row=1, column=0, sticky=tk.W, padx=padding_x, pady=padding_y)
        self.password_label.grid(
            row=2, column=0, sticky=tk.W, padx=padding_x, pady=padding_y)
        self.username_entry.grid(row=1, column=1, sticky=(
            tk.W, tk.E), padx=padding_x, pady=padding_y)
        self.password_entry.grid(row=2, column=1, sticky=(
            tk.W, tk.E), padx=padding_x, pady=padding_y)
        self.login_button.grid(
            row=3, column=1, padx=padding_x, pady=padding_y, sticky=tk.E)
        self.create_account_button.grid(
            row=4, column=1, padx=padding_x, pady=(padding_y, 0), sticky=tk.E)

    def create_registration_page(self):
        self.registration_frame.grid(
            row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        self.welcome_label_registration = ttk.Label(
            self.registration_frame, text="Create Your Account", font=("Helvetica", 16))
        self.new_username_label = ttk.Label(
            self.registration_frame, text="New Username:")
        self.new_password_label = ttk.Label(
            self.registration_frame, text="New Password:")
        self.phone_label = ttk.Label(
            self.registration_frame, text="Phone Number:")
        self.address_label = ttk.Label(
            self.registration_frame, text="Address:")

        self.new_username_entry = ttk.Entry(self.registration_frame)
        self.new_password_entry = ttk.Entry(self.registration_frame, show="*")
        self.phone_entry = ttk.Entry(self.registration_frame)
        self.address_entry = ttk.Entry(self.registration_frame)

        self.register_button = ttk.Button(
            self.registration_frame, text="Register", command=self.register)
        self.back_to_login_button = ttk.Button(
            self.registration_frame, text="Back to Login", command=self.show_login_page)

        self.registration_frame.columnconfigure(1, weight=1)
        for i in range(7):
            self.registration_frame.rowconfigure(i, weight=1)

        padding_x = 40
        padding_y = 5

        self.welcome_label_registration.grid(
            row=0, column=0, columnspan=2, pady=10, padx=padding_x, sticky=tk.W + tk.E)
        self.new_username_label.grid(
            row=1, column=0, sticky=tk.W, padx=padding_x, pady=padding_y)
        self.new_password_label.grid(
            row=2, column=0, sticky=tk.W, padx=padding_x, pady=padding_y)
        self.phone_label.grid(
            row=3, column=0, sticky=tk.W, padx=padding_x, pady=padding_y)
        self.address_label.grid(
            row=4, column=0, sticky=tk.W, padx=padding_x, pady=padding_y)

        self.new_username_entry.grid(
            row=1, column=1, sticky=(tk.W, tk.E), padx=padding_x, pady=padding_y)
        self.new_password_entry.grid(
            row=2, column=1, sticky=(tk.W, tk.E), padx=padding_x, pady=padding_y)
        self.phone_entry.grid(
            row=3, column=1, sticky=(tk.W, tk.E), padx=padding_x, pady=padding_y)
        self.address_entry.grid(
            row=4, column=1, sticky=(tk.W, tk.E), padx=padding_x, pady=padding_y)

        self.register_button.grid(
            row=5, column=1, padx=padding_x, pady=padding_y, sticky=tk.E)
        self.back_to_login_button.grid(
            row=6, column=1, padx=padding_x, pady=(padding_y, 0), sticky=tk.E)

    def create_dropbox_page(self):
        self.dropbox_frame.grid(
            row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        self.welcome_label_dropbox = ttk.Label(
            self.dropbox_frame, text="Welcome to Your File Storage", font=("Helvetica", 16))
        self.file_listbox = tk.Listbox(
            self.dropbox_frame, selectmode=tk.SINGLE, height=10, width=50)
        self.file_list_label = ttk.Label(
            self.dropbox_frame, text="Uploaded Files:", font=("Helvetica", 12))
        self.upload_button = ttk.Button(
            self.dropbox_frame, text="Upload File", command=self.upload_file)
        self.friend_list_button = ttk.Button(
            self.dropbox_frame, text="Friend List", command=self.show_friend_list_page)
        self.received_files_button = ttk.Button(
            self.dropbox_frame, text="Received Files", command=self.show_download_files_page)
        self.stat_button = ttk.Button(
            self.dropbox_frame, text="Status Files", command=self.show_status_files_page)
        self.delete_account_button = ttk.Button(
            self.dropbox_frame, text="Delete Account", command=self.confirm_delete_account)
        self.logout_button = ttk.Button(
            self.dropbox_frame, text="Log Out", command=self.log_out)

        self.dropbox_frame.columnconfigure(0, weight=1)
        for i in range(9):
            self.dropbox_frame.rowconfigure(i, weight=1)

        padding_x = 20
        padding_y = 5

        self.welcome_label_dropbox.grid(
            row=0, column=0, columnspan=2, pady=10, padx=padding_x, sticky=tk.W + tk.E)
        self.file_list_label.grid(
            row=1, column=0, columnspan=2, pady=5, padx=padding_x, sticky=tk.W + tk.E)
        self.file_listbox.grid(
            row=2, column=0, columnspan=2, padx=padding_x, sticky=(tk.W, tk.E))
        self.upload_button.grid(
            row=4, column=0, columnspan=2, pady=padding_y, padx=padding_x, sticky=tk.E)
        self.friend_list_button.grid(
            row=5, column=0, columnspan=2, pady=padding_y, padx=padding_x, sticky=tk.E)
        self.received_files_button.grid(
            row=6, column=0, columnspan=2, pady=padding_y, padx=padding_x, sticky=tk.E)
        self.stat_button.grid(
            row=7, column=0, columnspan=2, pady=padding_y, padx=padding_x, sticky=tk.E)
        self.delete_account_button.grid(
            row=8, column=0, columnspan=2, pady=padding_y, padx=padding_x, sticky=tk.E)
        self.logout_button.grid(
            row=9, column=0, columnspan=2, pady=padding_y, padx=padding_x, sticky=tk.E)

    def log_out(self):
        # Implement the logic to log out
        # For example, reset the current_user attribute and show the login page
        self.current_user = None
        self.show_login_page()

    def confirm_delete_account(self):
        confirmation_window = tk.Toplevel(self.root)
        confirmation_window.title("Confirmation")
        confirmation_window.geometry("300x150")

        confirmation_label = ttk.Label(
            confirmation_window, text="Are you sure you want to delete your account?")
        confirmation_label.pack(pady=20)

        confirm_button = ttk.Button(
            confirmation_window, text="Confirm", command=lambda: self.delete_account(confirmation_window))
        confirm_button.pack(side=tk.LEFT, padx=10)

        cancel_button = ttk.Button(
            confirmation_window, text="Cancel", command=confirmation_window.destroy)
        cancel_button.pack(side=tk.RIGHT, padx=10)

    def delete_account(self, confirmation_window):
        current_user = self.current_user
        self.connect_to_db()
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM users WHERE username = ?", (current_user,))
        self.conn.commit()

        # After deleting the account, navigate back to the login page
        self.show_login_page()
        # Destroy the confirmation window
        confirmation_window.destroy()
        self.conn.close()

    def add_friend(self):
        new_friend = self.new_friend_entry.get()
        if new_friend and new_friend not in self.friend_list:
            if self.current_user not in self.friend_list:
                self.friend_list[self.current_user] = []
            self.friend_list[self.current_user].append(new_friend)
            self.save_friend_list()
            self.populate_friend_listbox()
            self.new_friend_entry.delete(0, tk.END)
        else:
            error_label = ttk.Label(
                self.friend_list_frame, text="Invalid friend name", foreground="red")
            error_label.grid(row=4, column=1, columnspan=2, pady=5)
            self.friend_list_frame.after(2000, error_label.grid_forget)

    def create_friend_list_page(self):
        self.friend_list_frame.grid(
            row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        self.welcome_label_friends = ttk.Label(
            self.friend_list_frame, text="Your Friend List", font=("Helvetica", 16))
        self.friend_listbox = tk.Listbox(
            self.friend_list_frame, selectmode=tk.SINGLE, height=10)
        self.new_friend_label = ttk.Label(
            self.friend_list_frame, text="New Friend:")
        self.new_friend_entry = ttk.Entry(self.friend_list_frame)
        self.add_friend_button = ttk.Button(
            self.friend_list_frame, text="Add Friend", command=self.add_friend)
        self.back_to_dropbox_button = ttk.Button(
            self.friend_list_frame, text="Back to Dropbox", command=self.show_dropbox_page)

        self.friend_list_frame.columnconfigure(0, weight=1)
        for i in range(6):
            self.friend_list_frame.rowconfigure(i, weight=1)

        padding_x = 20

        self.welcome_label_friends.grid(
            row=0, column=0, columnspan=2, pady=10, padx=padding_x, sticky=tk.W + tk.E)
        self.friend_listbox.grid(
            row=1, column=0, columnspan=2, pady=5, padx=padding_x, sticky=(tk.W, tk.E))
        self.new_friend_label.grid(
            row=2, column=0, sticky=tk.W, pady=5, padx=padding_x)
        self.new_friend_entry.grid(
            row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=padding_x)
        self.add_friend_button.grid(
            row=3, column=1, sticky=tk.E, pady=5, padx=padding_x)
        self.back_to_dropbox_button.grid(
            row=5, column=0, columnspan=2, pady=10, padx=padding_x, sticky=tk.W + tk.E)

    def create_download_files_page(self):
        self.download_files_frame.grid(
            row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        self.received_files_listbox = tk.Listbox(
            self.download_files_frame, selectmode=tk.SINGLE, height=10, width=50)
        self.received_files_label = ttk.Label(
            self.download_files_frame, text="Received Files:", font=("Helvetica", 12))
        self.download_button = ttk.Button(
            self.download_files_frame, text="Download Files", command=self.download_files)
        self.back_to_dropbox_button_download = ttk.Button(
            self.download_files_frame, text="Back to Dropbox", command=self.show_dropbox_page)

        self.download_files_frame.columnconfigure(0, weight=1)
        for i in range(6):
            self.download_files_frame.rowconfigure(i, weight=1)

        padding_x = 20

        self.received_files_label.grid(
            row=1, column=0, columnspan=2, pady=5, padx=padding_x, sticky=tk.W + tk.E)
        self.received_files_listbox.grid(
            row=2, column=0, columnspan=2, pady=5, padx=padding_x, sticky=(tk.W, tk.E))
        self.download_button.grid(
            row=4, column=0, columnspan=2, pady=5, padx=padding_x, sticky=tk.W + tk.E)
        self.back_to_dropbox_button_download.grid(
            row=5, column=0, columnspan=2, pady=10, padx=padding_x, sticky=tk.W + tk.E)

    def load_friend_list(self):
        try:
            with open("friend_list.json", "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return {}

    def save_login_info(self):
        return self.current_user

    def save_friend_list(self):
        with open("friend_list.json", "w") as file:
            json.dump(self.friend_list, file, indent=2)

    def show_login_page(self):
        self.dropbox_frame.grid_remove()
        self.registration_frame.grid_remove()
        self.friend_list_frame.grid_remove()
        self.download_files_frame.grid_remove()
        self.login_frame.grid()

    def show_registration_page(self):
        self.login_frame.grid_remove()
        self.dropbox_frame.grid_remove()
        self.friend_list_frame.grid_remove()
        self.download_files_frame.grid_remove()
        self.registration_frame.grid()

    def show_dropbox_page(self):
        self.login_frame.grid_remove()
        self.registration_frame.grid_remove()
        self.friend_list_frame.grid_remove()
        self.download_files_frame.grid_remove()
        self.dropbox_frame.grid()
        self.populate_file_listbox()

    def show_friend_list_page(self):
        self.login_frame.grid_remove()
        self.registration_frame.grid_remove()
        self.dropbox_frame.grid_remove()
        self.friend_list_frame.grid()
        self.populate_friend_listbox()

    def show_download_files_page(self):
        self.login_frame.grid_remove()
        self.registration_frame.grid_remove()
        self.dropbox_frame.grid_remove()
        self.friend_list_frame.grid_remove()
        self.download_files_frame.grid()
        self.populate_received_files_listbox()

    def show_status_files_page(self):
        self.login_frame.grid_remove()
        self.registration_frame.grid_remove()
        self.dropbox_frame.grid_remove()
        self.friend_list_frame.grid_remove()

    def populate_user_list(self):
        # Replace this with your logic to fetch and populate the user list
        user_list = ["User1", "User2", "User3", "User4"]
        for user in user_list:
            self.user_listbox.insert(tk.END, user)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        print("self.login_info", self.login_info.get(username))
        # Check if the username exists and the password is correct
        if username in self.login_info and self.verify_password(password, self.login_info.get(username)):
            self.current_user = username
            if username not in self.friend_list:
                self.friend_list[username] = []
            self.show_dropbox_page()
        else:
            # For simplicity, just show an error message here
            error_label = ttk.Label(
                self.login_frame, text="Invalid username or password", foreground="red")
            error_label.grid(row=4, column=1, columnspan=2, pady=5)
            self.login_frame.after(2000, error_label.grid_forget)

        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)

    def verify_password(self, plain_password, stored_info):
        # For simplicity, let's use a basic hash function (sha256) for password verification
        hashed_input_password = hashlib.sha256(
            plain_password.encode()).hexdigest()

        # Print the hashed input password and stored hashed password for debugging
        print("Hashed Input Password:", hashed_input_password)
        print("Stored Hashed Password:", stored_info)

        # Compare the hashed input password with the stored hashed password
        return hashed_input_password == stored_info

    def register(self):
        new_username = self.new_username_entry.get()
        new_password = self.new_password_entry.get()
        phone_number = self.phone_entry.get()
        address = self.address_entry.get()
        self.connect_to_db()
        cursor = self.conn.cursor()

        if new_username in self.login_info:
            error_label = ttk.Label(
                self.registration_frame, text="Username already exists try different name", foreground="red")
            error_label.grid(row=7, column=1, columnspan=2, pady=5)
            self.registration_frame.after(2000, error_label.grid_forget)
        else:
            # Hash the password and store the new account information
            hashed_password = hashlib.sha256(new_password.encode()).hexdigest()

            # Insert user data into the database
            cursor.execute('''
                INSERT INTO users (username, password, phone, address)
                VALUES (?, ?, ?, ?)
            ''', (new_username, hashed_password, phone_number, address))

            self.conn.commit()
            self.show_login_page()

            # Clear input fields after successful registration
            self.new_username_entry.delete(0, tk.END)
            self.new_password_entry.delete(0, tk.END)
            self.phone_entry.delete(0, tk.END)
            self.address_entry.delete(0, tk.END)
        # Load login information from the db file
        self.login_info = self.load_login_info()
        self.conn.close()

    def __del__(self):
        # Close the database connection when the object is deleted
        self.conn.close()

    def load_uploaded_files_list(self):
        try:
            with open("uploaded_files.json", "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return {}

    def upload_file(self):
        selected_friend = self.prompt_select_friend()
        file_path = filedialog.askopenfilename()

        if file_path and selected_friend:
            # Get the current user name
            current_user_name = self.current_user

            # Extract the file name from the original path
            original_file_name = os.path.basename(file_path)

            # Format the new file name based on the specified pattern
            formatted_file_name = f"{current_user_name}_{selected_friend}_{original_file_name}"

            uploaded_file_info = {
                'friend': selected_friend,
                'file_name': formatted_file_name
            }

            if current_user_name not in self.uploaded_files:
                self.uploaded_files[current_user_name] = []
            self.uploaded_files[current_user_name].append(uploaded_file_info)
            self.save_uploaded_files()
            self.populate_file_listbox()

            # Copy the file to the destination folder.
            destination_folder = r'C:\Users\hyunj\OneDrive\Desktop\FTP'
            destination_path = os.path.join(
                destination_folder, formatted_file_name)

            try:
                shutil.copy(file_path, destination_path)
                print(
                    f"File '{formatted_file_name}' copied successfully to {destination_folder}")
            except Exception as e:
                print(f"Error copying file: {e}")

        else:
            error_label = ttk.Label(
                self.dropbox_frame, text="No friend or file selected", foreground="red")
            error_label.grid(row=3, column=0, columnspan=2, pady=5)
            self.dropbox_frame.after(2000, error_label.grid_forget)

    def load_uploaded_files(self):
        try:
            with open("uploaded_files.json", "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return {}

    def save_uploaded_files(self):
        with open("uploaded_files.json", "w") as file:
            json.dump(self.uploaded_files, file, indent=2)

    def populate_file_listbox(self):
        self.file_listbox.delete(0, tk.END)
        if self.current_user not in self.uploaded_files:
            return
        for uploaded_file in self.uploaded_files[self.current_user]:
            friend = uploaded_file['friend']
            file_name = uploaded_file['file_name']
            self.file_listbox.insert(tk.END, f"{friend}: {file_name}")

    def prompt_select_friend(self):
        selected_friend_var = tk.StringVar()

        friend_combobox = ttk.Combobox(
            self.dropbox_frame, values=list(self.friend_list[self.current_user]), textvariable=selected_friend_var, state="readonly")
        friend_combobox.set("Select a Friend")
        friend_combobox.grid(row=3, column=0, columnspan=2, pady=5)

        self.dropbox_frame.wait_variable(selected_friend_var)

        selected_friend = selected_friend_var.get()

        friend_combobox.destroy()
        return selected_friend

    def download_files(self):
        # FTP directory
        ftp_directory = r'C:\Users\hyunj\OneDrive\Desktop\FTP'

        # Get the current user name
        current_user_name = self.current_user

        # Destination folder on the desktop for the current user
        destination_folder = os.path.join(
            r'C:\Users\hyunj\OneDrive\Desktop', current_user_name)

        # Create the destination folder if it doesn't exist
        os.makedirs(destination_folder, exist_ok=True)

        # Iterate through files in the FTP directory
        for filename in os.listdir(ftp_directory):
            # Split the filename into parts using '_' as a separator
            parts = filename.split('_')

            # Check if the current user's name is the receiver
            if len(parts) == 3 and parts[1] == current_user_name:
                source_path = os.path.join(ftp_directory, filename)
                destination_path = os.path.join(destination_folder, filename)

                try:
                    # Copy the file to the current user's desktop folder
                    shutil.copy(source_path, destination_path)
                    print(
                        f"File '{filename}' downloaded successfully to {destination_folder}")
                except Exception as e:
                    print(f"Error downloading file: {e}")

    def populate_received_files_listbox(self):
        self.received_files_listbox.delete(0, tk.END)
        # TODO: Add logic to fetch received files and populate the listbox
        pass

    def populate_friend_listbox(self):
        self.friend_listbox.delete(0, tk.END)
        if self.current_user not in self.friend_list:
            return
        for friend in self.friend_list[self.current_user]:
            self.friend_listbox.insert(tk.END, friend)


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()

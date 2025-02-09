import os
import json
import csv
from pymongo import MongoClient
from bson import Binary
from tkinter import filedialog, messagebox
import customtkinter as ctk
from datetime import datetime

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["user_files_db"]
collection = db["user_uploads"]

# Function to store the user's file in MongoDB
def store_user_file(name, file_path):
    _, file_extension = os.path.splitext(file_path)
    
    # Get the current date and time
    now = datetime.now()

    # Fetch date and time separately as strings
    current_date = now.strftime("%Y-%m-%d")  # Format as YYYY-MM-DD
    current_time = now.strftime("%H:%M:%S")  # Format as HH:MM:SS
    
    document = {
        "user_name": name,
        "file_name": os.path.basename(file_path),
        "date_upload": current_date,  # Store date as string
        "time_upload": current_time     # Store time as string
    }

    # Process based on file type
    if file_extension == ".csv":
        with open(file_path, "r") as f:
            reader = csv.DictReader(f)
            data = list(reader)
            document["file_type"] = "csv"
            document["content"] = data

    elif file_extension == ".json":
        with open(file_path, "r") as f:
            data = json.load(f)
            document["file_type"] = "json"
            document["content"] = data

    elif file_extension == ".txt":
        with open(file_path, "r") as f:
            text_data = f.read()
            document["file_type"] = "text"
            document["content"] = text_data

    elif file_extension in [".jpg", ".png", ".jpeg"]:
        with open(file_path, "rb") as f:
            binary_data = f.read()
            document["file_type"] = "image"
            document["data"] = Binary(binary_data)

    elif file_extension in [".pdf", ".docx"]:
        with open(file_path, "rb") as f:
            binary_data = f.read()
            document["file_type"] = file_extension[1:]  # 'pdf' or 'docx'
            document["data"] = Binary(binary_data)

    else:
        messagebox.showerror("Error", f"Unsupported file type: {file_extension}")
        return

    collection.insert_one(document)
    messagebox.showinfo("Success", f"{file_extension.upper()} data stored for {name}.")

# Function to open and retrieve stored file
def retrieve_and_open_file():
    user_name = name_entry.get()
    file_name = file_name_entry.get()
    document = collection.find_one({"user_name": user_name, "file_name": file_name})
    
    if not document:
        messagebox.showerror("Error", f"No file found for {user_name} with name {file_name}")
        return

    file_type = document.get("file_type")
    
    if file_type == "pdf" or file_type == "docx":
        output_path = f"output_{file_name}"
        with open(output_path, "wb") as f:
            f.write(document["data"])
        messagebox.showinfo("File Retrieved", f"{file_type.upper()} saved to {output_path}")
        
        if os.name == 'nt':  # Windows
            os.startfile(output_path)
        elif os.name == 'posix':  # macOS or Linux
            os.system(f"open '{output_path}'")

    elif file_type == "csv":
        print("CSV Data:")
        for row in document["content"]:
            print(row)

    elif file_type == "json":
        print("JSON Data:")
        print(json.dumps(document["content"], indent=2))

    elif file_type == "text":
        print("Text Data:")
        print(document["content"])

    elif file_type == "image":
        output_path = f"output_{file_name}"
        with open(output_path, "wb") as f:
            f.write(document["data"])
        messagebox.showinfo("File Retrieved", f"Image saved to {output_path}")
        
        if os.name == 'nt':  # Windows
            os.startfile(output_path)
        elif os.name == 'posix':  # macOS or Linux
            os.system(f"open '{output_path}'")

    else:
        print(f"Unsupported file type: {file_type}")

# Function to handle file upload process
def upload_file():
    name = name_entry.get()
    if not name:
        messagebox.showerror("Input Error", "Please enter your name.")
        return
    file_path = filedialog.askopenfilename(title="Select a file")
    if file_path:
        store_user_file(name, file_path)

# Set up customtkinter UI
app = ctk.CTk()
app.geometry("400x350")
app.title("File Upload and Retrieval")

# User Name Section
name_label = ctk.CTkLabel(app, text="Enter your name:")
name_label.pack(pady=(10, 5))

name_entry = ctk.CTkEntry(app, width=300)
name_entry.pack(pady=5)

# Button to upload a file
upload_button = ctk.CTkButton(app, text="Upload File", command=upload_file)
upload_button.pack(pady=(20, 10))

# Separator
separator = ctk.CTkLabel(app, text="---------------------")
separator.pack(pady=10)

# Retrieval Section
retrieve_label = ctk.CTkLabel(app, text="Retrieve a File")
retrieve_label.pack(pady=(20, 5))

file_name_entry = ctk.CTkEntry(app, width=300, placeholder_text="Enter file name (e.g., example.pdf)")
file_name_entry.pack(pady=5)

# Button to retrieve a file
retrieve_button = ctk.CTkButton(app, text="Retrieve File", command=retrieve_and_open_file)
retrieve_button.pack(pady=20)

app.mainloop()

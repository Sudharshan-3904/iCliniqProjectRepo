import os
import json
import csv
from pymongo import MongoClient
from bson import Binary
from datetime import datetime
from tkinter import Tk, filedialog, messagebox

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["user_files_db"]
collection = db["user_uploads"]

# Function to store the user's file in MongoDB
def store_user_file(name, file_path, category):
    _, file_extension = os.path.splitext(file_path)
    
    # Get the current date and time
    now = datetime.now()

    # Fetch date and time separately as strings
    current_date = now.strftime("%Y-%m-%d")  # Format as YYYY-MM-DD
    current_time = now.strftime("%H:%M:%S")  # Format as HH:MM:SS
    
    document = {
        "user_name": name,
        "file_name": os.path.basename(file_path),
        "category": category,
        "date_upload": current_date,  # Store date as string
        "time_upload": current_time   # Store time as string
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
        print(f"Error: Unsupported file type: {file_extension}")
        return

    collection.insert_one(document)
    print(f"{file_extension.upper()} data stored for {name} under category {category}.")

# Function to open and retrieve stored file
def retrieve_and_open_file(user_name, file_name):
    document = collection.find_one({"user_name": user_name, "file_name": file_name})
    
    if not document:
        print(f"No file found for {user_name} with name {file_name}")
        return

    file_type = document.get("file_type")
    output_path = f"output_{file_name}"

    if file_type in ["pdf", "docx", "image"]:
        with open(output_path, "wb") as f:
            f.write(document["data"])
        print(f"{file_type.upper()} file saved to {output_path}")
        
        # Open the file with the default application
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

    else:
        print(f"Unsupported file type: {file_type}")

# Function to handle file upload process
def upload_file():
    name = input("Enter your name: ")
    if not name:
        print("Input Error: Please enter your name.")
        return

    # Prompt for category
    category = input("Enter the category (e.g., MRI, CT, X-ray): ")
    
    # Open file dialog for file selection
    root = Tk()
    root.withdraw()  # Hide the main Tkinter window
    file_path = filedialog.askopenfilename(title="Select a file")
    root.destroy()  # Close the Tkinter instance

    if file_path:
        store_user_file(name, file_path, category)

# Function to handle file retrieval process
def retrieve_file():
    user_name = input("Enter the user name : ")
    file_name = input("Enter the file name (e.g., example.pdf): ")
    retrieve_and_open_file(user_name, file_name)

# Main execution
if __name__ == "__main__":
    while True:
        action = input("\nSelect an action: [1] Upload File [2] Retrieve File [3] Exit\nEnter choice: ")
        if action == "1":
            upload_file()
        elif action == "2":
            retrieve_file()
        elif action == "3":
            print("Exiting.")
            break
        else:
            print("Invalid choice. Please select again.")

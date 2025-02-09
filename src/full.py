import sqlite3
import json
from uuid import uuid4
from werkzeug.security import generate_password_hash, check_password_hash
import requests
import os
import pandas as pd
import csv
from pymongo import MongoClient
from bson import Binary
from datetime import datetime
from tkinter import Tk, filedialog

class Auth:
    def __init__(self):
        self.db_file_path = 'data\\users.db'
        self._init_db()
    
    def _init_db(self):
        conn = sqlite3.connect(self.db_file_path)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            username TEXT UNIQUE NOT NULL,
                            password TEXT NOT NULL)''')
        conn.commit()
        conn.close()
    
    def register(self, username: str, password: str) -> bool:
        conn = sqlite3.connect(self.db_file_path)
        cursor = conn.cursor()
        hashed_password = generate_password_hash(password)
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", 
                         (username, hashed_password))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def login(self, username: str, password: str) -> tuple[bool, int]:
        conn = sqlite3.connect(self.db_file_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        user = cursor.fetchone()
        conn.close()
        
        if user and check_password_hash(user[2], password):
            return True, user[0]
        return False, -1

class Chatbot:
    MODEL_URL = "http://127.0.0.1:1234/v1/chat/completions"

    def __init__(self) -> None:
        self.db_file_path = 'data\\chatbot.db'
        self.init_db()
        self.current_chat_id = None

    def init_db(self) -> None:
        conn = sqlite3.connect(self.db_file_path)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS chats (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id INTEGER,
                            chat_id TEXT,
                            title TEXT,
                            messages TEXT,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        conn.commit()
        conn.close()

    def chat_with_model(self, user_id: int, user_input: str) -> str:
        conn = sqlite3.connect(self.db_file_path)
        cursor = conn.cursor()
        
        if not self.current_chat_id:
            self.current_chat_id = str(uuid4())
            conversation_history = []
        else:
            cursor.execute("SELECT messages FROM chats WHERE user_id=? AND chat_id=?", 
                         (user_id, self.current_chat_id))
            result = cursor.fetchone()
            conversation_history = json.loads(result[0]) if result else []
        
        payload = {
            "model": "phi-4",
            "messages": conversation_history + [{"role": "user", "content": user_input}],
            "temperature": 0.8,
            "max_tokens": 1000,
            "top_k": 40,
            "repeat_penalty": 1.1,
            "top_p": 0.95,
            "min_p": 0.05,
        }
        
        try:
            response = requests.post(self.MODEL_URL, json=payload)
            response.raise_for_status()
            reply = response.json()['choices'][0]['message']['content']
            
            conversation_history.append({"role": "assistant", "content": reply})
            cursor.execute(
                "INSERT OR REPLACE INTO chats (user_id, chat_id, title, messages) VALUES (?, ?, ?, ?)",
                (user_id, self.current_chat_id, user_input[:30], json.dumps(conversation_history))
            )
            conn.commit()
            return reply
        except requests.RequestException as e:
            return f"Error communicating with model: {e}"
        finally:
            conn.close()

    def get_chat_history(self, user_id: int) -> list:
        if not self.current_chat_id:
            return []
        
        conn = sqlite3.connect(self.db_file_path)
        cursor = conn.cursor()
        cursor.execute("SELECT messages FROM chats WHERE user_id=? AND chat_id=?", 
                      (user_id, self.current_chat_id))
        result = cursor.fetchone()
        conn.close()
        
        return json.loads(result[0]) if result else []

    def start_new_chat(self):
        self.current_chat_id = None

class FileStorage:
    def __init__(self):
        self.client = MongoClient("mongodb://localhost:27017/")
        self.db = self.client["user_files_db"]
        self.collection = self.db["user_uploads"]

    def store_file(self, user_id: int, file_path: str, category: str) -> None:
        _, file_extension = os.path.splitext(file_path)
        now = datetime.now()
        
        document = {
            "user_id": user_id,
            "file_name": os.path.basename(file_path),
            "category": category,
            "date_upload": now.strftime("%Y-%m-%d"),
            "time_upload": now.strftime("%H:%M:%S")
        }

        with open(file_path, "rb") as f:
            if file_extension in [".csv", ".json", ".txt"]:
                document["content"] = f.read().decode()
                document["file_type"] = file_extension[1:]
            else:
                document["data"] = Binary(f.read())
                document["file_type"] = file_extension[1:]

        self.collection.insert_one(document)

    def retrieve_file(self, user_id: int, file_name: str) -> str:
        document = self.collection.find_one({"user_id": user_id, "file_name": file_name})
        if not document:
            return ""
            
        if "content" in document:
            return document["content"]
        
        output_path = f"output_{file_name}"
        with open(output_path, "wb") as f:
            f.write(document["data"])
        return output_path

class FileProcessor:
    def __init__(self):
        self.data = None

    def load_data(self, data) -> None:
        self.data = pd.DataFrame(data)
    
    def filter_data(self, column: str, condition: str):
        if self.data is None or column not in self.data.columns:
            return None
        return self.data.query(f"`{column}` {condition}")

    def sort_data(self, column: str, ascending: bool = True):
        if self.data is None or column not in self.data.columns:
            return None
        return self.data.sort_values(by=column, ascending=ascending)

class IClinique:
    def __init__(self):
        self.auth = Auth()
        self.chatbot = Chatbot()
        self.file_storage = FileStorage()
        self.file_processor = FileProcessor()
        self.current_user = None
        
    def login(self, username: str, password: str) -> bool:
        success, user_id = self.auth.login(username, password)
        if success:
            self.current_user = user_id
            return True
        return False
    
    def register(self, username: str, password: str) -> bool:
        return self.auth.register(username, password)
    
    def chat(self, user_input: str) -> str:
        if not self.current_user:
            return "Please login first"
        return self.chatbot.chat_with_model(self.current_user, user_input)
    
    def upload_file(self, category: str) -> None:
        if not self.current_user:
            return
            
        root = Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(title="Select a file")
        root.destroy()
        
        if file_path:
            self.file_storage.store_file(self.current_user, file_path, category)
    
    def retrieve_file(self, filename: str) -> None:
        if not self.current_user:
            return
        file_data = self.file_storage.retrieve_file(self.current_user, filename)
        if file_data:
            self.file_processor.load_data(file_data)
    
    def filter_file_data(self, column: str, condition: str):
        return self.file_processor.filter_data(column, condition)
    
    def sort_file_data(self, column: str, ascending: bool = True):
        return self.file_processor.sort_data(column, ascending)
    
    def get_chat_history(self) -> list:
        if not self.current_user:
            return []
        return self.chatbot.get_chat_history(self.current_user)
    
    def start_new_chat(self) -> None:
        self.chatbot.start_new_chat()
    
    def logout(self) -> None:
        self.current_user = None
import sqlite3
import json
from uuid import uuid4
from werkzeug.security import generate_password_hash, check_password_hash
import requests
import os
import pandas as pd
import re
from io import StringIO
from pymongo import MongoClient
from bson.binary import Binary
from datetime import datetime
import time
from unstract.llmwhisperer import LLMWhispererClientV2
import os
import dotenv
from tabulate import tabulate

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
        self.medi_bot_model = "meditron-7b"
        self.init_db()
        self.system_prompt = {"role": "system", "content": "Provide clear and concise medical instructions or information in simple language. Avoid academic discussions or references to research papers."}
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

    def chat_with_model(self, user_id: int, user_input: str, query_df: pd.DataFrame = pd.DataFrame()) -> str:
        conn = sqlite3.connect(self.db_file_path)
        cursor = conn.cursor()
        
        if not self.current_chat_id:
            self.current_chat_id = str(uuid4())
            conversation_history = []
        else:
            cursor.execute("SELECT messages FROM chats WHERE user_id=? AND chat_id= ?", 
                           (user_id, self.current_chat_id))
            result = cursor.fetchone()
            conversation_history = json.loads(result[0]) if result else []
        

        print("user input: ", user_input)
        payload = {
            "model": self.medi_bot_model,
            # "messages": conversation_history + [self.system_prompt, {"role": "user", "content": f"{user_input}, " + "```{}```".format(query_df.to_string() if not query_df.empty else "")}],
            # "messages": [self.system_prompt, {"role": "user", "content": f"{user_input}, " + (("```{}```".format(query_df.to_string())) if not query_df.empty else "")}],
            "messages": [self.system_prompt, {"role": "user", "content": user_input}],
            "temperature": 0.05,  
            "max_tokens": 150,  
            "top_k": 20,  
            "repeat_penalty": 2.0,  
            "top_p": 0.3,  
            "min_p": 0.4
        }
            
        print("Chatbot Class Entered")

        with open("algo_ops\\payloads\\to_medi_bot.txt", 'w') as f:
            f.write(json.dumps(payload))
        
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

class DataExtractor:
    def __init__(self):
        self.str_to_md_model = "granite-3.2-8b-instruct"
        self.extracted_text = ""
        self.extracted_md_table = ""
        self.file_path = ""
        self.extracted_df = None
        self.request_timeout = 5
    
    def load_env_data(self, api_key_name: str) -> str:
        dotenv.load_dotenv("data.env")
        key = os.getenv(api_key_name)
        key = str(key)

        return key if key else ""
    
    def get_table_string(self) -> None:
        llm_api_key = self.load_env_data("LLM_WHISPERER_API_KEY")
        print("Got key, pinging for structure")

        client = LLMWhispererClientV2(base_url="https://llmwhisperer-api.us-central.unstract.com/api/v2", api_key=llm_api_key)

        result = client.whisper(file_path=self.file_path)

        while True:
            status = client.whisper_status(whisper_hash=result["whisper_hash"])
            if status["status"] == "processed":
                resultx = client.whisper_retrieve(
                    whisper_hash=result["whisper_hash"]
                )
                break
            
            time.sleep(self.request_timeout)
        
        print("Got table String")
        
        with open("algo_ops\\texts\\extracted_struct_str.txt", 'w') as f:
            f.write(resultx['extraction']['result_text'])
        
        self.extracted_text = resultx['extraction']['result_text']
    
    def get_markdown_table(self) -> None:
        print("Got string, pinging for markdown table")

        if self.extracted_text == "":
            return ""
        
        MODEL_URL = "http://127.0.0.1:1234/v1/chat/completions"

        payload = {
            "model": self.str_to_md_model,
            "messages": [{"role": "user", "content": f"the output should have all the tables in the following text as separate tables in markdown format ensure that the return string only has the markdown code```{self.extracted_text}```"}],
            "temperature": 0.2,
            "max_tokens": 15000,
            "top_k": 40,
            "repeat_penalty": 1.0,
            "top_p": 0.3,
            "min_p": 0.05,
            }
        
        with open("algo_ops\\payloads\\to_granite.txt", 'w') as f:
            f.write(json.dumps(payload))
        
        try:
            response = requests.post(MODEL_URL, json=payload)
            response.raise_for_status()
            reply = response.json()['choices'][0]['message']['content']
        except requests.RequestException as e:
            return None
        
        with open("algo_ops\\texts\\extracted_md_table.md", 'w') as f:
            f.write(reply)
        
        self.extracted_md_table = reply

    def create_dataframe(self) -> None:
        print("Got Markdown Table, pinging for dataframe")
        while "```" in self.extracted_md_table:
            self.extracted_md_table = self.extracted_md_table.replace("```", "")
        
        lines = self.extracted_md_table.strip().split('\n')
        headers = [header.strip() for header in lines[0].split('|') if header]

        data = []
        for line in lines[2:]:
            row = [cell.strip() for cell in line.split('|') if cell]
            data.append(row)
        
        try:
            print(f"Columns: {headers}")
            print(f"Number of rows: {len(data)}")
            df = pd.DataFrame(data, columns=headers)
            df.to_csv("algo_ops\\texts\\extracted_table.csv", index=False)
            print("Got Data Frame")
            self.extracted_df = df
        except Exception as e:
            print(f"Error creating DataFrame: {e}")
            self.extracted_df = pd.DataFrame()


    # TODO: Restructure the code to ping llm whisperer for the file path and not the file name
    def extract_df_from_file(self, file_path: str) -> pd.DataFrame:
        # if not os.path.isfile(file_path):
        #     raise FileNotFoundError(f"File not found: {file_path}\n Choose an existing File")
        # print("Got File Path")
        
        # self.file_path = file_path
        # self.get_table_string()

        with open("algo_ops\\texts\\extracted_struct_str.txt", 'r') as f:
            self.extracted_text = f.read()

        self.get_markdown_table()
        self.create_dataframe()

        return self.extracted_df if self.extracted_df is not None else pd.DataFrame()

class ICliniq:
    def __init__(self):
        self.auth = Auth()
        self.chatbot = Chatbot()
        self.file_storage = FileStorage()
        self.file_processor = FileProcessor()
        self.data_extractor = DataExtractor()
        self.extracted_df = pd.DataFrame() 
        self.current_user = None
        self.uploaded_file_path = ""
        
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
        
        if self.uploaded_file_path:
            self.extracted_df = self.data_extractor.extract_df_from_file(self.uploaded_file_path)
        else:
            self.extracted_df = pd.DataFrame()

        print("iClinique Class Entered")
        return self.chatbot.chat_with_model(self.current_user, user_input, self.extracted_df)
    
    def upload_file(self, category: str, file_path: str = "") -> None:
        if not self.current_user:
            return
        
        self.uploaded_file_path = file_path
        print("Gotten File Path")

        # TODO -Reenable the file storage functionality
        # self.file_storage.store_file(self.current_user, file_path, category)
        # self.data_extractor.file_path = self.uploaded_file_path
        # BUG - File is being extrcated as soon as uploaded. clarify for further details
        self.extracted_df = self.data_extractor.extract_df_from_file(self.uploaded_file_path)
    
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


# TODO - Test the validity of the responses to any given string
thing = ICliniq()
thing.login("sujit", "sujit")
thing.upload_file("test", "algo_ops\\texts\\extracted_struct_str.txt")
res = thing.chat("What is adviced in the report")
print(res)

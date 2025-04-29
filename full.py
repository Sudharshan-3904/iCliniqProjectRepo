"""
iCliniq Medical Assistant System
-------------------------------

This is the main file for the iCliniq system, containing core classes and methods.
It serves as the entry point and handles system initialization and main execution loop.

Key Components:
- Authentication (Auth): Manages user authentication and session handling
- Chatbot: Handles medical chat interactions and response generation
- File Management: Handles document storage and retrieval
- Data Processing: Manages medical data extraction and processing

Technical Stack:
- Database: SQLite (user auth) + MongoDB (file storage)
- AI Model: gemma-3-12b-it for medical chat
- File Processing: LLMWhisperer for data extraction

"""

import sqlite3
import json
from werkzeug.security import generate_password_hash, check_password_hash
import requests
import os
import pandas as pd
from pymongo import MongoClient
from bson.binary import Binary
from datetime import datetime
import time
from unstract.llmwhisperer import LLMWhispererClientV2
import os
import dotenv
import logging
from logging.handlers import RotatingFileHandler
from tenacity import retry, stop_after_attempt, wait_exponential

def setup_logging() -> logging.Logger:
    """
    Configure and initialize the application's logging system.
    
    Creates a rotating file handler that:
    - Stores logs in the 'logs' directory
    - Rotates files at 10MB
    - Keeps 5 backup files
    - Logs both to file and console
    
    Returns:
        logging.Logger: Configured logger instance
    """
    log_dir = 'logs'
    os.makedirs(log_dir, exist_ok=True)
    os.makedirs('testing_res', exist_ok=True)

    main_logger = logging.getLogger('iCliniq')

    if not main_logger.handlers:
        main_logger.setLevel(logging.INFO)

        # Configure rotating file handler
        file_handler = RotatingFileHandler(
            os.path.join(log_dir, 'app.log'),
            maxBytes=10485760,  # 10MB
            backupCount=5
        )

        # Configure console output
        console_handler = logging.StreamHandler()

        # Set uniform formatting for all logs
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        main_logger.addHandler(file_handler)
        main_logger.addHandler(console_handler)

    return main_logger

# Initialize main logger
logger = setup_logging()

# Disable propagation for component loggers to avoid duplicate logs
logging.getLogger('iCliniq.auth').propagate = False
logging.getLogger('iCliniq.chatbot').propagate = False
logging.getLogger('iCliniq.storage').propagate = False

# Custom Exception Classes
class DatabaseError(Exception):
    """
    Raised when database operations fail.
    
    Attributes:
        message (str): Error description
        operation (str): Failed database operation
        details (dict): Additional error context
    """
    def __init__(self, message: str, operation: str = None, details: dict = None):
        self.message = message
        self.operation = operation
        self.details = details or {}
        super().__init__(self.message)

class APIError(Exception):
    """
    Raised when external API communications fail.
    
    Attributes:
        message (str): Error description
        endpoint (str): Failed API endpoint
        status_code (int): HTTP status code
    """
    def __init__(self, message: str, endpoint: str = None, status_code: int = None):
        self.message = message
        self.endpoint = endpoint
        self.status_code = status_code
        super().__init__(self.message)

class FileProcessingError(Exception):
    """File operation failures"""
    def __init__(self, message: str, file_path: str = None, operation: str = None):
        self.message = message
        self.file_path = file_path
        self.operation = operation
        super().__init__(self.message)

class AuthenticationError(Exception):
    """Authentication and authorization failures"""
    def __init__(self, message: str, user: str = None, action: str = None):
        self.message = message
        self.user = user
        self.action = action
        super().__init__(self.message)

class DataProcessingError(Exception):
    """Data processing and transformation failures"""
    def __init__(self, message: str, data_type: str = None, operation: str = None):
        self.message = message
        self.data_type = data_type
        self.operation = operation
        super().__init__(self.message)

class Auth:
    """
    Singleton class handling user authentication and session management.
    
    Uses SQLite database for storing user credentials with secure password hashing.
    Implements singleton pattern to ensure single database connection pool.
    
    Attributes:
        db_file_path (str): Path to SQLite database file
        logger (Logger): Component-specific logger instance
    """
    _instance = None
    _initialized = False

    def __new__(cls):
        """Ensure single instance creation (Singleton pattern)"""
        if cls._instance is None:
            cls._instance = super(Auth, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize authentication system and database connection"""
        if not Auth._initialized:
            self.logger = logging.getLogger('iCliniq.auth')
            try:
                os.makedirs('data', exist_ok=True)
                self.db_file_path = 'data\\users.db'
                self.logger.info("Initializing authentication system")
                self._init_db()
                Auth._initialized = True
            except sqlite3.Error as e:
                self.logger.error(f"Database initialization failed: {e}", exc_info=True)
                raise DatabaseError(
                    message="Failed to initialize authentication database",
                    operation="init_db",
                    details={"error": str(e)}
                )

    def _init_db(self):
        """
        Initialize SQLite database and create users table if not exists.
        
        Table Schema:
            - id: AUTO INCREMENT PRIMARY KEY
            - username: UNIQUE TEXT
            - password: Hashed password TEXT
        
        Raises:
            RuntimeError: If database initialization fails
        """
        try:
            if not os.path.exists(self.db_file_path):
                os.makedirs(os.path.dirname(self.db_file_path), exist_ok=True)
            conn = sqlite3.connect(self.db_file_path)
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                username TEXT UNIQUE NOT NULL,
                                password TEXT NOT NULL)''')
            conn.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"Database initialization failed: {e}")

    def register(self, username: str, password: str) -> bool:
        self.logger.info(f"Attempting to register user: {username}")
        conn = None
        try:
            conn = sqlite3.connect(self.db_file_path)
            cursor = conn.cursor()
            hashed_password = generate_password_hash(password)

            cursor.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, hashed_password)
            )
            conn.commit()

            self.logger.info(f"Successfully registered user: {username}")
            return True

        except sqlite3.IntegrityError as e:
            self.logger.warning(
                f"Registration failed - username already exists: {username}",
                exc_info=True
            )
            raise AuthenticationError(
                message="Username already exists",
                user=username,
                action="register"
            )
        except sqlite3.Error as e:
            self.logger.error(f"Database error during registration: {e}", exc_info=True)
            raise DatabaseError(
                message="Registration failed due to database error",
                operation="register",
                details={"username": username, "error": str(e)}
            )
        finally:
            if conn:
                conn.close()

    def login(self, username: str, password: str) -> tuple[bool, int]:
        conn = sqlite3.connect(self.db_file_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[2], password):
            return (True, user[0])
        return False, -1

class Chatbot:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Chatbot, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not Chatbot._initialized:
            self.logger = logging.getLogger('iCliniq.chatbot')
            self.MODEL_URL = "http://127.0.0.1:1234/v1/chat/completions"
            self.logger.info("Initializing chatbot system")
            self._setup()
            Chatbot._initialized = True

    def _setup(self):
        self.db_file_path = 'data\\chatbot.db'
        self.medi_bot_model = "gemma-3-12b-it"
        self.init_db()
        self.system_prompt = {"role": "system", "content": "You are a medical chatbot. You are doing to do differential diagnosis when the user presents you with a set of symptoms. Explain in a short paragraph except when the user specifically says to. Ask basic information about the user when needed."}
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

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    def chat_with_model(self, user_id: int, user_input: str, query_df: pd.DataFrame = pd.DataFrame()) -> str:
        self.logger.info(f"Processing chat request for user_id: {user_id}")
        try:
            payload = self._prepare_payload(user_id, user_input, query_df)
            self.logger.debug(f"Prepared payload for model request: {payload}")

            response = requests.post(self.MODEL_URL, json=payload)
            response.raise_for_status()

            reply = response.json()['choices'][0]['message']['content']
            self.logger.info(f"Successfully received model response for user_id: {user_id}")

            self._store_chat_history(user_id, user_input, reply)

            return reply

        except requests.RequestException as e:
            self.logger.error(f"API request failed: {e}", exc_info=True)
            raise APIError(
                message="Failed to communicate with chat model",
                endpoint=self.MODEL_URL,
                status_code=getattr(e.response, 'status_code', None)
            )
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse API response: {e}", exc_info=True)
            raise DataProcessingError(
                message="Invalid response format from chat model",
                data_type="json",
                operation="parse_response"
            )

    def _prepare_payload(self, user_id, user_input: str, query_df: pd.DataFrame) -> dict:
        try:
            conn = sqlite3.connect(self.db_file_path)
            cursor = conn.cursor()

            if not self.current_chat_id:
                self.current_chat_id = user_id
            else:
                cursor.execute("SELECT messages FROM chats WHERE user_id=? AND chat_id= ?",
                               (user_id, self.current_chat_id))

            payload = {
                "model": self.medi_bot_model,
                "messages": [self.system_prompt, {"role": "user", "content": f"{user_input}" + ((", ```{}```".format(query_df.to_string())) if not query_df.empty else "")}],
                "temperature": 0.0,
                "max_tokens": 500,
                "top_k": 0,
                "top_p": 1.0,
                "min_p": 0.4
            }

            with open("algo_ops\\payloads\\to_medi_bot.txt", 'w') as f:
                f.write(json.dumps(payload))

            return payload
        finally:
            if conn:
                conn.close()

    def _store_chat_history(self, user_id: int, user_input: str, reply: str) -> None:
        try:
            conn = sqlite3.connect(self.db_file_path)
            cursor = conn.cursor()

            conversation_history = self._get_conversation_history(user_id)
            conversation_history.append({"role": "user", "content": user_input})
            conversation_history.append({"role": "assistant", "content": reply})

            cursor.execute(
                "INSERT OR REPLACE INTO chats (user_id, chat_id, title, messages) VALUES (?, ?, ?, ?)",
                (user_id, self.current_chat_id, user_input[:30], json.dumps(conversation_history))
            )
            conn.commit()
        finally:
            if conn:
                conn.close()

    def _get_conversation_history(self, user_id: int) -> list:
        try:
            conn = sqlite3.connect(self.db_file_path)
            cursor = conn.cursor()
            cursor.execute("SELECT messages FROM chats WHERE user_id=? AND chat_id=?",
                           (user_id, self.current_chat_id))
            result = cursor.fetchone()
            return json.loads(result[0]) if result else []
        finally:
            if conn:
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
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FileStorage, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not FileStorage._initialized:
            self.logger = logging.getLogger('iCliniq.storage')
            try:
                self.client = MongoClient("mongodb://localhost:27017/")
                self.db = self.client["user_files_db"]
                self.collection = self.db["user_uploads"]
                self.logger.info("Successfully initialized MongoDB connection")
                FileStorage._initialized = True
            except Exception as e:
                self.logger.error("Failed to connect to MongoDB", exc_info=True)
                raise DatabaseError(
                    message="Failed to connect to MongoDB",
                    operation="init_connection",
                    details={"error": str(e)}
                )

    def store_file(self, user_id: int, file_path: str, category: str) -> None:
        self.logger.info(f"Attempting to store file for user_id: {user_id}, path: {file_path}")
        try:
            if not os.path.exists(file_path):
                self.logger.error(f"File not found: {file_path}")
                raise FileProcessingError(
                    message="File not found",
                    file_path=file_path,
                    operation="store_file"
                )

            with open(file_path, "rb") as f:
                file_data = Binary(f.read())

            document = {
                "user_id": user_id,
                "file_name": os.path.basename(file_path),
                "category": category,
                "data": file_data,
                "uploaded_at": datetime.now()
            }

            self.collection.insert_one(document)
            self.logger.info(f"Successfully stored file for user_id: {user_id}")

        except IOError as e:
            self.logger.error(f"Failed to read file: {e}", exc_info=True)
            raise FileProcessingError(
                message="Failed to read file",
                file_path=file_path,
                operation="read"
            )
        except Exception as e:
            self.logger.error(f"MongoDB operation failed: {e}", exc_info=True)
            raise DatabaseError(
                message="Failed to store file in database",
                operation="insert_file",
                details={"user_id": user_id, "file_path": file_path}
            )

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
        try:
            os.makedirs("algo_ops\\texts", exist_ok=True)
            os.makedirs("algo_ops\\payloads", exist_ok=True)

            llm_api_key = self.load_env_data("LLM_WHISPERER_API_KEY")
            if not llm_api_key:
                raise ValueError("LLM_WHISPERER_API_KEY not found in environment")

            client = LLMWhispererClientV2(base_url="https://llmwhisperer-api.us-central.unstract.com/api/v2",
                                        api_key=llm_api_key)

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
        except requests.RequestException as e:
            raise RuntimeError(f"API request failed: {e}")
        except ValueError as e:
            raise
        except Exception as e:
            raise RuntimeError(f"Table extraction failed: {e}")

    def get_markdown_table(self) -> None:
        print("Got string, pinging for markdown table")

        if self.extracted_text == "":
            return ""

        MODEL_URL = "http://127.0.0.1:1234/v1/chat/completions"

        payload = {
            "model": self.str_to_md_model,
            "messages": [{"role": "user", "content": f"the output should have all the tables in the following text as separate tables in markdown format ensure that the return string only has the markdown code```{self.extracted_text}```"}],
            "temperature": 0.2,
            "max_tokens": 300,
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
            self.extracted_df = df
        except Exception as e:
            print(f"Error creating DataFrame: {e}")
            self.extracted_df = pd.DataFrame()


    def extract_df_from_file(self, file_path: str) -> pd.DataFrame:
        if ("/" in file_path) or ("\\\\" in file_path):
            while '/' in file_path:
                file_path = file_path.replace('/', '\\')
            while '\\' in file_path:
                file_path = file_path.replace('\\', '\\\\')

        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"File not found: {file_path}\n Choose an existing File")

        try:
            self.file_path = file_path
            self.get_table_string()
            self.get_markdown_table()
            self.create_dataframe()
        except Exception as e:
            print(f"Error processing file: {e}")

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
        if self.current_user == 0:
            return "Please login first"

        if self.extracted_df is None:
            self.extracted_df = pd.DataFrame()

        return self.chatbot.chat_with_model(self.current_user, user_input, self.extracted_df)

    def upload_file(self, category: str, file_path: str = "") -> None:
        if not self.current_user:
            return

        self.uploaded_file_path = file_path
        try:
            self.file_storage.store_file(self.current_user, file_path, category)
        except Exception as e:
            print(f"Error storing file: {e}")

        try:
            self.data_extractor.file_path = self.uploaded_file_path
            self.extracted_df = self.data_extractor.extract_df_from_file(self.uploaded_file_path)
        except Exception as e:
            print(f"Error extracting data from file: {e}")
            self.extracted_df = pd.DataFrame()

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

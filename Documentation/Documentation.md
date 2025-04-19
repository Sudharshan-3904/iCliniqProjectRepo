# iCliniq Medical Assistant Documentation

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Core Components](#core-components)
4. [Status & Development](#status--development)
5. [Future Roadmap](#future-roadmap)
6. [Technical Requirements](#technical-requirements)

## System Overview

The iCliniq Medical Assistant is an integrated platform providing medical assistance through AI-powered chatbot interactions, secure file management, and intelligent data processing capabilities. The system focuses on:

- Medical document processing and analysis
- AI-powered medical chat assistance
- Secure user authentication
- Structured data extraction
- Multi-lingual support

## Architecture

### Core Components

1. **Auth Service**

   - SQLite-based user authentication
   - Secure user registration and login
   - Session management

2. **Chatbot Engine**

   - AI model integration
   - Multi-lingual support
   - Chat history tracking
   - Context-aware responses

3. **File Management**

   - MongoDB storage backend
   - Support for multiple file types
   - Structured file organization

4. **Data Processing**
   - OCR capabilities
   - Table structure extraction
   - Data filtering and sorting
   - Format conversion

### Class Structure

#### 1. Auth

```python
class Auth:
    def __init__()
    def _init_db()
    def register(username: str, password: str) -> bool
    def login(username: str, password: str) -> tuple[bool, int]
```

#### 2. Chatbot

```python
class Chatbot:
    def __init__()
    def init_db()
    def chat_with_model(user_id: int, user_input: str, query_df: pd.DataFrame) -> str
    def get_chat_history(user_id: int) -> list
    def start_new_chat()
```

#### 3. FileStorage

```python
class FileStorage:
    def __init__()
    def store_file(user_id: int, file_path: str, category: str) -> None
    def retrieve_file(user_id: int, file_name: str) -> str
```

#### 4. FileProcessor

```python
class FileProcessor:
    def __init__()
    def load_data(data) -> None
    def filter_data(column: str, condition: str)
    def sort_data(column: str, ascending: bool)
```

#### 5. DataExtractor

```python
class DataExtractor:
    def __init__()
    def load_env_data(api_key_name: str) -> str
    def get_table_string() -> None
    def get_markdown_table() -> None
    def create_dataframe() -> None
    def extract_df_from_file(file_path: str) -> pd.DataFrame
```

#### 6. ICliniq (Main Interface)

```python
class ICliniq:
    def __init__()
    def login(username: str, password: str) -> bool
    def register(username: str, password: str) -> bool
    def chat(user_input: str) -> str
    def upload_file(category: str, file_path: str) -> None
    def retrieve_file(filename: str) -> None
    def filter_file_data(column: str, condition: str)
    def sort_file_data(column: str, ascending: bool)
    def get_chat_history() -> list
    def start_new_chat() -> None
    def logout() -> None
```

## Status & Development

### Current Features

1. Basic chatbot functionality with multilingual support
2. File storage using MongoDB and SQLite
3. OCR capabilities for document processing
4. Table structure extraction
5. Basic data filtering and searching

### In Development

1. RAG model implementation
2. Structured file storage improvements
3. Local ML model for translation
4. Enhanced data extraction capabilities

## Future Roadmap

### Short Term

- Implement RAG model for improved chat responses
- Enhance data extraction accuracy
- Optimize database queries
- Implement structured file storage

### Long Term

- Deploy ML/DL model for advanced OCR
- Implement YOLO v5 for document processing
- Create local translation model
- Scale compute resources

## Technical Requirements

### System Dependencies

- Python 3.8+
- MongoDB
- SQLite3
- Tesseract OCR
- PaddleOCR

### Computing Resources

- vCPUs for processing
- Sufficient vRAM for model operations
- Storage for document management
- Recommended: AWS EC2 or similar cloud compute

### Example Usage

```python
# Basic implementation example
thing = ICliniq()
thing.login("username", "password")
thing.upload_file("test", "path/to/file.txt")
response = thing.chat("What is advised in the report")
print(response)
```

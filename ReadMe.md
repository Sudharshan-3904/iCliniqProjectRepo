# iCliniq Medical Assistant

## System Overview
The iCliniq Medical Assistant is an integrated platform providing medical assistance through AI-powered chatbot interactions, secure file management, and intelligent data processing capabilities. The system consists of multiple components including:

- **Auth**: Handles user authentication via SQLite database
- **Chatbot**: Connects with an external AI model for medical chat-based responses
- **FileStorage**: Stores and retrieves files in a MongoDB database
- **FileProcessor**: Processes and filters medical data stored in files
- **DataExtractor**: Extracts tabular data from structured medical texts
- **ICliniq**: A higher-level class managing all functionalities together

## Key Features
- Medical document processing and analysis
- AI-powered medical chat assistance
- Secure user authentication
- Structured data extraction
- Multi-lingual support

## Technical Requirements

### System Dependencies
- Python 3.8+
- MongoDB
- SQLite3
- Tesseract OCR
- PaddleOCR

### Computing Resources
- Sufficient vCPUs for processing
- Adequate vRAM for model operations
- Storage for document management
- Recommended: AWS EC2 or similar cloud compute

## Modules and Classes

### 1. `Auth`
Handles user authentication and database management.

#### Methods:
- `__init__()`: Initializes the SQLite database
- `_init_db()`: Creates the users table if it does not exist
- `register(username: str, password: str) -> bool`: Registers a new user
- `login(username: str, password: str) -> tuple[bool, int]`: Logs in a user

### 2. `Chatbot`
Facilitates interactions with a chatbot model.

#### Methods:
- `__init__()`: Initializes chatbot database and parameters.
- `init_db()`: Creates the chats table.
- `chat_with_model(user_id: int, user_input: str, query_df: pd.DataFrame) -> str`: Sends user input to the chatbot.
- `get_chat_history(user_id: int) -> list`: Retrieves previous chat history.
- `start_new_chat()`: Starts a new chat session.

### 3. `FileStorage`
Stores and retrieves user-uploaded files in MongoDB.

#### Methods:
- `__init__()`: Initializes MongoDB connection.
- `store_file(user_id: int, file_path: str, category: str) -> None`: Stores files.
- `retrieve_file(user_id: int, file_name: str) -> str`: Retrieves stored files.

### 4. `FileProcessor`
Handles basic data operations such as filtering and sorting.

#### Methods:
- `__init__()`: Initializes data storage.
- `load_data(data) -> None`: Loads data into a DataFrame.
- `filter_data(column: str, condition: str)`: Filters data based on conditions.
- `sort_data(column: str, ascending: bool)`: Sorts data.

### 5. `DataExtractor`
Extracts structured data from text and converts it into a DataFrame.

#### Methods:
- `__init__()`: Initializes extraction parameters.
- `load_env_data(api_key_name: str) -> str`: Loads API keys from environment variables.
- `get_table_string() -> None`: Extracts table structure from text.
- `get_markdown_table() -> None`: Converts text tables to markdown format.
- `create_dataframe() -> None`: Converts markdown tables to DataFrame.
- `extract_df_from_file(file_path: str) -> pd.DataFrame`: Extracts structured data from a given file.

### 6. `ICliniq`
Main class integrating all functionalities.

#### Methods:
- `__init__()`: Initializes all components.
- `login(username: str, password: str) -> bool`: Logs in a user.
- `register(username: str, password: str) -> bool`: Registers a new user.
- `chat(user_input: str) -> str`: Sends input to the chatbot.
- `upload_file(category: str, file_path: str) -> None`: Uploads a file.
- `retrieve_file(filename: str) -> None`: Retrieves a stored file.
- `filter_file_data(column: str, condition: str)`: Filters data from files.
- `sort_file_data(column: str, ascending: bool)`: Sorts file data.
- `get_chat_history() -> list`: Retrieves chat history.
- `start_new_chat() -> None`: Starts a new chat.
- `logout() -> None`: Logs out the user.

## User Interfaces

### 1. Streamlit Interface
- Web-based interactive interface
- Real-time chat visualization
- File upload/download capabilities
- Data visualization features
- State-Managed

### 2. GUI (Graphical User Interface)
- Desktop application interface
- Native file system integration
- Local processing capabilities
- Offline mode support

### 3. CLI (Command Line Interface)
- Terminal-based interaction
- Scripting and automation support
- Batch processing capabilities
- Server deployment options

## Current Status & Development

### Implemented Features
- Basic chatbot functionality with multilingual support
- File storage using MongoDB and SQLite
- OCR capabilities for document processing
- Table structure extraction
- Basic data filtering and searching

### In Development
- RAG model implementation
- Structured file storage improvements
- Local ML model for translation
- Enhanced data extraction capabilities

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

## Basic Usage Example
```python
# Initialize and use the system
thing = ICliniq()
thing.login("username", "password")
thing.upload_file("test", "path/to/medical/report.txt")
response = thing.chat("What is advised in the report")
print(response)
```

## License
This project is licensed under the MIT License - see the LICENSE.md file for details.


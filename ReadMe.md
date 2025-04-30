# System Documentation

## System Overview

The system provides an integrated platform for user authentication, chatbot interactions, file storage and processing, and data extraction. It consists of multiple components including:

-   **Auth**: Handles user authentication via SQLite database.
-   **Chatbot**: Connects with an external AI model for chat-based responses.
-   **FileStorage**: Stores and retrieves files in a MongoDB database.
-   **FileProcessor**: Processes and filters data stored in files.
-   **DataExtractor**: Extracts tabular data from structured text.
-   **ICliniq**: A higher-level class managing all functionalities together.

## Modules and Classes

### 1. `Auth`

Handles user authentication and database management.

#### Methods:

-   `__init__()`: Initializes the SQLite database.
-   `_init_db()`: Creates the users table if it does not exist.
-   `register(username: str, password: str) -> bool`: Registers a new user.
-   `login(username: str, password: str) -> tuple[bool, int]`: Logs in a user.

### 2. `Chatbot`

Facilitates interactions with a chatbot model.

#### Methods:

-   `__init__()`: Initializes chatbot database and parameters.
-   `init_db()`: Creates the chats table.
-   `chat_with_model(user_id: int, user_input: str, query_df: pd.DataFrame) -> str`: Sends user input to the chatbot.
-   `get_chat_history(user_id: int) -> list`: Retrieves previous chat history.
-   `start_new_chat()`: Starts a new chat session.

### 3. `FileStorage`

Stores and retrieves user-uploaded files in MongoDB.

#### Methods:

-   `__init__()`: Initializes MongoDB connection.
-   `store_file(user_id: int, file_path: str, category: str) -> None`: Stores files.
-   `retrieve_file(user_id: int, file_name: str) -> str`: Retrieves stored files.

### 4. `FileProcessor`

Handles basic data operations such as filtering and sorting.

#### Methods:

-   `__init__()`: Initializes data storage.
-   `load_data(data) -> None`: Loads data into a DataFrame.
-   `filter_data(column: str, condition: str)`: Filters data based on conditions.
-   `sort_data(column: str, ascending: bool)`: Sorts data.

### 5. `DataExtractor`

Extracts structured data from text and converts it into a DataFrame.

#### Methods:

-   `__init__()`: Initializes extraction parameters.
-   `load_env_data(api_key_name: str) -> str`: Loads API keys from environment variables.
-   `get_table_string() -> None`: Extracts table structure from text.
-   `get_markdown_table() -> None`: Converts text tables to markdown format.
-   `create_dataframe() -> None`: Converts markdown tables to DataFrame.
-   `extract_df_from_file(file_path: str) -> pd.DataFrame`: Extracts structured data from a given file.

### 6. `ICliniq`

Main class integrating all functionalities.

#### Methods:

-   `__init__()`: Initializes all components.
-   `login(username: str, password: str) -> bool`: Logs in a user.
-   `register(username: str, password: str) -> bool`: Registers a new user.
-   `chat(user_input: str) -> str`: Sends input to the chatbot.
-   `upload_file(category: str, file_path: str) -> None`: Uploads a file.
-   `retrieve_file(filename: str) -> None`: Retrieves a stored file.
-   `filter_file_data(column: str, condition: str)`: Filters data from files.
-   `sort_file_data(column: str, ascending: bool)`: Sorts file data.
-   `get_chat_history() -> list`: Retrieves chat history.
-   `start_new_chat() -> None`: Starts a new chat.
-   `logout() -> None`: Logs out the user.

## System Execution

The system is executed using the `ICliniq` class. An example usage:

```python
thing = ICliniq()
thing.login("sujit", "sujit")
thing.upload_file("test", "algo_ops\\texts\\extracted_struct_str.txt")
res = thing.chat("What is advised in the report")
print(res)
```

## Future Improvements

-   Improve chatbot accuracy by refining queries.
-   Enhance error handling.
-   Optimize database queries for better performance.
-   Enable dynamic selection of AI models.

## Dependencies

The system requires the following Python libraries:

-   `sqlite3`: For user authentication and chat history storage.
-   `werkzeug.security`: For password hashing and verification.
-   `requests`: For making HTTP requests to external APIs.
-   `pandas`: For data manipulation and analysis.
-   `pymongo`: For file storage in MongoDB.
-   `bson.binary`: For handling binary data in MongoDB.
-   `dotenv`: For loading environment variables.
-   `unstract.llmwhisperer`: For interacting with the LLM Whisperer API.

Ensure all dependencies are installed before running the system.

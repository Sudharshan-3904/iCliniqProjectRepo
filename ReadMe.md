# ICliniq System Documentation

## 1. System Overview

ICliniq is an integrated healthcare management system that combines user authentication, AI-powered chat capabilities, and robust file management features. The system is designed to provide a secure, efficient, and user-friendly platform for healthcare-related interactions and data management.

## 2. Architecture

### 2.1 Core Components

-   **Authentication System (Auth)**
-   **AI Chatbot Interface (Chatbot)**
-   **File Management System (FileStorage)**
-   **Data Processing Engine (FileProcessor)**
-   **Main Integration Layer (ICliniq)**

### 2.2 Database Structure

-   **SQLite** database for user management
-   **MongoDB** for file storage
-   **Real-time** chat history storage

## 3. Technical Specifications

### 3.1 Authentication Module

-   Secure password hashing using **Werkzeug**
-   SQLite database for user credentials

**Features:**

-   User registration with unique username enforcement
-   Secure login with hashed password verification
-   Session management

### 3.2 Chatbot Module

-   Integration with local AI model (**phi-4**)

**Features:**

-   Conversation history tracking
-   Dynamic chat session management
-   Configurable model parameters
-   Error handling for API communication

### 3.3 File Management System

-   **MongoDB-based** storage solution

**Supported file types:**

-   CSV
-   JSON
-   TXT
-   Binary files

**Features:**

-   File categorization
-   Timestamp tracking
-   User-specific file storage
-   Secure retrieval system

### 3.4 Data Processing Capabilities

-   **Pandas-based** data analysis

**Features:**

-   Dynamic data loading
-   Column-based filtering
-   Customizable sorting
-   Data validation

## 4. Security Features

-   Password hashing
-   User authentication
-   Secure file storage
-   Session management
-   Database security

## 5. API Documentation

### 5.1 Authentication API

```python
register(username: str, password: str) -> bool
login(username: str, password: str) -> bool
```

### 5.2 Chatbot API

```python
chat(user_input: str) -> str
get_chat_history() -> list
start_new_chat() -> None
```

### 5.3 File Management API

```python
upload_file(category: str) -> None
retrieve_file(filename: str) -> None
filter_file_data(column: str, condition: str)
sort_file_data(column: str, ascending: bool = True)
```

## 6. Dependencies

```plaintext
- sqlite3
- werkzeug.security
- requests
- pandas
- pymongo
- tkinter
- json
- uuid
- os
- datetime
```

## 7. Installation and Setup

### 7.1 Prerequisites

-   Python 3.x
-   MongoDB server
-   Local AI model server

### 7.2 Configuration

-   MongoDB connection: `localhost:27017`
-   AI model endpoint: `http://127.0.0.1:1234/v1/chat/completions`
-   **Database paths:**
    -   Users: `data/users.db`
    -   Chatbot: `data/chatbot.db`

## 8. Usage Examples

### 8.1 System Initialization

```python
system = ICliniq()
```

### 8.2 User Authentication

```python
system.register("username", "password")
system.login("username", "password")
```

### 8.3 Chat Interaction

```python
response = system.chat("Hello, how can you help me?")
history = system.get_chat_history()
```

### 8.4 File Operations

```python
system.upload_file("medical_records")
system.retrieve_file("patient_data.csv")
```

## 9. Error Handling

-   Database connection errors
-   API communication failures
-   File processing errors
-   Authentication failures

## 10. Performance Considerations

-   Efficient database queries
-   Optimized file storage
-   Memory management for large files
-   Connection pooling

## 11. Future Enhancements

-   Multi-factor authentication
-   Enhanced data analytics
-   Real-time collaboration features
-   Extended file format support
-   Advanced chat capabilities

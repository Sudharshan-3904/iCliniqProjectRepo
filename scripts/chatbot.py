import argparse
import sqlite3
import json
from uuid import uuid4
from werkzeug.security import generate_password_hash, check_password_hash
import requests
import os
from datetime import datetime

MODEL_URL = "http://127.0.0.1:1234/v1/chat/completions"

def init_db():
    if not os.path.exists('chatbot.db'):
        conn = sqlite3.connect('chatbot.db')
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            username TEXT UNIQUE NOT NULL,
                            password TEXT NOT NULL)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS chats (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id INTEGER,
                            chat_id TEXT,
                            title TEXT,
                            messages TEXT,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY(user_id) REFERENCES users(id))''')
        conn.commit()
        conn.close()

def register_user(username, password):
    conn = sqlite3.connect('chatbot.db')
    cursor = conn.cursor()
    hashed_password = generate_password_hash(password)
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        print("Registration successful.")
    except sqlite3.IntegrityError:
        print("Username already exists.")
    finally:
        conn.close()

def login_user(username, password):
    conn = sqlite3.connect('chatbot.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=?", (username,))
    user = cursor.fetchone()
    conn.close()
    if user and check_password_hash(user[2], password):
        return user[0]
    else:
        print("Invalid credentials.")
        return None

def chat_with_model(user_id, user_input, chat_id=None):
    conn = sqlite3.connect('chatbot.db')
    cursor = conn.cursor()
    
    if not chat_id:
        chat_id = str(uuid4())
        conversation_history = []
    else:
        cursor.execute("SELECT messages FROM chats WHERE user_id=? AND chat_id=?", (user_id, chat_id))
        result = cursor.fetchone()
        conversation_history = json.loads(result[0]) if result else []
    
    payload = {
        "model": "llama-3.2-3b-instruct",
        "messages": conversation_history + [{"role": "user", "content": user_input}],
        "temperature": 0.8,
        "max_tokens": 100,
        "top_k": 40,
        "repeat_penalty": 1.1,
        "top_p": 0.95,
        "min_p": 0.05,
    }
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(MODEL_URL, json=payload, headers=headers)
        response.raise_for_status()
        reply = response.json().get('choices', [{}])[0].get('message', {}).get('content', "No reply generated.")
        print(f"AI: {reply}")
        
        conversation_history.append({"role": "assistant", "content": reply})
        cursor.execute(
            "INSERT INTO chats (user_id, chat_id, title, messages, created_at) VALUES (?, ?, ?, ?, datetime('now'))",
            (user_id, chat_id, user_input[:30], json.dumps(conversation_history))
        )
        conn.commit()
    except requests.RequestException as e:
        print(f"Error communicating with model: {e}")
    finally:
        conn.close()

def main():
    parser = argparse.ArgumentParser(description="Chatbot CLI")
    parser.add_argument("--register", nargs=2, metavar=('username', 'password'), help="Register a new user")
    parser.add_argument("--login", nargs=2, metavar=('username', 'password'), help="Login with existing credentials")
    parser.add_argument("--chat", metavar='message', help="Chat with the AI model")
    parser.add_argument("--chat_id", metavar='chat_id', help="Specify a chat ID for continued conversation")
    args = parser.parse_args()

    init_db()

    if args.register:
        username, password = args.register
        register_user(username, password)
    elif args.login:
        username, password = args.login
        user_id = login_user(username, password)
        if user_id:
            print(f"Logged in as {username}")
            while True:
                user_input = input("You: ")
                if user_input.lower() in {"exit", "quit"}:
                    break
                chat_with_model(user_id, user_input, args.chat_id)
    elif args.chat:
        print("You need to login first to chat.")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

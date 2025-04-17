import sqlite3
import pandas as pd
import json
import requests
from uuid import uuid4


class Chatbot:
    MODEL_URL = "http://127.0.0.1:1234/v1/chat/completions"

    def __init__(self) -> None:
        self.db_file_path = 'data\\chatbot.db'
        self.medi_bot_model = "gemma-3-12b-it"
        self.init_db()
        self.system_prompt = {"role": "system", "content": "The output should be like a conversation from an experinced doctor. Make sure not to include any academic discussions or references to research papers."}
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
        # conn = sqlite3.connect(self.db_file_path)
        # cursor = conn.cursor()
        
        # if not self.current_chat_id:
        #     self.current_chat_id = str(uuid4())
        #     conversation_history = []
        # else:
        #     cursor.execute("SELECT messages FROM chats WHERE user_id=? AND chat_id= ?", 
        #                    (user_id, self.current_chat_id))
        #     result = cursor.fetchone()
        #     conversation_history = json.loads(result[0]) if result else []
        

        # print("user input: ", user_input)
        payload = {
            "model": self.medi_bot_model,
            # "messages": conversation_history + [self.system_prompt, {"role": "user", "content": f"{user_input}, " + "```{}```".format(query_df.to_string() if not query_df.empty else "")}],
            # "messages": [self.system_prompt, {"role": "user", "content": f"{user_input}, " + (("```{}```".format(query_df.to_string())) if not query_df.empty else "")}],
            "messages": [self.system_prompt, {"role": "user", "content": user_input}],
            "temperature": 0.0,
            "max_tokens": 150,  
            "top_k": 0,  
            # "repeat_penalty": 2.0,  
            "top_p": 1.0,  
            "min_p": 0.4
        }
            
        with open("algo_ops\\payloads\\to_medi_bot.txt", 'w') as f:
            f.write(json.dumps(payload))
        
        try:
            response = requests.post(self.MODEL_URL, json=payload)
            response.raise_for_status()
            reply = response.json()['choices'][0]['message']['content']
            
            # conversation_history.append({"role": "assistant", "content": reply})
            # cursor.execute(
            #     "INSERT OR REPLACE INTO chats (user_id, chat_id, title, messages) VALUES (?, ?, ?, ?)",
            #     (user_id, self.current_chat_id, user_input[:30], json.dumps(conversation_history))
            # )
            # conn.commit()
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


thing = Chatbot()
response = thing.chat_with_model(1, "first aid for dislocated shoulder")
print(response)
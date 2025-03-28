import dotenv
import os
from unstract.llmwhisperer import LLMWhispererClientV2
import requests
import time
import pandas as pd
import json


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

        print(result)

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
            "temperature": 0.8,
            "max_tokens": 15000,
            "top_k": 40,
            "repeat_penalty": 1.1,
            "top_p": 0.95,
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
            print(f"Nummber of columns: {len(headers)}")
            print(f"Number of rows: {len(data)}")
            df = pd.DataFrame(data, columns=headers)
            df.to_csv("algo_ops\\texts\\extracted_table.csv", index=False)
            print("Got Data Frame")
            self.extracted_df = df
        except Exception as e:
            print(f"Error creating DataFrame: {e}")
            self.extracted_df = pd.DataFrame()
    
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


thing = DataExtractor()
df = thing.extract_df_from_file(r"E:\Tester\iCliniq\sampleDocs\general_report.pdf")
print(df)
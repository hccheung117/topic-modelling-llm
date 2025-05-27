import os

import requests
from dotenv import load_dotenv

load_dotenv()

LLM_API_KEY = os.getenv("LLM_API_KEY")
LLM_BASE_URL = os.getenv("LLM_BASE_URL")


class Agent:
    def __init__(self, model: str, instructions: str):
        self.model = model
        self.instructions = instructions
        self.temperature = 0
        self.json_mode = False

    def configure(self, temperature=None, json_mode=None):
        if temperature is not None:
            self.temperature = temperature
        if json_mode is not None:
            self.json_mode = json_mode
        return self

    def complete(self, input: str):
        headers = {
            "Authorization": f"Bearer {LLM_API_KEY}",
            "Content-Type": "application/json",
        }

        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": self.instructions},
                {"role": "user", "content": input},
            ],
            "temperature": self.temperature,
            "json_mode": self.json_mode,
        }
        response = requests.post(
            LLM_BASE_URL + "/chat/completions", headers=headers, json=data
        )
        if response.ok:
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()
        else:
            response.raise_for_status()
            return None


def compute_embeddings(texts: list[str]):
    headers = {
        "Authorization": f"Bearer {LLM_API_KEY}",
        "Content-Type": "application/json",
    }
    data = {"input": texts, "model": "gemini-embedding-exp-03-07"}
    r = requests.post(LLM_BASE_URL + "/embeddings", headers=headers, json=data)
    r.raise_for_status()
    return [item["embedding"] for item in r.json()["data"]]
